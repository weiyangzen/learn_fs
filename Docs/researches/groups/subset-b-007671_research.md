# subset-b-007671 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_handler.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_handler.c

## Purpose
`nodemap_handler.c` is the central control plane for Lustre nodemaps. It owns the active nodemap configuration pointer, the global activation flag, nodemap lifecycle, member classification, ID/ACL mapping, range and banlist mutations, fileset policy, RBAC/capability/security properties, ioctl command dispatch, and module init/exit. The file coordinates in-memory state with MGS-backed IAM persistence through `nodemap_idx_*()` calls implemented elsewhere.

## Important APIs, types, and functions
Key global state is `bool nodemap_active`, `DEFINE_MUTEX(active_config_lock)`, and `struct nodemap_config *active_config`. The lock protects active configuration replacement, hash lookup/mutation, proc entry transfer, and member reclassification; `nodemap_active` is a lock-free copy used in hot mapping paths.

Important exported APIs include:
- Lookup and lifecycle: `nodemap_lookup_unlocked()`, `nodemap_lookup_sha()`, `nodemap_getref()`, `nodemap_putref()`, `nodemap_create()`, `nodemap_add()`, `nodemap_del()`, `nodemap_config_alloc()`, `nodemap_config_dealloc()`, `nodemap_config_set_active()`, `nodemap_mod_init()`, `nodemap_mod_exit()`.
- Classification and membership: `nodemap_classify_nid()`, `nodemap_add_member()`, `nodemap_del_member()`, `nodemap_member_switch()`, `nm_member_revoke_all()`.
- Mapping: `nodemap_map_id()`, `nodemap_map_acl()`, `nodemap_map_suppgid()`, `nodemap_id_is_squashed()`, `nodemap_check_resource_ids()`, `nodemap_can_setquota()`.
- Configuration mutation: `nodemap_add_range()`, `nodemap_del_range()`, `nodemap_add_banlist()`, `nodemap_del_banlist()`, `nodemap_add_idmap()`, `nodemap_del_idmap()`, `nodemap_add_offset()`, `nodemap_del_offset()`, setters for allow-root, trusted IDs, deny-unknown, map mode, RBAC, squash IDs, audit, encryption, raise privileges, mount denial, GSS identification, SELinux policy, capabilities, and filesets.
- User entry points: `server_iocontrol_nodemap()` parses `LCFG_NODEMAP_*` commands and calls the appropriate helper; `nodemap_test_nid()` and `nodemap_test_id()` provide read-only validation helpers.

## Control flow and behavior
Module initialization creates debugfs state, allocates a fresh `nodemap_config`, creates the default nodemap, activates that config with `nodemap_config_set_active()`, then drops the temporary creation reference. Config switching builds a list of nodemaps from the new hash, transfers debugfs/stat pointers from old nodemaps with the same name, registers debugfs entries for new nodemaps, switches `active_config`, updates `nodemap_active`, deallocates the old config, and optionally revokes locks if nodemap enforcement was just disabled.

Client classification starts in `nodemap_add_member()`. If the security context names a nodemap, the code verifies it exists and has `nmf_gss_identify`; otherwise it falls back to NID range classification. `nodemap_classify_nid()` handles `0@lo` by selecting the first non-loopback local NID, checks ban ranges first if the caller requests ban status, then searches regular ranges, falling back to the default nodemap. The chosen nodemap is refcounted and passed to `nm_member_add()`.

ID mapping is centralized in `__nodemap_map_id()`. If nodemaps are inactive or the nodemap is missing, the input ID is returned. For FS-to-client mapping, offsets are removed first and out-of-range IDs squash. Root UID/GID is preserved only when root access is allowed; otherwise normal mapping/squash rules apply. Mapping can be disabled per ID class by `nmf_map_mode`, trusted nodemaps bypass explicit maps, the default nodemap squashes unknowns, and non-default nodemaps consult client-to-FS or FS-to-client rbtrees. Client-to-FS mapping applies offsets at the end and may squash before offsetting if the mapped ID exceeds the configured offset limit. `nodemap_map_acl()` applies this logic to POSIX ACL entries and drops entries that map to squash IDs.

