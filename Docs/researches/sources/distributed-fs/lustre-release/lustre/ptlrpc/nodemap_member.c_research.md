# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_member.c

## Purpose
`nodemap_member.c` manages live `obd_export` membership lists attached to nodemaps. It adds/removes exports, switches exports during reclassification, decides when nodemap changes require client lock revocation, and creates per-nodemap duplicated MDT/OST stats files on first use.

## Important APIs, types, and functions
Public functions are `nm_member_add()`, `nm_member_del()`, `nm_member_delete_list()`, `__nodemap_member_switch()`, `nm_member_reclassify_nodemap()`, `nm_member_revoke_locks()`, and `nm_member_revoke_locks_always()`. Internal helpers include `nm_register_obd_stats()`, `nm_member_exp_revoke()`, `idmaps_match()`, and `nodemap_change_need_update()`. A temporary rhashtable cache stores comparison results during reclassification.

## Control flow and behavior
`nm_member_add()` runs under `active_config_lock`, rejects NULL exports, detects duplicate membership, takes export and nodemap references, stores the nodemap in `ted_nodemap`, links the export, and registers stats. `nm_member_del()` unlinks the export, clears `ted_nodemap`, and drops the held references.

`__nodemap_member_switch()` moves a live export without ever making `ted_nodemap` NULL, replaces the old nodemap pointer, links into the new list, compares old and new security-relevant state, and revokes locks if the effective context changed or the export became banned. `nm_member_reclassify_nodemap()` iterates members, obtains peer NIDs, honors GSS-authenticated nodemap names when valid, otherwise classifies by NID, updates `exp_banned`, and switches exports as needed.

Lock revocation skips inactive nodemaps, recovery, non-MDT exports unless forced, loopback, and LWP connections.

## State and persistence
This file maintains runtime state only: export membership lists, export-to-nodemap pointers, refs, ban flags, duplicated stats pointers, and temporary comparison cache entries. It does not persist configuration.

## Dependencies and integration points
Dependencies include OBD exports/devices/types, Lustre stats/debugfs, LDLM lock revocation, LNet NIDs, import security references, nodemap lookup/classification APIs, idmap rbtrees, capabilities, and rhashtable. It is reached from connection setup/teardown through handler membership APIs.

## Risks and edge cases
Lock ordering is delicate: reclassification holds a member-list lock and may take another nodemap's member-list lock while relying on `active_config_lock` serialization. New security-relevant nodemap fields must be added to `nodemap_change_need_update()` or clients may keep stale cached permissions. Refcount balance across add/delete/switch is critical.

## Test signals
Test duplicate add, add/delete refcount balance, disconnect racing reclassification, range and banlist changes, GSS consistency checks, banned/unbanned transitions, lock revocation skip cases, comparison-cache behavior, and a field-change matrix for revocation.
