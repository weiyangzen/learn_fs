# Group Research: group_1410_openbsd_src_sources_os_bsd_openbsd_src_sys_sys_limits_h_sources_os__7ff7b1654b32

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/openbsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/limits.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/limits.h

Defines common scalar limits for OpenBSD user/kernel headers: character width, signed/unsigned integer extrema, `MB_LEN_MAX`, long/long-long limits, and BSD-visible `UID_MAX`/`GID_MAX`.

It includes machine-specific limits and conditionally exposes POSIX/XPG symbols such as `LONG_BIT`, `WORD_BIT`, and legacy floating-point limit aliases via `<machine/_float.h>`. Its main role in this subset is foundational ABI consistency for filesystem and kernel headers that depend on fixed type ranges.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/limits.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/lock.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/lock.h

Compatibility lock flag header mapping historical `LK_*` vnode lock flags onto `rwlock(9)` flags. It defines shared/exclusive lock modes, nonblocking acquisition, recursive-exclusive failure, and “exclusive held by other thread” status.

Adds LK-specific `LK_DRAIN` and `LK_RETRY`, used by VFS/vnode locking paths that still speak the older lock API.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/lock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/lockf.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/lockf.h

Kernel-only advisory record locking interface. It forward-declares `struct lockf_state` and exposes `lf_init`, `lf_advlock`, and `lf_purgelocks`.

This is the VFS-facing bridge for `fcntl`/advisory byte-range locks associated with files and vnodes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/lockf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/malloc.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/malloc.h

Defines OpenBSD kernel malloc flags, allocator sysctl IDs, memory accounting types, and allocator statistics structures. Flags include `M_WAITOK`, `M_NOWAIT`, `M_CANFAIL`, and `M_ZERO`.

The `M_*` type table is broad and includes many filesystem-relevant categories such as `M_MOUNT`, `M_VNODE`, `M_DQUOT`, `M_UFSMNT`, `M_MSDOSFSMNT`, `M_FUSEFS`, `M_UDFMOUNT`, and softdep allocation classes. `INITKMEMNAMES` maps these IDs to sysctl-visible names.

Kernel-only content defines `kmemstats`, `kmemusage`, `kmembuckets`, bucket sizing constants, address-to-kmem metadata macros, allocator globals, `malloc`, `mallocarray`, `free`, `sysctl_malloc`, and memory poisoning helpers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/malloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/mbuf.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/mbuf.h

Defines mbufs, OpenBSD’s packet buffer representation. It specifies mbuf and cluster sizing, `struct m_hdr`, packet headers, packet-filter metadata, external storage descriptors, the full `struct mbuf` layout, flags, checksum/offload bits, mbuf types, allocation macros, packet tag support, mbuf statistics, and queue/list helpers.

Kernel APIs cover allocation, freeing, header movement, copy/defrag/pullup/pulldown/split/append operations, external cluster management, packet tags, per-CPU statistics, and locked `mbuf_queue` operations.

Although network-centered, mbufs also appear in VFS export handling and socket/file interactions, making this header relevant to NFS/export and kernel I/O infrastructure.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/mbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/memrange.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/memrange.h

Defines `/dev/mem` memory range attribute controls. Public structures describe memory ranges by base, length, flags, and owner, with ioctl commands `MEMRANGE_GET` and `MEMRANGE_SET`.

Flags cover cacheability and firmware/fixed/active state, including write-combining support via `MEMRANGE_WC_RANGE`. Kernel content defines machine hooks through `mem_range_ops`, `mem_range_softc`, and attach/get/set/reload routines.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/memrange.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/mman.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/mman.h

Defines memory mapping ABI constants: `PROT_*`, `MAP_SHARED`, `MAP_PRIVATE`, `MAP_FIXED`, anonymous mappings, stack/conceal flags, `MAP_FAILED`, `madvise`/`posix_madvise` values, `minherit` modes, `msync` flags, and `mlockall` flags.

Userland prototypes include `mmap`, `mprotect`, `munmap`, `msync`, `mlock`, `munlock`, `madvise`, `minherit`, `mimmutable`, `mquery`, and POSIX shared memory APIs. Filesystems care about this interface for file-backed mappings and executable/write-permission policy.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/mman.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/mount.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/mount.h

Core VFS mount ABI and kernel mount interface. It defines `fsid_t`, file handles, export arguments, per-filesystem mount argument structures for UFS/MFS/ISO/NFS/MSDOS/NTFS/UDF/tmpfs/FUSE, NFS option flags, `statfs`, filesystem type names, `struct mount`, and mount flag bitmasks.

