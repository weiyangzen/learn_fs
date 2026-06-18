# Research: subset-b-007120

Grouped research for GlusterFS FUSE bridge sources. Each section is bounded for reconciliation into the required source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-bridge.c -->
# sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-bridge.c

## Purpose

`fuse-bridge.c` is the main GlusterFS FUSE translator implementation. It mounts and manages `/dev/fuse`, negotiates the FUSE protocol, dispatches kernel requests into GlusterFS FOPs, serializes FOP callbacks back into FUSE replies, manages kernel cache invalidation, handles FUSE interrupts, performs graph-switch migration for open file descriptors, and exposes translator lifecycle, dump, callback, and option tables.

It is the central integration point between Linux/Mac/BSD FUSE messages and GlusterFS translator-stack operations. Most handlers follow the same pattern: allocate a `fuse_state_t`, initialize inode/path/fd resolution, resume once resolution completes, issue a `FUSE_FOP` into the active subvolume, translate the callback into a FUSE response, then free state and destroy the call stack.

## Important APIs, Types, and Functions

- `fuse_std_ops[]` maps FUSE opcodes to handlers such as `fuse_lookup`, `fuse_getattr`, `fuse_open`, `fuse_readv`, `fuse_write`, `fuse_setxattr`, `fuse_getlk`, `fuse_setlk`, `fuse_init`, and optional `fuse_copy_file_range`, `fuse_readdirp`, `fuse_lseek`, `fuse_batch_forget`, and `fuse_fallocate`.
- `send_fuse_iov`, `send_fuse_data`, and `send_fuse_err` construct `struct fuse_out_header`, set `unique`, calculate lengths, write replies with `sys_writev`, and optionally record traffic through the fuse dump stream.
- `check_and_dump_fuse_W` validates reply writes, degrades masked FUSE notification errno logging, rate-tracks repeated `/dev/fuse` errno classes, and writes outbound dump records when enabled.
- `fuse_entry_cbk`, `fuse_attr_cbk`, `fuse_fd_cbk`, `fuse_create_cbk`, `fuse_readv_cbk`, `fuse_writev_cbk`, `fuse_xattr_cbk`, and lock callbacks are the main response translators from GlusterFS callback signatures to FUSE structures.
- `fuse_invalidate`, `fuse_invalidate_entry`, `fuse_invalidate_inode`, and `notify_kernel_loop` implement reverse FUSE invalidation notifications for dentry and inode cache invalidation.
- `fuse_interrupt_record_new`, `fuse_interrupt_record_insert`, `fuse_interrupt_finish_fop`, `fuse_interrupt_finish_interrupt`, `fuse_interrupt`, `timed_response_loop`, `fuse_flush_interrupt_handler`, and `fuse_setlk_interrupt_handler` implement the FUSE interrupt protocol, including delayed `EAGAIN` retry responses for interrupts that arrive before the target request registers interest.
- `fuse_thread_proc` reads FUSE requests from `/dev/fuse`, stages headers and payloads in `iobuf`/heap storage, handles mount-status synchronization, maps root UIDs, and dispatches work asynchronously via `gf_async`.
- `fuse_dispatch` invokes the selected handler table and releases the request iobuf after asynchronous dispatch.
- `fuse_init` negotiates protocol features such as `FUSE_ASYNC_READ`, `FUSE_POSIX_LOCKS`, `FUSE_FLOCK_LOCKS`, `FUSE_DONT_MASK`, `FUSE_BIG_WRITES`, `FUSE_DO_READDIRPLUS`, `FUSE_AUTO_INVAL_DATA`, `FUSE_ASYNC_DIO`, and `FUSE_WRITEBACK_CACHE`.
- `fuse_first_lookup`, `fuse_nameless_lookup`, `fuse_graph_setup`, `fuse_graph_sync`, `fuse_handle_graph_switch`, `fuse_migrate_fd`, `fuse_migrate_fd_open`, and `fuse_migrate_locks` handle active graph initialization and migration of open descriptors and locks across graph switches.
- `init`, `fini`, `notify`, `mem_acct_init`, `fuse_priv_dump`, `fuse_itable_dump`, `fuse_history_dump`, `options`, `cbks`, `dumpops`, and `xlator_api` provide the translator entry points and exported metadata.

