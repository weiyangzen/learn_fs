# Group Research: group_503_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_ab0316549e19

Scope: `Docs/research_subset_a.md`, source tree `sources/os/illumos/illumos-gate`.

Read validation: every listed source file was read completely. The checked content totals 10,055 lines across 12 files in the working tree, matching the prompt metadata.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_write.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_write.c

## Purpose
Implements SMB1 server write command handling for normal writes, write-and-close, write-and-unlock, obsolete write-raw rejection, WriteAndX, and the common write/truncate backend.

## Main Behavior
- Each SMB command has pre/post handlers that allocate/free `smb_rw_param_t`, decode request words/data offsets, and emit DTrace start/done probes.
- `smb_com_write()` writes at a 32-bit offset; a zero byte count truncates or extends the disk file to the offset.
- `smb_com_write_and_close()` performs the same write/truncate operation, then closes the open file with an optional last-write timestamp.
- `smb_com_write_and_unlock()` only allows disk tree shares, writes the data, then unlocks the written range using the SMB1 16-bit PID.
- `smb_com_write_raw()` is retained only for observability and always returns `NT_STATUS_NOT_SUPPORTED`.
- `smb_pre_write_andx()` supports 12-word and 14-word forms, including 64-bit offsets and large writes via `CAP_LARGE_WRITEX` or a Win7 compatibility heuristic.
- `smb_common_write()` dispatches by share type: disk/print queues go through filesystem write paths and byte-range lock checks; IPC writes go through named pipe write handling.
- `smb_write_truncate()` applies `SMB_AT_SIZE` via `smb_node_setattr()` after checking range lock access.

## Integration Points
- Depends on SMB request decode/encode helpers, `smbsr_lookup_file()`, ofile credentials, byte-range lock helpers, SMB filesystem operations, named pipe writes, oplock breaking, and node notification.
- Uses `smb_ofile_t` seek position updates after successful write/truncate.
- Updates change-notification behavior lazily through `f_written` and `smb_node_notify_modified()` rather than notifying every write.

## Risks and Notes
- `smb_com_write_and_close()` contains an explicit comment questioning whether its data decode format should be `"3.#B"` instead of `".#B"`.
- Partial write counts are reflected back to clients; most successful filesystem writes are expected to match the requested count.
- Stable-write mode and node write-through flags map to `FSYNC`.
- Lock-conflict paths set SMB errors directly and suppress generic errno translation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smbsrv.conf -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smbsrv.conf

## Purpose
Driver configuration file for the illumos SMB server pseudo device.

## Main Behavior
- Contains only the CDDL/license header, legacy ident comment, and one driver configuration directive.
- Declares `name="smbsrv" parent="pseudo";`, placing `smbsrv` under the pseudo-device parent.

## Integration Points
- Consumed by illumos driver configuration machinery when installing or attaching the SMB server kernel module.
- Complements the SMB server implementation files under `fs/smbsrv`.

## Risks and Notes
- No tunables or properties are defined here.
- Any runtime SMB server policy is configured elsewhere; this file only establishes the pseudo-device relationship.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smbsrv.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sock_notsupp.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sock_notsupp.c

## Purpose
Provides a default `sock_downcalls_t` vector for protocol operations that are unsupported.

## Main Behavior
- Defines stub functions for accept, bind, listen, connect, name lookup, socket options, send, send-uio, receive-uio, poll, shutdown, ioctl, and close.
- All stubs return `EOPNOTSUPP` except `sock_clr_flowctrl_notsupp()`, which is a no-op.
- Exports `sock_down_notsupp`, a populated downcall table using those stubs.

## Integration Points
- Used by socket modules or protocol glue that need a complete downcall vector while explicitly marking operations unavailable.
- Depends on the public sockfs/socket protocol interfaces in `sys/socket_proto.h`.

## Risks and Notes
- `sock_poll_notsupp()` returns `EOPNOTSUPP` in a `short`, matching the downcall shape but semantically representing an unsupported operation rather than poll events.
- The table is intentionally simple and does not maintain socket state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sock_notsupp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon.c

## Purpose
Implements the common sockfs public wrapper layer and sonode lifecycle routines shared by system-call sockets and kernel sockets.

