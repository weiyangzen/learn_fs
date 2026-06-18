# Group Research: group_489_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_p_910c613b2f47

Scope checked against `Docs/research_subset_a.md`; all six listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port.c

## Role

Core event-port syscall implementation for illumos `portfs`. It registers the `portfs` system call module, creates event-port vnodes/file descriptors, dispatches all user-facing port operations, manages per-port queues, alert mode, waiting threads, event copyout, timeout handling, source registration, and kstats.

## Major Responsibilities

- Defines the `portfs` syscall entry and 32-bit wrapper.
- Implements `PORT_CREATE`, `PORT_GET`, `PORT_GETN`, `PORT_ASSOCIATE`, `PORT_DISSOCIATE`, `PORT_SEND`, `PORT_SENDN`, `PORT_DISPATCH`, and `PORT_ALERT`.
- Creates `VPORT` vnodes backed by `port_t`.
- Enforces resource controls:
  - `project.port-max-ids` for number of ports.
  - `process.port-max-events` for per-port event capacity.
- Initializes per-port queues, source cache, fd cache skeleton, ownership metadata, and timestamps.
- Pre-associates static kernel event sources such as AIO.
- Sends user and library events into the queue.
- Implements alert mode, which wakes all waiters and returns `PORT_SOURCE_ALERT`.
- Implements `port_getn()` queue draining, temporary get-list use, callback-based delivery filtering, native/ILP32 copyout, timeout looping, and poll wakeups.

## Key Functions

- `_init()` builds dummy VFS/vnode ops, initializes global `port_control`, creates `port_cache`, installs kstats, and installs the syscall module.
- `portfs()` is the main syscall dispatcher. It validates port file descriptors and routes to creation, get, associate, send, dispatch, dissociate, and alert operations.
- `port_create()` allocates `port_t`, creates a `VPORT` vnode, allocates a file descriptor, applies rctl checks, increments global counts, and calls `port_init()`.
- `port_init()` initializes locks, event queues, source cache, fd cache skeleton, metadata, and static kernel sources.
- `port_send()` allocates and posts a `PORT_SOURCE_USER` event.
- `port_dispatch_event()` posts private library/kernel events, optionally marking them non-shareable.
- `port_sendn()` sends one user event to multiple port descriptors and returns per-entry errors through the caller’s error array.
- `port_alert()` stores alert state and signals every currently waiting getter.
- `port_getn()` is the central retrieval engine. It handles counting mode, alert mode, blocking and nonblocking waits, timeout conversion, temporary queue transfer, callback validation, free/discard semantics, copyout, and wakeup handoff.
- `port_copy_event()` and `port_copy_event32()` convert kernel events to user ABI records and invoke source callbacks before final delivery.
- `port_get_timeout()` converts native or 32-bit timeout structures.
- `port_queue_thread()` orders waiters by requested event count, favoring smaller requests.
- `port_get_kevent()` iterates event lists for both normal get and close paths.
- `port_kstat_init()` exposes the number of active event ports.

## Event Queue Semantics

Events are queued as `port_kevent_t` records. `port_getn()` moves the main queue into `portq_get_list` before callback processing so new producers can continue enqueueing without being blocked by potentially slow delivery callbacks.

Delivery is callback-mediated. A source callback can update event bits, release source resources, or deny delivery to the current process. Denied events are reinserted into the temporary list, which is important for shared ports where non-shareable or owner-specific events must remain available to the right process.

`PORT_KEV_FREE` events are discarded during retrieval. Wired/cached events remain under their source’s ownership; default events return to the port cache after delivery.

## Alert Mode

Alert mode is modeled as port state, not a normal queued event. `port_alert()` sets `PORTQ_ALERT`, records event/user payload and owner pid, and marks all current waiters with per-thread alert data. Future `port_get()`/`port_getn()` calls return the alert event immediately until alert mode is cleared.

## Concurrency And Locking

- `port_control.pc_mutex` protects global port counts.
- `port_mutex` protects per-port close/init state.
- `portq_mutex` protects queue state, waiters, alert state, close state, and poll flags.
- `portq_source_mutex` protects the per-port source cache.
- `port_block()`/`port_unblock()` serialize queue-drain operations against other getters.
- `port_getn()` deliberately drops `portq_mutex` while invoking callbacks and preparing user records, after moving events to a temporary queue.
- Close coordination uses `portq_thrcnt`, `portq_getn`, `PORTQ_CLOSE`, and `portq_closecv`.