## Control Flow

Startup begins in `init`. It validates `mountpoint`, initializes `fuse_private_t`, loads options, creates the status pipe, calls `gf_fuse_mount`, optionally starts auto-unmount support, configures event history and operation tables, and wraps the handler table with `fuse_dumper` when fuse traffic dumping is configured. Child graph notifications later call `notify`; on child up/down/connecting, `fuse_graph_setup` prepares the graph inode table and the first set of FUSE reader threads is launched.

`fuse_thread_proc` is the hot path. Before the mount is fully reported by the mount helper, it polls both the status pipe and FUSE fd. For each FUSE request, it obtains an iobuf, reads the fixed header and payload with `sys_readv`, verifies message length, handles graph synchronization before and after the read, copies non-write spillover payload into a contiguous header buffer, remaps configured UIDs to root, and either returns `ENOSYS` or queues `fuse_dispatch` through `gf_async`. `FUSE_WRITE` is special because the data payload is kept in the second iovec/iobuf instead of appended to the header allocation.

Regular FUSE handlers allocate `fuse_state_t` with `GET_STATE`, initialize one or two `fuse_resolve_t` slots, and call `fuse_resolve_and_resume`. Resume functions validate resolution and issue a GlusterFS FOP with `FUSE_FOP`. Callback functions translate GlusterFS output into FUSE protocol structures and complete the request. Failure paths commonly convert inode-based `ENOENT` into `ESTALE` so the VFS retries stale cache state.

Namespace and inode cache behavior is tightly coupled to lookups and creates. `fuse_lookup_resume` creates a new inode and may request namespace xdata when no GFID exists. `fuse_entry_cbk` validates non-null GFIDs, links the inode, marks fresh linked inodes with `LOOKUP_NOT_NEEDED`, increments lookup counts, sets namespace inode state from xdata, and returns entry/attribute timeouts. New-entry operations reuse this callback, with `fuse_newentry_cbk` mapping `ENOENT` to `ESTALE`.

Open and create flow creates GlusterFS `fd_t` objects, attaches `fuse_fd_ctx_t`, reserves a FUSE fdtable slot, issues open/create/opendir, and returns a FUSE file handle containing the `fd_t *`. `fuse_fd_cbk` and `fuse_create_cbk` set `FOPEN_DIRECT_IO`, `FOPEN_KEEP_CACHE` or Darwin purge flags, inherit direct-I/O flags from existing fds, bind successful descriptors, and clean fdtable slots on reply interruption or backend failure.

Read/write flow resolves from the FUSE file handle. `fuse_readv_cbk` forwards backend vectors as a FUSE iov response. `fuse_write` keeps payload in `state->vector` and pins the input iobuf through an iobref in `fuse_write_resume`; `fuse_writev_cbk` returns the byte count in `struct fuse_write_out`.

Directory flow returns packed `struct fuse_dirent` or `struct fuse_direntplus` buffers capped by the kernel-requested size. `readdirp` also links returned inodes, sets lookup counts for non-dot entries, and returns per-entry attr/entry timeout metadata.

Xattr flow enforces Gluster-specific policy before entering the stack. `fuse_setxattr` rejects protected GFID/volume-id xattrs, handles log-control xattrs internally, uses `"inode-invalidate"` as a control xattr to enqueue invalidation, blocks ACL/SELinux/capability xattrs when disabled, flips selected geo-replication xattrs from `system` to `trusted`, and stores values in a dict with an extra NUL byte. `fuse_getxattr_resume` answers virtual GFID xattrs internally, otherwise delegates to `getxattr`/`fgetxattr`; `fuse_xattr_cbk` handles get/list replies, filters internal and geo-rep xattrs, and enforces the kernel xattr length limit.

