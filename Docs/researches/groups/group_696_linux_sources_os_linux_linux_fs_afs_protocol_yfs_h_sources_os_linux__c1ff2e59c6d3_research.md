# Group Research: group_696_linux_sources_os_linux_linux_fs_afs_protocol_yfs_h_sources_os_linux__c1ff2e59c6d3

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/os/linux/linux/fs/afs` files. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/protocol_yfs.h -->
# File Research: sources/os/linux/linux/fs/afs/protocol_yfs.h

## Scope

This header defines YFS protocol constants and packed XDR wire structures used by the Linux AFS client when talking to YFS-compatible file servers and cache-manager callback services.

## APIs And Constants

- Service IDs: `YFS_FS_SERVICE`, `YFS_CM_SERVICE`, and callback maximum `YFSCBMAX`.
- Callback opcodes in `enum YFS_CM_Operations`, including probe, callback-state, server preference, cell lookup, and `YFSCBCallBack`.
- File-server opcodes in `enum YFS_FS_Operations`, including fetch/store status, data, ACLs, create/remove/rename/link/mkdir/symlink, locks, volume status, and YFS-specific opaque ACL operations.
- XDR conversion helpers: `xdr_to_u64()` and `u64_to_xdr()`.
- Packed XDR records for 64-bit integers, vnode/FID values, fetch/store status, callbacks, RPC flags, VolSync, volume status, and store-volume-status.
- YFS volume type, volume-state flags, file-lock type constants, and viced capability flags.

## Dependencies

- Uses Linux byte-order helpers `ntohl()` and `htonl()` and big-endian `__be32` wire fields.
- Consumed by YFS client RPC encoders/decoders and callback service handling.

## Risks And Invariants

- Every structure is `__packed` because it mirrors network XDR layout.
- 64-bit values are transferred as two 32-bit words; conversion helpers must be used consistently.
- Negative lock constants such as `yfs_LockNone = -1` are protocol values, not ordinary unsigned flags.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/protocol_yfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/rotate.c -->
# File Research: sources/os/linux/linux/fs/afs/rotate.c

## Scope

This file implements fileserver selection, address rotation, retry policy, and diagnostic dumping for AFS/YFS file-server operations.

## Public And Internal APIs Covered

- `afs_clear_server_states()` releases per-operation endpoint-state references.
- `afs_select_fileserver()` is the main iterator used by operation execution to choose the next server/address or stop with a final error.
- `afs_dump_edestaddrreq()` emits debug state for address-selection failures when cursor debugging is enabled.

## Control Flow And Behavior

- Iteration starts by taking the volume server list, allocating one `afs_server_state` per server, snapshotting endpoint state/probe sequence/address mask, and preferring the vnode callback server when possible.
- If a vnode has an outstanding server affinity but that server no longer serves the volume, callbacks are cleared. `AFS_OPERATION_CUR_ONLY` instead fails with `-ESTALE`.
- Successful calls update volume state through `afs_update_volume_state()` and may restart if RO volume replication state requires retrying from the beginning.
- Fileserver aborts are translated carefully: `VNOVOL` refreshes VLDB state, `VMOVED` triggers volume update and restart, busy/offline errors mark per-server volume state and may sleep, quota/full errors map to local `-EDQUOT`/`-ENOSPC`, and unsupported opcodes can drive downgrade retry.
- Network failures rotate addresses first, then servers. Probe state determines responsive addresses and server eligibility.
- Address choice uses address preference priority and records `last_error` on failed addresses.
- When all servers are exhausted, accumulated endpoint/probe errors are folded into the operation result; busy volumes may sleep and restart.

## State And Data Structures

- Operates on `struct afs_operation` fields including `server_list`, `server_states`, `untried_servers`, `server_index`, `estate`, `addr_tried`, `addr_index`, `flags`, and cumulative error state.
- Uses per-server flags such as `AFS_SE_VOLUME_BUSY`, `AFS_SE_VOLUME_OFFLINE`, and `AFS_SE_EXCLUDED`.
- Updates vnode callback server affinity and callback promise state under `cb_lock`.

## Dependencies

- Relies on volume status refresh in `afs_check_volume_status()`, server record checking in `afs_check_server_record()`, fileserver probing helpers, address-preference helpers, and callback invalidation helpers.
- Uses RxRPC peer addresses for diagnostics.

## Risks And Invariants

- Server and address bitmasks assume the list sizes fit in an unsigned long bitset.
- `CUR_ONLY` operations, especially lock-related ones, must not silently move to another server.
- Callback promises are cleared when server affinity changes to avoid trusting stale validity state.
- Volume busy/offline sleeps must respect interruptible versus uninterruptible operation flags.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/rotate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/rxrpc.c -->
# File Research: sources/os/linux/linux/fs/afs/rxrpc.c

## Scope

This file maintains the AFS RxRPC socket, manages outgoing and incoming RxRPC calls, drives asynchronous call processing, sends cache-manager replies, and provides receive/extract helpers for RPC unmarshalling.

## Public And Internal APIs Covered

- Socket lifecycle: `afs_open_socket()` and `afs_close_socket()`.
- Call allocation/lifetime: `afs_alloc_flat_call()`, `afs_flat_call_destructor()`, `afs_put_call()`, `afs_deferred_put_call()`.
- Outgoing calls: `afs_make_call()` and `afs_wait_for_call_to_complete()`.
- Receive path: `afs_deliver_to_call()`, `afs_extract_data()`, `afs_protocol_error()`.
- Server-side replies: `afs_send_empty_reply()` and `afs_send_simple_reply()`.
- Incoming-call preallocation: `afs_charge_preallocation()` plus RxRPC callbacks for new/discarded/attached calls and OOB notification.

## Control Flow And Behavior

- `afs_open_socket()` creates an AF_RXRPC kernel socket, sets minimum encryption security, enables managed responses, creates the RxGK cache-manager token key, binds AFS and YFS callback services, installs RxRPC callbacks, listens, and charges incoming-call preallocation.
- `afs_make_call()` computes total transmit length, begins an RxRPC call, sends the fixed request and optional write iterator, and handles async self-references and abort cleanup.
- `afs_deliver_to_call()` repeatedly invokes the call-type deliver function while data is pending, translates unmarshalling/protocol errors to RxRPC aborts, runs completion callbacks, and queues follow-up work.
- Synchronous waiters sleep on `call->waitq` and deliver pending data themselves; async calls are queued on `afs_async_calls`.
- Incoming calls are accepted from preallocated `afs_call` objects, associated with peers/servers, routed by the first operation ID, and then delivered by callback-manager handlers.
- `afs_extract_data()` wraps `rxrpc_kernel_recv_data()` and advances AFS client/server call states when a full packet stream has been received.

## State And Data Structures

- Global `afs_async_calls` workqueue handles async RxRPC attention.
- `struct afs_call` tracks call type, RxRPC call, peer, key, server/vlserver, request/reply buffers, state, waitqueue, errors, abort codes, service ID, write iterator, and async refs.
- `struct afs_net` stores the socket, outstanding-call counter, preallocated incoming call, and OOB work.

## Dependencies

- Kernel RxRPC API: socket creation, begin/send/recv/abort/shutdown calls, peer access, security query, notifications, and call life checks.
- AFS call-type deliver/work/done/destructor hooks declared elsewhere in the AFS subsystem.

## Risks And Invariants

- Async calls take an extra self-reference; error paths must cancel queued work and drop that reference exactly once.
- `nr_outstanding_calls` gates socket teardown and must reach zero before release.
- Receive-state transitions distinguish client replies from server requests/reply acknowledgements.
- Protocol unmarshalling errors abort with protocol-specific RxRPC abort codes so peer-side failures are diagnosable.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/rxrpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/security.c -->
# File Research: sources/os/linux/linux/fs/afs/security.c

## Scope

This file handles AFS authentication key selection, anonymous fallback, per-vnode permit caching, and VFS permission checks against AFS ACL-derived access masks.

## Public And Internal APIs Covered

- Key lookup: `afs_request_key()` and RCU-safe `afs_request_key_rcu()`.
- Permit cache lifecycle: `afs_put_permits()`, `afs_clear_permits()`, and module-exit `afs_clean_up_permit_cache()`.
- Permit update/check: `afs_cache_permit()`, `afs_check_permit()`, and internal RCU permit lookup.
- VFS permission hook: `afs_permission()`.

## Control Flow And Behavior

- Key requests use `request_key_net()` for the cell key description. `-ENOKEY` falls back to a lazily allocated anonymous RxRPC null key.
- Permit lists cache caller access returned by file-server status replies for specific keys. Lists are sorted by key pointer, hashed globally, reference-counted, and shared when identical.
- `afs_cache_permit()` updates a vnode permit cache only if the callback break observed during the RPC is still current; otherwise it discards the candidate to avoid caching stale ACL state.
- RCU pathwalk permission checks only use already available validity and permit state; missing data returns `-ECHILD`.
- Blocking permission checks validate the vnode, fetch status if needed, then interpret AFS directory/file permissions.
- Directories require lookup for read/execute/chdir and delete or insert for writes. Files require lookup, mode-bit checks, read ACL for read/exec, and write ACL for writes.

## State And Data Structures

- Global `afs_permits_cache` stores interned `struct afs_permits` lists protected by `afs_permits_lock`.
- `afs_key_lock` serializes anonymous-key allocation per cell.
- Each vnode has an RCU `permit_cache` pointer that is cleared on callback break.

## Dependencies

- Linux keyring RxRPC key type, VFS permission API, RCU, spinlocks, and file-server status fetching.
- AFS callback validity helpers and access-mask constants.

## Risks And Invariants

- Permit caches are valid only while callback state remains unbroken.
- RCU readers must not observe freed permit/key memory; permit destruction is deferred through `call_rcu()`.
- Anonymous-key checks are special-cased to use `vnode->status.anon_access`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/server.c -->
# File Research: sources/os/linux/linux/fs/afs/server.c

## Scope

This file manages AFS fileserver records: lookup by UUID or RxRPC peer, creation from VLDB data, address-list updates, active/reference counts, garbage collection, callback give-up, and purge waiting.

## Public And Internal APIs Covered

- Lookup/use: `afs_find_server()`, `afs_lookup_server()`, `afs_get_server()`, `afs_use_server()`.
- Release: `afs_put_server()`, `afs_unuse_server()`, `afs_unuse_server_notime()`.
- Maintenance: `afs_purge_servers()`, `afs_wait_for_servers()`, `afs_check_server_record()`.
- Internal helpers allocate/install servers, look up addresses through VL servers, update address records, and run timer/workqueue destruction.

## Control Flow And Behavior

- Servers are stored in a per-cell RB tree keyed by UUID and exposed through a per-net proc list.
- Creating a new server allocates a record marked `UNCREATED`, installs it under the cell write lock, looks up addresses through VLDB, and immediately probes the fileserver.
- Concurrent creators wait on `AFS_SERVER_FL_CREATING`; failure records `create_error` before restoring `UNCREATED`.
- Active counts and references are separate: active use suppresses expiry timers, while references control RCU freeing.
- Unused servers are timer-delayed before GC unless expired or the cell is being removed.
- Destruction removes the server from cell/proc/probe lists, optionally gives up callbacks, unbinds RxRPC peer appdata, drops endpoint state and cell refs, and frees through RCU.
- `afs_check_server_record()` serializes address-list refresh with `AFS_SERVER_FL_UPDATING` and retries waiters a limited number of times.

## State And Data Structures

- `struct afs_server` contains UUID tree node, endpoint state, address version, flags, active/ref counts, timer, destroy work, volumes list, probe state, callback-token data, and service ID.
- Address lookup uses `afs_vl_cursor` and dispatches YFS `GetEndpoints` for YFS VL servers or AFS `GetAddrsU` otherwise.

## Dependencies

- Volume-location client/rotation code, fileserver probing, RxRPC peer appdata, per-cell locks, RCU, timers, and workqueues.

## Risks And Invariants

- Creation failure ordering uses barriers so waiters see `create_error` after `UNCREATED`.
- Server removal must happen only after active use drains.
- Callback give-up is needed before discarding servers that may still hold callback promises.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/server.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/server_list.c -->
# File Research: sources/os/linux/linux/fs/afs/server_list.c

## Scope

This file builds and maintains per-volume fileserver lists derived from VLDB records and attaches those volume/server relationships to per-server volume lists.

## Public And Internal APIs Covered

- `afs_alloc_server_list()` builds a refcounted `afs_server_list` for a volume.
- `afs_put_serverlist()` releases server uses and frees the list through RCU.
- `afs_annotate_server_list()` compares a replacement list with the existing list.
- `afs_attach_volume_to_servers()`, `afs_reattach_volume_to_servers()`, and `afs_detach_volume_from_servers()` maintain per-server volume linkage.

## Control Flow And Behavior

- Server-list allocation filters VLDB entries by requested volume type.
- RO replication state is inferred from `NEWREPSITE` and usable server counts. If at least half of usable sites are new replicas, old sites are excluded; otherwise new replica sites are excluded.
- `DONTUSE` sites are marked excluded.
- Each VLDB server UUID is resolved to an active `afs_server` record, and duplicate server records are skipped.
- Entries are insertion-sorted by UUID to make replacement comparison and reattachment deterministic.
- Volume attachment inserts each server entry into the server’s volume list in volume-ID order.
- Reattachment preserves callback expiry for unchanged server entries and uses `list_replace()` where possible.

## State And Data Structures

- `struct afs_server_list` holds refcount, lock, number of servers, replication mode, attachment state, sequence, and flexible `servers[]`.
- `struct afs_server_entry` stores server pointer, volume pointer, flags, callback expiry, and list link.

## Dependencies

- VLDB entry parsing, server lookup/creation, per-cell `vs_lock`, and server active-use accounting.

## Risks And Invariants

- Server lists pin active server uses until released.
- Sorted UUID ordering is assumed by comparison and reattachment logic.
- Exclusion flags are annotations that influence rotation but do not remove entries from the list.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/server_list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/super.c -->
# File Research: sources/os/linux/linux/fs/afs/super.c

## Scope

This file registers the `afs` filesystem, parses mount options/source syntax, validates mount contexts, creates/reuses superblocks, manages AFS inode slab objects, and implements `statfs`.

## Public And Internal APIs Covered

- Filesystem lifecycle: `afs_fs_init()` and `afs_fs_exit()`.
- `afs_fs_type` and `afs_super_ops`.
- Mount context operations: parameter parsing, `afs_get_tree()`, and context cleanup.
- Inode lifecycle: slab initialization, `afs_alloc_inode()`, `afs_destroy_inode()`, `afs_free_inode()`.
- Superblock display/stat: device-name/options display and `afs_statfs()`.

## Control Flow And Behavior

- Initialization creates `afs_inode_cache` and registers the filesystem. Exit unregisters, verifies no active inodes remain, runs an RCU barrier, and destroys the cache.
- Source parsing accepts AFS mount syntax such as `%cell:volume`, `#cell:volume`, `.readonly`, `.backup`, and `none` for dynroot.
- Mount validation requires a cell and key for non-dynroot mounts, performs alias detection when needed, creates a volume, and forces RO mounts/local flock mode for non-RW volumes.
- `sget_fc()` reuses matching non-dynroot superblocks by net namespace, cell, and volume ID, or dynroot superblocks by net namespace.
- `afs_fill_super()` initializes basic superblock fields, xattr handlers, BDI, root inode/dentry, dentry operations, and volume activation.
- `afs_kill_super()` clears `volume->sb` before killing the anon superblock, then deactivates volume cache state and frees super info.
- `afs_statfs()` reports fixed dynroot values or issues a get-volume-status operation.