Kernel content defines VFS sysctl structures, buffer cache stats, `struct vfsops`, VFS dispatch macros, filesystem operation externs, NFS export radix structures, mount busying flags, global `mountlist`, mount allocation/ref/busy helpers, export lookup helpers, sync/shutdown/unmount paths, and VFS configuration lookup.

This is one of the central files in the group: it specifies the contract between filesystems and the OpenBSD VFS.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/mplock.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/mplock.h

Defines the machine-independent multiprocessor kernel lock when `__USE_MI_MPLOCK` is active. The lock tracks per-CPU ticket/depth state, global tickets/users, and optional WITNESS lock metadata.

Exports initialization, acquire/release, release-all, reacquire-count, and held-test routines, plus the global `kernel_lock`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/mplock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/msg.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/msg.h

System V message queue ABI and kernel implementation declarations. User-visible content defines `MSG_NOERROR`, `msgqnum_t`, `msglen_t`, `struct msqid_ds`, and `msgctl`/`msgget`/`msgsnd`/`msgrcv`.

Kernel content defines queued message and queue structures, queue lifecycle flags, reference macros, `msginfo` limits, sysctl export structure, default sizing constants, and `msginit`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/msg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/msgbuf.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/msgbuf.h

Defines the circular kernel message buffer layout used for kernel/console logs. `struct msgbuf` stores magic, read/write pointers, real buffer size, dropped-byte count, and the byte buffer.

Kernel declarations include default console buffer size, global message/console buffers, initialization routines, and `msgbuf_putchar`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/msgbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/mtio.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/mtio.h

Magnetic tape ioctl ABI. Defines operation requests (`struct mtop`), tape operations like rewind, write EOF, space records/files, erase, set block size/density, status structure `struct mtget`, device type constants, drive status bits, and tape ioctl command numbers.

Kernel-only content defines minor-device bit layout for unit, no-rewind, and density selection. This matters to device-special file ioctl handling.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/mtio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/mutex.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/mutex.h

Defines OpenBSD spinning mutexes: CPU-owned, non-recursive, IPL-raising locks for kernel mutual exclusion. The MI implementation stores owner, requested IPL, old IPL, and optional WITNESS metadata.

Provides initializers, lock-object flags, diagnostic assertions, initialization wrappers, `mtx_enter`, `mtx_enter_try`, `mtx_leave`, ownership checks, and DDB-specific mutex support.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/mutex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/namei.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/namei.h

Defines pathname lookup state. `struct nameidata` includes path source, dirfd, segment type, start/root directories, pledge/unveil requirements, result vnodes, symlink state, and embedded `componentname` passed to VOP lookup routines.

Kernel definitions include namei operations (`LOOKUP`, `CREATE`, `DELETE`, `RENAME`), lookup modifiers, cache flags, `NDINIT` helpers, name cache entry layout, lookup/cache APIs, unveil integration APIs, cache stats/sysctl names, and unveil permission bits.

This is a key VFS path-resolution header linking lookup, vnode cache behavior, pledge, and unveil.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/namei.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/param.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/param.h

Global OpenBSD system parameters and kernel utility macros. It declares BSD/OpenBSD version constants, includes base types and syslimits, defines process/file/path maxima, scheduler sleep priorities, device/block constants, block/page conversion macros, path and symlink limits, bit macros, rounding/min/max helpers, `offsetof`, `nitems`, and fixed-point CPU/load scaling constants.

Filesystem relevance is direct through `MAXBSIZE`, `DEV_BSIZE`, block conversion helpers, `MAXPATHLEN`, and common kernel constants used across VFS and storage code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/param.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/pciio.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/pciio.h

PCI device ioctl ABI. Defines PCI selector, config-space I/O, ROM access, VPD request, and VGA arbitration structures.

Ioctls include config read/write, masked read, ROM length/data retrieval, VGA get/set, and VPD retrieval. Useful for device nodes and storage/controller diagnostic tooling.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/pciio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/pclock.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/pclock.h

Defines a small producer-consumer generation lock `struct pc_lock`. Kernel APIs support initialization, single-producer enter/leave, multi-producer enter/leave, and consumer enter/leave validation.

Used by timing/accounting paths such as process CPU usage aggregation where readers need coherent snapshots without heavyweight locking.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/pclock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/percpu.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/percpu.h

Per-CPU memory and counter framework. Defines `struct cpumem`, iteration state, counter references, boot-memory initializers, allocation/free APIs, iteration APIs, and inline enter/leave helpers.

Counter helpers provide per-CPU increment/decrement/add/packet accounting with generation numbers on multiprocessor builds. Used by mbuf statistics and other scalable kernel counters.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/percpu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/pipe.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/pipe.h

