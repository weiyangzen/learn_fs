# Group Research: group_938_linux_stable_sources_os_linux_linux_stable_fs_afs_proc_c_sources_os__15f6de43d11b

Scope: `Docs/research_subset_a.md`. This grouped report covers the listed Linux stable AFS files under `sources/os/linux/linux-stable/fs/afs/`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/proc.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/proc.c

## Scope

Implements the `/proc/fs/afs` control and inspection interface for kAFS, including namespace-wide cell/server/stat/sysname files and per-cell volume/VL-server subdirectories.

## APIs And Behavior

- `afs_proc_init()` creates `/proc/fs/afs` entries: `cells`, `rootcell`, `servers`, `stats`, `sysname`, and `addr_prefs`; `afs_proc_cleanup()` removes them.
- `afs_proc_cell_setup()` creates per-cell `vlservers` and `volumes` files; `afs_proc_cell_remove()` removes them.
- `afs_proc_cells_write()` accepts `add <cell> <args>` and preloads/pins cells through `afs_lookup_cell()`.
- `afs_proc_rootcell_write()` initializes the workstation cell once, rejecting paths, relative names, and repeated setup.
- `afs_proc_sysname_write()` replaces the `@sys` substitution list, validating count, path separators, recursion, and dot entries.
- Seq-file show/start/next/stop routines expose cells, address preferences, volumes, VL servers, file servers, sysnames, and aggregate counters.

## State And Dependencies

The file reads and updates `struct afs_net`, `struct afs_cell`, `struct afs_volume`, `struct afs_server`, `struct afs_vlserver`, address preference lists, and `struct afs_sysnames`. Iteration is RCU/read-lock based; sysname replacement uses `sysnames_lock`; root cell setup serializes with the proc inode lock.

## Risks And Invariants

Proc writes are small command parsers and rely on pre-copied kernel buffers from procfs helpers. The sysname list must avoid recursive `@sys` suffixes and path components. VL/server display paths dereference RCU-managed address lists and assume the proc entry's private cell/net data remains valid until removal.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/protocol_afs.h -->
# File Research: sources/os/linux/linux-stable/fs/afs/protocol_afs.h

## Scope

Defines small AFS3 fileserver protocol constants related to capability replies.

## API Surface

The header declares `AFSCAPABILITIESMAX` and capability word-0 flags for UAE error translation, 64-bit file operations, ACL write-lock behavior, and deprecated sane-ACL handling.

## Dependencies And Risks

These constants are consumed by RPC/probe code that interprets fileserver capabilities. Correct bit values matter because they drive feature downgrade/upgrade decisions in the client.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/protocol_afs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/protocol_uae.h -->
# File Research: sources/os/linux/linux-stable/fs/afs/protocol_uae.h

## Scope

Defines Universal AFS Error codes used as RxRPC abort values for portable errno-style error reporting.

## API Surface

The file is a single enum mapping UAE-prefixed values from `UAEPERM` through `UAEMEDIUMTYPE`, with numeric values in the `0x2f6df00` range and comments matching Linux errno meanings.

## Dependencies And Risks

Fileserver rotation and RPC error translation compare abort codes from this enum to map remote errors into local `-errno` results. Values must remain wire-compatible; changing them would break protocol interpretation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/protocol_uae.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/protocol_yfs.h -->
# File Research: sources/os/linux/linux-stable/fs/afs/protocol_yfs.h

## Scope

Declares YFS/RxYFS service IDs, operation numbers, XDR wire structures, helpers, volume flags, lock types, and capability bits.

## APIs And Behavior

- Defines `YFS_FS_SERVICE`, `YFS_CM_SERVICE`, callback and fileserver operation opcodes, including 64-bit fetch/store, ACL, rename, and symlink operations.
- Provides packed XDR structures for YFS FIDs, status, callbacks, store status, volume sync/status, and RPC flags.
- Provides `xdr_to_u64()` and `u64_to_xdr()` conversion helpers for split 64-bit XDR values.
- Defines YFS volume status flags and lock type constants.

## Dependencies And Risks

YFS client marshalling/unmarshalling depends on exact packing and byte-order conversion. Signed lock constants and packed 64-bit fields are protocol ABI details.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/protocol_yfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/rotate.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/rotate.c

## Scope

Implements fileserver selection and retry rotation for AFS operations across volume server lists and endpoint address lists.

## APIs And Behavior

