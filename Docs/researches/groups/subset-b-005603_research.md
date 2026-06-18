<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/internal.h -->
# sources/distributed-fs/ceph-client/fs/afs/internal.h

## Purpose
Central private header for the Linux kAFS client. It defines the shared in-memory model for cells, VL servers, fileservers, volumes, vnodes, calls, operation cursors, mount context, address lists, permits, callbacks, and all internal cross-file entry points.

## Important APIs, Types, And Functions
Key types include `afs_net`, `afs_cell`, `afs_vlserver`, `afs_server`, `afs_volume`, `afs_vnode`, `afs_call`, `afs_operation`, `afs_vl_cursor`, `afs_server_list`, `afs_addr_list`, `afs_endpoint_state`, `afs_permits`, and `afs_fs_context`. Inline helpers bridge VFS objects to AFS state (`AFS_FS_I`, `AFS_FS_S`, `afs_i2net`, `afs_v2net`), manage call state, cache auxiliary data, callback promises, dentry versions, inode size, and operation errors. The header declares the subsystem APIs implemented by address, cell, callback, dir, file, flock, fsclient, fs_operation, fs_probe, inode, mountpoint, proc, rotate, rxrpc, security, server, super, validation, VL, volume, write, xattr, and YFS modules.

## Control Flow
Most source files in `fs/afs` include this header and communicate through the structures it defines. Higher-level VFS operations create `afs_operation` objects, rotation code chooses servers and addresses, RxRPC call helpers send protocol operations, reply parsers update `afs_vnode_param` status/callback state, and validation/security code consume those updates.

## State And Persistence
The state is kernel-resident and mostly per network namespace, superblock, volume, vnode, server, and call. Lifetime is guarded by refcounts, active counts, RCU, workqueues, timers, seqlocks, rwsems, spinlocks, and atomics. Persistent external state is on AFS servers; local caching integrates with fscache/netfs and pagecache.

## Dependencies And Integration Points
Depends on Linux VFS, netfs, fscache, keyrings, RxRPC, DNS resolver, procfs, workqueues, timers, RCU, network namespaces, and tracepoints. It also binds AFS3, YFS, RxKAD, and RxGK protocol support.

## Risks And Edge Cases
The main risks are lifetime mismatches across RCU/refcounted objects, callback promise races, server-list replacement during operations, address/probe staleness, mount context alias switching, and subtle error prioritisation. `ASSERT*` macros can BUG the kernel when internal invariants are violated.

## Test Signals
Useful signals include successful AFS mounts, dynroot/autocell behavior, callback break handling, server failover, VLDB lookup, procfs diagnostics, tracepoint coverage, lockdep/KASAN/KCSAN, and operation retries under server/network failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/main.c -->
# sources/distributed-fs/ceph-client/fs/afs/main.c

## Purpose
Module entry and per-network-namespace lifecycle for the kAFS client. It registers module parameters, allocates global workqueues, initializes per-net AFS state, creates the RxRPC transport, and registers the AFS filesystem.

## Important APIs, Types, And Functions
Exports `afs_wq`, `afs_debug`, `afs_init_sysname`, and `afs_net_id`. `afs_net_init()` initializes `afs_net` fields, cell/server/proc/sysname state, timers, and the RxRPC socket. `afs_net_exit()` tears this down. `afs_init()` allocates `afs`, `kafsd`, and `kafs_lockd` workqueues, registers pernet operations, registers the filesystem, and creates `/proc/fs/afs` symlink. `afs_exit()` reverses this.

## Control Flow
`late_initcall(afs_init)` runs after networking so a socket can be created. On namespace creation, `afs_net_init()` sets up bookkeeping, procfs, root cell data, and transport. On module exit, filesystem registration and pernet state are removed before workqueues and permit cache are cleaned.

## State And Persistence
State is in `struct afs_net` per net namespace plus global workqueues and proc symlink. `rootcell` and `debug` module parameters affect initialization and runtime debugging. No persistent disk state is written.

## Dependencies And Integration Points
Integrates with module loading, pernet operations, procfs, workqueues, key/security setup, cell management, fileserver probing, RxRPC socket setup, and filesystem registration in `super.c`.