Range mutations validate conflicts against banlists, create `lu_nid_range` objects, insert them into regular or ban trees, link them to nodemap lists, persist with `nodemap_idx_range_add()`/`del()`, reclassify affected members, and revoke locks for nodemaps whose authorization view changed. Dynamic nodemaps must have a parent and their range must be included in the parent's range; GSS-identification nodemaps cannot have NID ranges.

Fileset mutations support legacy primary filesets and newer IAM-backed primary/alternate filesets. Parent/child dynamic nodemap constraints prevent children from widening namespace access or making read-only parent filesets writable. Add/delete/modify operations update in-memory primary strings and alternate fileset rbtrees while coordinating IAM changes through `nodemap_idx_fileset_*()` helpers. `nodemap_fileset_get_root()` resolves the effective mount root and read-only flag from requested fileset, primary fileset, and longest matching alternate fileset.

The ioctl dispatcher copies and validates a userspace `lustre_cfg`, routes read-only tests and SHA lookup separately, and sends most mutations through `cfg_nodemap_cmd()` or `cfg_nodemap_fileset_cmd()`. It marks read-only commands through `out_ro_cmd` and reports llog fileset cleanup needs through `out_clean_llog_fileset`.

## State and persistence
Persistent configuration is written only through the storage-layer `nodemap_idx_*()` API. This handler updates memory first in many setters, then calls a matching index add/update/delete and revokes locks. Fileset code is more transactional: it often saves old state, updates IAM, and attempts undo on failure. `nmf_fileset_use_iam` tracks migration from legacy params llog filesets to IAM-backed records.

State guarded here includes `active_config`, nodemap hash entries, SHA rhashtable entries, range/ban interval trees, per-nodemap idmap rbtrees, alternate fileset rbtrees, member lists, sub-nodemap parent lists, dynamic nodemap count, and debugfs/stat pointers. Refcounting is central: hash lookups return referenced nodemaps, member exports hold nodemap refs, SHA table insertion takes an extra ref, and destruction occurs outside `active_config_lock` where possible.

## Dependencies and integration points
This file integrates with LNet NID parsing/matching, libcfs hash/rhashtable helpers, Linux rbtrees/rwsems/refcounting/crypto SHA-256/capability APIs, Lustre OBD exports and ioctl config structures, POSIX ACL xattrs, MDT/OST lock revocation through `ldlm_revoke_export_locks()`, debugfs through `lprocfs_nodemap_register()`, and MGS nodemap storage via `nodemap_idx_*()`.

Downstream users include MDT request handling, quota paths, layout handling, xattr and identity translation paths that call `nodemap_get_from_exp()` and `nodemap_map_id()`. Upstream control comes from ioctl `LCFG_NODEMAP_*` commands and legacy `lctl set_param` fileset writes.

## Risks and edge cases
The file has high concurrency risk: correct lock ordering among `active_config_lock`, range-tree rwsems, ban-tree rwsems, `nm_idmap_lock`, `nm_fileset_alt_lock`, and member-list locks is essential. Config replacement intentionally moves debugfs/stat pointers between nodemap objects, so stale pointers and double-free regressions are plausible.

Mutation and persistence ordering is subtle. Some setters update memory before persistence and do not roll back on `nodemap_idx_nodemap_update()` failure; tests should confirm whether callers tolerate in-memory state diverging from IAM on storage errors. Fileset operations have undo paths, but some undo failures are logged rather than fully recovered. `nodemap_del()` accepts a nullable `out_clean_llog_fileset` in recursive/dynamic deletion paths but dereferences it when old llog fileset cleanup is needed, so that path deserves focused inspection.

Security-sensitive risks include accidentally allowing dynamic children to raise privileges beyond parents, incorrect GSS nodemap/name mismatch handling, offset boundary mistakes that avoid intended squash, map-mode parsing accepting malformed combinations, quota RBAC checks missing a command class, and range/banlist conflicts around large NID netmasks versus NID4 interval trees.

