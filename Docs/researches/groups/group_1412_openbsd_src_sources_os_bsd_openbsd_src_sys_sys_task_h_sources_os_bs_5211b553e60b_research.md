# Group Research: group_1412_openbsd_src_sources_os_bsd_openbsd_src_sys_sys_task_h_sources_os_bs_5211b553e60b

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/task.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/task.h

Defines the OpenBSD kernel task queue interface. `struct task` contains a TAILQ link, callback, argument, flags, and an NKCOV process pointer. The only task state flag here is `TASK_ONQUEUE`.

Kernel-only declarations expose the global task queues `systq` and `systqmp`, creation/destruction, barriers, setup, enqueue, delete, and `task_pending()`. `TASKQ_MPSAFE` marks queues that can run without the big kernel lock. This is a small deferred-work API, comparable to timeouts but for queued callback execution rather than time-based scheduling.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/task.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/termios.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/termios.h

Defines the POSIX/BSD terminal attribute ABI: control-character indexes, input/output/control/local flags, baud constants, and `struct termios`. Visibility is controlled by `__BSD_VISIBLE`, `__XPG_VISIBLE`, and `_KERNEL`.

Userland declarations include `tcgetattr`, `tcsetattr`, `tcdrain`, `tcflow`, `tcflush`, `tcsendbreak`, speed helpers, `tcgetsid`, and BSD helpers `cfmakeraw`/`cfsetspeed`. Under BSD visibility it also includes `sys/ttycom.h` and, after the include guard, `sys/ttydefaults.h`, so default terminal state macros are available to BSD consumers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/termios.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/time.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/time.h

Defines `timeval`, `timespec`, `timezone`, interval timers, timeval/timespec arithmetic macros, and userland time-related prototypes. Kernel/standalone/libc paths add `struct bintime` and inline conversions among binary fractional time, nanoseconds, microseconds, `timespec`, and `timeval`.

Kernel/standalone declarations expose clock read APIs (`bintime`, `nanotime`, uptime/boottime/runtime variants), `clock_gettime`, interval timer maintenance, `settime`, rate checks, calendar conversion, BCD helpers, and saturated nanosecond conversion helpers. Filesystem code commonly depends on this through `timespec` in vnode attributes and inode timestamps.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/time.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/timeout.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/timeout.h

Declares the kernel timeout/callout structure. `struct timeout` stores circular queue linkage, absolute target time, callback, argument, optional KCOV process, tick time, flags, and kernel clock id.

Flags distinguish initialized, queued, triggered, process-context, and MPSAFE timeouts. Kernel API covers setup, relative add in ticks/sec/msec/usec/nsec, absolute `timespec` scheduling, deletion, deletion barriers, global barriers, clock adjustment, hardclock update, and startup. This is the timed deferred-callback primitive used by subsystems such as tty restart handling.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/timeout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/times.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/times.h

Defines the POSIX `struct tms` CPU accounting result for `times(3)`: user/system CPU time for the process and terminated children. It defines `clock_t` via `sys/_types.h` if not already present.

Outside the kernel it declares `clock_t times(struct tms *)`. This header is pure ABI surface with no kernel implementation details beyond avoiding the userland prototype under `_KERNEL`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/times.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/timetc.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/timetc.h

Defines the kernel/libc timecounter interface and rejects ordinary userland inclusion. `struct timecounter` describes hardware counters through a read callback, mask, frequency, quality, name, private pointer, user exposure flag, list linkage, frequency adjustment, and computed precision.

`struct timekeep` is the shared timekeeping data layout with generation, scale, offsets, boottime, naptime, and counter mask/user flags. Exports include `tc_init`, quality reset, setclock, realtime clock set, tick processing, sysctl, frequency/time adjustment, and global `timecounter`, `timekeep_object`, and `timekeep`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/timetc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/tprintf.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/tprintf.h

Declares terminal-targeted kernel printf support. `tpr_t` is a session pointer wrapper. The API opens a target from a `struct proc`, closes it, and prints formatted kernel messages through `tprintf`.

The `tprintf` prototype carries a `__kprintf__` format attribute, giving compile-time format checking for kernel-style format strings.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/tprintf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/tracepoint.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/tracepoint.h

