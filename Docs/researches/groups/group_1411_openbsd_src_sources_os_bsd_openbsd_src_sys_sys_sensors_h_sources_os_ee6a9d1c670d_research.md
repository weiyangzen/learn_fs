# Group Research: group_1411_openbsd_src_sources_os_bsd_openbsd_src_sys_sys_sensors_h_sources_os_ee6a9d1c670d

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/sensors.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/sensors.h

Hardware sensor ABI and kernel sensor registry declarations.

This header defines the public sensor taxonomy used by OpenBSD `hw.sensors`: temperature, fan, voltage, power, current, capacity, drive state, timedelta, humidity, frequency, angle, distance, pressure, acceleration, velocity, and energy. User-visible `struct sensor` and `struct sensordev` expose descriptions, timestamps, values, type/status, per-type numbering, invalid/unknown flags, device names, and per-type maximum indices.

Under `_KERNEL`, it defines the kernel-side `ksensor` and `ksensordev` list structures plus registration, lookup, attach/detach, and periodic task APIs. The compatibility note is explicit: new fields should be appended to public structs.

Filesystem/storage relevance: not a filesystem header, but `SENSOR_DRIVE_*` states model disk/drive health and lifecycle, and `hw.sensors` is a common storage-monitoring surface for disk controllers and enclosure drivers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/sensors.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/shm.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/shm.h

System V shared memory public ABI and kernel hooks.

This header defines shared-memory flags for `shmat(2)`, accepted `shmctl(2)` commands, `SHMLBA`, the public `struct shmid_ds`, and BSD-visible `struct shminfo`/`struct shm_sysctl_info`. It also provides `KERN_SHMINFO_*` identifiers and `CTL_KERN_SHMINFO_NAMES` for exposing shared-memory limits and segment data through sysctl.

Kernel builds get global `shminfo`, the `shmsegs` table, and lifecycle hooks for shared-memory initialization, fork inheritance, process exit cleanup, and `sysctl_sysvshm()`. Userland gets the standard `shmat`, `shmctl`, `shmdt`, and `shmget` prototypes.

Filesystem/storage relevance: shared memory is VM-backed rather than filesystem-backed here, but its sysctl accounting and process VM lifecycle interact with the same kernel resource-limit and memory-pressure environment that file-backed mappings use.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/shm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/siginfo.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/siginfo.h

`siginfo_t` layout and signal-code namespace.

This header defines `union sigval`, user/kernel signal-origin tests, generic `SI_*` codes, architecture-related signal cause codes for `SIGILL`, `SIGFPE`, `SIGSEGV`, and `SIGBUS`, plus trap and child-status codes. Unsupported `SIGPOLL` and `SIGPROF` layouts remain disabled in `#if 0`, but accessor macros still name those union members for compatibility with historical shape.

The public `siginfo_t` is fixed at `SI_MAXSZ` 128 bytes and stores signal number, code, errno, and a padded union for process, child, and fault data. Kernel builds expose `initsiginfo()`.

Filesystem/storage relevance: indirect. Filesystem syscalls can be interrupted or can trigger signal delivery paths, and `SIGXFSZ` is named in the disabled file-info block, but this header mainly defines process-signal ABI rather than VFS behavior.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/siginfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/sigio.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/sigio.h

Async I/O signal ownership structures.

This header declares `struct sigio_ref` as the stable reference slot embedded by devices and sockets that support `SIGIO`/`SIGURG` ownership. Kernel builds define `struct sigio`, which records whether signals target a process or process group, links into process/group revocation lists, remembers the owning reference slot, credentials, and pgid.

The kernel API initializes, copies, frees, revokes lists, gets ownership, and sets ownership for `FIOASYNC`/`SIOC*PGRP` style behavior. Lock annotations identify `sigio_lock` as the protecting lock.