## Test signals
Useful tests include ioctl-level add/delete/range/idmap/offset/RBAC/fileset round trips, persistence failure injection for each `nodemap_idx_*()` family, dynamic parent-child privilege and fileset restriction tests, NID4 and large-NID netmask classification tests, banlist classification and lock revocation tests, ACL mapping with squashed entries, offset boundary tests at start/limit/start+limit overflow, GSS SHA lookup and `gssonly_identification` constraints, default nodemap rejection cases, and config reload tests that verify member reclassification and debugfs entry transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_idmap.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_idmap.c

## Purpose
`nodemap_idmap.c` implements the in-memory UID, GID, and PROJID mapping tables used by nodemaps. Each mapping is represented once but linked into two rbtrees so lookup is efficient in both client-to-filesystem and filesystem-to-client directions.

## Important APIs, types, and functions
The core type is `struct lu_idmap`, with `id_client`, `id_fs`, `id_client_to_fs`, and `id_fs_to_client`. Public helpers are `idmap_create()`, `idmap_insert()`, `idmap_delete()`, `idmap_search()`, `idmap_delete_tree()`, and `idmap_copy_tree()`.

`idmap_insert()` selects one forward and one backward root from the nodemap according to `NODEMAP_UID`, `NODEMAP_GID`, or `NODEMAP_PROJID`. It searches both roots before insertion to prevent split-brain mappings, returns `NULL` on clean insert, `ERR_PTR(-EEXIST)` when both sides already match, a conflicting existing map when only one side matches, or `ERR_PTR(-EINVAL)` for an invalid ID type.

## Control flow and behavior
Creation allocates and initializes both rb nodes as clear. Insert walks the forward tree by `id_client` and the backward tree by `id_fs`. A new map is linked into both trees only when neither side is already present. A partial conflict is deliberately returned to the caller; `nodemap_add_idmap_helper()` in the handler deletes the old persistent index and retries insertion with the new map.

Search chooses the correct rbtree for ID type and direction, then performs a normal integer comparison walk. Delete erases both rb nodes from their corresponding roots and frees the object.

`idmap_delete_tree()` and `idmap_copy_tree()` traverse representative roots with `rbtree_postorder_for_each_entry_safe()`. They only need to visit one tree per ID class because each `lu_idmap` is shared by the two directional trees. Copy allocates new map nodes and inserts them into the destination nodemap, intended for initial inheritance when a sub-nodemap attaches to a parent.

## State and persistence
This file is memory-only. It does not call `nodemap_idx_*()` and does not persist records directly. The caller must hold `nm_idmap_lock` for normal mutation and lookup safety; comments note that copy is only called during initial sub-nodemap attachment and does not take the lock internally.

## Dependencies and integration points
The code depends on Linux rbtrees, Lustre `OBD_ALLOC_PTR`/`OBD_FREE_PTR`, and `nodemap_internal.h` for `struct lu_nodemap` field names and nodemap ID enums. It is called by handler mapping paths, idmap add/delete ioctl handlers, member-change comparison, and nodemap inheritance/destruction.

## Risks and edge cases
`idmap_search()` leaves `root` as `NULL` for invalid type/direction combinations and then dereferences it; current callers pass valid enums, but defensive tests should cover future API misuse. `idmap_destroy()` asserts rb nodes are not empty, so callers must only destroy nodes still considered linked by the local convention. `idmap_delete_tree()` uses copied root values and frees nodes without clearing the source roots; this is safe during nodemap teardown but would be unsafe as a general clear-and-reuse operation.

There is a likely typo in `idmap_copy_tree()` error cleanup: when insertion of `idmap_new` fails, it frees `idmap` rather than `idmap_new`. That would be dangerous if the path is reachable because it could corrupt the source tree and leak the newly allocated node.

## Test signals
Test one-to-one inserts, duplicate inserts, client-side conflicts, filesystem-side conflicts, invalid enum handling, lookup in both directions for UID/GID/PROJID, deletion from both trees, deletion-tree teardown under leak checking, and parent-to-child copy failure injection to validate cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_idmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_internal.h -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_internal.h

## Purpose
`nodemap_internal.h` is the private contract shared by the nodemap implementation files in `ptlrpc`. It defines internal constants and data structures for NID ranges, ID maps, fileset records, and alternate filesets, and declares the cross-file APIs used by handler, range, idmap, member, lproc, fileset-alt, and storage code.