## Risks And Edge Cases
Partial initialization must unwind in reverse order without leaving sockets, proc entries, cells, servers, or work items live. Namespace teardown depends on outstanding server and call counters reaching zero. Architecture-specific `afs_init_sysname` drives `@sys` substitution defaults.

## Test Signals
Module load/unload, namespace creation/destruction, rootcell module parameter handling, `/proc/net/afs` creation, workqueue allocation failure injection, and clean `rcu_barrier()`/outstanding-counter behavior are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/misc.c -->
# sources/distributed-fs/ceph-client/fs/afs/misc.c

## Purpose
Shared error translation and cumulative error prioritisation for AFS operations.

## Important APIs, Types, And Functions
`afs_abort_to_error()` maps AFS/Vice, VLDB, UAE, RxKAD, RxGK, Kerberos, and RxRPC abort codes into Linux negative errno values. `afs_prioritise_error()` updates an `afs_error` accumulator based on response quality and failure precedence, including abort-derived errors and network reachability errors.

## Control Flow
RPC paths record per-call errors and abort codes. Rotation and VL code call `afs_prioritise_error()` as addresses and servers fail; final operation completion reports the selected accumulated errno. `-ECONNABORTED` is special: it is translated through `afs_abort_to_error()` and marks the accumulator as having received a server response.

## State And Persistence
The file mutates only caller-provided `struct afs_error` fields (`error`, `abort_code`, `responded`, `aborted`). It has no durable state.

## Dependencies And Integration Points
Depends on `afs_fs.h`, `protocol_uae.h`, RxKAD/RxGK constants, and Kerberos error constants. Used by fileserver rotation, VL probing, and operation wrappers.

## Risks And Edge Cases
Incorrect mappings leak protocol-specific aborts to userspace or cause wrong retry/failover behavior. Error precedence deliberately preserves stronger failures such as timeout, memory, no network, rfkill, and address reachability over weaker later errors; changing order can alter user-visible errno.

## Test Signals
Inject server aborts (`VNOVOL`, `VMOVED`, `VDISKFULL`, UAE errors), auth failures, unsupported opcodes, and network errors, then verify returned errno and retry/failover decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/mntpt.c -->
# sources/distributed-fs/ceph-client/fs/afs/mntpt.c

## Purpose
Implements AFS mountpoint and autocell automount behavior. AFS mountpoints are special symlinks or pseudo-directory entries that trigger creation of a submount for another cell/volume.

## Important APIs, Types, And Functions
Provides `afs_mntpt_file_operations`, `afs_mntpt_inode_operations`, `afs_autocell_inode_operations`, `afs_d_automount()`, and `afs_mntpt_kill_timer()`. Internal helpers reject normal lookup/open on mountpoints, parse mountpoint parameters with `afs_mntpt_set_params()`, and create submounts with `afs_mntpt_do_automount()`.

## Control Flow
When VFS automounts a mountpoint dentry, `afs_d_automount()` creates a submount context, inherits the source net namespace, derives cell and volume from either pseudo-directory name or symlink contents, mounts through `fc_mount()`, then puts the mount on an expiry list. A delayed work item periodically calls `mark_mounts_for_expiry()`.

## State And Persistence
Maintains a global `afs_vfsmounts` expiry list and delayed expiry work on `afs_wq`. Mountpoint interpretation updates a temporary `afs_fs_context`; the mounted volume/cell state is owned by the resulting superblock.

## Dependencies And Integration Points
Uses fs_context submount APIs, VFS automount expiry, AFS cell lookup, symlink reading via `afs_get_link()`, and mount parsing in `super.c`.

## Risks And Edge Cases
Bad symlink content, overlong cell names, backup-to-backup mount crossing, pseudo-directory names beginning with `.`, and net namespace replacement are sensitive. Expiry work must be cancelled only after the mount list is empty.

## Test Signals
Automount regular AFS mountpoint symlinks, autocell pseudo-directories, forced RW (`.` prefix), backup volume rejection, malformed symlink content, and mount expiry after inactivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/mntpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/proc.c -->
# sources/distributed-fs/ceph-client/fs/afs/proc.c