Defines kernel pipe buffer and pipe endpoint state. `struct pipebuf` tracks circular buffer count/input/output/size/storage. `struct pipe` stores lock pointer, buffer, kqueue notes, timestamps, async I/O state, peer linkage, containing pair, state flags, and busy count.

Flags cover async I/O, read/write waiters, teardown, EOF, and exclusive I/O locking. Kernel entry point is `pipe_init`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/pipe.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/pledge.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/pledge.h

Defines pledge promise bitmasks, including filesystem/path promises (`rpath`, `wpath`, `cpath`, `dpath`), I/O/device domains, networking, process control, exec, ioctl classes, and `error` behavior. `PLEDGE_USERSET` marks bits userland may request.

When `PLEDGENAMES` is set, provides bit-to-string mappings. Kernel declarations expose syscall, namei, fd-passing, sysctl, chown, socket, ioctl, flock, fcntl, swapctl, kill, and PROT_EXEC validation hooks.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/pledge.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/poll.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/poll.h

Defines `pollfd_t`, `nfds_t`, standard poll event bits, `INFTIM`, and kernel-only `POLL_NOHUP`. Userland declarations expose `poll` and, when visible, `ppoll`.

This is part of the descriptor readiness ABI used by files, pipes, sockets, devices, and kqueue-related wakeup paths.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/poll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/pool.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/pool.h

Defines OpenBSD’s fixed-size item allocator and pool-cache statistics. Public/sysctl-visible structures report pool sizing, allocation counts, failures, page counts, idle pages, and per-CPU cache activity.

Kernel/libkvm content defines pool allocators, page-size capability encoding, `struct pool` with page lists, locks, object counts, hard limits, per-CPU caches, request queues, instrumentation, and physical memory constraints. Kernel APIs include pool init/destroy, low/high water settings, hard limits, constraints, get/put, async requests, wakeup, reclaim, prime, diagnostics, and DMA allocator wrappers.

This allocator backs many VFS/kernel objects including process, vnode-adjacent, and network allocations.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/pool.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/proc.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/proc.h

Defines OpenBSD process and thread core structures. It includes sessions, process groups, time-usage accounting, shared `struct process`, per-thread `struct proc`, process/thread flags, status values, PID/TID limits, fork/exit flags, global process lists, pools, lookup helpers, scheduler/process lifecycle APIs, credential refresh, single-threading controls, condition variables, CPU sets, and time-usage helpers.

`struct process` holds shared identity, credentials, fd table, vmspace, parent/child/group/session relationships, signal state, timers, rusage, pledge/unveil state, pinsyscall data, limits, and process metadata. `struct proc` holds per-thread run queue state, scheduler state, signal masks, credentials, profiling state, machine-dependent state, and debug/core fields.

Filesystem relevance includes current process credentials, fd tables, root/cwd interactions through other structures, pledge/unveil enforcement, syncer process declaration, and resource accounting.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/proc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/protosw.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/protosw.h

Defines protocol switch and socket protocol user-request interfaces. `struct pr_usrreqs` contains socket lifecycle and operation callbacks; `struct protosw` binds socket type, domain, protocol number, flags, packet/control hooks, user-request table, timers, init, and sysctl callback.

Also defines protocol flags, PRU request numbers/names, control-input commands, control-output command types, protocol lookup functions, domain/protocol switch externs, and inline wrappers for protocol operations with `EOPNOTSUPP` fallbacks where optional.

Relevant to filesystem work through sockets, NFS/export paths, and file descriptor readiness/I/O behavior.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/protosw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ptrace.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/ptrace.h

Defines ptrace request ABI: trace/read/write/continue/kill/attach/detach, memory I/O descriptor, event masks, process state reporting, thread iteration, and machine-dependent request inclusion.

Kernel declarations validate machine ptrace support and expose reparent/untrace, register read/write, PC setting, single-step, permission, and traced-process memory I/O helpers. Userland exposes `ptrace`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ptrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/queue.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/queue.h

Foundational intrusive collection macros for singly linked lists, lists, simple queues, XOR simple queues, tail queues, and singly linked tail queues. It defines head/entry types, initializers, traversal, safe traversal, insert, remove, replace, concat, first/next/last helpers, and optional debug invalidation.

This header underpins many structures in this group, including mounts, process lists, pool internals, mbuf tags/lists, name cache, and SysV IPC queues.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/queue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/radioio.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/radioio.h

Radio device ioctl ABI. Defines FM/TV frequency/channel bounds, IF frequency, `struct radio_info`, capability bits, status bits, tuner modes, channel fields, and ioctls to get/set device info or start hardware search.