## Main Behavior
- `socket_create()` resolves a `sockparams` entry by family/type/protocol, optionally creates ephemeral entries by device or module, invokes the socket module create function, initializes the sonode, and opens the vnode reference.
- `socket_newconn()` creates a child sonode for passive opens using the parent socket parameters and protocol lower handle.
- Wrapper functions delegate bind/listen/accept/connect/name/options/send/recv/ioctl/poll/shutdown through the active `sonodeops_t`.
- `socket_listen()` normalizes negative backlog to zero and applies BSD-style backlog inflation.
- `socket_connect()` treats `AF_UNSPEC` as disconnect/unconnect and maps `EHOSTUNREACH` to `ENETUNREACH` for XPG callers.
- `socket_sendmsg()` and `socket_recvmsg()` handle uio cache flags, partial-transfer errno normalization, and SIGPIPE on `EPIPE`.
- `sonode_constructor()` allocates and initializes the vnode, queues, locks, condition variables, filter fields, and receive/send state.
- `sonode_init()` resets per-instance state, vnode identity, protocol fields, socket options, poll state, callbacks, and zone ownership.
- `sonode_fini()` cancels timers, wakes pollers, tears down direct I/O and filters, releases peer credentials, invalidates the vnode, and asserts queues are drained.

## Integration Points
- Calls into `sockparams`, socket modules, `sonodeops_t`, vnode operations, sockfilter cleanup, and sodirect setup/teardown.
- Provides the stable `socket_*` interface declared in `sockcommon.h`.
- Works with both native non-STREAM sockfs sockets and TPI fallback sockets.

## Risks and Notes
- Creation carefully preserves original lookup errors when fallback lookup by wildcard protocol changes errno.
- `socket_destroy()` invalidates and releases the vnode; actual resource destruction is completed by vnode inactive paths.
- The constructor/destructor include many assertions that queue/filter state is empty when cache objects are destroyed.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon.h

## Purpose
Internal sockfs header declaring common socket wrappers, sonode operations, protocol upcalls, queue helpers, notification helpers, lifecycle routines, and timer macros.

## Main Behavior
- Declares `socket_create()`, `socket_newconn()`, and common `socket_*` operation wrappers.
- Defines `SOCKET_TIMER_CANCEL()` and `SOCKET_TIMER_START()` for receive push timer management under `so_lock`.
- Declares unsupported sonode ops and the generic `so_*` operations implemented in `sockcommon_sops.c`.
- Declares protocol upcalls such as `so_newconn()`, `so_connected()`, `so_queue_msg()`, `so_set_prop()`, and `so_txq_full()`.
- Declares accept queue, connect wait, send wait, signal, receive queue, uio/mblk copy, OOB, ioctl, option, fallback, zcopy, and notification helpers.
- Exposes `so_sonodeops` and `so_upcalls`.
- Defines socket signal event bits for write, read, and urgent notifications.

## Integration Points
- Included by the common sockfs implementation, socket filters, TPI fallback code, and socket vnode operations.
- Bridges `sys/socket_proto.h` downcall/upcall interfaces to internal `sonode` state management.

## Risks and Notes
- Several timer macros deliberately drop and reacquire `so_lock`, so callers must respect their locking contract.
- The declarations show the split between public wrapper APIs (`socket_*`), sonode ops (`so_*`), and protocol callbacks/upcalls.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon_sops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon_sops.c

## Purpose
Implements the generic non-STREAM sonode operations and protocol upcall table used by sockfs native socket modules.

## Main Behavior
- Provides unsupported sonode operations returning `EOPNOTSUPP`.
- `so_bind()`, `so_listen()`, `so_connect()`, `so_accept()`, name, option, shutdown, ioctl, send, receive, and poll paths wrap protocol downcalls with fallback blocking and optional socket filter hooks.
- IPv4/IPv6 bind validation applies historical SunOS compatibility and stricter X/Open checks.
- Send paths support direct `sd_send_uio` or mblk construction via `socopyinuio()`, enforce atomic max packet size, honor send flow control, process OOB, and run outbound filters.
- `so_sendmblk_impl()` sends prebuilt mblk chains, splitting by protocol max packet size and supporting filter-injected output.
- Receive paths use direct protocol receive when available, otherwise dequeue sockfs receive queues, decode TPI control messages, translate options to control messages, set `MSG_EOR`/`MSG_TRUNC`, and handle OOB.
- Poll reports errors, writable state, accept queue readiness, receive data/OOB, `POLLRDHUP`, `POLLHUP`, protocol poll events, and edge-trigger bookkeeping.
- Protocol upcalls update connected/disconnected state, accept new connections, set protocol properties, queue inbound messages, signal OOB, set errors, notify zero-copy completion, and release async-close references.
- Exports `so_sonodeops` and `so_upcalls`.

