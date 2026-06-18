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