## Purpose
Implements `/proc/net/afs` diagnostics and configuration for a network namespace.

## Important APIs, Types, And Functions
Exports `afs_proc_init()`, `afs_proc_cleanup()`, `afs_proc_cell_setup()`, `afs_proc_cell_remove()`, and `afs_put_sysnames()`. It implements seq_file views and writers for `cells`, `rootcell`, `servers`, `stats`, `sysname`, `addr_prefs`, and per-cell `vlservers` and `volumes`.

## Control Flow
Namespace initialization creates the proc tree. Readers iterate RCU-protected cell/server/volume/VL lists and print refcounts, active counts, DNS status, probe state, endpoint lists, address preferences, and counters. Writers allow adding pinned cells, setting the initial root cell once, changing `@sys` substitutions, and delegating address preference writes.

## State And Persistence
Proc writes mutate in-kernel namespace state: cell database, workstation cell, `afs_sysnames`, and address preferences. No file-backed persistence exists; values reset with namespace/module lifetime.

## Dependencies And Integration Points
Integrates procfs/seq_file, RCU lists from cell/server/volume management, DNS status enums, RxRPC peer address formatting, and address preference parsing.

## Risks And Edge Cases
Writers parse simple whitespace-delimited commands and must reject invalid names, recursive `@sys`, path separators, excessive substitutions, and repeated rootcell assignment. Readers rely on RCU and lock pairing; VL display assumes a valid server list when iterating.

## Test Signals
Read all proc files under active and empty namespaces, add cells through `cells`, set `rootcell`, update `sysname`, observe server/VL probe diagnostics, and run under lockdep with concurrent cell/server churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/protocol_afs.h -->
# sources/distributed-fs/ceph-client/fs/afs/protocol_afs.h

## Purpose
Defines small AFS3 fileserver capability constants shared by protocol clients.

## Important APIs, Types, And Functions
Defines `AFSCAPABILITIESMAX` and capability bits for UAE error translation, 64-bit file operations, write-lock ACL behavior, and historical sane ACL signaling.

## Control Flow
No executable control flow. Capability replies parsed elsewhere use these masks to set server feature flags such as 64-bit fetch/store support and error translation behavior.

## State And Persistence
No state. The constants influence runtime server capability state stored in `struct afs_server`.

## Dependencies And Integration Points
Used by fileserver capability probing/client code together with AFS3/YFS operation selection and error translation.

## Risks And Edge Cases
Wrong bit assignments would mis-detect server abilities, causing unsupported opcodes or missed 64-bit operation support. Deprecated capability meanings should not be overinterpreted.

## Test Signals
Probe OpenAFS/AFS3 servers with different capabilities and verify selected RPC variants and error mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/protocol_afs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/protocol_uae.h -->
# sources/distributed-fs/ceph-client/fs/afs/protocol_uae.h

## Purpose
Defines the Universal AFS Error code namespace used by newer AFS/YFS services to return portable errno-like abort values.

## Important APIs, Types, And Functions
Contains a single enum mapping `UAE*` names to the `0x2f6df00` error table, covering common POSIX errno values plus network, quota, stale, medium, and remote I/O errors.

## Control Flow
No executable control flow. `misc.c` translates selected UAE abort codes to Linux errno values, and rotation code recognizes some UAE values directly for volume/full/quota/I/O decisions.

## State And Persistence
No state. The values are wire ABI constants and must remain stable.

## Dependencies And Integration Points
Integrated with fileserver/VL RPC unmarshalling and abort handling. Complements legacy Vice and VL abort constants.

## Risks And Edge Cases
Because this is a protocol ABI list, changing numeric values breaks interoperability. Only some codes are explicitly translated in `afs_abort_to_error()`; unhandled codes fall back to `-EREMOTEIO`.

## Test Signals
Server abort injection with UAE values should produce expected Linux errno for mapped cases and safe fallback for unmapped cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/protocol_uae.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/protocol_yfs.h -->
# sources/distributed-fs/ceph-client/fs/afs/protocol_yfs.h

## Purpose
Defines YFS service IDs, cache-manager and fileserver operation numbers, XDR wire structures, conversion helpers, volume/lock constants, and capability flags.