- `afs_clear_server_states()` releases per-operation endpoint-state references.
- `afs_select_fileserver()` drives the operation cursor: refreshes volume status, starts server iteration, waits for probes, picks a responding server/address by priority, handles abort/error outcomes, and decides whether to retry, switch server, refresh VLDB state, or fail.
- Handles special volume aborts including `VNOVOL`, `VMOVED`, `VBUSY`, `VOFFLINE`, quota/full errors, opcode downgrade, old OpenAFS timeout aliases, and UAE errors.
- `afs_dump_edestaddrreq()` emits limited debug state for destination-address failures.

## State And Dependencies

The rotation cursor mutates `struct afs_operation` fields such as `server_list`, `server_states`, `server_index`, `addr_index`, `addr_tried`, cumulative error, callback server, and VolSync state. It depends on volume status refresh, fileserver probes, server record validation, endpoint address preferences, callback promise clearing, and AFS/YFS RPC operation dispatch.

## Risks And Invariants

The code preserves callback/lock affinity when `AFS_OPERATION_CUR_ONLY` is set and treats server-list changes as restart points. RO replication cutover is guarded through `afs_update_volume_state()`. Error prioritization and retry flags prevent infinite VMOVED/VNOVOL loops while still allowing busy/offline volumes to recover.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/rotate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/rxrpc.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/rxrpc.c

## Scope

Maintains the RxRPC socket and call lifecycle used for outbound AFS/YFS RPCs and inbound cache-manager callback RPCs.

## APIs And Behavior

- `afs_open_socket()` creates and binds the callback socket for AFS and YFS callback services, configures security/managed responses, creates the RxGK CM key, installs RxRPC notifications, and precharges incoming calls.
- `afs_close_socket()` stops listening, flushes async work, drains outstanding calls, shuts down the socket, and releases keys.
- Call allocation/free helpers manage refs, work items, flat request/reply buffers, peer/server references, and deferred destruction.
- `afs_make_call()` begins an RxRPC call, sends fixed request data and optional write iter data, handles async extra refs, aborts on send failures, and records errors.
- `afs_deliver_to_call()` advances client/server call state, invokes type-specific unmarshalling, handles local/remote aborts, queues post-processing work, and marks completion.
- Incoming callback paths preallocate calls, attach RxRPC calls, decode operation IDs, route to cache-manager handlers, and send empty/simple replies.
- `afs_extract_data()` is the common receive helper that transitions call states when payloads complete.

## State And Dependencies

The file owns `afs_async_calls`, per-net socket state, incoming-call preallocation, `struct afs_call` state transitions, RxRPC peer/appdata, and socket notification callbacks. It depends on `net/af_rxrpc`, cache-manager routing, tracepoints, and call-type deliver/done/destructor hooks.

## Risks And Invariants

Call refs are split across synchronous waiters, async work, RxRPC notifications, and deferred free paths. Socket shutdown waits for `nr_outstanding_calls` to reach zero. Unmarshalling failures must abort with client/server marshal abort codes matching call direction.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/rxrpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/security.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/security.c

## Scope

Handles RxRPC key acquisition, anonymous-key fallback, per-vnode permit caching, and VFS permission checks against AFS ACL access masks.

## APIs And Behavior

- `afs_request_key()` and `afs_request_key_rcu()` find a cell key or use/create the cell anonymous key.
- `afs_cache_permit()` records caller access returned by status-fetching RPCs, building sorted key/access permit lists and deduplicating them through a global hash cache.
- `afs_clear_permits()` and `afs_put_permits()` invalidate and free permit lists with RCU.
- `afs_check_permit()` checks cached access or fetches status to populate it.
- `afs_permission()` maps VFS permission masks to AFS directory/file ACL bits and Unix mode bits, supporting RCU pathwalk fallback.
- `afs_clean_up_permit_cache()` warns if permit cache buckets remain populated at module exit.

## State And Dependencies

Uses global `afs_permits_cache`, `afs_permits_lock`, and `afs_key_lock`, plus each vnode's RCU `permit_cache`. It depends on kernel keyrings, `key_type_rxrpc`, status fetching, callback-break validation, and vnode status fields.

## Risks And Invariants

Permit lists are immutable once published and keyed by key pointer/access pairs. Callback breaks or changed access must detach stale permit lists before reuse. RCU permission checks must return `-ECHILD` when key acquisition or validation cannot be completed locklessly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/server.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/server.c