Provides kernel tracepoint macros. When `_KERNEL` and `NDT > 0`, it includes DTrace-style `dtvar.h` and maps `TRACEPOINT`/`TRACEINDEX` to static/indexed DT enter macros.

When dynamic tracing is not built, both macros compile away. This lets kernel code keep trace hooks without runtime or build-time dependencies when tracing support is absent.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/tracepoint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/tree.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/tree.h

Defines generic intrusive tree APIs: macro-generated splay trees, macro-generated red-black trees, and a newer runtime-described red-black tree wrapper family. The splay API provides heads, entries, rotations, insertion, removal, find, next, min/max, and foreach traversal.

The classic `RB_*` macros generate type-specialized red-black insert/remove/find/near-find/next/prev/min/max functions with optional `RB_AUGMENT`. The later `RBT_*` API uses `struct rb_type`, `struct rb_tree`, and `struct rb_entry` plus helper functions such as `_rb_insert`, `_rb_remove`, `_rb_find`, and poisoning/checking helpers. This file underpins many kernel indexed containers, including vnode buffer and namecache trees.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/tree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/tty.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/tty.h

Defines core tty kernel state plus a small amount of public ABI. It includes `termios`, queues, select state, and timeouts. Public pieces include tty sysctl ids, `struct ptmget`, `PTMGET`, `/dev/ptm`, and tty group id.

`struct tty` holds raw/canonical/output clists, statistics, device id, state/flags, foreground process group/session, select state, termios, window size, driver callbacks, watermarks, restart timeout, and timestamp. Kernel declarations cover clist operations, tty read/write/ioctl/open/close, wakeups, line editing, flow/modem handling, controlling tty operations, PPP/NMEA/MSTS/EndRun line discipline hooks, and tty allocation/free.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/tty.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ttycom.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/ttycom.h

Defines tty ioctl ABI constants and small structures. `struct winsize` stores rows/columns/pixel size; `struct tstamps` controls timestamp reasons.

The ioctl set covers exclusivity, flushing, termios get/set, line discipline get/set, break/DTR/modem controls, process group/session, pty packet mode, remote mode, window size, user control mode, status, console/control tty, external processing, signal generation, drain, device flags, and timestamping. It also defines modem bit constants and line discipline numeric ids.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ttycom.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ttydefaults.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/ttydefaults.h

Defines system-wide default terminal flags and control characters. Defaults enable common canonical input, echo, signals, extended processing, output post-processing, and 9600 baud.

If `TTYDEFCHARS` is defined before inclusion, the file emits a `ttydefchars[NCCS]` initializer array and then undefines `TTYDEFCHARS`. This conditional definition pattern is intentional but means the header can emit storage in exactly the translation unit that requests it.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ttydefaults.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/types.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/types.h

Central OpenBSD system type header. It defines BSD aliases (`u_char`, `u_int`, etc.) under `__BSD_VISIBLE`, exact-width integer types, BSD `u_int*_t`, deprecated quad types, VM address/size types, and core POSIX/system types such as `dev_t`, `ino_t`, `uid_t`, `gid_t`, `off_t`, `time_t`, `clock_t`, and `pid_t`.

Under BSD userland visibility it declares `lseek`, `ftruncate`, and `truncate` to ensure `off_t` promotion. It also provides `major`, `minor`, and `makedev`. Kernel mode gets common forward declarations and a `bool` definition backed by `_Bool`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ucred.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/ucred.h

Defines kernel credentials. `struct ucred` contains a refcount and copied credential fields: effective/real/saved uid and gid plus supplementary groups. `cr_startcopy` marks the first field copied by `crset`.

`struct xucred` is the userspace/syscall credential shape. Kernel APIs allocate, hold, copy, duplicate, set, free, convert from `xucred`, and check superuser privileges. `NOCRED` and `FSCRED` are sentinel credential pointers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ucred.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/uio.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/uio.h

Defines vectored I/O structures. Public `struct iovec` contains base pointer and length. BSD-visible enums identify read/write direction and user/system address space; kernel `struct uio` adds iovec array, count, file offset, residual bytes, segment flag, direction, and associated process.