## Important APIs, Types, And Functions
Key definitions include `YFS_FS_SERVICE`, `YFS_CM_SERVICE`, `enum YFS_CM_Operations`, `enum YFS_FS_Operations`, `struct yfs_xdr_u64`, `xdr_to_u64()`, `u64_to_xdr()`, YFS fid/status/callback/store/volsync/volume-status structs, volume type flags, lock types, and capability masks.

## Control Flow
No runtime flow in the header. YFS client code uses operation constants to marshal requests and XDR structs to parse replies. Rotation and probe paths switch to YFS op implementations when probes identify a YFS service.

## State And Persistence
No local state. It defines wire formats for server state such as fid, status, callback expiration, volume sync times, ACLs, and locks.

## Dependencies And Integration Points
Used by RxRPC call construction, YFS fileserver clients, cache-manager service handling, capability probing, and validation logic that consumes YFS VolSync/callback replies.

## Risks And Edge Cases
Packed struct layout and endian conversion must match wire ABI exactly. Mis-sized fields or wrong opcodes break interoperability. Signed lock constants and 64-bit conversions are particularly sensitive.

## Test Signals
YFS server mount, capability probe upgrade, 64-bit fetch/store, YFS rename/remove variants, lock operations, callback handling, and VolSync validation are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/protocol_yfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/rotate.c -->
# sources/distributed-fs/ceph-client/fs/afs/rotate.c

## Purpose
Selects fileservers and endpoint addresses for a volume operation, handles retry/failover, interprets server aborts, and coordinates volume/server-list refreshes.

## Important APIs, Types, And Functions
Exports `afs_clear_server_states()`, `afs_select_fileserver()`, and `afs_dump_edestaddrreq()`. Internal flow uses `afs_start_fs_iteration()`, `afs_busy()`, and `afs_sleep_and_retry()`. It consumes `afs_operation`, `afs_server_list`, `afs_server_state`, `afs_endpoint_state`, and cumulative error helpers.

## Control Flow
On first iteration it refreshes volume status, snapshots the current server list, records endpoint probe state, and tries to preserve the vnode callback server. Each later call evaluates the previous RPC result. Success may still trigger RO replication checks. Abort handling covers `VNOVOL`, `VMOVED`, `VOFFLINE`, `VBUSY`, quota/full, unsupported op downgrade, and transient network errors. It waits for probes, picks the best-priority responsive address, and returns true when a call should be issued.

## State And Persistence
Mutates operation cursor fields, per-address `last_error`, server-list flags (`VOLUME_BUSY`, `OFFLINE`, `vnovol_mask`), volume update flags, callback server/promise state on the vnode, and preferred address selection. State is transient but affects subsequent retries and volume validation.

## Dependencies And Integration Points
Depends on fs probe waiters, server record update, address preferences, volume status checks, AFS/Vice/UAE abort constants, RxRPC peer metrics, and validation’s `afs_update_volume_state()`.

## Risks And Edge Cases
Failover must not violate file locks (`CUR_ONLY`), regress RO replica data, loop forever on `VMOVED`/`VNOVOL`, or hide state-changing timeout ambiguity. Probe-state supersession and callback server changes are race-prone.

## Test Signals
Exercise multi-server volumes, address failure, busy/offline volumes, VMOVED/VNOVOL refresh, unsupported opcode downgrade, RO release in progress, file lock current-server-only operations, and `CONFIG_AFS_DEBUG_CURSOR` diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/rotate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/rxrpc.c -->
# sources/distributed-fs/ceph-client/fs/afs/rxrpc.c

## Purpose
Owns the RxRPC socket used by kAFS, client call lifecycle, asynchronous receive processing, incoming cache-manager callback dispatch, reply sending, and receive extraction.

## Important APIs, Types, And Functions
Exports `afs_async_calls`, `afs_open_socket()`, `afs_close_socket()`, `afs_charge_preallocation()`, `afs_put_call()`, `afs_deferred_put_call()`, `afs_make_call()`, `afs_deliver_to_call()`, `afs_wait_for_call_to_complete()`, `afs_alloc_flat_call()`, `afs_flat_call_destructor()`, `afs_send_empty_reply()`, `afs_send_simple_reply()`, `afs_extract_data()`, and `afs_protocol_error()`. It defines RxRPC kernel callbacks and the initial incoming `CB.xxxx` call type.