Filesystem/storage relevance: this is relevant to descriptors whose readiness is exposed through file operations, especially sockets, ttys, fifos, and device vnodes. Regular filesystem files generally do not depend on async signal ownership.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/sigio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/signal.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/signal.h

Public signal numbers, masks, actions, alternate stack ABI, and prototypes.

This header defines OpenBSD signal numbers 1 through 32, `_NSIG`, default/ignore/error handler sentinels, `sigset_t`, `struct sigaction`, action flags, `sigprocmask` operations, BSD `sig_t` and `struct sigvec` compatibility, `sigmask()`, and alternate signal stack types and constants. Visibility gates expose BSD, POSIX, XPG, and POSIX.1-2024 additions such as `SOCK_CLOFORK` elsewhere and `SIGWINCH` here.

It includes `<machine/signal.h>` for machine signal context and exposes the historical `signal()` prototype outside the kernel.

Filesystem/storage relevance: indirect but operationally important. Signals interrupt blocking filesystem, pipe, socket, and device operations; `SIGXFSZ` is the user-visible signal for file-size resource-limit violations.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/signal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/signalvar.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/signalvar.h

Kernel-private signal action and delivery declarations.

This header defines `struct sigacts`, the per-process signal-disposition state protected by the process signal mutex and atomics. It tracks handlers, catch masks, alternate-stack signals, interrupt/restart behavior, reset-on-catch behavior, siginfo delivery, ignored signals, caught signals, and `SAS_*` flags.

It also defines internal temporary actions, pending-signal checks, default signal property bits, `sigcantmask`, `struct sigctx`, and machine-independent signal APIs such as `coredump()`, `execsigs()`, `cursig()`, `psignal()`, `trapsignal()`, `sigexit()`, and signal action allocation/init/free helpers. Machine-dependent delivery enters through `sendsig()`.

Filesystem/storage relevance: core-dump generation is filesystem-facing, and signal interruption semantics affect blocking VFS/device/socket operations. Most definitions are process-control plumbing rather than filesystem metadata.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/signalvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/smr.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/smr.h

Safe memory reclamation primitives and SMR-aware list macros.

This header defines `struct smr_entry` callback records, SMR startup/read-side/callback/barrier APIs, and pointer access macros using `READ_ONCE`, `WRITE_ONCE`, and producer barriers. Diagnostic builds assert whether the current CPU is inside or outside an SMR critical section.

Most of the file adapts queue-style containers for lock-free SMR readers: `SMR_SLIST_*`, `SMR_LIST_*`, and `SMR_TAILQ_*`. Reader traversal uses SMR pointer reads, while mutation macros are explicitly `_LOCKED` and preserve removed elements' forward links so concurrent readers can finish iteration safely.

Filesystem/storage relevance: SMR is a generic kernel concurrency primitive. It matters to filesystem and VFS code when shared lookup tables, caches, or object lists need lockless readers with deferred reclamation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/smr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/socket.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/socket.h

Public socket ABI: types, options, address families, message headers, ancillary data, sysctl names, and prototypes.

This header defines socket types, creation flags, `SOL_SOCKET` options, linger/splice structures, routing-table constants, address/protocol families, `sockaddr`, `sockaddr_storage`, `sockproto`, shutdown modes, peer credentials, and CTL_NET sysctl name tables. It covers PF_ROUTE, PF_UNIX, PF_LINK, PF_KEY, BPF, and pflow sysctl subtrees.

The send/receive ABI is defined through `struct msghdr`, `struct mmsghdr`, `MSG_*` flags, `struct cmsghdr`, CMSG alignment/navigation macros, and socket-level ancillary types `SCM_RIGHTS` and `SCM_TIMESTAMP`. Userland prototypes cover classic socket calls, batched send/receive, `accept4()`, peer-id lookup, and routing-table selection. Kernel builds get `sstosa()`.

Filesystem/storage relevance: sockets are file descriptors and participate in VFS file operation dispatch, descriptor passing, kqueue, poll/select, and UNIX-domain pathname sockets. `SCM_RIGHTS` also transports file descriptors, including filesystem-backed files.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/socket.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/socketvar.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/socketvar.h