## Integration Points
- Heavily uses helpers from `sockcommon_subr.c`, notifications from `socknotify.c`, filter APIs from `sockfilter.c`, and protocol downcalls from socket modules.
- Supports ksocket callbacks and sodirect receive acceleration.
- `so_newconn()` feeds the accept queue and handles deferred filter-controlled connections.

## Risks and Notes
- Many operations use `SO_BLOCK_FALLBACK()`/`SO_UNBLOCK_FALLBACK()` so TPI fallback can quiesce active operations safely.
- `so_getsockopt()` emulates successful default `SOL_SOCKET` gets for unsupported protocol options to preserve previous sockfs behavior.
- Close handling may be synchronous or asynchronous; async close relies on a later `so_closed()` upcall to drop the protocol vnode reference.
- Filter injection is tracked with `so_filter_tx` so close waits until injected transmit operations finish.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon_sops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon_subr.c

## Purpose
Provides the core sockfs support machinery: accept queues, blocking waits, signals, mblk/uio copying, receive queue management, ioctl/option common handling, TPI fallback, and kernel receive callbacks.

## Main Behavior
- Accept queue helpers dequeue, flush, and destroy pending or deferred child sockets.
- Connect and send wait helpers sleep on condition variables, honor nonblocking flags, timeouts, fallback, close, and signal interruption.
- `socket_sendsig()` sends `SIGPOLL`/`SIGURG` to process or process group targets in the socket zone.
- `socopyinuio()` copies user data into mblk chains with protocol write offset/tail reservations; `socopyoutuio()` copies mblk data back to uio.
- Receive queue helpers merge mblk chains, prepend partially read data, maintain `so_rcv_queued`, preserve `b_next` message boundaries, and coordinate flow-control release.
- `so_dequeue_msg()` is the main queued receive engine, handling peek, truncation, OOB marks, timers, blocking waits, sodirect/UIOA state, control/data splitting, and flow-control transitions.
- OOB helpers manage urgent-data state, mark behavior, inline delivery, and non-inline `MSG_OOB` reads.
- `socket_sonode_create()` allocates sonodes from `socket_cache`, validates upcall/downcall versions, assigns defaults, and sets protocol receive thresholds.
- `socket_init_common()` initializes passive children by inheriting listener state or active sockets by attaching automatic filters, creating protocol handles, activating downcalls, and applying wildcard protocol options.
- `socket_ioctl_common()` handles nonblocking, async, ownership, at-mark, read-count, and peer credential ioctls.
- `socket_strioc_common()` handles selected STREAM ioctls and otherwise attempts TPI fallback.
- `socket_getopt_common()` handles or validates common `SOL_SOCKET` gets, including `SO_ERROR`, domain/type/acceptconn, timeouts, receive buffer compatibility, send buffer info, and copy-avoid with filters.
- `so_tpi_fallback()` quiesces native sockets, creates TPI sockparams, converts the sonode, migrates queued data and OOB state to STREAMS messages, converts accepted children, flushes accept queues, swaps ops to `sotpi_sonodeops`, and wakes pollers.
- `so_krecv_set()` installs/removes kernel receive callbacks after flushing queued data; `so_krecv_unblock()` releases receive flow control for such callbacks.

## Integration Points
- Used by `sockcommon_sops.c`, TPI code, socket vnode operations, filters, and ksocket consumers.
- Coordinates with `sockparams`, `sotpi_convert_sonode()`, `sotpi_revert_sonode()`, sodirect, STREAMS ioctls, and protocol fallback callbacks.

## Risks and Notes
- Receive queue invariants are subtle: `b_next` separates messages, `b_cont` chains data/control, and `b_prev` stores tail pointers.
- `so_check_flow_control()` intentionally drops `so_lock`; callers must not unlock again.
- Fallback is disabled when filters or kernel receive callbacks are active.
- TPI fallback has a debug integrity check to catch lost state if conversion fails and must revert.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon_vnops.c

## Purpose
Defines the vnode operations for sockfs socket vnodes.

