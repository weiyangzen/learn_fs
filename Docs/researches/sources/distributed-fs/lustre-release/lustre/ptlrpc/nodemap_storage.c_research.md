# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_storage.c

## Purpose

`nodemap_storage.c` owns persistent storage and wire export of Lustre nodemap configuration. It serializes `struct lu_nodemap` state into the `LUSTRE_NODEMAP_NAME` dt index, loads the index back into a fresh `struct nodemap_config`, registers MGS and target-side cache files, and serves nodemap config pages to MGC clients through MGS bulk config reads.

## Important APIs, Types, and Functions

The file revolves around `struct nodemap_key`, `union nodemap_rec`, `struct nm_config_file`, `struct lu_nodemap_fileset_info`, dt index objects, and the global MGS handle `nodemap_mgs_ncf`. Key exported APIs are `nodemap_idx_nodemap_add/update/del`, cluster role/offset/capability add/update/delete helpers, `nodemap_idx_range_add/del`, `nodemap_idx_idmap_add/del`, `nodemap_idx_fileset_add/update/update_header/del/clear`, `nodemap_idx_nodemap_activate`, `nm_config_file_register_mgs/tgt`, `nm_config_file_deregister_mgs/tgt`, `nodemap_process_idx_pages`, `nodemap_index_read`, and `nodemap_get_config_req`.

Local helpers initialize typed keys and records: cluster records capture name, squash IDs, map mode, audit/encryption, readonly/deny mount, GSS, and fileset-IAM flags; role records capture RBAC and privilege-raise masks; offset records capture UID/GID/projid offset ranges; ID map records capture client-to-filesystem IDs; range records support legacy NID4 start/end or newer NID prefix plus netmask; fileset header and fragment records split paths across fixed-size records.

## Control Flow

Write operations follow a consistent pattern: create a local `lu_env`, build a key/record pair, operate on the MGS nodemap index, and finalize the environment. `nodemap_idx_insert_batch`, `nodemap_idx_update`, and `nodemap_idx_delete_batch` declare dt operations, start a local transaction, take the dt write lock, execute insert/delete work, bump the dt object version through `nodemap_inc_version`, unlock, and stop the transaction. Add paths insert new records, update paths delete then insert, and delete paths tolerate `-ENOENT` only where explicitly documented.

Nodemap deletion walks the nodemap's RB trees and lists to remove associated role, offset, capability, UID/GID/projid maps, normal ranges, ban ranges, then the cluster record. Fileset operations use a header subid plus a contiguous subid range for fragments. Add and delete paths track partial progress and attempt undo; if undo fails, they clear the entire fileset subid range and return `-EIO` to signal that the on-disk fileset was wiped to avoid partial corruption.

Load flow is two-pass. `nodemap_load_entries` first walks only cluster records to create all nodemap objects and preserve their saved IDs, then restarts the iterator to process attributes, ranges, maps, global state, capabilities, offsets, and fileset fragments. `nodemap_process_keyrec` dispatches by encoded index type and subid. It uses the most recently referenced nodemap plus a linked list of loaded nodemaps to resolve attribute records that follow cluster records in the index. After loading, missing default nodemap and missing global active records are synthesized and written to disk before the new config is activated.

Wire export flow uses `nodemap_index_read` and `nodemap_page_build` to walk the dt index into `lu_idxpage` containers. The same two-pass ordering is used on the wire: cluster records first, attributes second. `nodemap_get_config_req` validates an `MGS_CFG_T_NODEMAP` request, allocates folios, fills pages from the index, updates the export's nodemap version, and sends pages through PTLRPC bulk put.

## State and Persistence Behavior

Persistent state is the nodemap dt index. Every successful insert, update, and batch delete increments the dt version so clients can detect in-flight config changes. Records are endian-normalized with `cpu_to_le*` and `le*_to_cpu` for scalar fields. Dynamic nodemaps (`nm_dyn`) are intentionally not persisted by the public add/delete/update helpers.

Runtime state includes `nodemap_mgs_ncf` for the MGS index, `ncf_list_head` for registered non-MGS target cache files, and `nodemap_config_loaded` guarded by `nodemap_config_loaded_lock`. `nodemap_config_set_active_mgc` prioritizes network-loaded MGS config over disk cache, resizes preallocated fileset strings to actual length, marks the config loaded, and rewrites all registered target caches from active in-memory config.

Target registration loads disk cache only if no config is already loaded; otherwise it writes the current active config into a fresh local cache. MGS registration loads from the supplied object and makes that object the authoritative persistent store. Deregistration drops dt object references and removes target entries from the list.

## Dependencies and Integration Points

The file depends on Lustre dt object APIs (`dt_trans_create`, declare/start/stop, `dt_insert`, `dt_delete`, iterators, index walk, version get/set), local object/index helpers, LNet NID conversion, nodemap core helpers from `nodemap_internal.h`, PTLRPC bulk transfer, MGS config request capsules, RB trees and lists inside nodemap objects, active config locking, and generated wire-layout constants validated by `wiretest.c`.

It integrates with MGS configuration distribution, MGC network loading, target local cache synchronization, nodemap admin operations that call the `nodemap_idx_*` persistence helpers, and security behavior that consumes the active nodemap config.

## Risks and Edge Cases

The loader assumes attributes can be associated with a previously loaded cluster record; corrupt or unexpectedly ordered indexes can produce `-ENOENT`. Fileset persistence is intentionally defensive but complex: partial add/delete undo mutates `nfi_fragment_cnt` and may wipe a subid range on undo failure. Range serialization rejects non-NID4 legacy range records and oversized netmask prefix records. Offset loading only uses the UID start/limit helper path, so the stored GID/projid offset fields are not independently restored there. Several operations require an MGS config file and return `-EINVAL` when no MGS is registered. `nodemap_cache_find_create` can unlink and recreate an index, so read-only devices and local OID recovery paths need careful coverage.

Concurrency risk is mostly around global config and cache transitions: active config is protected by `active_config_lock`, config loaded state has its own mutex, and target cache list operations have `ncf_list_lock`, but stale `ncf_obj == NULL` entries can exist after previous save failures and are skipped. Bulk export resets `ii_hash_end` to 0 if the dt version changes between reads, requiring clients to restart.

## Test Signals

Useful tests exercise add/update/delete of nodemap cluster records, roles, offsets, capabilities, UID/GID/projid maps, normal and ban ranges, and dynamic nodemap no-op behavior. Fileset tests should cover single-fragment, multi-fragment, alternate fileset IDs, readonly header update, partial insert/delete failure injection, clear-on-undo failure, invalid fragment count, and header subid alignment. Load tests should cover two-pass reconstruction, missing default/global records, legacy non-IAM fileset preservation, NID4 versus NID-mask ranges, corrupt record ordering, and endian round trips. Integration signals include MGS/TGT register/deregister, config-loaded gating, target cache rewrite after MGC activation, dt version restart behavior in `nodemap_index_read`, and PTLRPC bulk response sizing in `nodemap_get_config_req`.