## State And Data Structures

- `struct afs_super_info` stores net namespace, flock mode, dynroot flag, cell, and volume.
- `struct afs_fs_context` stores parsed mount state, selected cell/volume/key, volume type, force flag, and options.
- `struct afs_vnode` slab initialization sets locks, lists, callback work, writeback key list, and validation state.

## Dependencies

- Linux fs_context, superblock, inode slab, net namespace, netfs, fscache through volume activation, AFS volume/cell/key code, dynroot, dentry ops, and xattrs.

## Risks And Invariants

- `source=none` is valid only with `dyn`.
- Non-RW volumes are mounted read-only and use local flock semantics.
- Reused superblocks must already be active.
- Inode allocation must reset fields that can leak from slab reuse.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/symlink.c -->
# File Research: sources/os/linux/linux/fs/afs/symlink.c

## Scope

This file implements symlink-content caching, validation-aware `get_link`/`readlink`, single-shot symlink reads, cache writeback of symlink blobs, and eviction/invalidation of symlink copies.

## Public And Internal APIs Covered

- Symlink cache lifecycle: `afs_invalidate_symlink()`, `afs_evict_symlink()`, `afs_init_new_symlink()`.
- VFS inode ops: `afs_get_link()` and `afs_readlink()`.
- Address-space op: `afs_symlink_writepages()`.
- Exported operation tables: `afs_symlink_inode_operations` and `afs_symlink_aops`.