Lock flow maps `struct fuse_file_lock` into `gf_flock` and uses the GlusterFS `lk` FOP. `fuse_setlk_cbk` inserts successful locks into fd lock context. Optional setlk interrupt handling clones enough state for a secondary fgetxattr probe against internal blocked-lock xattrs and coordinates ownership of response/freeing through the interrupt record state machine.

FUSE INIT flow validates kernel major version, records the negotiated minor version, starts the timed response thread, starts the reverse invalidation thread when notifications are supported, sets queue/congestion values, adjusts legacy write header size for old protocols, negotiates caching/read/write feature flags, and responds with an appropriately sized `fuse_init_out`.

Graph switching is coordinated by `fuse_graph_sync`. New graphs are staged in `priv->next_graph`, initial root lookup is issued after activation, old graphs are marked switched, new FUSE requests wait while `handle_graph_switch` is true, open fds are migrated by opening corresponding fds on the new subvolume, and lock state is copied via lockinfo xattrs. Old subvolumes are notified parent-down only after in-flight winds drop to zero.

Shutdown paths are intentionally process-wide. Read-loop terminal errors initiate unmount logging and send `SIGTERM`. `fini` prevents duplicate execution, unmounts unless auto-unmount is active, closes the connection, removes the mountpoint option, and sends `SIGTERM`.

## State and Persistence Behavior

Persistent per-mount state is stored in `fuse_private_t` on the xlator. It contains the FUSE fd, mountpoint, active/next graph pointers, fdtable, timeouts, feature flags, reader-thread state, graph-switch synchronization fields, invalidation/timed/interrupt queues, gid cache, event-history controls, fuse dump fd, and option-derived policy flags.

Per-request state is stored in `fuse_state_t` and owned by a call frame until response completion. It holds locs, fd refs, xattr/xdata dicts, FUSE header pointer, offsets, sizes, locks, GFID, resolve slots, iobuf references, and resume function state. `free_fuse_state` wipes locs/resolves, unrefs dicts/fds, frees the FUSE header, decrements active-subvolume winds, and can trigger parent-down notification for switched graphs with no remaining winds.

Per-file-handle state is stored in `fuse_fd_ctx_t` attached to `fd_t`. It tracks open flags, migration failure, and an active fd for graph-switch migration. `fuse_fd_ctx_destroy` frees active fd references and removes fd context.

Invalidation and timed responses are in-memory queues protected by mutex/cond pairs. They are not persisted across process restart. Fuse dump output is persisted to the configured dump file and includes simple metadata records for inbound `R` and outbound `W` messages. Event history is an in-memory circular buffer exposed through statedump when enabled.

The inode identity model uses root nodeid `1`; other FUSE nodeids are cast inode pointers. This makes inode lifetime and lookup/forget accounting critical. `FORGET` and `BATCH_FORGET` decrement inode lookup counts through `inode_forget_with_unref`.

## Dependencies and Integration Points

This file depends on the GlusterFS core translator APIs, call frames/stacks, inode/fd tables, dict/xdata, syncop helpers, iobuf/iobref, event history, gid cache, graph notification, lock owner conversion, and FUSE mount helpers. It also depends on the platform-specific FUSE kernel headers surfaced through `fuse-bridge.h` and compile-time feature macros such as `FUSE_KERNEL_MINOR_VERSION`, `HAVE_FUSE_NOTIFICATIONS`, `HAVE_SEEK_HOLE`, `GF_DARWIN_HOST_OS`, and host OS flags.

Primary external integration points are `/dev/fuse` read/write protocol handling, mount helper status pipe, platform FUSE mount/unmount helpers, kernel invalidation notifications, GlusterFS FOP tables on `active_subvol`, syncop calls for graph migration, statedump, process signals, and translator notifications from the graph manager.