Kernel socket and socket-buffer internal contract.

This header defines `struct sockbuf`, `struct socket`, optional splice state, accept queues, socket state bits, buffer flags, and the lock annotations used throughout OpenBSD socket code. It exposes the kernel socket operation prototypes for fileops, append/drop/flush buffer operations, creation, connect/listen/accept, send/receive, socket options, shutdown, wakeup, locking, syscall helpers, and debug checks.

Inline helpers manage reference taking, splice checks, notification tests, buffer space computation, atomic-send detection, readable/writeable tests, sockbuf accounting, and empty-buffer fixup. The header also declares `sb_max` and `socket_pool`.

Filesystem/storage relevance: important at the descriptor layer. Sockets share file-table, kqueue, ioctl, stat, close, and descriptor-passing paths with VFS objects. UNIX-domain sockets can be filesystem nodes, and socket buffers can carry rights to files.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/socketvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/sockio.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/sockio.h

Socket and network-interface ioctl command namespace.

This header defines ioctl numbers for socket process-group and out-of-band mark operations, interface address/flag/metric/media/MTU/configuration operations, multicast, tunnel, bridge, VLAN, MPLS, pflow, pfsync, carp, MBIM, and many interface-specific control surfaces. It uses `_IO*` macros from `<sys/ioccom.h>` and references request structures defined by networking headers.

The file is pure ABI constant definition; it does not define the request structs themselves.

Filesystem/storage relevance: mostly network-facing. It matters to VFS only through the generic `ioctl(2)` dispatch on file descriptors and special device/socket descriptor handling.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/sockio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/softintr.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/softintr.h

Machine-independent soft interrupt interface.

This small kernel-only header is enabled when `__USE_MI_SOFTINTR` is defined. It assigns soft interrupt levels for clock, network, and tty work, defines `NSOFTINTR`, and declares initialization, establish, disestablish, dispatch, and schedule functions.

Filesystem/storage relevance: indirect. Filesystem code generally runs in process or kernel thread context, but tty, network, and clock soft interrupts can wake descriptor waiters, update timers, or drive I/O-adjacent work.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/softintr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/specdev.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/specdev.h

Special-device vnode metadata and operation declarations.

This header defines `struct specinfo`, the vnode-attached metadata for block and character special devices. It records hash-chain membership, special-device list linkage, mountpoint, raw device number, advisory-lock state, last read block, and clone-device parent/bitmap state. `struct cloneinfo` records a cloned vnode and original private data.

It provides shorthand macros mapping vnode fields to `v_specinfo` members, clone encoding constants, special-device hash constants, the global `speclisth` table, and prototypes for `spec_*` vnode operations such as open, close, read, write, ioctl, strategy, fsync, inactive, pathconf, and advisory lock.

Filesystem/storage relevance: high. Special vnodes are the bridge between VFS and device drivers, including raw/block storage devices used for mounted filesystems, swap, and direct disk access.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/specdev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/srp.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/srp.h

Safe reference pointer and SRP list interface.

This header defines `struct srp` as a protected pointer slot, hazard/reference state, garbage-collection callbacks, and singly linked lists built from SRP pointers. On multiprocessor kernels, SRP operations use hazard protection and finalization; on uniprocessor kernels, many operations collapse to locked direct access.

The SRPL macros provide locked insertion/removal and protected traversal for singly linked lists while invoking reference callbacks and GC updates as links change. The list API is designed for readers that enter/follow/leave references safely while writers update under external locking.

Filesystem/storage relevance: generic concurrency support. VFS, device, network, or storage code can use SRP when pointer replacement and deferred destruction are needed without blocking readers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/srp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/stacktrace.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/stacktrace.h

Fixed-size kernel stacktrace capture ABI.