## Control Flow And Behavior

- Symlink contents are stored as refcounted `struct afs_symlink` objects under an RCU vnode pointer.
- Locally created symlinks are installed immediately and optionally copied into a folio-queue buffer for fscache writeback.
- Reads enforce AFS’s requirement to fetch symlink contents in one unit. Files larger than `PAGE_SIZE - 1` fail with `-EFBIG`.
- `afs_get_link()` supports RCU pathwalk only when a cached symlink exists and vnode validity is still good; otherwise it returns `-ECHILD`.
- Blocking lookup validates the vnode, takes `validate_lock`, downloads contents if missing, references the cached symlink, and returns it with a delayed put callback.
- If fscache is not enabled, the temporary folio-queue buffer is freed after reading.
- Writeback writes the symlink blob only when a callback promise still exists, then frees the buffer on success.

## State And Data Structures

- Uses `vnode->symlink`, `vnode->directory`, and `vnode->directory_size` to store content and cache/writeback buffers.
- `validate_lock` protects replacement and coherent read/download transitions.

## Dependencies

- Netfs single read/writeback helpers, fscache cookie state, folio queues, VFS delayed-call symlink API, and AFS validation.

## Risks And Invariants

- Symlink reads must be single-shot to avoid observing content modified between partial reads.
- RCU pathwalk cannot trigger validation or allocation.
- Cached symlink content is invalidated on callback/data-version changes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/validation.c -->
# File Research: sources/os/linux/linux/fs/afs/validation.c

