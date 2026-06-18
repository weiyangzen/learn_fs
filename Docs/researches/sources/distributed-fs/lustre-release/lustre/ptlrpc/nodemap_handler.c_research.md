# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_handler.c

## Purpose
`nodemap_handler.c` is the central control plane for Lustre nodemaps. It owns the active nodemap configuration pointer, the global activation flag, nodemap lifecycle, member classification, ID/ACL mapping, range and banlist mutations, fileset policy, RBAC/capability/security properties, ioctl command dispatch, and module init/exit. The file coordinates in-memory state with MGS-backed IAM persistence through `nodemap_idx_*()` calls implemented elsewhere.

## Important APIs, types, and functions
Key global state is `bool nodemap_active`, `DEFINE_MUTEX(active_config_lock)`, and `struct nodemap_config *active_config`. The lock protects active configuration replacement, hash lookup/mutation, proc entry transfer, and member reclassification; `nodemap_active` is a lock-free copy used in hot mapping paths.

Important exported APIs include lookup/lifecycle (`nodemap_lookup_unlocked()`, `nodemap_lookup_sha()`, `nodemap_create()`, `nodemap_add()`, `nodemap_del()`, config alloc/dealloc/switch, module init/exit), classification/membership (`nodemap_classify_nid()`, `nodemap_add_member()`, `nodemap_del_member()`, `nodemap_member_switch()`), mapping (`nodemap_map_id()`, `nodemap_map_acl()`, `nodemap_map_suppgid()`, `nodemap_id_is_squashed()`, `nodemap_check_resource_ids()`, `nodemap_can_setquota()`), mutation setters for ranges, banlists, idmaps, offsets, filesets, RBAC/capabilities/security flags, and `server_iocontrol_nodemap()`.

## Control flow and behavior
Initialization creates debugfs state, allocates a config, creates the default nodemap, switches it active, then drops the temporary creation reference. Config switching transfers debugfs/stat pointers for same-name nodemaps, registers new entries, updates `active_config` and `nodemap_active`, deallocates the old config, and revokes locks if enforcement was disabled.

Client classification first honors a GSS-authenticated nodemap name when present and permitted, otherwise classifies by NID. `nodemap_classify_nid()` handles `0@lo`, checks ban ranges before regular ranges, and falls back to the default nodemap. ID mapping handles inactive/missing nodemap passthrough, offset unapply/apply, root exceptions, map-mode masks, trusted IDs, default squashing, explicit idmap lookup, and squash fallback. ACL mapping rewrites ACL_USER/ACL_GROUP entries and removes entries that map to squash IDs.

Range and banlist mutations validate conflicts, update interval-tree/list state, persist through `nodemap_idx_range_*()`, reclassify affected members, and revoke locks. Dynamic nodemaps must have a parent and ranges included within that parent. Fileset mutation supports IAM-backed primary and alternate filesets plus legacy llog compatibility, with parent-child constraints to prevent dynamic children widening namespace or read-write access.

`server_iocontrol_nodemap()` copies and validates a userspace `lustre_cfg`, handles read-only tests/SHA lookup separately, and routes most mutations through `cfg_nodemap_cmd()` or `cfg_nodemap_fileset_cmd()`.

## State and persistence
Persistent configuration is written through `nodemap_idx_*()` calls. Runtime state includes `active_config`, nodemap hash/SHA hash entries, range and ban interval trees, idmap rbtrees, alternate fileset rbtrees, member/subnodemap lists, dynamic nodemap count, refcounts, debugfs entries, and stats pointers. Fileset code has the most explicit undo handling; many scalar setters update memory then attempt persistence.

## Dependencies and integration points
The file integrates with LNet NID parsing/matching, libcfs hash/rhashtable, Linux rbtrees/rwsems/refcounts/crypto/capabilities, OBD exports and ioctls, POSIX ACL xattrs, LDLM lock revocation, ldebugfs registration, and MGS nodemap storage. MDT, layout, xattr, quota, and request paths consume its exported mapping and export lookup APIs.

## Risks and edge cases
High-risk areas are lock ordering across active config, range trees, idmap/fileset locks, and member locks; memory/persistence divergence when scalar `nodemap_idx_*()` updates fail; fileset undo failures; dynamic privilege escalation checks; GSS nodemap mismatch behavior; offset boundary/squash logic; and range/banlist conflict handling for large NIDs. `nodemap_del()` also deserves review because recursive calls pass a NULL llog-cleanup pointer while later code may write it if legacy filesets exist.

## Test signals
Exercise ioctl add/delete/range/idmap/offset/RBAC/fileset flows, persistence failure injection, dynamic parent-child restrictions, NID4 and large-NID classification, banlist reclassification, lock revocation, ACL mapping, offset boundaries, GSS SHA lookup, default nodemap rejection cases, and config reload/debugfs transfer.