## Scope

Manages AFS fileserver records: lookup by UUID or RxRPC peer, creation, address discovery, probing, reference/active counts, update, expiration, and destruction.

## APIs And Behavior

- `afs_find_server()` maps an incoming RxRPC peer to an active server reference.
- `afs_lookup_server()` finds or creates a UUID-keyed server, looks up addresses through the VL service, probes the server, and waits for concurrent creation if needed.
- `afs_get_server()`, `afs_use_server()`, `afs_put_server()`, `afs_unuse_server()`, and `afs_unuse_server_notime()` manage object and active-use lifetimes.
- Timer/destroyer paths expire inactive servers, give up callbacks, unbind peer appdata, remove proc/probe links, and RCU-free records.
- `afs_check_server_record()` refreshes address lists when a server is marked stale, serializing updates with a flag bit.

## State And Dependencies

Servers live in each cell's UUID rb-tree and the net namespace proc list. Each server owns endpoint state, probe state, callback token data, volume links, timer/work items, locks, and cell references. Address discovery depends on VL cursor operations and AFS/YFS VL address RPCs.

## Risks And Invariants

Creation uses `UNCREATED`/`CREATING` bits plus waiters to avoid duplicate records. Active count zero starts GC unless the server or cell is already expiring. Peer appdata must be cleared before final server destruction to prevent stale callback routing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/server.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/server_list.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/server_list.c

## Scope

Builds and maintains per-volume fileserver lists derived from VLDB records.

## APIs And Behavior

- `afs_alloc_server_list()` chooses VLDB sites matching the volume type, applies `DONTUSE` and `NEWREPSITE` replication cutover rules, creates/uses server records, sorts entries by UUID, and returns a refcounted list.
- `afs_annotate_server_list()` detects meaningful changes between old and new lists, including excluded flags and RO replication state.
- `afs_attach_volume_to_servers()`, `afs_reattach_volume_to_servers()`, and `afs_detach_volume_from_servers()` maintain each server's sorted volume attachment list.
- `afs_put_serverlist()` drops server active-use refs and RCU-frees the list.

## State And Dependencies

The list contains `struct afs_server_entry` records with server refs, volume backpointers, flags, callback expiry, and list links. It depends on VLDB parsed entries, `afs_lookup_server()`, cell `vs_lock`, and volume server-list RCU replacement.

## Risks And Invariants

Server lists are sorted by UUID so replacement can preserve callback metadata and reattach efficiently. RO release handling intentionally excludes old or new replica sites until a majority cutover condition is met.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/server_list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/super.c

## Scope

Implements AFS filesystem registration, mount context parsing/validation, superblock creation/reuse, inode-cache management, and `statfs`.

## APIs And Behavior

- `afs_fs_init()` creates the vnode slab and registers the `afs` filesystem; `afs_fs_exit()` unregisters and destroys it.
- Mount parsing handles `source`, `dyn`, `autocell`, and `flock=` options, including `%`/`#` source prefixes and `.readonly`/`.backup` suffixes.
- `afs_validate_fc()` resolves the cell, gets a key, detects aliases, creates a volume, and forces read-only/local-locking behavior for RO/backup volumes.
- `afs_get_tree()` allocates `afs_super_info`, reuses matching superblocks, or fills new dynroot/volume superblocks.
- Inode slab hooks initialize/reset vnode locks, callback state, writeback key lists, directory/symlink cache pointers, and flags.
- `afs_statfs()` issues AFS/YFS get-volume-status operations for real volumes and returns fixed values for dynroot.

## State And Dependencies

Uses `struct file_system_type`, `super_operations`, fs-context private state, `afs_super_info`, volume/cell/key refs, dynroot helpers, root inode lookup, fscache activation, and netfs writeback integration.

## Risks And Invariants