## Scope

This file implements vnode and volume validity checks based on callbacks, callback expiry, RO snapshot changes, VolSync timestamps, and data-version invalidation.

## Public And Internal APIs Covered

- `afs_check_validity()` fast-checks whether a vnode can be used without network validation.
- `afs_update_volume_state()` processes successful operation callback/VolSync state.
- `afs_validate()` performs blocking vnode/volume validation and cache invalidation.

## Control Flow And Behavior

- The header comment defines the validity model: server callback initialization, vnode callbacks for RW data, volume callbacks for RO/backup releases, VolSync creation/update timestamps, and scrub/snapshot counters.
- `afs_check_validity()` rejects vnodes with broken volume counters, missing/expiring vnode or volume callback promises, RO snapshot changes, scrub counter changes, or `AFS_VNODE_ZAP_DATA`.
- VolSync creation changes initialize timestamps, detect RW restore or timestamp regression, advance RO snapshot state on expected releases, and query VLDB/server exclusion state to handle ongoing RO replication.
- VolSync update regressions increment the volume scrub counter.
- `afs_update_volume_state()` records volume/server callback expiry when an operation received callbacks and advances `cb_v_check`.
- `afs_validate()` serializes through `vnode->validate_lock`, optionally takes the volume callback-check mutex, fetches status when callback state is stale, maps `-ENOENT` to deleted/`-ESTALE`, updates vnode snapshot/scrub mirrors, and zaps data or symlink contents when needed.
- Regular-file cache invalidation preserves dirty/locked/mapped/writeback pages where appropriate; directories and symlinks are discarded more aggressively.