## Main Behavior
- Registers vnode operations for open, close, read, write, ioctl, setfl, getattr, setattr, access, fsync, inactive, fid, seek, poll, and dispose.
- Open increments `so_count`; close decrements it and initiates socket close when the last open reference goes away.
- Read/write translate vnode I/O into `socket_recvmsg()` and `socket_sendmsg()` with a minimal `nmsghdr`; non-byte-stream writes set `MSG_EOR`.
- `socket_vop_setfl()` records `FNDELAY`/`FNONBLOCK` and handles BSD `FASYNC` compatibility through `FIOASYNC`.
- `socket_vop_getattr()` fabricates socket vnode attributes, including stable-ish 32-bit node IDs derived from the sonode pointer and STREAM/TPI timestamp behavior.
- `socket_vop_setattr()` updates atime/mtime/ctime only for STREAM/TPI sockets.
- Access checks delegate to the underlying STREAMS device for STREAM/TPI sockets and allow non-STREAM sockets.
- Fsync returns `EINVAL`, fid returns `EINVAL`, and seek returns `ESPIPE`.
- Inactive releases the vnode and destroys the underlying socket when the vnode count reaches zero.

## Integration Points
- `socket_vnodeops_template` is installed by sockfs setup and used by sonode construction.
- Calls `socket_close_internal()` and `socket_destroy_internal()` from `sockcommon.c`.
- Cooperates with `socktpi` for STREAM-mode sockets.

## Risks and Notes
- Attribute values are intentionally synthetic and do not affect filesystem nodes backing AF_UNIX pathnames.
- The node-id derivation is explicitly capped to 32 bits to avoid surprises for non-largefile-aware 32-bit processes.
- Close cleans locks, shares, and STREAM state before final socket teardown.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockfilter.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockfilter.c

## Purpose
Implements the illumos socket filter framework: configured filter entries, loaded filter modules, per-socket filter instances, attach/detach, callback dispatch, deferred accepts, flow control, and filter data injection.

## Main Behavior
- Maintains global filter entry and filter module lists, plus a taskq-backed list for closing over-aged deferred connections.
- `sof_init()` initializes lists, locks, deferred-close taskq, and global kstats.
- `sof_setsockopt()` handles `SOL_FILTER` programmatic attach/detach through `FIL_ATTACH` and `FIL_DETACH`, serializing stack mutation with the fallback rwlock.
- `sof_getsockopt()` reports attached filters through `FIL_LIST`.
- Automatic filters attach during socket initialization; programmatic filters attach on request; passive accepted sockets inherit listener filters bottom-up.
- Filter entries are matched to `sockparams` socket tuples and inserted into per-sockparams automatic or programmatic filter lists with placement hints.
- Filter modules register/unregister through `sof_register()`/`sof_unregister()` and are demand-loaded from `SOCKMOD_PATH` when needed.
- `sof_entry_add()` and `sof_entry_remove_by_name()` coordinate with `sockparams` under `sockconf_lock`.
- Per-socket filter instances form a top-to-bottom stack and hold references to their filter entries and modules.
- Dispatch helpers run filter callbacks for data out, data in processing, bind, listen, connect, accept, shutdown, name lookup, options, and ioctl.
- Deferred passive connections can be moved from the deferred accept list to the normal accept queue via `sof_newconn_ready()`, dropped after timeout, or moved between listeners for KSSL.
- Flow-control APIs let filters assert receive or send flow control; injection APIs let filters inject inbound or outbound mblks and report whether they became flow-controlled.
- `sof_bypass()` disables callbacks for an instance while leaving it attached.

## Integration Points
- Works with `sockparams.c` for socket-type matching and cleanup.
- Hooks into `sockcommon_sops.c` send/receive/control paths and `socknotify.c` notification events.
- Uses `sockconf_lock`, `so_fallback_rwlock`, `so_lock`, accept queue locks, kstats, taskq, and DTrace probes.
- Public filter callbacks and return values come from `sys/sockfilter.h`.

## Risks and Notes
- Filter attach paths must be nonblocking while holding `sockconf_lock` as writer.
- `SOFEF_CONDEMED` entries are freed only after active instance references drain.
- Deferred-close backlog is capped; if too large, new deferred drops are refused and counted in kstats.
- `sof_filter_data_in_proc()` can change receive queue length and must adjust `so_rcv_queued` while respecting flow-control semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockfilter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockfilter_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockfilter_impl.h

## Purpose
Internal header for the sockfs socket filter framework.

## Main Behavior
- Defines `sof_module_t`, `sof_entry_t`, `sof_instance_t`, and filter/global kstat structures.
- Sets filter constants such as maximum name length, max socket tuple count, and module path.
- Defines entry flags for automatic, programmatic, and condemned filters.
- Defines instance flags for bypass, deferred accept, receive flow control, and send flow control.
- Declares filter entry, sockparams, sonode attach/cleanup/notify, option, dispatch, and data filtering functions.
- Defines `SOF_INTERESTED()` and `__SOF_FILTER_OP()` macros for checking callbacks and walking the filter stack.
- Provides convenience macros for outbound data filtering.