Source parsing determines RW/RO/backup semantics that later affect server selection and mount writability. Superblock matching is by net namespace, cell, and volume ID. Inode reuse requires explicit reset of all non-static vnode state in `afs_alloc_inode()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/symlink.c

## Scope

Caches, validates, reads, exposes, and writes back AFS symlink contents.

## APIs And Behavior

- RCU/refcount helpers manage `struct afs_symlink` objects attached to vnodes.
- `afs_init_new_symlink()` installs newly created symlink text and optionally stages it in a folio queue for fscache writeback.
- `afs_read_symlink()`/`afs_do_read_symlink()` perform a single-unit netfs read, cap size at one page minus NUL, copy data into a NUL-terminated symlink object, and optionally discard transient folio buffers.
- `afs_get_link()` supports RCU pathwalk for already-valid cached links and locked slow-path download/validation otherwise.
- `afs_readlink()` copies cached link content to userspace.
- `afs_symlink_writepages()` writes staged symlink data to cache and frees the folio queue.

## State And Dependencies

Uses vnode `symlink`, `directory`, `directory_size`, `validate_lock`, callback promise state, fscache cookies, netfs single-read/writeback helpers, and VFS inode/address-space operation tables.

## Risks And Invariants

AFS symlinks are read as one unit to avoid content races across partial reads. RCU pathwalk may only return cached data when vnode validity is already proven. Cached symlink text is invalidated on callback-driven data changes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/validation.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/validation.c

## Scope

Implements vnode and volume validity checks using callback promises, volume callbacks, VolSync timestamps, and cache-scrub counters.

## APIs And Behavior

- `afs_check_validity()` performs a lockless validity test against vnode deletion, callback expiry, volume callback break/check counters, RO snapshot counters, scrub counters, and zap flags.
- VolSync helpers update volume creation/update times, detect RO snapshot advance, RW/backup regressions, excluded servers during replication, and scrub-triggering timestamp regressions.
- `afs_update_volume_state()` records callback expiry for server/volume entries and advances `cb_v_check` after successful operations.
- `afs_validate()` serializes validation, optionally locks the volume callback check, fetches status when promises/counters are stale, handles deleted vnodes, updates vnode snapshot/scrub mirrors, invalidates mmaps, zaps regular data, or invalidates symlink content.

## State And Dependencies

Touches `struct afs_vnode`, `struct afs_volume`, server-list callback expiry, vnode/volume callback counters, page cache, mmap mappings, symlink cache, and `afs_fetch_status()`. It depends on callback handling elsewhere to increment break counters.

## Risks And Invariants

Volume-level and vnode-level callback state must be reconciled in order. RO volume snapshot changes should advance `cb_ro_snapshot`, while regressions or unexpected creation-time changes scrub caches. Status fetches are the authoritative repair path when callback promises expire or are broken.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/validation.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/vl_alias.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/vl_alias.c

## Scope

Detects when a newly discovered AFS cell is an alias of an already known cell.

## APIs And Behavior

- Samples volumes in a candidate cell with `afs_create_volume()`.
- Compares root or sampled volume IDs, sorted server UUID lists, and fileserver address-list peer matches.
- For YFS VL servers, queries the canonical cell name and resolves it to an existing/master cell when it differs.
- Falls back to comparing `root.cell` volume data, or querying arbitrary known volumes in cells without `root.cell`.
- `afs_cell_detect_alias()` serializes alias detection and records `cell->alias_of` on success.

## State And Dependencies

Uses cell volume rb-trees, proc cell list, root-volume cache, volume/server/address-list comparisons, VL cursor RPCs, and cell lookup refs. It depends on volume creation and server-list address discovery being sufficiently complete for comparison.

## Risks And Invariants

Alias detection is heuristic unless YFS canonical names are available. The code avoids aliasing against cells already marked as aliases and transfers cell references into `alias_of` on success.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/vl_alias.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/vl_list.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/vl_list.c

## Scope

Allocates VL-server records/lists and parses DNS server-list payloads into AFS VL server/address structures.

## APIs And Behavior

- `afs_alloc_vlserver()` and `afs_put_vlserver()` manage named VL server records with locks, probe state, service ID, port, and address list.
- `afs_alloc_vlserver_list()` and `afs_put_vlserverlist()` manage ordered VL server lists.
- `afs_extract_vl_addrs()` parses IPv4/IPv6 DNS address records and builds an address list, preferring IPv6 when available.
- `afs_extract_vlserver_list()` validates DNS server-list v1 payloads, reuses existing server records by name/port, updates address lists, sorts entries by priority then weight, and records DNS source/status.

## State And Dependencies

Depends on DNS payload structures, address merge helpers, cell `vl_servers`, and RCU-managed address-list replacement. Existing VL server lists are consulted to preserve server objects across DNS refreshes.

## Risks And Invariants

Payload parsing must advance over names and addresses even when some entries are unusable. Empty address records are accepted only if a server already has addresses. Malformed non-memory failures dump the DNS payload for diagnostics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/vl_list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/vl_probe.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/vl_probe.c

## Scope

Probes volume-location servers to determine reachability, preferred endpoint, RTT, and YFS service support.

## APIs And Behavior

- `afs_send_vl_probes()` starts `VL.GetCapabilities` probes for unprobed servers.
- `afs_vlserver_probe_result()` records each async probe result, marks responding/failed address bits, stores errors/abort codes, detects YFS via service ID, updates preferred address and RTT, and wakes waiters.
- `afs_wait_for_vl_probes()` waits until an untried server responds or probing finishes/interruption occurs, then picks the lowest-RTT responding server.

## State And Dependencies

Uses per-vlserver `probe`, `probe_outstanding`, flags, waitqueues, address-list `responded`/`probe_failed` bits, and RxRPC smoothed RTT. Probe RPCs are created by `afs_vl_get_capabilities()` in `vlclient.c`.

## Risks And Invariants

Probe completion must clear `PROBING` exactly once when the outstanding count reaches zero. YFS detection changes the server service ID used by later VL calls. Local key/network errors are tracked separately from unreachable endpoint failures.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/vl_probe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/vl_rotate.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/vl_rotate.c

## Scope

Implements the VL-server operation cursor and retry/address rotation logic.

## APIs And Behavior

- `afs_begin_vlserver_operation()` initializes a cursor with cell, key, debug ID, and default cumulative error.
- `afs_select_vlserver()` refreshes DNS/VL server lists, sends probes, selects responding VL servers by preferred/lowest RTT, iterates endpoint addresses, updates preferred addresses after responses, and handles retryable transport/op-not-supported errors.
- `afs_end_vlserver_operation()` releases cursor refs, dumps limited debug information for address failures, and returns the prioritized cumulative error.

## State And Dependencies

The cursor owns refs to a VL server list and current address list, tracks untried servers, tried addresses, selected server/address, call result, response state, retry flags, and cumulative error. It depends on DNS cell refresh, VL probes, and `afs_prioritise_error()`.

## Risks And Invariants

The cursor restarts at most once on retry flags to avoid loops. Preferred address updates occur only after a call responded. DNS lookup unavailability or not-found status is translated before any VL RPC is attempted.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/vl_rotate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/vlclient.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/vlclient.c

## Scope

Implements AFS and YFS Volume Location Service client RPC marshalling and reply delivery.

## APIs And Behavior

- `afs_vl_get_entry_by_name_u()` calls `VL.GetEntryByNameU`, unmarshalling volume IDs, flags, server UUIDs, server masks, and address versions into `afs_vldb_entry`.
- `afs_vl_get_addrs_u()` calls `VL.GetAddrsU` for a fileserver UUID and returns IPv4 address lists.
- `afs_vl_get_capabilities()` starts async `VL.GetCapabilities` probes used by VL probing.
- `afs_yfsvl_get_endpoints()` calls `YFSVL.GetEndpoints`, parsing IPv4/IPv6 endpoint vectors and ignoring volume endpoints after validating them.
- `afs_yfsvl_get_cell_name()` calls `YFSVL.GetCellName` and returns a bounded NUL-terminated canonical cell name.

## State And Dependencies

Each RPC uses `struct afs_call`, VL cursor peer/address selection, flat-call buffers, XDR structures from `afs_vl.h`, address merge helpers, and call-type deliver/destructor hooks. Probe calls carry VL server/address-list refs until completion.

## Risks And Invariants

Unmarshallers are staged state machines and must reject oversized counts, bad endpoint types, and malformed lengths with protocol errors. UUID byte-order conversion differs between legacy AFS VL structs and YFS opaque UUID payloads.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/vlclient.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/volume.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/volume.c

## Scope

Manages AFS volume records, VLDB lookup, volume type selection, fileserver-list replacement, fscache volume activation, and volume-status refresh.

## APIs And Behavior

- `afs_create_volume()` looks up a VLDB entry, applies forced/default RW/RO/backup selection rules, and creates or reuses a cell volume record.
- Allocation initializes volume IDs, name, type, callback/VolSync state, locks, open mmap tracking, and initial server list.
- Volumes are inserted into the cell rb-tree/proc list by volume ID and attached to server volume lists.
- Refcount drop schedules `afs_destroy_volume()`, which detaches from servers, removes cell indexes, drops server list/cell refs, and RCU-frees the record.
- `afs_activate_volume()`/`afs_deactivate_volume()` acquire and relinquish fscache volume cookies when enabled.
- `afs_check_volume_status()` serializes VLDB refreshes, updates renamed volumes and server lists, adjusts refresh interval for RO replication, and handles waiters.

## State And Dependencies

Depends on VL cursor lookup, server-list construction/annotation/reattachment, cell volume locks, fscache, volume flags, and operation keys. Volume server-list replacement uses RCU plus sequence counters.

## Risks And Invariants

Type selection implements AFS mount-point traversal rules. Server-list replacement must preserve attachments and callback expiry where possible. `AFS_VOLUME_WAIT`/`UPDATING` bits serialize refresh and bound stale wait retries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/volume.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/write.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/write.c

## Scope

Integrates AFS regular-file writeback with the netfs library and fileserver StoreData RPCs.

## APIs And Behavior

- `afs_begin_writeback()` selects a valid cached author key for regular-file writeback.
- `afs_prepare_write()` sets the stream subrequest max length.
- `afs_issue_write()` queues `afs_issue_write_worker()`, which builds a StoreData operation, sets vnode modification/data-version delta, attaches the subrequest iterator, waits for completion, and terminates the netfs subrequest.
- `afs_retry_request()` rotates writeback keys after auth/key failures.
- `afs_writepages()` wraps `netfs_writepages()` under `validate_lock` to avoid races with truncation/status validation.
- `afs_fsync()` validates the vnode with the file key and then waits on dirty/writeback pages.
- `afs_page_mkwrite()` validates before allowing writable mmap faults.
- `afs_prune_wb_keys()` drops unused writeback keys once no dirty/writeback pages remain.

## State And Dependencies

Uses vnode writeback key lists, netfs writeback requests/subrequests, `afs_operation`, StoreData AFS/YFS RPCs, vnode status commit, page-cache tags, and validation locks.

## Risks And Invariants

Writes may need to retry with different author keys. StoreData operations are marked uninterruptible and advance data version by one. Writeback avoids blocking async callers on `validate_lock` in `WB_SYNC_NONE`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/xattr.c

## Scope

Exposes AFS metadata and ACL operations through Linux extended attributes.

## APIs And Behavior

- `afs.acl` gets/sets AFS3 ACLs through `afs_fs_fetch_acl()` and `afs_fs_store_acl()`.
- `afs.yfs.acl`, `afs.yfs.acl_inherited`, `afs.yfs.acl_num_cleaned`, and `afs.yfs.vol_acl` expose YFS opaque ACL data and metadata; setting is supported only for `afs.yfs.acl`.
- Read-only xattrs `afs.cell`, `afs.fid`, and `afs.volume` return cell name, formatted FID, and volume name.
- Handler tables publish AFS ACL, metadata, and YFS-prefix handlers for non-dynroot superblocks.

## State And Dependencies

Uses `struct afs_operation`, vnode volume/cell/FID state, AFS and YFS ACL RPCs, status commit on success, and allocated ACL buffers.

## Risks And Invariants

`XATTR_CREATE` is rejected for ACL mutation. YFS unsupported operations are translated from `-ENOTSUPP` to `-ENODATA`. Buffer sizing follows xattr conventions: size zero queries required length, too-small buffers return `-ERANGE`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/xdr_fs.h -->
# File Research: sources/os/linux/linux-stable/fs/afs/xdr_fs.h

## Scope

Defines AFS fileserver XDR structures and constants for file status and directory page/block/entry layout.

## API Surface

- `struct afs_xdr_AFSFetchStatus` mirrors AFS fetch-status wire fields, including low/high size and data-version pieces, access masks, mode, parent FID, timestamps, lock count, and abort code.
- Directory constants define hash-table size, 32-byte dirent slots, 2048-byte blocks, blocks per page, slot/block limits, and reserved block counts.
- `union afs_xdr_dirent`, `struct afs_xdr_dir_hdr`, `union afs_xdr_dir_block`, and `struct afs_xdr_dir_page` describe packed directory storage.
- `afs_dir_calc_slots()` computes standardized dirent slot count from a filename length, including the historical first-slot size miscalculation.

## Dependencies And Risks

Directory parsing/editing code depends on these packed layouts and constants matching AFS on-disk/wire directory format. The slot calculation intentionally preserves protocol-compatible behavior even though the physical first slot has more name bytes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/xdr_fs.h -->