## State And Data Structures

- Volume fields include `cb_v_break`, `cb_v_check`, `cb_scrub`, `cb_ro_snapshot`, `cb_expires_at`, `creation_time`, and `update_time`.
- Vnode fields include `cb_expires_at`, `cb_ro_snapshot`, `cb_scrub`, flags, and validation lock.
- Operations provide pre/post VolSync values and returned callback records.

## Dependencies

- File-server status fetch, volume status refresh, callback promise helpers, page-cache invalidation, symlink invalidation, and tracepoints.

## Risks And Invariants

- Callback expiry uses a 10-second deadline margin.
- Volume timestamp updates are serialized by `volsync_lock` to prevent racing operations from fighting.
- RO release handling must distinguish expected snapshot advancement from regression requiring cache scrub.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/validation.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/vl_alias.c -->
# File Research: sources/os/linux/linux/fs/afs/vl_alias.c

## Scope

This file detects when a newly discovered AFS cell is an alias of an already known cell by querying YFS canonical cell names or comparing sampled volume/server/address data.

## Public And Internal APIs Covered

- `afs_cell_detect_alias()` is the external alias-detection entry point.
- Internal helpers sample volumes, compare fileserver address lists and volume server lists, compare `root.cell`, query known volumes in other cells, and request YFS canonical cell names.

## Control Flow And Behavior

- The preferred path asks YFS VL servers for the canonical cell name. If it differs from the requested name, the canonical cell is looked up and installed as `cell->alias_of`.
- If YFS canonical naming is unsupported, the code samples `root.cell` and compares it against root volumes of existing non-alias cells.
- Cells without `root.cell` are compared by picking an existing volume from another known cell, looking for a same-named volume in the candidate cell, then comparing volume IDs, server UUID lists, and endpoint address lists.
- Address-list comparison treats matching RxRPC peer pointers as evidence that fileservers overlap.
- Detection is serialized by `net->cells_alias_lock` and clears `AFS_CELL_FL_CHECK_ALIAS` after a non-error decision.

## State And Data Structures

- Uses `cell->alias_of`, `cell->root_volume`, per-net `proc_cells`, and per-cell volume RB trees.
- Temporary sampled volumes are ordinary `afs_volume` records obtained through `afs_create_volume()`.

## Dependencies

- Volume creation, VL cursor rotation, YFS VL `GetCellName`, cell lookup, RCU traversal, and per-cell/per-net locks.

## Risks And Invariants

- Alias detection can perform network lookups and may return `-ERESTARTSYS`.
- Comparing volumes relies on stable sorted server lists and shared peer objects for address matches.
- `alias_of` transfers a held cell reference on success.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/vl_alias.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/vl_list.c -->
# File Research: sources/os/linux/linux/fs/afs/vl_list.c

## Scope

This file manages VL server records and lists, including allocation/freeing and parsing DNS server-list payloads into prioritized VL server/address records.

## Public And Internal APIs Covered

- `afs_alloc_vlserver()`, `afs_put_vlserver()`.
- `afs_alloc_vlserver_list()`, `afs_put_vlserverlist()`.
- `afs_extract_vlserver_list()` parses DNS payloads for a cell.
- Internal helpers parse little-endian fields and extract IPv4/IPv6 address lists.

## Control Flow And Behavior

- VL server records are refcounted, named, ported, lock-protected, and initialized with RTT, service ID, probe waitqueue, and address pointer.
- DNS payload parsing validates content type/version, allocates a list sized by header server count, and keeps a reference to the previous list to reuse matching server records.
- Each DNS server entry includes name length, priority, weight, port, source, status, protocol, and address count.
- Only UDP or unspecified protocol is accepted. Port zero defaults to `AFS_VL_PORT`.
- Address extraction accepts IPv4 and IPv6 records, merges them into an `afs_addr_list`, and prefers IPv6 when available.
- Empty address lists are ignored unless the server already has addresses.
- New entries are insertion-sorted by lower priority first, then higher weight.
- Parsing errors dump the DNS buffer except for allocation failure.

## State And Data Structures

- `struct afs_vlserver` stores name, port, addresses, flags, RTT, probe state, and locks.
- `struct afs_vlserver_list` stores refcount, lock, source/status, preferred/index fields, count, and flexible server entries.