## Risks and Edge Cases

- Nodeids are pointer-cast inode addresses except for root. Incorrect inode ref/lookup/forget accounting can produce stale kernel handles, use-after-free, or leaks.
- Many paths rely on converting `ENOENT` to `ESTALE` to force VFS retry. Missing one of these conversions can leave stale dentries visible to callers.
- Graph switching is concurrency-sensitive: requests increment `winds`, new requests wait under `handle_graph_switch`, and old graph parent-down depends on winds reaching zero.
- FUSE interrupt handling has race-prone ownership rules between the interrupted FOP and interrupt handler. The `INTERRUPT_NONE`, `INTERRUPT_WAITING_HANDLER`, `INTERRUPT_HANDLED`, and `INTERRUPT_SQUELCHED` transitions are critical.
- `fuse_setlk_resume` clones `fuse_state_t` shallowly for interrupt handling and then manually frees only selected fields. Changes to `fuse_state_t` ownership rules can break this path.
- `fuse_create_cbk` contains explicitly racy fd inode replacement when linked inode differs from the newly created inode. It should not be reused casually.
- `fuse_fd_inherit_directio` depends on an fd context already being present. Open/create paths must create fdctx before callbacks rely on it.
- `fusedump_setup_meta` uses `sizeof(*dir)` where `dir` is a `char *`, which records pointer size rather than one byte; changing dump consumers should account for this historical format.
- `timed_response_loop` computes sleep delta as `timespec_sub(&now, &scheduled, &delta)` after `now < scheduled`; correctness depends on GlusterFS `timespec_sub` semantics.
- Xattr filtering and namespace flipping are policy-heavy and special-case geo-replication, ACLs, SELinux, capability, virtual GFID, volume-id, and control xattrs. Policy changes need integration testing.
- `fini` and read-loop termination kill the full process with `SIGTERM`; callers should not expect translator-local shutdown only.
- Optional feature handlers are compiled conditionally and may be `ENOSYS` depending on kernel header version and mount options.

## Test Signals

Useful tests include FUSE mount init negotiation across kernel minor versions; lookup/create/open/read/write/readdir/readdirplus behavior; forget/batch-forget lookup accounting; negative timeout responses; direct-I/O and keep-cache flag behavior; setxattr/getxattr/listxattr/removexattr policy cases; virtual GFID xattrs; `inode-invalidate` control xattr and reverse invalidation queue behavior; lock get/set/setw and interrupt races; flush interrupt behavior; graph switch while fds and locks are active; read-loop behavior on short reads, EPERM rate limiting, ENODEV/EBADF; fuse dump file format; statedump output; mount failure/status pipe handling; and shutdown/unmount behavior.

Regression tests should watch for non-empty replies with correct `fuse_out_header.len`, exact `unique` propagation, fdtable cleanup on failed/interrupted open/create, no leaked `fuse_state_t` fields under error paths, and correct `[FUSE_COPY_FILE_RANGE]` behavior only when explicitly enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-bridge.h -->
# sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-bridge.h

## Purpose

`fuse-bridge.h` defines the shared data structures, macros, and function prototypes used by the GlusterFS FUSE bridge implementation, helper layer, and resolver layer. It is the contract for the mount/fuse translator: FUSE handler signatures, private mount state, request state, resolve state, fd context, interrupt/timed/invalidation queues, core helper prototypes, and the macros that issue GlusterFS FOPs from FUSE handlers.

## Important APIs, Types, and Macros