## Dependencies

This file depends on vnode operations from `port_vnops.c`, fd association logic from `port_fd.c`, file-watch association logic from `port_fop.c`, kernel event source APIs declared through `sys/port_impl.h`, AIO close callbacks, rctl, kstats, and poll wakeup integration.

## Research Notes

This file is the control-plane center of event ports. The most important behavior is the separation between event allocation/posting and event delivery. Event sources reserve slots up front, queue completed events later, and reclaim or reuse slots through callback and flag semantics during `port_getn()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port_fd.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port_fd.c

## Role

Implements `PORT_SOURCE_FD`, the event-port source that monitors file descriptors through the existing `VOP_POLL()`/`pollwakeup()` machinery. It manages per-port fd association caches, pollhead binding, one-shot event delivery, reassociation, dissociation, close cleanup, and fd sharing checks across processes.

## Major Responsibilities

- Associate a file descriptor with a port for poll-style events.
- Reactivate an already associated fd with new event masks and user data.
- Allocate one cached `port_kevent_t` per associated fd.
- Store fd associations in a per-port hash table of `portfd_t`/`polldat_t`.
- Integrate with `addfd_port()`/`delfd_port()` so fd close can clean up port associations.
- Bind `polldat_t` entries to filesystem/device `pollhead_t` values.
- Submit immediate events when `VOP_POLL()` returns readiness.
- Remove queued events during reassociation or dissociation.
- Destroy fd caches during per-process close and last close.

## Key Functions

- `port_associate_fd()` validates the fd, creates the fd source association on first use, allocates cache state, installs the fd into the interested-list, performs `VOP_POLL()`, binds pollheads, and sends immediate events if readiness exists.
- `port_dissociate_fd()` removes the caller-owned fd association, deactivates it by clearing `PORT_KEV_VALID`, removes queued events, and frees the object.
- `port_fd_callback()` enforces cross-process delivery rules and handles close callbacks. For delivery, another process may consume fd events only when it has the same fd number and same `file_t *`.
- `port_cache_lookup_fp()` finds an association by fd number and `file_t`.
- `port_bind_pollhead()` disassociates any prior pollhead, associates the `polldat_t` with the new pollhead, then reruns `VOP_POLL()` to close the race between readiness and pollhead linkage.
- `port_cache_insert_fd()` and `port_cache_grow_hashtbl()` maintain the per-port fd hash table.
- `port_remove_portfd()` removes the fd/port relationship if the fd is still open.
- `port_close_sourcefd()` is the source close callback. It removes all associations owned by the closing pid and, on last close, waits for all outstanding fd entries to disappear before destroying the cache.

## Association Model

Each associated fd owns a cached event slot. The association is active while `PORT_KEV_VALID` is set. When readiness is detected, the code clears `PORT_KEV_VALID`, stores the readiness mask, and sends the cached event. After userspace consumes the event, the application must call `port_associate()` again to reactivate the fd.

Reassociation updates the user pointer and event mask, removes any still-queued old event, clears stale validity, and performs a fresh poll.

## Race Handling

`VOP_POLL()` can drop and reacquire the port fd-cache lock through poll infrastructure. After polling, the code revalidates that the same `portfd_t` still exists and that the registering thread still owns the in-progress association attempt. If another thread dissociated or reassociated the same fd, the function returns the current poll error and leaves application-level synchronization to callers.

`port_bind_pollhead()` reruns `VOP_POLL()` after `polldat_associate()` so a readiness change that occurs between the first poll and pollhead binding is not lost.

## Shareability

Fd events are conditionally shareable after fork or descriptor passing only when the consuming process has the same fd number pointing to the same `file_t`. Dissociation is stricter: only the pid that first associated the fd can dissociate it.

## Research Notes

This file is the bridge between event ports and classic poll. Its key invariant is that a cached fd event is one-shot: valid while armed, invalid once fired, and rearmed only by explicit reassociation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port_fd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port_fop.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port_fop.c

## Role

Implements `PORT_SOURCE_FILE`, the event-port source for file and directory change notification. It uses FEM vnode-operation hooks and FSEM filesystem unmount hooks to observe file activity, pathname identity changes, mounted-over events, and unmounts.

## Major Responsibilities

- Register file watches from user `file_obj_t`/`file_obj32_t` objects.
- Maintain a per-port `portfop_cache_t` keyed by user object pointer and pid.
- Maintain per-vnode `portfop_vp_t` lists of active/inactive watches.
- Lazily install FEM hooks on watched vnodes.
- Lazily install FSEM unmount hooks on watched filesystems.
- Deliver file events through cached `port_kevent_t` records.
- Deactivate watches after event delivery, preserving inactive entries for fast reassociation.
- Remove watches and send exception events when file identity changes.
- Clean up all per-pid and last-close file-watch state.
- Handle hard-link/name-sensitive exception behavior.

## Key Data And Structures

- `portfop_t` represents one watch: watched vnode, optional directory vnode, basename, user object pointer, pid, event mask, cached event, port cache, and state flags.
- `portfop_vp_t` is attached to `vnode_t.v_fopdata` and owns the per-vnode watch list, FEM pointer, count, oldest inactive pointer, and filesystem-watch linkage.
- `portfop_vfs_t` tracks watched vnodes for a filesystem and owns the FSEM hook state.
- `portvfs_hash` indexes watched filesystems by `vfs_t`.

## Key Functions

- `port_associate_fop()` copies in the user file object, resolves the path and directory vnode, validates vnode event support, associates the `PORT_SOURCE_FILE` source, creates or reuses a watch, and checks timestamps for immediate events.
- `port_dissociate_fop()` removes a watch owned by the current pid and returns success only if the watch was active or had a queued event removed.
- `port_fop_associate_source()` creates the per-port source cache on first use.
- `port_pfp_setup()` allocates `portfop_t` and cached event state, installs vnode/FEM and filesystem/FSEM hooks as needed, inserts the watch into port and vnode caches, and holds required vnode references.
- `port_fop_getdvp()` resolves the user pathname to vnode and directory vnode, also storing the final path component.
- `port_resolve_vp()` normalizes special mntfs and real-vnode cases.
- `port_check_timestamp()` compares supplied atime/mtime/ctime against current vnode attributes and immediately posts matching access/modified/attrib events.
- `port_fop_sendevent()` delivers events to matching watches, handles active/inactive ordering, converts non-matching hard-link exceptions to `FILE_ATTRIB`, and removes exception watches.
- `port_fop_excep()` sends exception events using fresh non-cached events, then frees the old watch.
- `port_remove_fop()` removes a watch from vnode and port caches, removes queued events, and uninstalls FEM hooks if the vnode has no remaining watches.
- `port_close_fop()` removes all watches for a closing pid and destroys the source cache on last close.
- `port_fop_unmount()` handles filesystem unmount by blocking new watches, uninstalling FSEM hooks, sending `UNMOUNTED` events to all watched vnodes, releasing holds, and removing the filesystem record.

## Hook Coverage

The FEM hook table wraps operations that can affect observed timestamps or identity, including open, read, write, map, setattr, create, remove, link, rename, mkdir, rmdir, readdir, symlink, setsecattr, and vnode event notifications.

The simple wrapper hooks call the underlying `vnext_*()` operation first and only generate events on successful completion. `port_fop_vnevent()` maps filesystem-provided vnode notifications such as rename source/destination, remove, rmdir, create, link, mounted-over, and truncate.

## Watch Lifecycle

A watch starts active at the head of the vnode list. When a normal event is sent, it becomes inactive and moves to the tail. Reassociation reactivates it, updates event/user data, removes any queued prior event, and moves it back to the active region. Exception events remove and free the watch because the watched object identity is gone or changed.

Inactive watches are retained for performance, but `port_fop_trimpfplist()` attempts to discard old inactive watches when a vnode exceeds `port_fop_maxpfps`.

## Locking

The primary lock order is `pfc_lock` followed by `pvp_mutex`. Some cleanup paths use temporary lists because exception delivery needs the reverse context and cannot safely acquire the cache lock while inside the vnode hook list traversal. Vnode references that require `VN_RELE()` are collected and released after dropping locks.

## Research Notes

This file is the most complex portfs source file because it combines user object identity, pathname lookup, vnode identity, hard-link semantics, event-port one-shot behavior, and filesystem unmount coordination. The design intentionally avoids blocking unmounts in the general case, but NFS-style filesystems are treated specially unless unmount is forced.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port_fop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port_vnops.c

## Role

Defines vnode operations for event-port vnodes. These vnodes are not normal filesystem files; they represent kernel event queues exposed as file descriptors.

## Major Responsibilities

- Provides the `port_vnodeops_template` used by `port.c`.
- Implements open, close, getattr, access, inactive, realvp, and poll behavior for `VPORT` nodes.
- Coordinates per-process close cleanup versus final port destruction.
- Discards non-shareable or owner-specific events when a process closes a shared port descriptor.
- Wakes pollers based on queued events and available queue capacity.
- Frees port resources on vnode inactive.

## Key Functions

- `port_open()` is a no-op for already-created port vnodes.
- `port_close()` performs the critical close lifecycle:
  - For non-last close, clears alert mode owned by the current pid, calls source close callbacks for that pid, and discards owned non-shareable events.
  - For last close, marks `PORTQ_CLOSE`, wakes/waits for active getters, calls source close callbacks with `lastclose`, waits for outstanding events, destroys fd cache if unused, and calls `port_close_events()`.
- `port_discard_events()` marks current-process non-shareable events as `PORT_KEV_FREE`.
- `port_close_events()` drains queued events, invokes close callbacks, frees event records, and waits for pending `pollwakeup()` interactions.
- `port_poll()` reports `POLLIN` when queued events exist and `POLLOUT` when the queue has remaining capacity; it also installs the port pollhead for future wakeups.
- `port_getattr()` synthesizes attributes for the event-port vnode.
- `port_inactive()` decrements global counters, frees the vnode, destroys locks, and frees `port_t`.
- `port_access()` allows access unconditionally.
- `port_realvp()` returns the port vnode itself.

## Close Semantics

Event ports can be shared across processes through fork or fd passing. A non-last close removes only resources owned by the closing process. Last close requires full teardown and waits until all event slots allocated to sources have either been queued back to the port or freed.

## Poll Semantics

The port vnode behaves as readable when events are queued and writable when more event slots may be allocated. Poll waiters use `pp->port_pollhd`, and flags in `portq_flags` remember whether `POLLIN` or `POLLOUT` wakeups are needed.

## Research Notes

This file owns the vnode-facing lifetime rules. It is small, but it is where shared-port semantics and final cleanup become observable through standard file descriptor operations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prcontrol.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prcontrol.c

## Role

Implements `/proc` control writes. User processes write command records to `/proc/<pid>/ctl` or lwp control files, and this file parses those records, locks the target process/lwp, and applies control operations such as stop, run, signal control, register writes, watchpoints, agent lwp creation, address-space I/O, credential mutation, privilege mutation, and zone credential changes.

## Major Responsibilities

- Defines command sizing metadata for native and ILP32 `/proc` control commands.
- Buffers and validates one or more control records from a `uio_t`.
- Handles variable-size commands such as `PCSCREDX`, `PCSPRIV`, and `PCSXREG`.
- Provides native and 32-bit command interpreters.
- Applies process/lwp stop and run controls.
- Changes signal masks, pending/current signals, fault masks, syscall tracing masks, and `/proc` flags.
- Writes general, floating-point, extra register, and resume-address state.
- Creates `/proc` agent lwps.
- Reads/writes target address spaces through `prusrio()`.
- Changes process credentials, privileges, and temporary zone credentials.
- Manages watchpoint setup/cancelation by pausing lwps and editing watched areas.

## Command Parsing

`prwritectl_common()` is the shared parser for native and ILP32 writes. It reads enough data to identify a command, consults `proc_control_info_t`, reads static and dynamic payload sizes, rounds records as required by `/proc` ABI rules, locks the target, and invokes either `pr_control()` or `pr_control32()`.

Important details:

- It unlocks the target before `uiomove()` or buffer reallocation to avoid holding process locks across memory allocation or user I/O.
- It supports multiple commands in a single write.
- It handles ILP32 payload alignment by copying unaligned data to a temporary aligned buffer when needed.
- A positive command error stops the batch. A `-1` return means a timeout or special wait condition occurred after unlock, and processing may continue according to caller semantics.

## Native And 32-bit Control

`pr_control()` handles native command payloads. `pr_control32()` converts 32-bit structures and rejects commands that cannot apply to non-32-bit targets with `EOVERFLOW`. Both reject system processes and both unlock the `prnode_t` before returning most command errors.

The command tables cover `PCSTOP`, `PCDSTOP`, `PCWSTOP`, `PCTWSTOP`, `PCRUN`, signal operations, syscall entry/exit masks, flags, register writes, watchpoints, agent creation, address-space read/write, credentials, privileges, and zone changes.

## Stop/Run Logic

- `pr_stop()` marks target lwps with `TP_PRSTOP`, wakes interruptible waits, sets virtual stops where appropriate, pokes threads into the kernel, and broadcasts `p_holdlwps`.
- `pr_wait_stop()` waits until the selected lwp or process representative is stopped, honoring optional millisecond timeouts.
- `pr_setrun()` validates stopped state, handles signal/fault clearing, single-step setup, directed stop, syscall abort, agent-lwp restrictions, representative-lwp demotion, and process-wide resume.
- `allsetrun()` clears `/proc` stop flags and sets all stopped lwps runnable.
- `pr_wait_die()` waits after `SIGKILL` so later operations see target disappearance.

## Signal, Fault, And Trace Control

- `pr_settrace()` sets the signal trace mask and toggles `P_PR_TRACE`.
- `pr_setsig()` installs or clears the current signal on the selected lwp, updates siginfo, handles zone id normalization, and applies SIGKILL/SIGCONT/jobcontrol side effects.
- `pr_kill()` queues a signal with caller pid/uid/zone metadata.
- `pr_unkill()` removes pending non-SIGKILL signals.
- `pr_setentryexit()` updates syscall entry/exit masks and toggles syscall tracing.
- `pr_sethold()` changes an lwp hold mask and wakes it if newly unblocked signals are pending.
- `pr_setfault()`, `pr_clearsig()`, and `pr_clearflt()` update fault/signal stop state.

## Register And Address Controls

Register writes require the selected lwp to be stopped, virtually stopped, or directed-stopped. The code drops `p_lock` before touching lwp register state because target stacks or register save areas may page fault.

Handled state includes general registers, fp registers, machine-dependent xregs, and saved resume address.

## Watchpoints

`pr_watch()` validates ranges and flags, clamps to user address limit, limits page span, and forces the process to be fully stopped. For self-watch operations it uses `holdwatch()`/`continuelwps()`. For other processes it pauses lwps with `pauselwps()`, waits for all to stop, then drops `p_lock` while setting or clearing watched areas.

`pr_cancel_watch()` performs similar pausing and then frees all watchpoints, disables watch state on threads, and restores page protections.

## Agent LWP

`pr_agent()` creates the special `/proc` agent lwp only when the target is fully stopped or directed-stopped and has no existing agent. It builds the lwp stopped, copies supplied registers, records spymaster `psinfo`, mirrors scheduling-class state, publishes `p_agenttp`, starts the lwp, and waits until the agent stops on `PR_REQUESTED`.

## Credential, Privilege, And Zone Mutation

- `pr_scred()` validates uid/gid values, checks setid policy, duplicates and replaces process credentials, updates uid process counts, and marks all threads to refresh credentials on syscall entry.
- `pr_spriv()` delegates privilege mutation to `priv_pr_spriv()` and marks threads for credential refresh.
- `pr_szoneid()` allows privileged temporary credential transitions only between the process zone and global zone, updates zone uid counts, and marks threads for refresh.

## Research Notes

This file is the procedural heart of procfs control. Its central engineering constraint is lock choreography: many commands must hold enough process state stable to be meaningful, but must drop locks before user I/O, allocation, register access, address-space I/O, or operations that may sleep.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prcontrol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prdata.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prdata.h

## Role

Private procfs header for illumos kernel procfs implementation. It defines procfs node/common structures, node types, internal flags, helper macros, usage accounting structures, and prototypes shared across procfs source files.

## Major Responsibilities

- Defines stop-state and alignment helpers used by procfs control/read paths.
- Defines `prcommon_t`, the shared process/lwp object referenced by procfs vnodes.
- Defines `prnode_t`, the per-vnode procfs node object.
- Enumerates all procfs node types, including process files, lwp files, fd/object/path/contract directories, and old procfs compatibility nodes.
- Declares kernel-only procfs helpers used by control, vnode, data, map, page-data, and machine-dependent code.
- Defines the chained procfs I/O buffer interface used to avoid very large single allocations.
- Declares 32-bit procfs conversion/control entry points when enabled.
- Documents machine-dependent xregs support requirements.

## Key Types

- `prcommon_t`: common process/lwp tracking object with wait mutex/CV, flags, writer/self-open counts, pid, data model, process pointer, thread pointer, slot/tid metadata, reference count, and pollhead.
- `prnode_t`: procfs vnode-private object with node type, mode, inode, hat id, common and process-common pointers, parent/child references, real vnode backing pointer for fd/object/path entries, owner, vnode pointer, contract pointer, and template type.
- `prnodetype_t`: node-type enum covering `/proc`, `/proc/self`, pid directories, address space, control/status files, map/xmap/rmap, credentials, sigact, auxv, lwp directories and lwp files, fd/fdinfo/object/path/contract trees, secflags, and legacy nodes.
- `prhusage_t`: internal high-resolution usage structure paralleling `prusage_t` with `hrtime_t` time fields and counters.

## Important Macros And Flags

- `DSTOPPED(t)` identifies a thread stopped due to a directed `/proc` stop.
- `round4`, `round8`, `round16`, and `roundlong` provide ABI-alignment helpers.
- `PRC_DESTROY`, `PRC_LWP`, `PRC_SYS`, `PRC_POLL`, and `PRC_EXCL` describe `prcommon_t` state.
- `PR_INVAL`, `PR_ISSELF`, `PR_AOUT`, and `PR_OFFMAX` describe per-node state.
- `VTOP()` and `PTOV()` convert between vnodes and procfs nodes.
- `PROCESS_NOT_32BIT()` is used by ILP32 procfs control paths to reject non-32-bit targets.

## Declared Interfaces

The header exports procfs internals including:

- Locking and lifetime: `pr_p_lock()`, `prlock()`, `prunlock()`, `prunmark()`, `prgetnode()`, `prfreenode()`.
- Control: `prwritectl()`, `prwritectl32()`, `pr_stop()`, `pr_wait_stop()`, `pr_setrun()`, `pr_wait_die()`, `allsetrun()`.
- Signal/fault/syscall tracing: `pr_setsig()`, `pr_kill()`, `pr_unkill()`, `pr_setentryexit()`, `pr_sethold()`, `pr_setfault()`.
- File/address-space helpers: `pr_getf()`, `pr_releasef()`, `prusrio()`.
- Maps and page data: `prgetmap()`, `prgetxmap()`, `prpdread()`, old procfs variants, and 32-bit variants.
- Usage/action conversion: `prgetusage()`, `praddusage()`, `prcvtusage()`, `prgetaction()`.
- Watchpoints: `set_watched_area()`, `clear_watched_area()`, `pr_free_watchpoints()`, `pr_cancel_watch()`.
- Machine-dependent register and xregs routines.

## Xregs Contract

The extended-register comment block is an important interface contract. It states that `prxregset_t` is opaque and variable-sized, and requires machine-dependent code to provide support detection, size calculation, write minimum sizing, write full sizing, read, and validated write operations. It explicitly warns that xregs write buffers may be unaligned because both ILP32 and LP64 procfs controls share the mechanism.

## Research Notes

This header defines the internal vocabulary used by `prcontrol.c` and the rest of procfs. Its most important architectural role is separating common process/lwp state (`prcommon_t`) from individual vnode nodes (`prnode_t`) while exposing enough internal helpers for procfs control, status, vnode, and machine-dependent implementations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prdata.h -->