## Dependencies

- DNS server-list payload format, address-list allocation/merge helpers, cell `vl_servers_lock`, RCU freeing, and VL probing flags.

## Risks And Invariants

- The parser must always advance through address payloads even when later ignoring an entry.
- Existing server records are reused by case-insensitive name plus port.
- Address pointers are replaced under `server->lock` and old lists are released after replacement.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/vl_list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/vl_probe.c -->
# File Research: sources/os/linux/linux/fs/afs/vl_probe.c

## Scope

This file probes volume-location servers to determine reachability, RTT, preferred address, and whether the server supports YFS VL service upgrade.

## Public And Internal APIs Covered

- `afs_vlserver_probe_result()` processes completion of one `VL.GetCapabilities` probe.
- `afs_send_vl_probes()` starts probes for unprobed VL servers in a list.
- `afs_wait_for_vl_probes()` waits until an untried server responds or probing finishes.

## Control Flow And Behavior

- A probe run snapshots a server address list, sets `probe_outstanding`, clears previous probe state, and sends async capability calls to each address in priority order.
- Probe completion classifies local errors, network failures, remote aborts, and successful responses.
- Successful or aborted-but-responsive calls mark the address as responded and update YFS/non-YFS capability flags based on returned service ID.
- RTT is read from the RxRPC peer; the lowest RTT becomes server RTT and preferred address.
- When all address probes finish without response, the server is marked nonresponding and RTT becomes `UINT_MAX`.
- `afs_wait_for_vl_probes()` installs waitqueue entries on probing servers, sleeps interruptibly until a response or all probing stops, then chooses the responding untried server with lowest RTT as list preferred.

## State And Data Structures

- Uses `server->probe`, `probe_outstanding`, `probe_wq`, `probe_lock`, `flags`, `rtt`, and address-list `responded`/`probe_failed` bitmaps.
- `struct afs_error` accumulates probe-start errors when no async probe is in progress.

## Dependencies

- Async `afs_vl_get_capabilities()` calls, RxRPC RTT access, address-list refs, VL server flags, wait queues, and error-prioritization helpers.

## Risks And Invariants

- `AFS_VLSERVER_FL_PROBING` is cleared with unlock semantics before waking waiters.
- Probe results must update RTT before setting responded flags.
- A server can respond as YFS or non-YFS; service ID is adjusted accordingly.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/vl_probe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/vl_rotate.c -->
# File Research: sources/os/linux/linux/fs/afs/vl_rotate.c

## Scope

This file implements VL server cursor initialization, selection, retry/address rotation, final cleanup, and diagnostics for volume-location operations.

## Public And Internal APIs Covered

- `afs_begin_vlserver_operation()` initializes a `struct afs_vl_cursor`.
- `afs_select_vlserver()` iterates over VL servers and addresses.
- `afs_end_vlserver_operation()` releases cursor state and returns the cumulative error.
- Internal `afs_vl_dump_edestaddrreq()` emits debug cursor state on address failures.

## Control Flow And Behavior

- Cursor start checks pending signals, initializes cumulative error to `-EDESTADDRREQ`, and assigns a debug ID.
- VL iteration refreshes DNS data when unavailable or expired, queues cell lookup, waits for initial DNS if needed, handles not-found/unavailable results, and snapshots the current VL server list.
- Selection sends probes for unprobed servers, waits for responsive candidates, prefers the list’s preferred server if still untried, otherwise chooses the lowest RTT responding server.
- For a selected server, it pins the address list and rotates through responded addresses not already tried or probe-failed, favoring the preferred address.
- Previous call results stop on success/local failure, rotate on network failures, rotate server on unsupported service, and retry the whole list once after call reset.
- Address-list preferred index is updated when a non-preferred address successfully responded.
- End cleanup releases pinned address/server lists and dumps state for address-related failures when configured.

## State And Data Structures

- `struct afs_vl_cursor` holds cell, key, server list, selected server, address list, untried bitmask, tried-address bitmask, indices, call result, flags, and cumulative error.
- Uses per-cell DNS status/source/expiry and `vl_servers` RCU pointer.

## Dependencies

- DNS cell lookup machinery, VL server list/probe code, address lists, RxRPC peer addresses, and error prioritization.

## Risks And Invariants

- Only one full-list retry is allowed after retryable reset paths.
- Cursor cleanup must release both address-list and server-list refs on every exit path.
- DNS status loads are ordered after lookup-count changes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/vl_rotate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/vlclient.c -->
# File Research: sources/os/linux/linux/fs/afs/vlclient.c

## Scope

This file implements AFS and YFS Volume Location Service client RPCs: volume lookup by name, fileserver address lookup, VL capability probes, YFS endpoint lookup, and YFS canonical cell-name lookup.

## Public And Internal APIs Covered