## Control Flow
`afs_open_socket()` creates an AF_RXRPC socket, binds AFS and YFS callback services, sets security/response behavior, installs callbacks, listens, and precharges incoming calls. Outgoing calls are allocated, optionally given flat buffers, started with `rxrpc_kernel_begin_call()`, transmit fixed and optional write data, then complete via synchronous waits or async work. Incoming calls use preallocated `afs_call` objects, read the operation ID, route through cache-manager dispatch, and send replies.

## State And Persistence
Tracks `afs_call` refcounts, RxRPC call handles, peer refs, call state transitions, outstanding call counts, spare incoming calls, and workqueue references. No disk persistence; network protocol state lives in RxRPC and remote peers.

## Dependencies And Integration Points
Integrates Linux AF_RXRPC, keyrings/security, callback service (`cmservice.c`), RxGK token setup, tracepoints, workqueues, server lookup by peer, and all RPC client files through `afs_call_type`.

## Risks And Edge Cases
Refcounting is delicate for async calls and notifications under spinlock. Send failures, immediate cancellation, remote abort parsing, unmarshalling errors, incoming preallocation exhaustion, and socket shutdown must not leak calls or leave waiters asleep.

## Test Signals
Mount/fetch/store workloads, callback storms, async fetch cancellation, module/netns teardown with outstanding calls, forced remote aborts, malformed replies, RxRPC security upgrade behavior, and leak/lockdep testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/rxrpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/security.c -->
# sources/distributed-fs/ceph-client/fs/afs/security.c

## Purpose
Manages AFS authentication key lookup, anonymous fallback keys, per-vnode access permit caching, and VFS permission checks.

## Important APIs, Types, And Functions
Exports `afs_request_key()`, `afs_request_key_rcu()`, `afs_put_permits()`, `afs_clear_permits()`, `afs_cache_permit()`, `afs_check_permit()`, `afs_permission()`, and `afs_clean_up_permit_cache()`. It uses a global hash table of immutable `afs_permits` lists, protected by spinlock and RCU, and an anonymous key allocation mutex.

## Control Flow
Permission checks request a key for the cell. RCU pathwalk uses nonblocking key lookup and cached validity only; blocking checks validate the vnode, then fetch/cache CallerAccess if missing. `afs_cache_permit()` builds or reuses sorted immutable permit arrays, handles callback-break races, and swaps them into the vnode under lock.

## State And Persistence
State includes cell anonymous keys, key refs in permit lists, vnode `permit_cache`, and the global permit-list deduplication hash. Caches are invalidated on callback break and freed through RCU. No durable persistence exists beyond keyring contents.

## Dependencies And Integration Points
Uses Linux keyrings/RxRPC key type, VFS permission hooks, AFS callback validation, `afs_fetch_status()`, vnode status ACL fields, and AFS ACL bit definitions.

## Risks And Edge Cases
RCU pathwalk must return `-ECHILD` when blocking work or allocation is required. Callback breaks during permit update must prevent stale ACL use. Key pointer sorting/hashing assumes stable key object identity and careful ref ownership.

## Test Signals
Authenticated and anonymous access, RCU pathwalk permission checks, ACL changes with callback invalidation, concurrent permission checks, key expiration/revocation, and permit-cache cleanup warnings at module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/server.c -->
# sources/distributed-fs/ceph-client/fs/afs/server.c

## Purpose
Creates, indexes, updates, references, expires, and destroys active fileserver records for a cell.

## Important APIs, Types, And Functions
Exports `afs_find_server()`, `afs_lookup_server()`, `afs_get_server()`, `afs_use_server()`, `afs_unuse_server()`, `afs_unuse_server_notime()`, `afs_put_server()`, `afs_purge_servers()`, `afs_wait_for_servers()`, and `afs_check_server_record()`. Internal helpers allocate/install UUID-indexed servers, query VLDB addresses, update address records, expire idle servers, and give up callbacks on teardown.