This header defines `STACKTRACE_MAX` as 19 program counters and `struct stacktrace` with a count and PC array. Kernel builds expose printing, capture at a skip depth, user-trace capture, and an inline `stacktrace_save()` wrapper.

Filesystem/storage relevance: diagnostic only. It can support lock, allocation, or error tracing in filesystem and storage code, but it contains no VFS policy.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/stacktrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/stat.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/stat.h

File status structure, mode bits, file flags, timestamp constants, and stat-family prototypes.

This header defines public `struct stat`, including mode, device, inode, links, owner/group, rdev, atime/mtime/ctime, size, block count, block size, BSD file flags, generation, and birth time. It provides POSIX and BSD timestamp aliases, permission bits, file-type bits, `S_IS*` tests, POSIX `S_TYPEIS*` stubs, BSD permission masks, block-size constant, and owner/superuser file flags.

Kernel builds get shorthand flag masks for opaque, append-only, and immutable checks. Userland gets prototypes for chmod/stat/mknod/mkdir/fifo/umask, POSIX `*at` and nanosecond timestamp operations, and BSD chflags/isfdtype calls.

Filesystem/storage relevance: central public filesystem ABI. This is the primary structure and constant set through which VFS and filesystems expose file metadata to userland.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/stat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/statvfs.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/statvfs.h

POSIX-style filesystem capacity/status ABI.

This header defines `struct statvfs` with block size, fragment size, total/free/available blocks, total/free/available file counts, filesystem id, mount flags, and maximum filename length. It defines `ST_RDONLY` and `ST_NOSUID`, plus userland prototypes for `statvfs()` and `fstatvfs()`.

Filesystem/storage relevance: direct. It is a public filesystem-capacity and mount-property reporting ABI layered over VFS/statfs-style data.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/statvfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/stdarg.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/stdarg.h

Compiler-backed variadic argument definitions.

This header wraps compiler builtins for `__gnuc_va_list`, `va_list`, `va_start`, `va_end`, `va_arg`, `__va_copy`, and C99 `va_copy`. It notes the standard rule that `va_arg` types must match default argument promotions.

Filesystem/storage relevance: generic C infrastructure. It is used by kernel and userland formatted printing/logging paths that filesystem and storage code may call, but it has no filesystem semantics.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/stdarg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/stdint.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/stdint.h

Standard fixed-width integer type and limit definitions.

This header maps OpenBSD machine types to C99 integer typedefs: exact-width, least-width, fast-width, pointer-capable, and maximum-width integer types. It defines min/max constants for those types, pointer difference limits, `sig_atomic_t`, `size_t`, wide-character and wide-int limits, and integer constant construction macros.

It handles 32-bit versus 64-bit pointer-size limits through `__LP64__` and uses compiler-provided fast-width limits.

Filesystem/storage relevance: foundational. Filesystem metadata, block counts, offsets, device ids, ABI structs, and serialization code depend on stable integer widths and limits.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/stdint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/swap.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/swap.h

Swap device userland reporting and control constants.

This header defines `struct swapent`, the user-visible swap-entry record containing device id, flags, total/in-use block counts, priority, and path. It defines `swapctl` commands for enabling, disabling, counting, querying stats, changing priority, and setting dump device, plus swap flags for in-use, enabled, busy, and fake/in-construction state.

Kernel builds also define `NETDEV` as the synthetic device id for NFS swap.

Filesystem/storage relevance: direct storage relevance. Swap can be backed by block devices or network storage, and dump-device selection overlaps with low-level storage-device management.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/swap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/syscall.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/syscall.h

Generated system call number table.

This generated header maps OpenBSD system call names to numeric `SYS_*` identifiers and records return/argument comments from `syscalls.master`. It spans process, file, VFS, VM, signal, socket, SysV IPC, kqueue, pledge/unveil, routing-table, thread, and `*at` interfaces, with obsolete slots preserved as comments to maintain ABI numbering. `SYS_MAXSYSCALL` is 331.