Userland prototypes include `readv`, `writev`, and BSD `preadv`/`pwritev`. Kernel prototypes include `ureadc`, iovec copy/free helpers, and file readv/writev syscall helpers. VFS and tty paths use this as the standard scatter/gather I/O carrier.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/uio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/un.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/un.h

Defines UNIX-domain socket address ABI. `struct sockaddr_un` has a length byte excluding NUL, address family, and 104-byte path.

BSD userland gets `SUN_LEN(su)`, computing the actual initialized address length from the path string. Kernel code only needs the structure definition here.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/un.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/unistd.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/unistd.h

Defines POSIX constants used by `unistd.h` and kernel/user ABI consumers: `_POSIX_VERSION`, `_POSIX_VDISABLE`, unsupported async/prio/sync I/O indicators, access mode bits, seek constants, and pathconf variable ids.

BSD visibility adds legacy `L_SET`/`L_INCR`/`L_XTND`, `struct __tfork`, `struct __kbind`, and kbind size limits. The pathconf ids are explicitly ABI-stable.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/unistd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/unpcb.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/unpcb.h

Defines UNIX-domain socket protocol control blocks. `struct unpcb` links a socket to an optional filesystem vnode, connected peer, referrer list, bound address, file backpointer for GC, fake inode, peer credentials, creation time, and per-AF socket list. Lock annotations identify immutable, socket-lock, and GC-lock protected fields.

Kernel declarations cover attach/detach, bind/listen/connect/accept/disconnect/shutdown/send/receive, address queries, socket stat, peer connection, garbage collection, and internalize/externalize/dispose of file descriptors in control messages. This is a key socket/VFS bridge because pathname sockets hold vnode references.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/unpcb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/user.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/user.h

Defines the minimal historical per-process `struct user`, now containing only the machine PCB. It includes machine PCB and resource headers.

The comments preserve the older swapped-process model, but this OpenBSD version is a very small architecture/process context wrapper rather than a broad process metadata store.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/user.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/utsname.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/utsname.h

Defines `SYS_NMLN` and the POSIX `struct utsname` fields: system name, node name, release, version, and machine, each 256 bytes.

Outside the kernel it declares `uname(struct utsname *)`. This is stable userland ABI with no filesystem-specific behavior.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/utsname.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/uuid.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/uuid.h

Defines DCE-style UUID layout: 32-bit low time, 16-bit mid time, version/time high, clock sequence bytes, and 6-byte node. It also defines internal node and printed-buffer lengths.

Kernel mode exposes `UUID_NODE_LEN`, `UUID_BUF_LEN`, `uuid_snprintf`, and `uuid_printf`; userland typedefs `struct uuid` as `uuid_t`. Useful for filesystem metadata formats that store UUIDs, though this file itself is format-generic.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/uuid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/varargs.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/varargs.h

Implements traditional pre-ANSI varargs macros for GNU C. It maps `va_alist`, `va_dcl`, `va_start`, `va_end`, `va_arg`, and `__va_copy` to compiler builtins and defines `va_list`.

This is legacy compatibility surface. New code should normally use `stdarg.h`, but this header preserves K&R-style varargs consumers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/varargs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/vmmeter.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/vmmeter.h

Defines system-wide VM and fork accounting structures. `struct vmtotal` records run queue, disk/page wait, sleeping/swapped runnable counts, virtual/real memory totals, shared memory counts, and free pages.

`struct forkstat` records counts and affected page totals for `fork`, `vfork`, `__tfork`, and kernel threads. The file also defines sysctl ids and names for fork stats.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/vmmeter.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/vnode.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/vnode.h

Defines the OpenBSD vnode core. `struct vnode` tracks UVM state, VOP table, vnode type/tag, flags, reference/write/hold counts, mount linkage, buffer trees/lists, sync list, type-specific union, namecache trees, filesystem-private data, and kqueue pollers. Vnode tags include `VT_EXT2FS`, which ext2fs uses.

Also defines `struct vattr`, I/O flags, mode bits, `VNOVAL`, vnode lifecycle flags, and bio flags. Kernel sections declare `struct vops`, all VOP argument structures and wrapper prototypes, global vnode state, type/mode conversion tables, and public vnode/VFS helpers such as `getnewvnode`, `vaccess`, `vflush`, `vget`, `vgone`, `vinvalbuf`, `vrele`, `vref`, `vn_open`, `vn_rdwr`, `vn_stat`, `vn_lock`, syncer helpers, and UVM vnode size/cache hooks.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/vnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/wait.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/wait.h