## Important APIs, types, and declarations
Important constants are `DEFAULT_NODEMAP`, `NODEMAP_NOBODY_UID/GID/PROJID`, and `NODEMAP_FILESET_PRIM_ID`. External globals are `proc_lustre_nodemap_root`, `nodemap_active`, `active_config_lock`, and `active_config`.

Important structures:
- `struct lu_nid_range`: one regular or banned NID range, with a unique ID, owning nodemap, per-nodemap/per-config list links, interval-tree node, large-NID netmask metadata, containing tree pointer, and a nested subtree for dynamic child ranges.
- `struct lu_idmap`: bidirectional client/filesystem ID mapping node with one rb node for each direction.
- `struct lu_nodemap_fileset_info`: normalized persistence payload for fileset IAM operations, including nodemap ID, fileset subids/fragments, path, read-only flag, and alternate flag.
- `struct lu_fileset_alt`: alternate fileset path node with ID, path buffer, size, read-only flag, and rb node.

Inline helpers split and compose nodemap index IDs (`nm_idx_get_type()`, `nm_idx_get_id()`, `nm_idx_set_type()`), compare NID4 interval inclusion (`__range_is_included()`, `range_is_included()`), and detect the default nodemap (`is_default_nodemap()`).

The declarations expose lifecycle/config functions, lookup, procfs/debugfs registration, range and ban-range creation/search/insert/delete, idmap create/search/copy/delete, alternate fileset helpers, member add/delete/reclassify/revoke, handler helper functions, MGS/loading predicates, and all persistence-layer `nodemap_idx_*()` entry points.

## Control flow and behavior
The header establishes the intended ownership boundaries. `nodemap_handler.c` owns high-level policy and persistence decisions; `nodemap_range.c` owns interval-tree operations; `nodemap_idmap.c` owns ID map rbtrees; `nodemap_member.c` owns export membership and lock revocation; `nodemap_lproc.c` owns debugfs presentation; storage code owns IAM persistence. Callers use the declarations here to keep those pieces loosely separated while sharing the same internal state objects.

The comments steer callers toward `nodemap_lookup_locked()` while retaining the `nodemap_lookup()` macro alias for in-flight patch compatibility. Range helpers make NID4-only interval comparisons explicit via `START()` and `LAST()`, while large-NID netmask support is carried in `rn_nidlist` and related list heads.

## State and persistence
This header does not store state directly, but it defines the fields that carry runtime and persistent identity: range IDs assigned by MGS/load paths, nodemap index type bits, fileset fragment metadata, and the functions that write IAM records. The `nodemap_idx_*()` declarations are the persistence bridge for nodemap records, cluster roles, offsets, filesets, capabilities, ranges, ID maps, activation state, and index reads.

## Dependencies and integration points
The header depends on libcfs hash support, Lustre nodemap and disk definitions, Linux rbtrees, LNet NID types, procfs/debugfs types, and Lustre export/config structures through included or transitive headers. It is included by the six researched nodemap implementation files and by related storage/fileset-alt code.

## Risks and edge cases
Because this is a private ABI across many implementation files, structure field semantics must remain synchronized with all users. Changing `lu_nid_range` list/rbtree fields can break regular/ban/dynamic range trees; changing `lu_idmap` rb nodes can break bidirectional map invariants; changing fileset IDs or fragment fields can break IAM persistence compatibility.

The `START()` and `LAST()` macros convert to NID4 values, so code must avoid using them for large NIDs except in paths that already checked `nid_is_nid4()`. The `nodemap_lookup` macro may obscure whether callers hold `active_config_lock`, increasing review burden around new lookup call sites.

## Test signals
Build coverage is the main signal for declaration drift. Runtime coverage should include all implementations that share these structures: range insertion/search, large-NID netmask matching, idmap bidirectional lookup, fileset IAM add/update/delete, dynamic nodemap inheritance, debugfs registration/removal, and config replacement. Static analysis should check lock annotations by convention around functions whose comments require `active_config_lock` or tree rwsems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_lproc.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_lproc.c

## Purpose
`nodemap_lproc.c` exposes nodemap runtime state through Lustre debugfs/ldebugfs files. It creates the global `nodemap` debugfs directory, per-nodemap directories, read-only views for ranges, ID maps, exports, properties, RBAC/capabilities, filesets, and a few write handlers for activation, legacy fileset setting, and SELinux policy.