- `afs_vl_get_entry_by_name_u()` dispatches `VL.GetEntryByNameU`.
- `afs_vl_get_addrs_u()` dispatches `VL.GetAddrsU`.
- `afs_vl_get_capabilities()` sends async `VL.GetCapabilities` probes.
- `afs_yfsvl_get_endpoints()` dispatches `YFSVL.GetEndpoints`.
- `afs_yfsvl_get_cell_name()` dispatches `YFSVL.GetCellName`.
- Static deliver functions incrementally unmarshal each reply type.

## Control Flow And Behavior

- `VL.GetEntryByNameU` encodes padded volume names, decodes the UVLDB entry, extracts server UUIDs, server flags, address versions, volume IDs, and volume-type existence bits.
- `VL.GetAddrsU` sends a UUID-based address query and decodes IPv4 address batches into an address list with returned uniquifier as version.
- `VL.GetCapabilities` is async, uses service upgrade, and reports completion through VL probe result hooks.
- `YFSVL.GetEndpoints` decodes counted endpoint lists, validates endpoint count/type/length, merges IPv4/IPv6 fileserver endpoints, and skips volume endpoints after validating their encoding.
- `YFSVL.GetCellName` decodes a bounded padded string and returns an allocated NUL-terminated cell name.
- Each synchronous dispatch records call error, abort code, and responded state back into the VL cursor before releasing the call.

## State And Data Structures

- Uses `struct afs_call` flat request/reply buffers, `ret_vldb`, `ret_alist`, `ret_str`, `vl_probe`, `vlserver`, `probe_index`, and staged `unmarshall` counters.
- Populates `struct afs_vldb_entry` and `struct afs_addr_list`.

## Dependencies

- RxRPC call framework from `rxrpc.c`, XDR structures from AFS/YFS protocol headers, address merge helpers, VL cursor selection state, and probe handling.

## Risks And Invariants

- String and endpoint lengths are protocol-validated before allocation/use.
- YFS endpoint decoding relies on staged extraction because each entry includes the next type/count boundary.
- Async capability calls transfer server/address refs to the call destructor.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/vlclient.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/volume.c -->
# File Research: sources/os/linux/linux/fs/afs/volume.c

## Scope

This file manages AFS volume records: VLDB lookup, volume creation/lookup, cell insertion/removal, server-list updates, reference lifetime, fscache activation, and refresh of volume status.

## Public And Internal APIs Covered

- `afs_create_volume()` creates or finds a volume from mount context/VLDB data.
- `afs_try_get_volume()`, `afs_get_volume()`, and `afs_put_volume()` manage references.
- `afs_activate_volume()` and `afs_deactivate_volume()` manage fscache volume cookies.
- `afs_check_volume_status()` refreshes stale or flagged volume records.

## Control Flow And Behavior

- VLDB lookup uses a VL cursor and `VL.GetEntryByNameU`; volume-ID refresh queries pass the ID as a decimal string.
- Volume allocation initializes identity, type, cell ref, name, callback/VolSync fields, locks, mmap list, and server list.
- Insertion into a per-cell RB tree returns an existing live record when possible; otherwise it installs the candidate and links it into proc visibility.
- `afs_create_volume()` applies mount traversal rules: forced type must exist; otherwise RO is preferred if present, then RW.
- Destruction detaches the volume from server lists, removes it from the cell, drops server list and cell refs, traces, and frees via RCU.
- Status update refreshes the volume name and rebuilds the server list. If annotations differ, it swaps in the new list, advances sequence, and reattaches volume/server links.
- Refresh interval is shortened while RO replication is ongoing.
- `afs_check_volume_status()` serializes refreshes with wait/update flags and retries waiters a limited number of times.

## State And Data Structures

- `struct afs_volume` stores VID/type/name, all type VIDs, cell, server-list RCU pointer, update deadline, cache cookie, callback counters, VolSync timestamps, and locks.
- Per-cell volume trees and proc hlist expose active volume records.

## Dependencies

- VL client/rotation, server-list management, fscache, RCU, workqueues, cell locking, and operation keys.

## Risks And Invariants

- Server-list replacement uses RCU and sequence updates with memory ordering.
- Volume records may be reused by concurrent lookups; candidate destruction handles duplicates.
- Refresh waiters return `-ESTALE` after repeated stale/update races.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/volume.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/write.c -->
# File Research: sources/os/linux/linux/fs/afs/write.c

## Scope

This file integrates AFS regular-file writeback with netfs: selecting writeback keys, issuing store-data RPCs, retrying with alternate keys, fsync validation, page-mkwrite validation, and pruning writeback key records.

## Public And Internal APIs Covered

- Netfs hooks: `afs_prepare_write()`, `afs_issue_write()`, `afs_begin_writeback()`, `afs_retry_request()`.
- VFS hooks: `afs_writepages()`, `afs_fsync()`, `afs_page_mkwrite()`.
- Key cleanup: `afs_prune_wb_keys()`.

## Control Flow And Behavior