Defines wait status encoding macros and wait option bits. It exposes `WIFSTOPPED`, `WSTOPSIG`, `WIFSIGNALED`, `WTERMSIG`, `WIFEXITED`, `WEXITSTATUS`, `WIFCONTINUED`, and XPG core-dump/status construction helpers.

Options include `WNOHANG`, `WUNTRACED`, `WCONTINUED`, POSIX `WEXITED`, `WSTOPPED`, `WNOWAIT`, and `WTRAPPED`; POSIX visibility also defines `idtype_t`. Userland prototypes include `wait`, `waitpid`, `waitid`, and BSD `wait3`/`wait4`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/wait.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/witness.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/witness.h

Defines lock-order debugging support. It maps lock objects to lock classes, defines generic lock-operation flags, and defines assertion flags such as locked, unlocked, shared, exclusive, recursed, and not-recursed.

Kernel prototypes cover witness initialization, lock init/order checking, lock/unlock/upgrade/downgrade tracking, relative ordering, warnings, assertions, spinlock display, no-release/release-ok marking, thread exit, and sysctls. When `WITNESS` is disabled, the public `WITNESS_*` macros compile to no-ops or neutral return values.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/witness.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/xcall.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/xcall.h

Defines the CPU crosscall API. `struct xcall` wraps a function and argument; `struct xcall_cpu` holds four pending xcall slots and a soft interrupt handle for each CPU.

The header documents the MD integration requirements: CPU device dependency, `cpu_info` member, establish call, MD IPI hook, and dispatch at `IPL_SOFTCLOCK`. Kernel API sets an xcall, sends one to a CPU, synchronously runs a callback on a CPU, establishes per-CPU state, and dispatches pending calls.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/xcall.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs.h

Defines ext2/ext3/ext4-compatible on-disk superblock structures and in-memory mount-derived state. `struct ext2fs` mirrors the superblock, including classic ext2 fields and many ext4-era fields; `struct m_ext2fs` stores computed block size, shifts/masks, group descriptor count, inode table layout, max file size, and loaded group descriptors.

The header defines supported feature masks: this implementation supports sparse super and large files as RO-compatible features and filetype as an incompatible write-capable feature, while several ext4 incompat flags are tolerated only for read-only handling. It also defines group descriptors, sparse-super group selection, byte-swap/load/save macros, block/device conversion macros, inode/block group calculations, block offset/rounding helpers, free-space calculation, and `NINDIR`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_alloc.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_alloc.c

Implements ext2 block and inode allocation/freeing. `ext2fs_alloc` checks global free space and reserved blocks, chooses a cylinder group from block preference or inode group, and delegates to `ext2fs_hashalloc`; successful allocation updates inode block count and change/update flags. `ext2fs_inode_alloc` chooses a group, allocates an inode bitmap bit, obtains the vnode with `VFS_VGET`, verifies it is unused, clears the dinode, and assigns a generation number.

Allocation policy uses preferred group, quadratic rehash, then brute-force group search. `ext2fs_alloccg` reads the block bitmap, honors a preferred bit when possible, searches for a free byte/bit, marks it allocated, updates superblock/group free counts, and delayed-writes the bitmap. `ext2fs_nodealloccg` does the same for inode bitmaps and directory counts. Free paths validate ranges/double-free cases, clear bitmap bits, and update counters. Corrupt bitmaps trigger panics.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_balloc.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_balloc.c

Allocates physical storage for a file logical block. `ext2fs_buf_alloc` handles direct blocks first: if present it reads the block; if absent it chooses a preference, allocates a block, records it in `i_e2fs_blocks`, marks inode change/update, gets a buffer, sets disk block number, and optionally clears it.

For indirect blocks it uses `ufs_getlbns`, allocates missing indirect blocks synchronously so metadata never points at garbage, wires the chain, and then allocates or returns the requested data block. On failure it frees newly allocated blocks, unwinds indirect pointers, invalidates cached indirect buffers, and adjusts block accounting. This file only handles classic block maps, not ext4 extent-tree allocation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_bmap.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_bmap.c