## Important APIs, types, and functions
The file-level state is `static LIST_HEAD(nodemap_pde_list)` and `static struct dentry *nodemap_root`. Public entry points are `nodemap_procfs_init()`, `nodemap_procfs_exit()`, `lprocfs_nodemap_register()`, and `lprocfs_nodemap_remove()`.

Important show/open handlers include `nodemap_idmap_show()`, `nodemap_ranges_show()`, `nodemap_ban_ranges_show()`, `nodemap_fileset_seq_show()`, `nodemap_exports_show()`, `nodemap_active_seq_show()`, `nodemap_id_seq_show()`, squash/trusted/admin/map-mode/RBAC/audit/encryption/raise/read-only/deny-mount/parent/GSS show functions, plus `nodemap_capabilities_seq_show()` and `nodemap_offset_seq_show()`.

Write handlers are `nodemap_active_seq_write()`, `nodemap_fileset_seq_write()`, and `nodemap_sepol_seq_write()`. File operation tables connect seq handlers to ldebugfs. `lprocfs_nodemap_vars` and `lprocfs_default_nodemap_vars` select which files are visible for normal versus default nodemaps.

## Control flow and behavior
Initialization creates `debugfs_lustre_root/nodemap` and adds the module-level `active` file. Per-nodemap registration allocates `struct nodemap_pde`, creates a child directory named after the nodemap, stores the nodemap name in `npe_name`, adds the appropriate variable table, links the PDE onto `nodemap_pde_list`, and stores it in `nodemap->nm_pde_data`. The private data passed to seq handlers is the stable name string from the PDE, not a direct nodemap pointer, so a config reload can replace nodemap structs without rewriting every debugfs file.

Most show handlers lookup the current nodemap by name, print a scalar or JSON-like list, and release the reference. Range show handlers hold `active_config_lock` and the relevant tree read lock while iterating per-nodemap range lists. ID map and fileset handlers take the corresponding nodemap rwsem. Export display takes `nm_member_list_lock` and prints NID, UUID, device, and ban status.

Activation writes parse a small boolean-like numeric string and call `nodemap_activate()`. Fileset writes allocate a user buffer and call `nodemap_set_fileset_prim_lproc()` for backward compatibility. SELinux writes copy into a bounded stack buffer and call `nodemap_set_sepol()` without the external permission check flag.

Removal deletes a nodemap's debugfs subtree, removes its PDE from the list, and frees it. Exit removes the global tree recursively and frees any remaining PDE records.

## State and persistence
This file presents state but mostly does not own it. Persistent changes occur indirectly through `nodemap_activate()`, `nodemap_set_fileset_prim_lproc()`, or `nodemap_set_sepol()`. The PDE list tracks allocated debugfs metadata and is also used during cleanup. Per-nodemap debugfs entries survive config replacement by transferring `nm_pde_data` in the handler.

## Dependencies and integration points
The file integrates with Linux debugfs, Lustre ldebugfs variable helpers, seq_file, nodemap lookup and setter APIs from `nodemap_handler.c`, member/range/idmap/fileset structures from `nodemap_internal.h`, libcfs capability formatting, and OBD export data for the exports view. The member code also creates per-nodemap `md_stats` and `dt_stats` files under the registered debugfs directory.

## Risks and edge cases
The output format is JSON-like but not strict JSON, so external tooling may be fragile. Several show paths read scalar nodemap fields without a dedicated property lock; they rely on simple field loads and active config/ref lifetime rather than snapshot consistency. `nodemap_procfs_init()` shadows `rc` inside the failure branch, so the function can return success even when root directory creation fails. `lprocfs_nodemap_register()` does not remove a created debugfs directory if a later step after creation fails, though current later work is limited.

Write handlers are compatibility-sensitive: fileset writes bypass `checkperm` and use legacy local fileset behavior, while sepol writes call `nodemap_set_sepol(..., false)`. User-buffer parsing tests should verify exact limits and newline behavior.