Filesystem-facing entries include open/close/read/write, link/unlink/rename, stat/lstat/fstat/fstatat, chmod/chown/chflags, mkdir/rmdir/mknod/mkfifo, mount/unmount/sync/fsync, statfs/getfsstat/fhstatfs, getfh/fhopen/fhstat, pathconf, truncate/ftruncate, pread/pwrite variants, quotactl, access/faccessat, openat, readlinkat, renameat, symlinkat, unlinkat, and `__getcwd`.

Filesystem/storage relevance: central syscall ABI map for every user-to-kernel filesystem entry point. The file is generated and should not be manually edited.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/syscall.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/syscall_mi.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/syscall_mi.h

Machine-independent syscall entry/return helpers.

This header implements inline MI syscall processing after MD register setup. `pin_check()` enforces pinsyscalls by verifying the syscall instruction address lies in approved libc/program/ld.so regions or the sigtramp sigreturn slot; failures can KTRACE, print diagnostics, mark accounting, single-thread the process, and abort it.

`mi_syscall()` refreshes credentials, emits tracepoints/DTrace/KTRACE events, validates the userspace stack mapping, runs pin and pledge checks, optionally takes the global kernel lock depending on `SY_NOLOCK`, and invokes the selected `sysent` handler. `mi_syscall_return()` handles tracing and `userret()`, `mi_child_return()` synthesizes fork/vfork/tfork returns for new threads/processes, and `mi_ast()` handles profiling and preemption AST work.

Filesystem/storage relevance: every filesystem syscall crosses this path. Pledge, pinsyscalls, KTRACE, stack validation, and kernel-lock policy all affect VFS syscall execution.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/syscall_mi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/syscallargs.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/syscallargs.h

Generated syscall argument structs and handler prototypes.

This generated header defines the `syscallarg(x)` union used to extract syscall arguments correctly on little- and big-endian machines, then declares one argument struct per syscall that takes arguments. The structs cover file/VFS, VM, sockets, signals, process control, SysV IPC, kqueue, threads, pledge/unveil, and `*at` variants.

The second half declares kernel handler prototypes for implemented syscalls, with compile-time feature gates for optional subsystems such as `PTRACE`, `KTRACE`, `ACCOUNTING`, NFS, and SysV IPC. Filesystem-facing prototypes include open, mount, stat families, file-handle calls, sync/fsync, getdents, access, chmod/chown/chflags, link/unlink/rename/symlink/readlink, directory creation/removal, fifo/node creation, truncate, positioned I/O, pathconf, quotactl, and `openat`/`unlinkat`/related calls.

Filesystem/storage relevance: central kernel ABI glue for filesystem syscalls. Like `syscall.h`, it is generated from `syscalls.master` and should be changed by editing the generator input, not this file.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/syscallargs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/sysctl.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/sysctl.h

Sysctl hierarchy ABI, exported kernel data structs, and kernel sysctl helper declarations.

This header defines the integer-MIB sysctl namespace: top-level `CTL_*` nodes, type descriptors, name tables, and a large `CTL_KERN` subtree with process, vnode, file, mbuf, pool, SysV IPC, watchdog, timecounter, audio/video, CPU, PF, timeout, and autoconf entries. It also defines `KERN_PROC` filters, SysV IPC info selectors, process-argument selectors, media subtrees, witness controls, interrupt counters, watchdog controls, timecounter controls, clock interrupt stats, `CTL_HW` hardware identifiers, battery controls, and `CTL_DEBUG` layout.

The file defines public reporting structs `kinfo_proc`, `kinfo_vmentry`, and `kinfo_file`, including stable layout comments, process/thread identity, credentials, signal state, VM metrics, rusage, pledge, vnode/file/socket/pipe/kqueue fields, and filesystem mount/name data. Kernel/libkvm builds get `FILL_KPROC()` helpers for populating `kinfo_proc`.