## Control Flow
Lookup first searches the cell UUID rb-tree under read lock. Missing records are allocated as `UNCREATED`, installed under write lock, marked `CREATING`, populated with VLDB addresses, and immediately probed. Other waiters sleep on the creating bit. Active uses cancel the idle timer; unuse schedules GC or destroy work. Address-version mismatch marks a server for update, which is serialized with `AFS_SERVER_FL_UPDATING`.

## State And Persistence
Server state includes UUID, active/ref counts, endpoint state, address version, service ID, probe lists, timers, callback-token data, volume attachments, proc/probe links, flags, and cell ref. All state is in memory and RCU-freed.

## Dependencies And Integration Points
Integrates with VL rotation/client lookup, fileserver probing, RxRPC peer appdata, callback give-up RPC, procfs server listing, volume server lists, and namespace outstanding-server waiters.

## Risks And Edge Cases
Creation failure must wake waiters with the right error. Expiration logic appears sensitive to `net->live`/cell removal conditions. Address update waits can return stale failure after retries. Peer appdata must be unbound before RCU free.

## Test Signals
Concurrent volume lookups for the same UUID, VLDB address changes, server GC after inactivity, cell purge/netns exit, callback give-up on destroy, and probe-triggered service updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/server_list.c -->
# sources/distributed-fs/ceph-client/fs/afs/server_list.c

## Purpose
Builds and manages replaceable per-volume fileserver lists derived from VLDB records.

## Important APIs, Types, And Functions
Exports `afs_put_serverlist()`, `afs_alloc_server_list()`, `afs_annotate_server_list()`, `afs_attach_volume_to_servers()`, `afs_reattach_volume_to_servers()`, and `afs_detach_volume_from_servers()`. It works with `afs_server_list`, `afs_server_entry`, VLDB masks/flags, and volume/server attachment lists.

## Control Flow
Allocation filters VLDB server entries by requested volume type, applies `DONTUSE` exclusions, handles RO replication `NEWREPSITE` cutover when at least half usable sites are updated, looks up each fileserver, and insertion-sorts by UUID while deduplicating. Attach/reattach/detach maintain each server’s sorted `volumes` list under the cell volume-server lock.

## State And Persistence
Server lists are refcounted and RCU-freed. Entries retain active server uses while the list lives and carry per-volume flags and callback expiry. Attach state records whether list entries are linked into server volume lists.

## Dependencies And Integration Points
Depends on VLDB entry parsing, `afs_lookup_server()`, cell `vs_lock`, volume replacement in volume management, rotation server selection, and validation callback expiry state.

## Risks And Edge Cases
RO replication cutover policy directly affects consistency during `vos release`. Duplicate server UUIDs, empty usable lists, server lookup failures, and reattach diff logic can break failover or callback propagation.

## Test Signals
VLDB records with RW/RO/BK masks, `DONTUSE`, `NEWREPSITE`, duplicate servers, no servers, server-list replacement, and callback expiry preservation during reattach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/server_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/super.c -->
# sources/distributed-fs/ceph-client/fs/afs/super.c

## Purpose
Implements AFS filesystem registration, mount parameter parsing, superblock creation/reuse, inode slab lifecycle, mount option display, and statfs.

## Important APIs, Types, And Functions
Defines `afs_fs_type`, `afs_net_id`, `afs_super_ops`, `afs_fs_init()`, and `afs_fs_exit()`. Internal functions parse `source`, `dyn`, `autocell`, and `flock`, validate mount context, allocate/destroy `afs_super_info`, fill superblocks, allocate/free/destroy `afs_vnode` inodes, and issue volume status for `statfs`.

## Control Flow
Mount initialization creates an `afs_fs_context` defaulting to the workstation cell and RO volume type. `source` parsing determines cell, volume, suffix, and forced RW/RO/BK semantics. Validation gets a key, detects cell aliases, creates a volume, and makes non-RW mounts read-only with local flock. `sget_fc()` reuses matching volume superblocks or creates dynroot superblocks; root inode setup activates the volume.

## State And Persistence
State includes filesystem registration, inode kmem cache, active inode counter, superblock private data, mount context refs, volume activation, and `volume->sb` pointer. No durable local state is written.

