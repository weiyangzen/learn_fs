# Group Research: group_428_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_sys_pipe_c_sources_o_41aff9040e99

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_pipe.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_pipe.c

## Purpose
Implements FreeBSD pipe file descriptors, including `pipe2(2)`, anonymous pipe lifecycle, named-pipe integration hooks, pipe `fileops`, poll/kqueue readiness, and high-performance direct-copy pipe I/O.

## Main Elements
- `pipeops`: file operation table for read, write, ioctl, poll, kqueue, stat, close, chmod/chown, kinfo, and descriptor passing.
- `pipeinit()`: creates the UMA zone for `struct pipepair`, initializes pipe inode allocators, and assigns a pseudo device inode.
- `pipe_paircreate()`, `kern_pipe()`, `sys_pipe2()`, `freebsd10_pipe()`: allocate paired endpoints, file descriptors, flags, Capsicum filecaps, and compatibility syscall return behavior.
- `pipe_named_ctor()` / `pipe_dtor()`: construct and tear down pipe-backed named FIFO endpoints.
- `pipespace_new()` / `pipespace()`: allocate or resize pageable pipe KVA, enforce `RLIMIT_PIPEBUF`, reserve privileged pipe buffer space, and preserve circular-buffer contents during resize.
- `pipe_read()` and `pipe_write()`: core blocking/nonblocking pipe I/O with EOF handling, `PIPE_BUF` atomicity, wakeups, resource accounting, timestamps, and MAC checks.
- Direct-write path: `pipe_build_write_buffer()`, `pipe_direct_write()`, `pipe_clone_write_buffer()`, and `pipe_destroy_write_buffer()` pin writer pages and let readers copy from physical pages for larger user writes.
- Notification and metadata: `pipe_ioctl()`, `pipe_poll()`, `pipe_kqfilter()`, `filt_piperead()`, `filt_pipewrite()`, `pipe_stat()`, `pipe_fill_kinfo()`.
- Cleanup: `pipeclose()`, `pipe_free_kmem()`, `pipe_destroy()` coordinate EOF, busy users, peer wakeups, knote teardown, MAC label destruction, credentials, and UMA release.

## Dependencies And Integration
Uses kernel file descriptor allocation, `struct fileops`, UMA, VM pipe maps, resource limits, MAC framework hooks, selinfo/kqueue, signal ownership, vnode operations for named pipes, and syscall wrappers from `sysproto.h`. It is the main bridge between `pipe2(2)`/legacy pipe syscalls and FreeBSD’s generic file descriptor layer.

## Risk Notes
The file is concurrency- and resource-sensitive. Correctness depends on the split mutex plus `PIPE_LOCKFL` protocol because pipe locks are intentionally dropped around `uiomove()`. Direct writes rely on page pinning and must clone buffered data if interrupted. Pipe KVA accounting and resizing are defensive against system-wide exhaustion, but failures must preserve existing buffered data and wake waiters correctly.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_pipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_procdesc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_procdesc.c

## Purpose
Implements FreeBSD process descriptors: file descriptors representing processes for capability-style process management, polling, kqueue exit notification, stat/kinfo reporting, and close-time process cleanup.

## Main Elements
- `procdesc_ops`: file operation table for process descriptor objects; read/write/ioctl/truncate are invalid, while poll, kqueue, stat, close, kinfo, and comparison are supported.
- `procdesc_find()`: resolves a process descriptor fd to a locked live `struct proc`, with Capsicum rights validation.
- `procdesc_pid()`, `kern_pdgetpid()`, `sys_pdgetpid()`: expose the PID associated with a process descriptor.
- `procdesc_new()`, `procdesc_falloc()`, `procdesc_finit()`: allocate descriptor state during `pdfork()` setup and bind it to a `struct file`.
- `procdesc_exit()` and `procdesc_reap()`: synchronize process exit/reap with descriptor state, exit status, wait behavior, select, and kqueue notification.
- `procdesc_close()`: handles last close, marking the descriptor closed, reaping zombies, detaching live processes, reparenting to the reaper, and sending `SIGKILL` unless `PDF_DAEMON` is set.
- `procdesc_poll()` and `procdesc_kqfilter()`: report process-exit readiness with `POLLHUP` and `EVFILT_PROCDESC`/`NOTE_EXIT`.
- `procdesc_stat()`, `procdesc_fill_kinfo()`, `procdesc_cmp()`: provide file metadata, `procstat`/`kinfo_file` details, and `kcmp` ordering.

## Dependencies And Integration
Integrates with `proctree_lock`, process locking, file descriptor allocation, Capsicum rights, audit, kqueue/select, process reparenting/reaping, PID lifecycle tracking, and `pdfork`/process descriptor APIs declared in `procdesc.h`.

## Risk Notes
The close/exit/reap paths are delicate because the descriptor and process each hold references. The code uses `proctree_lock` to serialize descriptor close against process exit and avoids synchronous waiting during close to prevent deadlocks. Last close has strong side effects: it may kill a still-running process and change its parentage.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_procdesc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_process.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_process.c