- `fuse_handler_t` is the per-opcode handler signature: an xlator, FUSE input header, decoded message pointer, and optional iobuf.
- `enum fusedev_errno` and `fusedev_errno_cnt` classify selected `/dev/fuse` write error statuses for degraded logging/rate tracking.
- `struct fuse_private` is the primary mount-private state. It stores the FUSE fd, protocol minor, volfile and mountpoint data, reader threads, direct-I/O policy, timeouts, graph pointers, client identity policy, ACL/SELinux/capability flags, fdtable, gid cache, reverse invalidation queue, mount status pipe, background queue limits, readdirplus, graph switch controls, writeback cache settings, timed response queue, interrupt queue, feature toggles, inode/invalidation limits, and errno counters.
- `errnomask_t`, `MASK_ERRNO`, `GET_ERRNO_MASK`, and `ERRNOMASK_MAX` provide compact errno masks used to degrade expected notification/timed-response write failures.
- `struct fuse_invalidate_node` stores one prepared FUSE invalidate notification plus its error mask and queue link.
- `struct fuse_timed_message` stores delayed FUSE responses such as interrupt `EAGAIN` replies.
- `enum fuse_interrupt_state` and `struct fuse_interrupt_record` model FUSE interrupt races between request completion and interrupt handler completion.
- `struct fuse_graph_switch_args` packages old/new subvolume pointers for graph migration tasks.
- `FH_TO_FD` converts a FUSE file handle back to a referenced `fd_t *`; `_FH_TO_FD` performs the raw pointer cast.
- `GF_FUSE_SQUASH_INO` maps 64-bit inode numbers into 32-bit inode values when the mount option requests `enable-ino32`.
- `FUSE_FOP` is the central dispatch macro from a resolved `fuse_state_t` into an active-subvolume FOP. It validates active subvolume, allocates a call frame, attaches request state/op metadata, logs event history, and winds the stack.
- `GET_STATE` allocates `fuse_state_t`, sends `ENOMEM` on failure, frees the input header, and returns from the handler.
- `FUSE_ENTRY_CREATE` applies FUSE umask handling and ACL-aware `mode`/`umask` xdata setup for create-like operations.
- `fuse_log_eh_fop` and `fuse_log_eh` gate event-history logging on translator history and mount option state.
- `fuse_resolve_type_t`, `fuse_resolve_t`, and `fuse_state_t` define the path/inode/fd resolution and request state contract used by `fuse-resolve.c`, `fuse-bridge.c`, and `fuse-helpers.c`.
- `fuse_fd_ctx_t` stores per-FUSE-fd open flags, graph-migration failure, and active migrated fd.

Important declared functions include `fuse_loc_fill`, `get_call_frame_for_req`, `get_fuse_state`, `free_fuse_state`, `gf_fuse_stat2attr`, `gf_fuse_fill_dirent`, `inode_to_fuse_nodeid`, `fuse_ino_to_inode`, `send_fuse_err`, `fuse_gfid_set`, `fuse_flip_xattr_ns`, `fuse_fd_ctx_check_n_create`, `fuse_resolve_and_resume`, the resolve initializers, `fuse_ignore_xattr_set`, `fuse_fop_resume`, and `fuse_check_selinux_cap_xattr`.

## Control Flow Enabled by This Header

The header encodes the common FUSE handler flow. A handler receives a `fuse_in_header_t`, calls `GET_STATE`, initializes fields in `fuse_state_t`, schedules resolution through resolver functions, and eventually reaches a resume function. The resume function calls `FUSE_FOP`, which creates a GlusterFS call frame, binds `frame->root->state` to the FUSE state, sets operation numbers, optionally logs event history, and winds into the active subvolume operation. Callback code later uses the same `fuse_state_t` and header to serialize a FUSE reply and free resources.

It also defines how create-like handlers pass ACL and umask data. `FUSE_ENTRY_CREATE` adjusts mode when FUSE protocol minor is new enough, creates `state->xdata`, and inserts `umask` and original `mode` so lower translators can honor POSIX ACL defaults and permission behavior.

File handles are represented by `fd_t *` pointers returned to the kernel in FUSE open replies and recovered by `FH_TO_FD`. Inode nodeids use `inode_to_fuse_nodeid`, where root maps to `1` and other nodes are represented by inode pointers.

## State and Persistence Behavior