## Dependencies And Integration Points
Integrates VFS fs_context, net namespaces, AFS cell/volume creation, alias detection, key lookup, dynroot, inode/root lookup, xattrs, netfs writeback, mountpoint expiry, and statfs RPCs.

## Risks And Edge Cases
Mount source parsing controls security and semantics; mistakes can mount wrong cell/volume type. Alias switching requires key reacquisition. Inode slab reuse must reset all sensitive fields. Superblock reuse must match netns, cell, and volume ID exactly.

## Test Signals
Mount `%`/`#` sources with cell-qualified and default-cell names, `.readonly`, `.backup`, trailing `.`, dynroot, alias cells, non-RW read-only behavior, inode leak checks on unload, and statfs volume status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/validation.c -->
# sources/distributed-fs/ceph-client/fs/afs/validation.c

## Purpose
Determines whether cached vnode and volume state is valid, updates callback/VolSync state after operations, and invalidates local cache/pagecache when server state changes.

## Important APIs, Types, And Functions
Exports `afs_check_validity()`, `afs_update_volume_state()`, and `afs_validate()`. Internal helpers compare server exclusion state, update volume creation/update timestamps, detect RO snapshot release or regressions, and zap vnode data through fscache/pagecache invalidation.

## Control Flow
Fast validity checks compare vnode deletion, volume break/check counters, callback promise deadlines, RO snapshot and scrub counters, and zap flags. Blocking validation serializes on `vnode->validate_lock`, optionally locks `volume->cb_check_lock`, fetches status when callbacks expire or counters diverge, updates vnode mirrors of volume counters, and zaps data if scrub/zap state advanced. Operation completion calls `afs_update_volume_state()` to process VolSync and callback promises.

## State And Persistence
Mutates `volume->creation_time`, `update_time`, `cb_v_check`, `cb_ro_snapshot`, `cb_scrub`, `cb_expires_at`, server-entry callback expiry, vnode callback mirror counters, and local cache/pagecache contents. Persistence is remote AFS server state; local cache is invalidated as needed.

## Dependencies And Integration Points
Uses callback break logic, fileserver operation status fetch, volume server-list refresh, fscache/netfs, pagecache invalidation, and rotation success handling.

## Risks And Edge Cases
RO volume release must avoid serving older replicas. Timestamp regression requires cache scrub. Near-expiry callbacks use a 10-second deadline. Parallel operations race through VolSync updates and rely on locks/cmpxchg-style checks to avoid duplicate or missed breaks.

## Test Signals
Callback expiry, CB.InitCallBackState, vnode callback break, RO `vos release`, volume restore/regression, mmap invalidation, deleted vnode status fetch, and concurrent validations are core tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/validation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vl_alias.c -->
# sources/distributed-fs/ceph-client/fs/afs/vl_alias.c

## Purpose
Detects when an AFS cell is an alias of another known cell and selects the canonical/master cell for mounts.

## Important APIs, Types, And Functions
Exports `afs_cell_detect_alias()`. Internal helpers sample volumes, compare fileserver address lists, compare volume server lists, compare `root.cell`, query existing cells for known volumes, request YFS canonical cell names, and perform the full alias detection workflow.

## Control Flow
Alias detection is serialized by `cells_alias_lock`. It first asks YFS VL servers for a canonical cell name; if different, it looks up that cell and records `alias_of`. If unsupported, it samples `root.cell` and compares volume IDs, server UUIDs, and shared endpoint peers with existing cells. If no root volume exists, it samples another known volume from existing cells.

## State And Persistence
Mutates `cell->alias_of`, `cell->root_volume`, and clears `AFS_CELL_FL_CHECK_ALIAS` on successful detection. Sampled volumes and cells are refcounted. Alias knowledge is memory-only per net namespace.

## Dependencies And Integration Points
Depends on VL server rotation, YFS VL client canonical-name RPC, volume creation, cell lookup, volume/server lists, endpoint state, proc cell list, and mount validation in `super.c`.