Kernel builds expose the sysctl implementation ABI: `sysctlfn`, `sysctl_lock`, user-buffer locking, typed integer/string/struct/quad helpers, bounded integer helpers, process/file/route/socket queue dump helpers, and subsystem dispatchers for kern/hw/debug/net/cpu/vfs/SysV IPC/watchdog plus network submodules. Userland gets the `sysctl()` prototype.

Filesystem/storage relevance: very high. `CTL_VFS`, vnode/file counters, `KERN_FILE`, `KERN_NCHSTATS`, `KERN_NUMVNODES`, buffer-cache percentage, hardware disk names/stats/count, sensors, and process cwd/vmmap data all expose filesystem and storage state to userland.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/sysctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/syslimits.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/syslimits.h

Systemwide POSIX/BSD limit constants.

This header defines limits such as `ARG_MAX`, `CHILD_MAX`, `LINK_MAX`, `NAME_MAX`, `OPEN_MAX`, `PATH_MAX`, `PIPE_BUF`, `SYMLINK_MAX`, `SYMLOOP_MAX`, terminal/input limits, regex/utility limits, `IOV_MAX`, `TTY_NAME_MAX`, `LOGIN_NAME_MAX`, `HOST_NAME_MAX`, `GETENTROPY_MAX`, and `_MAXCOMLEN`.

Visibility macros gate POSIX, XPG, and BSD constants. Several values are directly ABI-significant for filesystem path parsing, link counts, descriptor defaults, symlink resolution, and pipe atomicity.

Filesystem/storage relevance: direct. `NAME_MAX`, `PATH_MAX`, `LINK_MAX`, `SYMLINK_MAX`, `SYMLOOP_MAX`, and `PIPE_BUF` are core VFS/userland contract limits.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/syslimits.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/syslog.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/syslog.h

Syslog priority/facility ABI and logging prototypes.

This header defines `/dev/log`, `LIOCSFD`, maximum log line size, priority constants, facility constants, priority/facility extraction macros, optional `SYSLOG_NAMES` lookup tables, `struct syslog_data`, mask macros, and `openlog()` option flags. Userland prototypes include regular and reentrant syslog APIs plus `sendsyslog()`.

Kernel builds define `LOG_PRINTF` and declare `logpri()`, `log()`, `addlog()`, and `logwakeup()` with kernel printf format checking.

Filesystem/storage relevance: diagnostic. Filesystem, VFS, and storage code use kernel logging paths for warnings and errors, while userland logging reaches `/dev/log`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/syslog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/systm.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/systm.h

Core kernel global declarations, syscall table shape, copy/print/memory helpers, sleep/wakeup APIs, hooks, network lock macros, and boot/root-device declarations.

This header declares global kernel state such as `securelevel`, panic/version strings, hardware identity, CPU/device counts, physical memory, dump/root/swap devices, root and swap vnodes, and the current process macro. It defines `struct sysent`, syscall handler type, `SY_NOLOCK`, endian-aware `SCARG()`, and optional syscall-debug declarations.

The function surface includes generic stubs, hash allocation, panic/assert/printf/uprintf/snprintf, spl assertions, table-full reporting, kernel/user copy helpers, memory routines, randomness, clock/profiling hooks, sleep queues, condition variables, wakeup/tsleep/msleep/rwsleep variants, watchdog hooks, startup hooks, `uiomove()`, network lock/assert macros, setjmp/longjmp, console/CPU configuration, disk/root mount selection, builtin memory macro mappings, DDB hooks, boot config hooks, and global kernel lock macros.

Filesystem/storage relevance: foundational. It declares root and swap device/vnode state, dump-device state, `diskconf()`, `mountroot`, `nfs_mountroot()`, `dk_mountroot()`, `uiomove()`, copyin/copyout, sleep/wakeup, securelevel policy affecting raw disks, and kernel lock/network lock primitives used by VFS, storage, and socket code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/systm.h -->