## Test signals
Test debugfs init/register/remove/exit under normal and failure injection, config replacement preserving per-nodemap entries, default versus non-default file lists, readable output for empty and populated idmaps/ranges/banlists/filesets/exports, active write parsing, fileset write limits and invalid paths, sepol length/format handling, and lockdep coverage for show handlers racing with nodemap mutation and deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_lproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_member.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_member.c

## Purpose
`nodemap_member.c` manages the live `obd_export` membership lists attached to nodemaps. It adds/removes exports, switches exports between nodemaps during reclassification, decides when nodemap changes require client lock revocation, and creates per-nodemap duplicated MDT/OST stats files on first use.

## Important APIs, types, and functions
Public functions are `nm_member_add()`, `nm_member_del()`, `nm_member_delete_list()`, `__nodemap_member_switch()`, `nm_member_reclassify_nodemap()`, `nm_member_revoke_locks()`, and `nm_member_revoke_locks_always()`.

Important internal helpers are `nm_register_obd_stats()`, `nm_member_exp_revoke()`, `idmaps_match()`, and `nodemap_change_need_update()`. The temporary comparison cache uses `struct nm_cmp_cache_entry`, `static struct rhashtable nm_cmp_cache`, and `static bool use_nm_cmp_cache`.

## Control flow and behavior
`nm_member_add()` must run under `active_config_lock`. It rejects NULL exports, detects duplicate membership, takes an export reference and nodemap reference, stores the nodemap in `exp->exp_target_data.ted_nodemap` under the export spinlock, links the export into the nodemap member list, and registers duplicated stats files if needed.

`nm_member_del()` requires both `active_config_lock` and the nodemap member-list lock. It asserts that the export points at the nodemap, unlinks the export, clears `ted_nodemap`, drops the nodemap ref held by the export, and drops the export ref held by list membership. `nm_member_delete_list()` drains an entire nodemap list.

`__nodemap_member_switch()` moves a live export without setting `ted_nodemap` to NULL. It unlinks from the old list, replaces the export's nodemap pointer, drops the old nodemap ref, links into the new list, registers stats, compares old and new nodemap security-relevant properties, and revokes locks if the member is newly banned or its effective security context changed.

`nm_member_reclassify_nodemap()` iterates a nodemap's members, obtains each export's peer NID, optionally honors a GSS-authenticated nodemap name from reverse import security state, otherwise calls `nodemap_classify_nid()`, updates `exp_banned`, and switches exports whose classification changed. A temporary rhashtable caches `nodemap_change_need_update()` results while reclassifying a nodemap to avoid repeated expensive comparisons.

Lock revocation is skipped when nodemap enforcement is inactive, when the export is in recovery, when the target is not MDT unless OST revocation is forced, and for loopback/LWP connections.

## State and persistence
This file maintains only live runtime state: export membership lists, export-to-nodemap pointers, export and nodemap references, ban flags, duplicated stats pointers, and a temporary comparison cache. It does not persist configuration. Its state is rebuilt naturally as clients reconnect or as handler-driven reclassification runs after config changes.

## Dependencies and integration points
The code depends on OBD exports/devices/types, Lustre stats/debugfs helpers, LDLM lock revocation, LNet NID checks, import security references, nodemap lookup/classification APIs, idmap rbtrees, Linux capabilities, and rhashtable. It is called by connection setup/teardown in MDT and other target paths through `nodemap_add_member()`/`nodemap_del_member()` in the handler.

## Risks and edge cases
This is lock-order sensitive. Reclassification holds a nodemap member-list lock while switching to a new nodemap and briefly taking the new nodemap's member-list lock; the code relies on `active_config_lock` serializing reclassifies to avoid deadlock. GSS classification has a delicate mismatch path that keeps the authenticated nodemap when range classification disagrees. Any missed `nodemap_putref()` or `class_export_put()` would leak live objects; any premature put could break active exports.

`nodemap_change_need_update()` compares only fields that affect cached permissions and mappings. New nodemap security properties must be added there if clients need lock revocation after they change. `idmaps_match()` iterates `id_fs_to_client` nodes and assumes it receives roots with that node type.