## Purpose
Implements process debugging support centered on `ptrace(2)`, including register access, traced-process memory I/O, VM map inspection, thread/LWP debug metadata, coredump requests, remote syscall execution, and ptrace relationship management.

## Main Elements
- Register helpers: `proc_read_regs()`, `proc_write_regs()`, `proc_read_fpregs()`, `proc_write_fpregs()`, `proc_read_dbregs()`, `proc_write_dbregs()` call machine-dependent register accessors with privilege checks for writes.
- Regset helpers: `proc_find_regset()`, `proc_read_regset()`, `proc_write_regset()` expose ELF-note-style dynamic register sets through `struct iovec`.
- 32-bit compatibility wrappers expose 32-bit register layouts and prevent unsafe 32-bit debugger writes to 64-bit targets.
- `proc_sstep()`: enables single-step execution through machine ptrace support.
- `proc_rwmem()`, `proc_readmem()`, `proc_writemem()`: read/write another process address space one page at a time via VM faults, held pages, `uiomove_fromphys()`, and instruction-cache sync for executable writes.
- `ptrace_vm_entry()`: enumerates VM map entries, protections, offsets, timestamps, vnode path, fsid, and fileid for `PT_VM_ENTRY`.
- `sys_ptrace()`: marshals user arguments into kernel buffers for every ptrace request, performs copyin/copyout, and delegates request execution to `kern_ptrace()`.
- `proc_set_traced()`, `ptrace_unsuspend()`, `proc_can_ptrace()`: manage tracing state, stopped-process eligibility, parent/debugger checks, and resumption.
- `kern_ptrace()`: central request dispatcher for attach/detach, continue/step/syscall tracing, event masks, syscall args/returns, memory I/O, registers, LWP info/lists, VM timestamps/entries, coredump requests, remote syscalls, and machine-dependent ptrace extensions.

## Dependencies And Integration
Connects process, thread, signal, VM, vnode, file descriptor, audit, syscall, and machine-dependent register subsystems. It relies on `proctree_lock`, `PROC_LOCK`, process holds, ptrace flags, `p_candebug()`, `p_cansee()`, VM map/object locking, and Capsicum rights for coredump fd access.

## Risk Notes
This is a high-risk security boundary. It enforces visibility/debug permissions, rejects system processes, serializes parallel ptrace requests with `P2_PTRACEREQ`, and uses privilege checks for memory/register writes. Lock ordering and lock drops around allocation, copyin/copyout, VM faults, and remote requests are central to avoiding deadlocks and races with exiting or reparented processes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_process.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_socket.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_socket.c

## Purpose
Defines socket file descriptor operations and generic socket AIO support, connecting FreeBSD sockets to the generic `struct file` layer, ioctl/poll/kqueue/stat/kinfo interfaces, close behavior, and asynchronous read/write execution.

## Main Elements
- `socketops`: `fileops` table for socket read, write, ioctl, poll, kqueue, stat, close, fdclose, chmod, kinfo, AIO queueing, comparison, and descriptor passing.
- `soo_read()` / `soo_write()`: perform MAC checks and call `soreceive()` / `sousrsend()`.
- `soo_ioctl()`: handles generic socket descriptor ioctls such as nonblocking, async, byte counts, ownership, process group, at-mark, and dispatches interface, routing, or protocol-specific ioctls.
- `soo_poll()` and `soo_kqfilter()`: delegate readiness and kqueue behavior to protocol switch methods.
- `soo_stat()`: synthesizes socket stat metadata, readability/writability mode bits, receive size, uid/gid, and protocol-specific `pr_sense`.
- `soo_close()` / `soo_fdclose()` / `soo_chmod()`: close sockets, notify protocols of fd close, and delegate chmod where supported.
- `soo_fill_kinfo()`: fills `kinfo_file` socket details for protocol/domain/type, PCB pointers, queues, local/peer socket addresses, and UNIX-domain peer pointers.
- Socket AIO subsystem:
  - `soaio_init()`, `soaio_enqueue()`, `soaio_kproc_create()`, `soaio_kproc_loop()` manage socket AIO worker kernel processes and job queues.
  - `soaio_process_job()` and `soaio_process_sb()` run queued read/write AIO jobs against socket buffers.
  - `sowakeup_aio()`, `soo_aio_cancel()`, `soo_aio_queue()`, `soaio_queue_generic()` integrate readiness wakeups, cancellation, and generic protocol AIO queueing.

## Dependencies And Integration
Uses socket/protocol switch APIs, sockbuf locking, virtual network context switching, MAC socket hooks, network routing/interface ioctls, AIO kernel job infrastructure, taskqueues, kprocs, file descriptor metadata, UNIX and INET PCB state, and select/kqueue readiness support.

## Risk Notes
AIO execution temporarily switches vmspace and credentials to match the submitting job, so credential restoration and cancellation correctness matter. The ioctl path mixes unlocked reads for some socket state with locked sockbuf access elsewhere. Protocol delegation means correctness depends on each protocol’s `pr_*` methods honoring locking and vnet expectations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_socket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_timerfd.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_timerfd.c