`fuse_private_t` persists for the lifetime of the mount translator. It is in-memory only, but it owns resources with external effects: FUSE fd, status pipe fds, dump fd, fdtable, event-history buffer, reader threads, reverse notification queue, timed response queue, gid cache, and graph references. Its boolean options and timeouts become the mount's runtime policy.

`fuse_state_t` is per-request and transient. It contains owned references and allocations that must be released by `free_fuse_state`: locs, resolve paths, dicts, names, fd refs, input header, locks, request vectors, and xdata. It also records the active subvolume selected at request allocation time, allowing graph-switch accounting to decrement winds on completion.

`fuse_resolve_t` is transient resolution state. Its fields track the desired resolution mode, fd/path/name/GFID hints, parent hints, result code, and resolved loc. `fuse-helpers.c` wipes these fields when the request ends.

`fuse_interrupt_record_t`, `fuse_timed_message_t`, and `fuse_invalidate_node_t` are queued transient objects. They persist only in memory until their worker loop or interrupt path consumes them.

## Dependencies and Integration Points

The header includes platform FUSE kernel headers, GlusterFS logging, statedump, list, dict, syncop, gidcache, mount helpers, memory types, and miscellaneous FUSE helpers. It assumes GlusterFS core types such as `xlator_t`, `fd_t`, `inode_t`, `loc_t`, `dict_t`, `call_frame_t`, `struct iatt`, `gf_dirent_t`, `gf_flock`, and `gf_boolean_t`.

Its macros integrate directly with lower xlator FOP vectors and GlusterFS event history. Compile-time FUSE feature macros change available structures and fields, so this header is sensitive to kernel FUSE header version and platform.

## Risks and Edge Cases

- `FH_TO_FD` and nodeid pointer casts require correct object lifetime. Any future serialization or cross-process use would be unsafe.
- `FUSE_FOP` sends an immediate FUSE error and frees state on frame allocation failure, but the macro comment notes earlier allocations may remain if callers added unmanaged fields.
- `GF_SELECT_LOG_LEVEL` appears malformed/incomplete as a macro expression in this snapshot and should be reviewed before use.
- `FUSE_ENTRY_CREATE` assumes a local `ret` variable exists in the calling scope and returns from the enclosing function on failure. Callers must match that convention.
- `fuse_log_eh` reads `this->private` and `this->history`; using it before `private` initialization or after teardown would be unsafe.
- `struct fuse_private` has many mutex-protected fields, but the header alone does not enforce locking. Callers must follow the locking protocols in implementation files.
- Feature fields are conditional by negotiated protocol minor and compile-time FUSE minor. Tests must cover downgraded protocol paths.

## Test Signals

Header-level behavior is best tested through integration tests that exercise the macros and state contracts: allocation failure in `GET_STATE`; no active subvolume path in `FUSE_FOP`; ACL/umask xdata setup in create/mkdir/mknod; file-handle conversion with reference management; inode/nodeid mapping for root and non-root; event-history logging on/off; errno-mask behavior through notification writes; and graph switch accounting tied to `state->active_subvol`.

Static analysis should check macro call-site assumptions, especially local variable dependencies in `FUSE_ENTRY_CREATE`, request state ownership in `FUSE_FOP`, and pointer-cast file handle/nodeid usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-helpers.c -->
# sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-helpers.c

## Purpose

`fuse-helpers.c` implements common support routines for the FUSE bridge: request-state allocation/freeing, GlusterFS call frame creation, caller group collection and caching, inode/nodeid and loc conversion, stat and dirent conversion to FUSE wire structures, and FUSE xattr namespace/policy helpers. These functions are used by the main bridge and resolver code to keep operation handlers focused on protocol and FOP flow.

## Important APIs and Functions