## Test signals
Test duplicate add, add/delete refcount balance, disconnect while reclassification runs, range and banlist changes moving exports, GSS-authenticated nodemap consistency checks, newly banned and unbanned logging/state, lock revocation skip cases for recovery/LWP/loopback/non-MDT, comparison-cache behavior, and field-change matrix tests that verify revocation when each security-relevant property or idmap changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_member.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_range.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_range.c

## Purpose
`nodemap_range.c` implements regular and banned NID range storage and lookup. It uses Linux interval-tree generation for NID4 address intervals, plus list-based `cfs_nidlist` matching for large-NID netmask ranges. The handler uses this file to classify clients, enforce non-overlap, and support dynamic sub-range nesting.

## Important APIs, types, and functions
Public APIs are `range_create()`, `ban_range_create()`, `range_find()`, `ban_range_find()`, `range_insert()`, `ban_range_insert()`, `range_delete()`, `ban_range_delete()`, `range_search()`, `ban_range_search()`, and `range_destroy()`.

Important internal helpers are `range_create_generic()`, `__range_find()`, `range_find_generic()`, `__range_insert()`, `range_insert_generic()`, `range_delete_generic()`, `__range_search()`, and `range_search_generic()`. `INTERVAL_TREE_DEFINE()` creates the `nm_range_*` interval-tree functions over `struct lu_nid_range::rn_rb`, `rn_subtree_last`, `START`, and `LAST`.

## Control flow and behavior
Creation validates that start and end NIDs are on the same LNet network. For non-netmask ranges it ensures the start address is not greater than the end address. For netmask ranges it requires identical start/end NIDs, validates prefix length, reconstructs a `<addr>/<prefix>@<net>` string, and parses it into `rn_nidlist`. Range IDs are loaded from disk when nonzero or allocated by incrementing the tree's highest ID.

Find/search split by NID type. NID4 ranges use interval-tree iteration. `__range_find()` recursively descends into `rn_subtree` when a range includes the queried interval, enabling dynamic child ranges nested under parent ranges. Large-NID netmask ranges live on setup lists and are checked with `cfs_match_nid()` and prefix-length comparisons.

Insertion rejects overlap by checking the target interval root first. Dynamic insertion may recurse into an including parent range's subtree and return that parent through `parent_range`; non-dynamic overlap returns `-EEXIST`. Netmask insertion uses the setup list and rejects exact duplicate netmask ranges. Successful deletion unlinks from the nodemap list and removes from either interval tree or netmask list before freeing.

Search for classification looks up the most-specific nested NID4 range by recursing into subtrees, or linearly checks large-NID netmask lists with `cfs_match_nid()`.

## State and persistence
The file owns in-memory tree/list placement and range ID allocation, not persistent storage. Persistence is driven by caller-side `nodemap_idx_range_add()` and `nodemap_idx_range_del()`. Runtime state includes each range's owning nodemap, per-nodemap `rn_list`, netmask `rn_nidlist`, containing `rn_tree`, and nested `rn_subtree`.

## Dependencies and integration points
The code depends on LNet NID conversion/matching, libcfs nidlist parsing/freeing, Linux interval-tree generic helpers, rbtrees, and `nodemap_internal.h`. It is used by handler range and banlist mutations, member classification, test helpers, and config teardown.

## Risks and edge cases
The interval tree operates on NID4 values, so callers and helpers must route large NIDs through the netmask list path. Netmask ranges are searched linearly, which is acceptable for small configuration sets but may become a scalability issue for many large-NID ranges. Dynamic nesting correctness depends on parent inclusion checks and lock coverage in the handler; an incorrectly inserted subtree could classify clients to an unintended child nodemap.

`range_destroy()` asserts `rn_list` is not empty, matching the current delete path where list removal occurs before destruction. Direct destruction of a never-linked range would violate that assertion. Error paths in callers must maintain list/tree invariants when `range_create_generic()` returns a partially initialized range.

## Test signals
Test NID4 create/find/search/insert/delete, overlapping regular ranges, nested dynamic ranges and most-specific classification, exact and non-exact finds, ban range separation, large-NID netmask parsing and matching, invalid netmask lengths, start/end network mismatch, start greater than end, duplicate netmask insertion, deletion from interval tree versus netmask list, and range ID preservation during load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_range.c -->