## Integration Points
- Included by `sockfilter.c`, `sockcommon_sops.c`, `sockcommon_subr.c`, `socknotify.c`, and `sockparams.c`.
- Depends on public filter APIs from `sys/sockfilter.h`.

## Risks and Notes
- `__SOF_FILTER_OP()` returns immediately when a filter does anything other than `SOF_RVAL_CONTINUE`, so callback ordering directly controls behavior.
- The misspelled flag name `SOFEF_CONDEMED` is part of the internal ABI within this source set.
- Instance list direction matters: many operations traverse top-down, while inbound data and notifications often traverse bottom-up.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockfilter_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socknotify.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socknotify.c

## Purpose
Centralizes socket state notifications, wakeups, signals, poll events, ksocket callbacks, and filter event notifications.

## Main Behavior
- All exported notification functions require `so_lock` on entry and drop it before returning.
- `so_notify_connected()` wakes connect waiters and reports writable/connected state.
- Disconnecting, disconnected, EOF, and shutdown notifications send final read/write wakeups only once using `SS_SENTLASTREADSIG` and `SS_SENTLASTWRITESIG`.
- Writable and data notifications wake blocked senders/readers, issue kernel socket callbacks or user poll/signal notifications, and clear edge-trigger poll state.
- Error notifications wake both read and write waiters and report poll input/output readiness.
- OOB notifications handle urgent signal, OOB data readiness, inline OOB read readiness, and sodirect cleanup.
- New connection notifications wake accept waiters and pollers.
- Helper functions `i_so_notify_last_rx()` and `i_so_notify_last_tx()` consolidate final read/write notification state.

## Integration Points
- Called from protocol upcalls in `sockcommon_sops.c`, queue/timer paths in `sockcommon_subr.c`, and shutdown/close paths.
- Invokes `socket_sendsig()`, `pollwakeup()`, `KSOCKET_CALLBACK()`, sodirect cleanup, and `sof_sonode_notify_filters()`.

## Risks and Notes
- The locking convention is unusual but explicit: callers must not expect `so_lock` to remain held.
- `SO_WAKEUP_READER` uses `cv_signal` because only one read waiter is allowed; writers use broadcast.
- Filter notifications are emitted after releasing `so_lock`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socknotify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockparams.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockparams.c

## Purpose
Manages sockfs socket-parameter records that map socket family/type/protocol tuples to socket modules and optional STREAMS devices.

## Main Behavior
- Initializes global configured sockparams and ephemeral sockparams lists plus global ephemeral allocation/reuse kstats.
- `sockparams_create()` builds a `sockparams` entry, initializes automatic/programmatic filter lists and per-entry kstats, validates module/device inputs, and opens STREAMS device vnodes when needed.
- `sockparams_destroy()` releases device vnodes, module references, kstats, filters, locks, and memory.
- Ephemeral sockparams are reused or created for caller-specified modules/devices and TPI fallback; the last reference removes them from the ephemeral list and destroys them.
- `sockparams_add()` inserts configured entries after kstat setup and filter initialization.
- `sockparams_delete()` removes unused configured entries or returns `EBUSY`.
- `solookup()` finds exact socket tuple entries, reports precedence-aware errors for unsupported family/protocol/type, lazily loads socket modules, and returns held entries.
- Filter cleanup/addition helpers remove or add filter references across configured and ephemeral sockparams.
- `sockparams_copyout_socktable()` copies the configured socket table to userland, including tuple, module name, device path, refcount, and flags.

## Integration Points
- Used by `socket_create()`, TPI fallback, socket configuration ioctls, socket filters, and module registration.
- Coordinates with `smod_lookup_byname()`, `SMOD_DEC_REF`, `sof_sockparams_init()`, `sof_sockparams_fini()`, and `sockconf_lock`.

## Risks and Notes
- Lock order is documented as `sockconf_lock -> sp_lock`.
- `solookup()` holds entries before dropping `sockconf_lock` for module loading so entries cannot disappear mid-load.
- Ephemeral entries are not placed on the global configured list and disappear when their refcount reaches zero.
- `sockparams_copyout_socktable()` can return `EAGAIN` if the configured table grows beyond the user-provided entry count while copying.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockparams.c -->