Primarily a character-device control header.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/radioio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/reboot.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/reboot.h

Defines reboot/boot flags passed across reboot paths, including halt, nosync, dump, powerdown, reset, random-seed, unhibernate, and confidential VM boot flags.

Also defines historical boot device encoding/decoding macros for type, adaptor, controller, unit, and partition, plus kernel `reboot` and `boot` declarations.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/reboot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/refcnt.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/refcnt.h

Small atomic reference counter abstraction. `struct refcnt` stores reference count and optional tracing index, with initializer and kernel APIs for init, traced init, take, release, release+wake, finalize, read, and shared-test.

Used by mount, process resource, semaphore, and other kernel lifetime-managed objects.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/refcnt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/resource.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/resource.h

Defines process priority constants, `getrusage` selectors, `struct rusage`, resource limit IDs, `RLIM_INFINITY`, `struct rlimit`, and BSD load average structure.

Kernel declarations expose average runnable load, `dosetrlimit`, `donice`, and `dogetrusage`; userland declarations expose priority, rlimit, and rusage syscalls. Filesystem relevance includes `RLIMIT_FSIZE`, `RLIMIT_NOFILE`, and block I/O usage accounting fields.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/resource.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/resourcevar.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/resourcevar.h

Kernel resource-limit internals. `struct plimit` stores the process rlimit array with a reference count for copy-on-write sharing after fork.

Defines profiling completion macro `ADDUPROF`, profiling/time accounting functions, time-usage aggregation helpers, rusage calculation, limit startup/free/fork/read helpers, inline `lim_cur`, per-proc limit lookup, rusage addition, and periodic resource checks.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/resourcevar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/rwlock.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/rwlock.h

Defines sleepable reader/writer locks and recursive rwlocks. The main `struct rwlock` stores encoded owner/reader count, waiter/read counters, name, WITNESS metadata, and trace index.

Provides lock-object flags, initializers, owner/count bit layout, read/write/downgrade/upgrade flags, nonblocking/interruptible/recurse behavior, diagnostic assertions, enter/exit/status APIs, recursive `rrwlock` APIs, and allocated reference-counted rwlock object helpers.

This lock type backs VFS mount locks, vnode-related locking flags via `lock.h`, and broader kernel synchronization.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/rwlock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/sched.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/sched.h

Scheduler and CPU accounting header. Defines CPU state indexes, `struct cpustats`, and kernel per-CPU scheduler state containing idle proc, run queues, dead proc queue, runtime, scheduler flags, clock interrupt handles, run counts, queue bitmaps, spin state, SMR deferred work, and current priority.

Kernel APIs cover scheduler clocking, round-robin handling, scheduler initialization, CPU initialization, idle/exit/switch paths, CPU choice, online/blocking sysctls, secondary CPU start/stop, run queue operations, wait chargeback, yield pause, and scheduler lock macros.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/sched.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/scsiio.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/scsiio.h

SCSI generic ioctl ABI. Defines command/sense buffer lengths, `scsireq_t` with command, user data buffer, lengths, sense data, status, return status, and error fields.

Flags identify read/write/iovec/escape/target requests; return statuses cover OK, timeout, busy, sense, and unknown. Ioctls include command execution, debug setting, reset, identify, probe, and detach. Relevant to block/storage device access.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/scsiio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/select.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/select.h

Defines `select`/`pselect` ABI support: `timeval`, `timespec`, `FD_SETSIZE`, internal fd mask type, `fd_set`, `FD_SET`, `FD_CLR`, `FD_ISSET`, `FD_ZERO`, BSD-visible `FD_COPY` and mask macros, and userland prototypes.

This is central descriptor readiness plumbing for files, pipes, sockets, and devices.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/select.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/selinfo.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/selinfo.h

Defines `struct selinfo`, the small kernel structure used to track processes/knotes waiting for I/O readiness. It contains a `klist` of notes.

Kernel API exposes `selwakeup`, used by selectable objects such as pipes, devices, sockets, and filesystem-backed descriptors to signal readiness changes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/selinfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/sem.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/sem.h

System V semaphore ABI and kernel declarations. Public content defines semaphore sysctl names, `struct sem`, `struct semid_ds`, `struct sembuf`, `SEM_UNDO`, `union semun`, `semctl` commands, and semaphore permissions.

Kernel content defines maximum values, internal `semid_ds_kern` with reference count, per-process undo structure, `seminfo`, sysctl export layout, default configuration constants, semaphore array extern, initialization/exit/sysctl functions, and userland `semctl`, `semget`, and `semop` declarations.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/sem.h -->