- `free_fuse_state` releases a completed `fuse_state_t`, wipes locs and resolve state, unrefs dicts and fds, frees the input header and name, decrements active-subvolume wind count, and notifies a switched graph when its last in-flight request completes.
- `get_fuse_state` allocates request state, waits for graph migration to stop accepting paused requests, selects the active subvolume, increments its `winds` counter, stores the active inode table and pool, and initializes the state lock.
- `get_call_frame_for_req` creates a GlusterFS frame, copies UID/GID/PID and lock owner from the FUSE header, loads supplementary groups, applies configured client PID override, and marks the frame as a FOP.
- `frame_fill_groups` populates supplemental groups from `getgrouplist` or platform process credential sources. Linux can read `/proc/<pid>/status`; Solaris reads `/proc/<pid>/cred`; Darwin/BSD use `sysctl`; unsupported platforms set zero groups.
- `get_groups` wraps `frame_fill_groups` with `gid_cache` lookup and insertion, and supports `gid-timeout = -1` as a way to suppress supplemental groups.
- `fuse_ino_to_inode` converts FUSE nodeid `1` to the active root inode and non-root nodeids back to referenced `inode_t *` pointers.
- `inode_to_fuse_nodeid` maps root GFID to `1` and non-root inodes to pointer-valued nodeids.
- `fuse_loc_fill` builds a GlusterFS `loc_t` for either an entry under a parent/name or an inode, including parent/inode refs, GFIDs, path, and basename.
- `gf_fuse_stat2attr` converts GlusterFS `struct iatt` into `struct fuse_attr`, including optional 32-bit inode squashing and Darwin-specific fields.
- `gf_fuse_fill_dirent` converts `gf_dirent_t` fields into a FUSE dirent payload.
- `fuse_flip_xattr_ns`, `fuse_do_flip_xattr_ns`, and `fuse_xattr_alloc_default` selectively translate geo-replication xattrs from unprivileged `system.*` namespace to `trusted.*`.
- `fuse_ignore_xattr_set` enforces which non-user xattrs geo-replication (`GF_CLIENT_PID_GSYNCD`) may set.
- `fuse_check_selinux_cap_xattr` allows or denies `security.selinux` and `security.capability` according to mount options.

## Control Flow

`get_fuse_state` is the first helper used by most FUSE handlers. It allocates zeroed state, waits on `priv->migrate_cond` while `handle_graph_switch` is true, snapshots the current active subvolume, increments `active_subvol->winds` under `priv->sync_mutex`, records the active inode table and call pool, attaches the FUSE input header, and initializes the per-state lock. This makes the request count visible to graph-switch teardown logic.

`get_call_frame_for_req` is called by the `FUSE_FOP` macro and some interrupt handlers. It creates a frame, records the operation number for logging, copies request credentials from the FUSE header, stores the lock owner when present, then fills supplemental groups. If `client-pid` was configured, it overrides the frame root PID after group collection. This frame is then wound into lower translators.

Group lookup first checks `priv->gid_cache_timeout`. With no cache configured, `frame_fill_groups` runs directly. With timeout `-1`, groups are disabled. Otherwise, `gid_cache_lookup` can satisfy the request; misses call platform-specific collection and then add a new cache entry.

`fuse_loc_fill` handles two resolution shapes. For parent/name requests, it resolves or reuses the parent inode, searches the child with `inode_grep`, and builds the path with `inode_path(parent, name, &path)`. For inode requests, it resolves the inode by nodeid, finds a parent with `inode_parent`, and builds an inode path. It then sets `loc->name` from the last path component and rejects non-root locs without parents.

Xattr helpers are policy filters used before main FUSE handlers enter the GlusterFS stack. Geo-replication may request selected `system.glusterfs.*` keys and have them translated to `trusted.glusterfs.*`; disallowed xattr sets return `-1`; ACL/SELinux/capability helpers let the bridge return `EOPNOTSUPP`/`ENODATA` before lower translators see unsupported metadata.

## State and Persistence Behavior