## Risks And Edge Cases
Alias detection is heuristic when canonical names are unavailable. Cells sharing some VL/fileserver endpoints or volumes can be ambiguous. Interruptible locking can fail. Comparing endpoint peers assumes address lists are current and sorted compatibly.

## Test Signals
YFS canonical cell aliases, DNS aliases pointing at the same VL servers, cells with shared `root.cell`, cells without `root.cell` but shared volumes, unrelated cells with same volume names, and mount alias switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vl_alias.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vl_list.c -->
# sources/distributed-fs/ceph-client/fs/afs/vl_list.c

## Purpose
Allocates, refcounts, parses, sorts, updates, and frees VL server records and weighted VL server lists from DNS resolver payloads.

## Important APIs, Types, And Functions
Exports `afs_alloc_vlserver()`, `afs_put_vlserver()`, `afs_alloc_vlserver_list()`, `afs_put_vlserverlist()`, and `afs_extract_vlserver_list()`. Internal helpers parse little-endian DNS server-list fields and extract IPv4/IPv6 address lists into `afs_addr_list`.

## Control Flow
`afs_extract_vlserver_list()` validates DNS server-list v1 payloads, snapshots the previous VL list, parses each server record, reuses matching prior VL server objects by name/port, extracts addresses, updates server address RCU pointer when nonempty, drops empty new records without old addresses, and insertion-sorts entries by lower priority then higher weight.

## State And Persistence
VL servers and lists are refcounted and RCU-freed. Server address pointers are replaced under `vlserver->lock`; list entries track DNS source/status, priority, weight, and preferred index. State is memory-only and refreshed from DNS/config.

## Dependencies And Integration Points
Uses DNS resolver server-list ABI, address merge helpers, RxRPC peer-backed address lists, cell `vl_servers`, VL probing/rotation, and procfs VL diagnostics.

## Risks And Edge Cases
Malformed DNS payloads trigger debug dumps. Empty address lists must preserve existing addresses when possible. Protocol must be UDP or unspecified. Duplicate handling is TODO, so duplicate records can affect ordering/probing.

## Test Signals
Parse AFSDB/SRV/NSS/config payloads with IPv4, IPv6, empty, malformed, duplicate, non-UDP, weighted, and priority-varied records; verify previous-server reuse and RCU address replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vl_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vl_probe.c -->
# sources/distributed-fs/ceph-client/fs/afs/vl_probe.c

## Purpose
Probes VL servers and their addresses to discover reachability, preferred endpoint, RTT, and whether the service is YFS-capable.

## Important APIs, Types, And Functions
Exports `afs_vlserver_probe_result()`, `afs_send_vl_probes()`, and `afs_wait_for_vl_probes()`. Internal helpers finish probe rounds, decrement outstanding probe counts, and issue `VL.GetCapabilities` calls to each unprobed address.

## Control Flow
`afs_send_vl_probes()` skips already probed servers and serializes new probe rounds with `AFS_VLSERVER_FL_PROBING`. Each round snapshots the address list, initializes probe state, probes addresses in address-preference order, and accumulates errors. Completion marks address response/failure bits, updates YFS/not-YFS flags and service ID, records best RTT/preferred address, and wakes waiters. `afs_wait_for_vl_probes()` sleeps until any untried server responds or all probing stops.

## State And Persistence
Mutates `vlserver->probe`, `rtt`, flags (`PROBED`, `PROBING`, `RESPONDING`, `IS_YFS`), address-list `responded`, `probe_failed`, and `preferred`, plus VL list preferred server. All state is memory-only.

## Dependencies And Integration Points
Uses VL capability RPC construction in `vlclient.c`, RxRPC peer RTT, address preference priorities, error prioritisation, wait queues, and VL rotation.

## Risks And Edge Cases
All-address local failures, key errors, and network failures must wake waiters and clear probing. Mixed YFS/non-YFS responses must settle service ID carefully. Wait allocation can fail with `-ENOMEM`; signal interruption returns `-ERESTARTSYS` only if no responder was found.

## Test Signals
Reachable/unreachable VL servers, mixed IPv4/IPv6 address preferences, YFS upgrade detection, remote aborts, key expiration, all probes failing, signal interruption while waiting, and preferred RTT selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vl_probe.c -->