Implements VOP block mapping for ext2fs. `ext2fs_bmap` returns the underlying device vnode when requested, then maps logical to physical blocks through either ext4 extents or classic direct/indirect block arrays depending on the inode `EXT4_EXTENTS` flag.

`ext4_bmapext` finds the covering extent and computes the physical block. `ext2fs_bmaparray` uses `ufs_getlbns`, direct inode block pointers, and indirect block traversal to resolve disk addresses; it reads indirect blocks as needed, recognizes cache-resident metadata, returns `-1` for holes, and computes sequential run length for clustering.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_bswap.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_bswap.c

Provides big-endian byte-swap helpers for ext2 metadata, which is little-endian on disk. On little-endian systems these helpers are not built because header macros use `memcpy`.

For big-endian builds, `e2fs_sb_bswap` copies the superblock then swaps selected superblock fields, `e2fs_cg_bswap` swaps group descriptor arrays, and `e2fs_i_bswap` swaps dinode fields and copies block pointers. The dinode helper only swaps extra inode size if the filesystem inode size exceeds the rev0 size; it does not fully swap every ext4 extra timestamp/checksum field.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_bswap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_dinode.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_dinode.h

Defines ext2 on-disk inode layout and inode constants. Reserved inode numbers include root inode 2, resize inode 7, and first normal inode 11. `NDADDR` is 12 and `NIADDR` is 3, matching the classic direct/single/double/triple indirect pointer layout.

`struct ext2fs_dinode` contains mode, uid/gid low/high, size low/high, timestamps, deletion time, link count, block count, flags, version, block pointers, generation, ACL fields, checksum fields, extra inode size, extra timestamps, creation time, and high version bits. Macros define ext2 mode bits, file types, inode flags such as immutable/append/extents/huge-file, inode size selection, device/short-symlink overlays, and endian load/save helpers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_dinode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_dir.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_dir.h

Defines ext2 directory entry layout and helper types. `struct ext2fs_direct` stores inode, record length, name length, file type, and max 255-byte name. `struct ext2fs_searchslot` records directory insertion/free-space search state.

The file defines ext2 directory file type ids, `inot2ext2dt()` conversion from inode mode type to ext2 directory type, `EXT2FS_DIRSIZ()` record size rounding, max directory size, and `struct ext2fs_dirtemplate` for `.` and `..` initialization.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_extents.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_extents.c

Implements read-side ext4 extent lookup helpers. Static binary searches find the applicable index entry at internal levels or extent entry at leaf level. `ext4_ext_in_cache` checks the inode extent cache and materializes a cached extent; `ext4_ext_put_cache` stores an extent start/logical range/type in the inode cache.

`ext4_ext_find_extent` starts from the inode-embedded extent header, validates magic, descends through index blocks with `bread`, releases previous path buffers while descending, and returns a path whose `ep_ext` points at the selected leaf extent. It returns `NULL` on bad magic or read failure. No extent mutation or allocation is implemented here.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_extents.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_extents.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_extents.h

Defines ext4 extent on-disk structures used by the ext2fs driver. It includes extent magic, cache status values, `struct ext4_extent`, `struct ext4_extent_index`, `struct ext4_extent_header`, `struct ext4_extent_cache`, and `struct ext4_extent_path`.

The exported API is limited to extent cache check/store and extent path lookup. This reinforces that extents are supported for mapping existing files, while classic ext2 block allocation remains separate.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_extents.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_extern.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_extern.h

Central external declaration header for ext2fs. It forward-declares kernel/VFS types, exports inode/dinode pools, and declares functions from allocation, block allocation, bmap, inode, lookup, subr, vfsops, readwrite, and vnops modules.

Important integration points include VFS mount/unmount/statfs/sync/vget/fh conversion/superblock update, VOP implementations for create/remove/link/rename/mkdir/rmdir/symlink/readlink/access/getattr/setattr/fsync/reclaim, and `IS_EXT2_VNODE(vp)` based on `VT_EXT2FS`. It also exports ext2fs vnode operation tables for regular, special, and FIFO vnodes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_extern.h -->