This file manages in-memory request and credential state. `free_fuse_state` is the authoritative cleanup path for `fuse_state_t`. It releases `state->loc`, `state->loc2`, `state->xdata`, `state->xattr`, `state->name`, `state->fd`, `state->finh`, and both resolve structures. In debug builds it poisons the state before freeing.

Graph-switch persistence is represented by `active_subvol->winds` and `active_subvol->switched`. Every request created by `get_fuse_state` increments winds; `free_fuse_state` decrements it and sends `GF_EVENT_PARENT_DOWN` when a switched graph reaches zero active requests.

Supplemental group state lives on the call stack. Cached group lists live in `priv->gid_cache`, keyed by PID/UID/GID. The helper allocates and transfers group arrays through `call_stack_set_groups` or `call_stack_alloc_groups`.

Loc and inode conversion functions manipulate inode refs and paths. The path allocated by `inode_path` becomes owned by the loc and is later released by `loc_wipe`.

Xattr helper allocations return duplicated or newly built key strings through `nkey`; callers own and eventually free or transfer those strings into dict state.

## Dependencies and Integration Points

The file depends on `fuse-bridge.h`, GlusterFS inode, fd, loc, dict, gid cache, call-stack, UUID, logging, and memory helpers. Platform integration includes Linux `/proc`, `getpwuid_r`, `gf_getgrouplist`, Solaris procfs credentials, BSD/Darwin `sysctl`, and standard password/group APIs.

It integrates with the main FUSE bridge through the declared helper prototypes in `fuse-bridge.h`, with resolver code through `fuse_resolve_t` cleanup, and with graph-switch logic through `priv->sync_mutex`, `priv->migrate_cond`, `active_subvol->winds`, and `active_subvol->switched`.

## Risks and Edge Cases

- `get_fuse_state` assumes an active subvolume exists and increments `active_subvol->winds` without a local null check. The broader graph setup must guarantee this before FUSE handlers run.
- `free_fuse_state` assumes `state`, `state->this`, and `state->active_subvol` are valid. Shallow copies of `fuse_state_t`, such as interrupt helper copies, must not be passed through full cleanup unless ownership is correct.
- Group collection from `/proc/<pid>/status` is race-prone when the process exits or PID namespaces are involved. PID zero is treated as a container-oriented special case with group zero.
- The Linux group parser retries after resizing, but it caps at `GF_MAX_AUX_GROUPS`; callers should not assume all groups are always preserved.
- `gid_cache_add` ownership of `agl.gl_list` depends on return value; failure frees locally.
- `fuse_loc_fill` is designed to resist repeated invocation leaks, but callers must still avoid reusing a partially filled loc incorrectly.
- `fuse_ino_to_inode` pointer-casts non-root nodeids and immediately `inode_ref`s them; invalid/stale kernel nodeids would be dangerous if lookup accounting failed elsewhere.
- `gf_fuse_fill_dirent` copies `d_len` bytes without appending NUL, which is correct for FUSE dirent format but important for consumers expecting strings.
- Xattr namespace flipping assumes the original key contains `.` and asserts in `fuse_do_flip_xattr_ns`; callers should only pass expected namespace-style keys.
- `fuse_ignore_xattr_set` intentionally allows `user.*` regardless of geo-replication restrictions and has a tightly curated allowlist for non-user namespaces.

## Test Signals

Targeted tests should cover request allocation during graph migration, wind count decrement and parent-down notification, cleanup of every owned `fuse_state_t` field on success and failure, group collection with cache hit/miss/disabled modes, PID zero fallback, missing `/proc` entries, `client-pid` override behavior, root and non-root nodeid conversion, `fuse_loc_fill` for parent/name and inode-only cases, inode path failure behavior, 32-bit inode squashing in `gf_fuse_stat2attr` and `gf_fuse_fill_dirent`, geo-rep xattr namespace flipping, xattr allow/deny matrices, ACL disabled behavior, and SELinux/capability option combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-helpers.c -->