## Purpose
Implements Linux-style timer file descriptors for FreeBSD, including descriptor creation, read semantics, timer programming, realtime-clock jump handling, poll/kqueue readiness, stat/kinfo, and close cleanup.

## Main Elements
- `struct timerfd`: stores user timer spec, clock id, creation flags, timer flags, expiration count, callout, select/kqueue state, cached boottime, realtime-jump state, timestamps, and synthetic inode.
- Global `timerfd_list`: tracks active timerfds so `timerfd_jumped()` can update realtime absolute timers after discontinuous clock changes.
- `timerfd_jumped()`: detects `CLOCK_REALTIME` absolute timer effects, marks cancel-on-set timers `ECANCELED`, handles backward jumps, adjusts pending absolute callouts, and wakes waiters.
- `timerfd_read()`: returns an 8-byte expiration count, blocks or returns `EAGAIN` if no expirations, and implements jump/cancel read semantics.
- `timerfd_ioctl()`: supports `FIOASYNC` and `FIONBIO` by updating file flags.
- `timerfd_poll()`, `timerfd_kqfilter()`, `filt_timerfdread()`: expose readable readiness when expiration count is nonzero and no consumed jump state blocks reporting.
- `timerfd_stat()`, `timerfd_fill_kinfo()`, `timerfd_close()`: report descriptor metadata, export kinfo details, remove from global list, drain callout/select state, and free memory.
- `timerfd_expire()`: callout handler that increments expiration count, accounts for missed periodic expirations, reschedules intervals, clears one-shot timers, and wakes readers.
- `kern_timerfd_create()`, `kern_timerfd_gettime()`, `kern_timerfd_settime()`: kernel implementations for syscall wrappers, validating clocks/flags/timespecs and manipulating descriptor state.
- `sys_timerfd_create()`, `sys_timerfd_gettime()`, `sys_timerfd_settime()`: user copyin/copyout syscall entry points.

## Dependencies And Integration
Uses `struct fileops`, file descriptor allocation, callouts, selinfo/kqueue, unr inode allocation, audit, timespec helpers, boottime/nanouptime conversion, Capsicum rights through `fget()`, and generated syscall entries for timerfd syscall numbers.

## Risk Notes
Clock conversion is subtle: absolute realtime timers are converted relative to cached boottime, and realtime jumps can cancel or adjust timers. Periodic expiration counting must avoid losing missed intervals. The file uses `cap_write_rights` for get/set fd lookup, which is worth verifying against intended Capsicum rights policy for read-only gettime use.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_timerfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/syscalls.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/syscalls.c

## Purpose
Generated syscall-name table for the native FreeBSD kernel ABI. It maps syscall numbers to symbolic names used by tracing, diagnostics, auditing, compatibility reporting, and other syscall-number-to-name consumers.

## Main Elements
- `syscallnames[]`: ordered string array from syscall number 0 through 602.
- Includes current native syscall names such as `read`, `write`, `openat`, `kevent`, `copy_file_range`, `timerfd_create`, `kcmp`, `pdrfork`, `pdwait`, and `renameat2`.
- Marks compatibility entries with prefixes such as `compat`, `compat4`, `compat6`, `compat10`, `compat11`, `compat12`, `compat13`, and `compat14`.
- Marks removed or obsolete entries with `obs_...`.
- Marks reserved local-use slots as `"#NNN"`.
- Contains process-descriptor syscalls at 518-520 and 600-601, pipe2 at 542, and timerfd syscalls at 585-587.

## Dependencies And Integration
Automatically generated from the syscall master inputs using configuration from `syscalls.conf`. The table must remain synchronized with syscall numbers, syscall switch generation, headers, libc syscall maps, and compatibility ABIs.

## Risk Notes
This file should not be hand-edited. Any mismatch between this table and the actual syscall switch/header generation would produce misleading tracing or audit names. Reserved and obsolete entries are intentionally retained to preserve syscall-number stability.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/syscalls.conf -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/syscalls.conf

## Purpose
Small generation configuration file for FreeBSD syscall artifacts.

## Main Elements
- `libsysmap="../../lib/libsys/syscalls.map"`: output or companion path for libsys syscall map generation.
- `libsys_h="../../lib/libsys/_libsys.h"`: output or companion path for generated internal libsys header data.
- `sysmk="../sys/syscall.mk"`: output or companion path for generated syscall makefile fragments.
- `syshdr_extra="#define \tSYS_exit\tSYS__exit"`: extra syscall header define mapping `SYS_exit` to `SYS__exit`.

## Dependencies And Integration
Used by the syscall generation tooling that emits kernel syscall tables, syscall names, headers, makefile fragments, and libsys metadata. It links the kernel syscall source definitions to generated artifacts under `sys/` and `lib/libsys/`.

## Risk Notes
Although only four lines, path or macro changes affect generated syscall ABI support files. The `SYS_exit` alias preserves expected user/kernel naming compatibility and should remain synchronized with generated syscall headers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/syscalls.conf -->