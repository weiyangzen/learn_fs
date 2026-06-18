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