- Writeback key selection walks `vnode->wb_keys` starting after the previous key, chooses the first valid key, and stores both the key and key record in the netfs request.
- Store-data completion commits returned status, records ctime, prunes keys, and updates store counters/byte stats.
- `afs_prepare_write()` sets a large stream subrequest maximum length.
- `afs_issue_write_worker()` allocates an uninterruptible AFS operation, sets vnode modification/data-version delta, position, length, write iterator, target size, and mtime, then waits for operation completion and reports progress to netfs.
- Permission/key errors mark the subrequest for retry if another writeback key is available.
- `afs_retry_request()` rotates writeback keys for write origins on credential failures and marks the stream failed if no valid key remains.
- `afs_writepages()` takes `validate_lock` to avoid racing with truncate/setattr page-cache invalidation.
- `afs_fsync()` validates the vnode with the file key before waiting on dirty pages.
- `afs_page_mkwrite()` validates before allowing netfs to make a page writable.

## State And Data Structures

- `vnode->wb_keys` stores authorizing keys used for dirty data.
- Netfs request private fields carry the selected `struct key` and `struct afs_wb_key`.

## Dependencies

- Netfs writeback APIs, AFS operation framework, StoreData RPC implementations, key validation, inode/page-cache writeback, and validation code.

## Risks And Invariants

- Writes must use credentials that authorized the dirtying process when possible.
- Validation lock prevents writeback racing with cache truncation.
- Key records are pruned only when no dirty/writeback tags remain and their usage count is otherwise idle.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/xattr.c -->
# File Research: sources/os/linux/linux/fs/afs/xattr.c

## Scope

This file exposes AFS metadata and ACL operations through Linux extended attributes, replacing pioctl-style metadata access for ACLs, cell name, FID, volume name, and YFS opaque ACL fields.

## Public And Internal APIs Covered

- Xattr handlers for `afs.acl`, `afs.cell`, `afs.fid`, `afs.volume`, and prefix `afs.yfs.`.
- ACL operation helpers for fetch/store AFS3 ACL and fetch/store YFS opaque ACL.
- Exported handler table: `afs_xattr_handlers`.

## Control Flow And Behavior

- `afs_xattr_get_acl()` issues an AFS FetchACL operation, returns the ACL size for size probes, copies data when the buffer is large enough, and returns `-ERANGE` otherwise.
- `afs_xattr_set_acl()` rejects `XATTR_CREATE`, copies the supplied ACL into the operation, and issues StoreACL.
- YFS gets support names `acl`, `acl_inherited`, `acl_num_cleaned`, and `vol_acl`. It requests only needed ACL payloads and maps unsupported YFS RPCs from `-ENOTSUPP` to `-ENODATA`.
- YFS set only accepts `afs.yfs.acl` and uses `StoreOpaqueACL2`.
- Metadata xattrs return the cell name, formatted FID (`vid:vnode:unique` with 96-bit vnode support), and volume name.
- Successful ACL operations commit vnode status from the returned status callback.

## State And Data Structures

- `struct afs_acl` holds variable-sized ACL data copied into/out of operations.
- `struct yfs_acl` holds YFS opaque ACL result fields, inherited flag, cleaned count, and optional volume ACL.

## Dependencies

- AFS/YFS filesystem RPC implementations, AFS operation framework, Linux xattr handler API, vnode status commit, and YFS ACL free helper.

## Risks And Invariants

- Xattr size-probe semantics return required length when `size == 0`.
- Store operations allocate/copy ACL data before RPC dispatch; operation `.put` frees it.
- YFS ACL handler must reject unsupported subnames to avoid ambiguous metadata writes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/xdr_fs.h -->
# File Research: sources/os/linux/linux/fs/afs/xdr_fs.h

## Scope

This header defines packed AFS fileserver XDR structures and directory-layout constants used for status decoding and AFS directory parsing/editing.

## APIs And Constants

- `struct afs_xdr_AFSFetchStatus` mirrors AFS FetchStatus wire fields, including type, link count, size/data-version split words, ownership, access masks, mode, parent FID parts, timestamps, group, sync counter, lock count, and abort code.
- Directory geometry constants define hash table size, dirent size, slots per block, block size, blocks per page, maximum slots/blocks, and reserved blocks.
- `union afs_xdr_dirent` describes the first directory entry slot and extended-name slots.
- `struct afs_xdr_dir_hdr`, `union afs_xdr_dir_block`, and `struct afs_xdr_dir_page` describe the on-wire directory block/page layout.
- `afs_dir_calc_slots()` computes directory-entry slot count using the standardized historical 16-byte first-name-slot calculation.

## Dependencies And Role

- Included by AFS directory and fileserver decoding code.
- Uses `PAGE_SIZE`, `__be16`, `__be32`, and packed layout annotations.

## Risks And Invariants

- Directory structures must match AFS on-disk/on-wire layout exactly.
- The slot calculation intentionally preserves a historical miscalculation; changing it would break interoperability.
- Directory block count per page assumes the AFS 2048-byte directory block size.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/xdr_fs.h -->