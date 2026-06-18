# Group Research: group_311_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_vfs_vnops_c_source_31fb6bd2641a

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. Every listed source file was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_vnops.c

Read completely: 1352 lines.

This file implements DragonFlyBSD's file-object-facing vnode operations. It provides `vnode_fileops` methods for open-backed file descriptors: read, write, ioctl, kqueue filter, stat, close, and seek.

Key responsibilities:
- `vn_open()` performs namecache lookup, create/open/truncate handling, permission/write checks, vnode locking, FUSE flag propagation, `VOP_NCREATE`, `VOP_OPEN`, and file pointer setup.
- `vn_rdwr()` and `vn_rdwr_inchunks()` package kernel read/write requests into `uio` structures, optionally splitting large I/O to avoid buffer-cache pressure.
- `vn_read()` and `vn_write()` translate file flags into VOP I/O flags, serialize shared file offsets with `FOFFSETLOCK`, apply sequential access heuristics, and call `VOP_READ_FP`/`VOP_WRITE_FP`.
- `vn_stat()` converts `vattr` data into `struct stat`, including device vnode timestamps, block size selection, generation-number privilege filtering, and ABI compatibility fields.
- `vn_ioctl()` handles generic vnode ioctls such as `FIONREAD`, `FIOASYNC`, `FIODTYPE`, forwards to `VOP_IOCTL`, and updates controlling tty state after `TIOCSCTTY`.
- `vn_lock()`, `vn_unlock()`, `vn_islocked*()` centralize vnode lock behavior and reclaimed-vnode checks.
- `vn_bmap_seekhole*()` implements `FIOSEEKHOLE`/`FIOSEEKDATA` through `VOP_BMAP`.
- `vn_seek()` implements `lseek`, including `SEEK_DATA` and `SEEK_HOLE`.

Important interactions:
- Depends on namecache/nlookup state, `VOP_*` vnode operations, mount write checks, quotas/accounting, file descriptor state, and buffer-cache backpressure helpers.
- `vn_open()` transfers `nd->nl_nch` into `fp->f_nchandle` when a file pointer is supplied.
- Write/truncate paths use both namecache-level `ncp_writechk()` and vnode-level `vn_writechk()` to account for nullfs/cross-mount cases.

Security/reliability notes:
- Open/create correctness depends on careful vnode/namecache lock handoff and ESTALE retry behavior.
- Offset serialization intentionally allows some heuristic races but protects `f_offset` integrity for normal shared-file reads/writes.
- Negative offsets are rejected for regular files and directories but allowed for special devices for 64-bit kvm-style address use.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_vopops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_vopops.c

Read completely: 2227 lines.

This file implements the vnode operation wrapper layer. All DragonFlyBSD VOP calls pass through these wrappers, which construct argument objects, select vnode operation descriptors, acquire legacy MP locks when needed, and dispatch into filesystem-specific operation tables.

Key responsibilities:
- Defines `syslink_desc` descriptors for every vnode op through `VNODEOP_DESC_INIT`.
- Wraps old path-based operations: lookup, create, whiteout, mknod, remove, link, rename, mkdir, rmdir, and symlink.
- Wraps primary vnode operations: open, close, access, getattr, setattr, read, write, ioctl, poll, kqfilter, mmap, fsync, fdatasync, readdir, readlink, inactive, reclaim, bmap, strategy, pathconf, advlock, balloc, pages, ACLs, extended attributes, mountctl, markatime, and allocate.
- Wraps the newer namecache API: nresolve, nlookupdotdot, ncreate, nmkdir, nmknod, nlink, nsymlink, nwhiteout, nremove, nrmdir, and nrename.
- Provides forwarding helpers for passthrough filesystems, cache-coherency dispatch, and journaling dispatch.
- Provides `_ap` forms that dispatch an already-built argument structure.

Important behavior:
- Most wrappers use `VFS_MPLOCK()` or `VFS_MPLOCK_FLAG()` to acquire the giant MP lock only for non-MPSAFE mounts or operation classes.
- `vop_open()` ages vnodes back toward active use by clearing/decrementing `VAGE*` flags.
- `vop_write()` performs quota pre-checks for regular files, estimates append growth, and updates VFS space accounting after success.
- `vop_nremove()` records attributes before deletion and subtracts file size from accounting when the removed object had one hard link.
- `vop_strategy()` has a special no-mount fallback for swap.

Security/reliability notes:
- This is a central ABI/locking boundary between generic VFS code and filesystem implementations.
- Quota/accounting estimates in `vop_write()` are based on pre-write size and requested length; unusual filesystem write semantics can make accounting approximate.
- Reclaim/inactive wrappers explicitly account for operations that can clear `vp->v_mount`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_vopops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_clock_id.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/_clock_id.h

Read completely: 57 lines.

This small public header defines POSIX clock IDs and timer flags under feature-test visibility guards.

Key contents:
- POSIX clocks: `CLOCK_REALTIME`, `CLOCK_MONOTONIC`, `CLOCK_THREAD_CPUTIME_ID`, and `CLOCK_PROCESS_CPUTIME_ID`.
- BSD/FreeBSD-derived clocks: `CLOCK_VIRTUAL`, `CLOCK_PROF`, uptime/realtime/monotonic precise and fast variants, and `CLOCK_SECOND`.
- Timer flags: BSD `TIMER_RELTIME` and POSIX `TIMER_ABSTIME`.

Security/reliability notes:
- No runtime logic. The main compatibility issue is that constants are only exposed when the relevant `__POSIX_VISIBLE`/`__BSD_VISIBLE` guards allow them.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_clock_id.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_fd_set.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/_fd_set.h

Read completely: 86 lines.

This header defines the `fd_set` type and classic `select(2)` bitset macros.

Key contents:
- Default `FD_SETSIZE` of 1024.
- `__fd_mask`, `__NFDBITS`, and `fd_set`.
- `FD_SET`, `FD_CLR`, `FD_ISSET`, `FD_ZERO`, and BSD-visible aliases such as `fd_mask`, `NFDBITS`, `howmany`, and `FD_COPY`.

Security/reliability notes:
- The macros do not bounds-check descriptor indexes; callers must ensure `0 <= fd < FD_SETSIZE`.
- `FD_ZERO` and `FD_COPY` use compiler builtins for fixed-size struct clearing/copying.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_fd_set.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_iovec.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/_iovec.h

Read completely: 48 lines.

This header defines the public `struct iovec` used by vectored I/O APIs.

Key contents:
- Declares `size_t` from machine types if not already declared.
- Defines `struct iovec` with `void *iov_base` and `size_t iov_len`.

Security/reliability notes:
- No runtime behavior. Its layout is ABI-sensitive for `readv`, `writev`, `uio`, and related kernel/user interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_iovec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_malloc.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/_malloc.h

Read completely: 180 lines.

This kernel-structure header defines DragonFlyBSD kmalloc slab allocator metadata and malloc-type accounting structures.

Key contents:
- Slab constants such as `KMALLOC_SLAB_SIZE`, `KMALLOC_SLAB_MAGIC`, and `KMALLOC_MAXFREEMAGS`.
- `struct kmalloc_slab` with lock state, type pointer, object size/count, circular free-object indices, existential lock state, bitmap, and free object array.
- `struct kmalloc_mgt` for per-CPU and global slab lists.
- `struct kmalloc_use` for per-CPU usage statistics and local object storage.
- `struct malloc_type`, `malloc_type_t`, `MALLOC_DECLARE`, allocator flags, and `KMGlobalData`.

Important interactions:
- Intended only for `_KERNEL` or `_KERNEL_STRUCTURES`, especially consumers like `sys/user.h`.
- Uses spinlocks, exislocks, cache alignment, and SMP CPU sizing.

Security/reliability notes:
- This is allocator-internal ABI. Incorrect structure layout or flag interpretation can corrupt kernel memory accounting and slab free lists.
- Double-free checking is enabled by `KMALLOC_CHECK_DOUBLE_FREE`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_malloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_null.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/_null.h

Read completely: 41 lines.

This header defines `NULL` if it is not already defined.

Key behavior:
- In C, `NULL` is `((void *)0)`.
- In GNU C++ 4+, `NULL` is `__null`.
- Otherwise, C++ receives integer `0`.

Security/reliability notes:
- No runtime behavior. The conditional definitions preserve C/C++ compatibility and avoid redefining existing `NULL`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_null.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_pthreadtypes.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/_pthreadtypes.h

Read completely: 81 lines.

This header provides namespace-light pthread type declarations.

Key contents:
- Forward declarations for internal pthread object structs.
- Opaque pointer typedefs for thread, attributes, barriers, conditions, mutexes, rwlocks, and spinlocks.
- `pthread_key_t` as `int`.
- `pthread_once_t` as a partly public `struct __pthread_once_s` with state and ABI spare pointer.

Security/reliability notes:
- No executable logic. ABI stability matters because public pthread types are used in many libc and application interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_pthreadtypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_siginfo.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/_siginfo.h

Read completely: 142 lines.

This header defines POSIX/XSI signal payload types and `si_code` constants.

Key contents:
- Declares `pid_t` and `uid_t` if needed.
- Defines `union sigval`.
- Defines generic `SI_*` codes and signal-specific codes for `SIGILL`, `SIGFPE`, `SIGSEGV`, `SIGBUS`, `SIGTRAP`, `SIGCHLD`, and `SIGPOLL`.
- Defines `siginfo_t` with signal number, errno, code, sender pid/uid, status, fault address, signal value, band event, and spare fields.

Security/reliability notes:
- No runtime logic. Layout and visibility are ABI-sensitive for signal delivery, `sigqueue`, timers, async I/O, and user handlers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_siginfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_sigset.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/_sigset.h

Read completely: 41 lines.

This header defines the internal signal-set storage type.

Key contents:
- `_SIG_WORDS` is 4.
- `struct __sigset` contains four unsigned integer words.

Security/reliability notes:
- No runtime logic. The fixed storage size is ABI-sensitive for signal masks and contexts.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_sigset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_termios.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/_termios.h

Read completely: 236 lines.

This header defines terminal control constants and `struct termios`.

Key contents:
- Control character indexes such as `VEOF`, `VERASE`, `VINTR`, `VSUSP`, `VMIN`, and `VTIME`, with BSD extensions under visibility guards.
- Input, output, control, and local flag bit definitions.
- Standard speed constants from `B0` through BSD high-speed values.
- Typedefs `tcflag_t`, `cc_t`, and `speed_t`.
- `struct termios` with input/output/control/local flags, control character array, and input/output speeds.
- BSD `CCEQ()` helper.

Security/reliability notes:
- No runtime behavior. Flag values and struct layout are stable user/kernel ABI for tty ioctls and libc termios functions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_termios.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_timespec.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/_timespec.h

Read completely: 47 lines.

This header defines `struct timespec`.

Key contents:
- Declares `time_t` if needed.
- Defines seconds plus nanoseconds fields: `tv_sec` and `tv_nsec`.

Security/reliability notes:
- No runtime logic. Layout is ABI-sensitive for POSIX time, clocks, timers, nanosleep, and stat timestamps.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_timespec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_timeval.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/_timeval.h

Read completely: 55 lines.

This header defines `struct timeval`.

Key contents:
- Declares `suseconds_t` and `time_t` if needed.
- Defines seconds plus microseconds fields: `tv_sec` and `tv_usec`.

Security/reliability notes:
- No runtime logic. Layout is ABI-sensitive for `gettimeofday`, select timeouts, BIO timestamps, and older BSD APIs.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_timeval.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_ucontext.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/_ucontext.h

Read completely: 81 lines.

This header defines user context and signal stack types.

Key contents:
- Includes signal-set and machine-specific machine context definitions.
- Defines `sigset_t`, `size_t`, and `stack_t` if needed.
- Defines `ucontext_t` with `uc_sigmask` and `uc_mcontext` first, then link, stack, coroutine function pointer, argument, and spare fields.

Important interactions:
- The first two fields are intentionally ordered to support compatibility with `sigcontext`/`ucontext_t` union-style handling.

Security/reliability notes:
- No runtime behavior. Layout is ABI-sensitive for signal delivery, context switching APIs, and architecture-specific `mcontext_t`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_ucontext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_uio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/_uio.h

Read completely: 76 lines.

This kernel-only header defines the `uio` transfer descriptor.

Key contents:
- `enum uio_rw`: `UIO_READ`, `UIO_WRITE`.
- `enum uio_seg`: user-space, system-space, and no-copy segment modes.
- Forward declarations for `iovec` and `thread`.
- `struct uio` with iovec pointer/count, offset, residual byte count, segment flag, read/write direction, and associated thread.

Important interactions:
- Used heavily by vnode, device, and filesystem read/write paths, including `vfs_vnops.c`.

Security/reliability notes:
- Header is guarded to `_KERNEL`/`_KERNEL_STRUCTURES`.
- `uio_resid` is `size_t`, not signed, which affects overflow and completion checks in I/O code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/_uio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/acct.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/acct.h

Read completely: 85 lines.

This header defines process accounting record formats.

Key contents:
- `comp_t`, a compact 3-bit exponent/13-bit fraction time/accounting type.
- `struct acct` with command name, user/system/elapsed time, start time, uid/gid, memory, I/O count, controlling tty, and accounting flags.
- Flags for fork-without-exec, superuser use, compatibility mode, core dump, and signal death.
- Accounting tick granularity `AHZ`.
- Kernel prototype `acct_process(struct proc *)`.

Security/reliability notes:
- No runtime logic here. The structure is on-disk/user-visible accounting ABI, so field widths and `AC_COMM_LEN` matter.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/acct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/acl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/acl.h

Read completely: 142 lines.

This header defines the POSIX.1e ACL user/kernel interface.

Key contents:
- ACL scalar types: `acl_type_t`, `acl_tag_t`, and `acl_perm_t`.
- `struct acl_entry` and `struct acl`, with `ACL_MAX_ENTRIES` set to 32.
- ACL tag constants for owner/user/group/mask/other entries.
- ACL type constants for access, default, AFS, CODA, and NTFS ACLs.
- Permission constants for read/write/execute.
- Userland syscall-entry prototypes and libc ACL helper prototypes.

Security/reliability notes:
- No executable logic. The comments warn that raw syscalls require strict ACL entry ordering; most callers should use library helpers.
- Structure layout and maximum entry count are ABI-sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/agpio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/agpio.h

Read completely: 159 lines.

This header defines the AGP/GART ioctl interface.

Key contents:
- AGP page size constants.
- AGP mode word extract/set macros for request queue, ARQ size, calibration, sideband addressing, AGP enable, 64-bit GART, over-4G, fast writes, AGP 3 mode, and rate.
- Compatibility aliases for older mode names.
- Ioctls for info, acquire/release, setup, allocate/deallocate, bind/unbind, and chipset flush.
- Data structs for version, info, setup, allocation, bind, and unbind.

Security/reliability notes:
- No runtime logic. The ioctl structures are user/kernel ABI for graphics aperture management.
- Mode macros assume caller supplies valid bitfield values; they mask target fields but do not range-check inputs.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/agpio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/aio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/aio.h

Read completely: 148 lines.

This header defines POSIX asynchronous I/O constants, control blocks, and prototypes.

Key contents:
- `aio_cancel` status constants.
- `LIO_*` opcodes and modes.
- `AIO_LISTIO_MAX` of 16.
- `aiocb_t` with file descriptor, offset, user buffer, byte count, sigevent, lio opcode, ignored priority, and internal result/error fields.
- Userland prototypes for `aio_read`, `aio_write`, `lio_listio`, `aio_error`, `aio_return`, `aio_cancel`, `aio_suspend`, `aio_fsync`, and `aio_waitcomplete`.

Security/reliability notes:
- No implementation logic. The `aiocb` layout and volatile buffer pointer are ABI-sensitive.
- Correct use requires exactly one `aio_return()` per submitted control block, as noted by the comments.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/aio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/alist.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/alist.h

Read completely: 110 lines.

This header defines the API and metadata for an aligned power-of-two resource bitmap allocator.

Key contents:
- Describes a radix tree with radix-16 meta nodes and radix-32 leaves.
- `alist_bmap_t` and `alist_blk_t` are 32-bit.
- `almeta_t` stores a bitmap and biggest contiguous allocation hint.
- `alist_t` tracks total blocks, radix, skip, free count, root pointer, and root coverage.
- Constants for meta/leaf radix, no-block sentinel, and known record counts.
- Prototypes for create/init/destroy, alloc/free, free-info query, and print.

Security/reliability notes:
- No implementation here. Allocation correctness depends on the implementation maintaining biggest-hint values that are never too small.
- Non-power-of-two allocations are rounded internally by the allocator, so callers must account for alignment behavior.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/alist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/assym.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/assym.h

Read completely: 52 lines.

This kernel-only header defines macros for exporting C constants to assembly generation.

Key contents:
- Rejects inclusion outside `_KERNEL` or `_KERNEL_STRUCTURES`.
- `ASSYM_BIAS` avoids zero-sized arrays.
- `ASSYM_ABS()` handles negative values without simple signed overflow.
- `ASSYM(name, value)` emits several char arrays encoding sign and 16-bit chunks of the absolute value in their sizes.

Security/reliability notes:
- This is build-time metaprogramming, not runtime logic.
- Correctness depends on consumers interpreting generated symbol sizes consistently.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/assym.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/atomic_common.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/atomic_common.h

Read completely: 131 lines.

This header provides common relaxed atomic load/store macros for machine atomic headers.

Key contents:
- Rejects direct inclusion unless `_CPU_ATOMIC_H_` is defined.
- Defines volatile relaxed loads and stores for bool, char, short, int, long, and fixed-width 8/16/32/64-bit types.
- Uses C11 `_Generic` or compiler generic-selection support to provide type checking where available.
- Defines public `atomic_load_*` and `atomic_store_*` macros, with 64-bit generic operations only under `__LP64__`.
- Defines pointer load/store helpers using volatile `typeof`.

Security/reliability notes:
- These are relaxed operations only; they do not imply memory ordering barriers.
- Macro arguments are evaluated in volatile contexts and should be real object pointers of the expected type.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/atomic_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/backlight.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/backlight.h

Read completely: 64 lines.

This header defines the backlight ioctl interface.

Key contents:
- Maximum brightness level count of 100.
- `struct backlight_props` with current brightness, number of levels, and level table.
- Backlight info type enum for panel and keyboard backlights.
- `struct backlight_info` with fixed-size name and type.
- Ioctls for get status, update status, and get info.

Security/reliability notes:
- No runtime logic. The ioctl structures are ABI-sensitive.
- Kernel ioctl handlers must validate `nlevels` against `BACKLIGHTMAXLEVELS`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/backlight.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/bio.h

Read completely: 105 lines.

This header defines DragonFlyBSD's BIO request object for block/storage I/O.

Key contents:
- Forward declarations for BIO tracking and disk structures.
- `biodone_t` completion callback typedef.
- `struct bio` with driver queue links, BIO stack pointers, buffer back-pointer, completion callback, logical offset, driver-private pointer, CRC, flags, and caller-info unions.
- BIO flags for synchronous completion, waiters, and done state.
- Prototype for `bio_start_transaction()`.

Important interactions:
- Used by buffer cache and device strategy paths; `buf.h` embeds arrays of BIOs in each buffer.
- Caller-owned and driver-owned info fields are explicitly separated.

Security/reliability notes:
- The BIO stack is a core storage-layer contract. Strategy layers must use the BIO passed to them rather than assuming `bio_buf->b_vp` matches their target.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/biotrack.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/biotrack.h

Read completely: 26 lines.

This header defines a minimal in-progress BIO tracking counter.

Key contents:
- `struct bio_track` with active I/O count.
- Macros to read and increment the active count.
- Kernel prototype `bio_track_wait()` for waiting on tracked I/O completion.

Security/reliability notes:
- Very small synchronization surface. Correctness depends on paired decrement/wakeup behavior in the implementation outside this header.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/biotrack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bitops.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/bitops.h

Read completely: 165 lines.

This header provides bit-mask and bit-field helper macros.

Key contents:
- `__BIT`/`__BIT64` for single-bit masks.
- `__BITS`/`__BITS64` for inclusive bit ranges.
- `__LOWEST_SET_BIT`, `__SHIFTOUT`, `__SHIFTIN`, and `__SHIFTOUT_MASK` for register bitfields.
- `ilog2()` using compile-time expansion for constants and `fls`/`flsl` for runtime values.

Security/reliability notes:
- Macro inputs are not generally validated; invalid shift counts or zero masks can produce undefined or nonsensical results.
- `__BIT(32)` and `__BIT64(64)` deliberately return zero to support range macro edge cases.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bitops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bitstring.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/bitstring.h

Read completely: 195 lines.

This header implements a byte-array bitstring macro library.

Key contents:
- `bitstr_t` as unsigned char.
- Helpers for byte index and bit mask.
- Macros for sizing, heap allocation, stack declaration, testing, setting, clearing, range clear/set, first clear bit, first set bit, last set bit, and clear-range search.

Security/reliability notes:
- Macro arguments may be evaluated multiple times in some simple helpers; callers should avoid side effects.
- No bounds checking is performed beyond some final comparisons in search macros.
- `bit_alloc()` depends on `calloc()` being visible to the including translation unit.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bitstring.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/blist.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/blist.h

Read completely: 134 lines.

This header defines bitmap resource lists, primarily used for swap-style block allocation.

Key contents:
- `swblk_t`/`u_swblk_t` block types and `SWAPBLK_NONE` sentinel.
- `blmeta_t` meta/leaf union plus biggest contiguous block hint.
- `blist_t` root object with total blocks, radix, skip, free count, root pointer, and root coverage.
- Radix constants, maximum block calculations, and maximum allocation size.
- Prototypes for create/destroy, allocate, allocate-at, free, fill/reserve, print, and resize.

Security/reliability notes:
- No implementation here. Tree sizing and overflow limits are central to allocator correctness.
- The comments note conservative maximum sizing because overflow detection is not fully trusted.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/blist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/boot.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/boot.h

Read completely: 52 lines.

This header maps boot environment variable names to reboot/boot flags.

Key contents:
- Static `howto_names[]` table mapping strings like `boot_askname`, `boot_cdrom`, `boot_ddb`, `boot_gdb`, `boot_single`, `boot_verbose`, `boot_vidcons`, and `boot_serial` to `RB_*` masks.
- Null terminator entry.

Security/reliability notes:
- The table is `static` in a header, so each including translation unit receives its own copy.
- Requires `RB_*` constants to be defined before meaningful use.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/boot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bootmaj.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/bootmaj.h

Read completely: 28 lines.

This header defines legacy boot major-number translation constants.

Key contents:
- Legacy major numbers for wd, wfd, fd, da, scsicd, and mcd boot devices.
- Character device major numbers for corresponding device classes.
- `BOOTMAJOR_CONVARY` initializer mapping old boot majors to current character-device majors or `-1`.

Security/reliability notes:
- No runtime logic. This is boot compatibility data for translating historical block-device major numbers after block devices were removed.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bootmaj.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/buf.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/buf.h

Read completely: 501 lines.

This header defines the kernel buffer-cache buffer object, BIO queue structures, flags, and public buffer-cache APIs.

Key contents:
- `buf_cmd_t` command enum for read, write, free blocks, format, flush, seek, and done.
- `struct buf` with vnode index trees, free/cluster links, vnode pointer, embedded BIO layers, flags, queue CPU/index, activity counters, buffer lock, command, sizes, residual/error, KVA/data pointers, dirty range, reference count, xio page list, bio ops, and dependency/private union.
- Logical and physical BIO aliases `b_bio1`, `b_bio2`, and `b_loffset`.
- `getblk`/`findblk` flags and a large set of `B_*` buffer state flags.
- BIO queue and cluster-save structures.
- `clrbuf()` helper and allocation/sequence constants.
- Kernel externs and prototypes for buffer lifecycle, read/write, clustering, pbufs, BIO stack, completion, physical I/O, VM page integration, nested I/O, and diagnostics.

Important interactions:
- Used by VFS, VM, filesystem, and block-device layers.
- Comments define strict layering: strategy routines should operate on the passed BIO, not directly on `bp->b_vp`.

Security/reliability notes:
- Buffer flags are highly stateful; invalid combinations can cause lost writes, stale cache data, or bad VM page state.
- `B_KVABIO` requires explicit KVA synchronization before direct `b_data` access across CPUs.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/buf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/buf2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/buf2.h

Read completely: 392 lines.

This kernel header provides inline helpers for buffer locks, BIO queues, buffer activity, dependency callbacks, completion chaining, and common read wrappers.

Key contents:
- `BUF_LOCKINIT`, `BUF_LOCK`, `BUF_TIMELOCK`, `BUF_UNLOCK`, `BUF_KERNPROC`, `BUF_LOCKINUSE`, and `BUF_LOCKFREE`.
- BIO queue helpers for init, insert, remove, first, and take-first.
- Buffer activity advance/decline helpers.
- `buf_dep_init`, dependency count/deallocate/start/complete/fsync/move/check callbacks via `bio_ops`.
- `biodone_chain()` for chained BIO completion.
- Inline wrappers for `bread`, `bread_kvabio`, `breadn`, `cluster_read`, and `cluster_read_kvabio`.

Important interactions:
- Depends on `buf.h`, mount/vnode headers, and VM page constants.
- Some dependency callbacks force `bkvasync_all()` if the vnode does not support KVABIO.

Security/reliability notes:
- Lock helpers mutate lock wait message/timeout fields, with comments noting benign races.
- Dependency callbacks run in sensitive flush paths and must preserve KVA coherency before filesystem callbacks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/buf2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bus.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/bus.h

Read completely: 695 lines.

This header defines DragonFlyBSD's kernel bus/device framework API.

Key contents:
- Core opaque types: `device_t`, `driver_t`, `devclass_t`, and interrupt handler typedefs.
- User-exported bus/device info structures.
- Device state enum and interrupt feature/trigger/polarity constants.
- Resource list entry/list definitions and resource-list helper prototypes.
- Root bus and generic bus method prototypes for attach/detach/probe, resource allocation, ivars, interrupts, suspend/resume/shutdown, and child management.
- Public bus resource wrappers, device accessors/mutators, devclass APIs, resource configuration APIs, and bus generation tracking.
- Driver/module macros for registering drivers on buses.
- Generic ivar accessor-generation macro.
- Bus-space convenience macros for 1/2/4/8-byte read/write, multi, region, set, stream, and barriers through `struct resource`.

Important interactions:
- Includes generated `device_if.h` and `bus_if.h`.
- Integrates with `bus_dma.h`, `bus_resource.h`, kobj methods, sysctl, config resources, and driver modules.

Security/reliability notes:
- This is a broad kernel driver ABI. Mismatched resource ownership, interrupt setup/teardown, or ivar IDs can destabilize device attach/detach paths.
- Probe priority constants are currently all zero except `BUS_PROBE_SPECIFIC`, so drivers cannot rely on nuanced priority ordering here.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bus.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bus_dma.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/bus_dma.h

Read completely: 317 lines.

This header defines the machine-independent bus DMA API.

Key contents:
- Includes machine-specific bus DMA types.
- DMA allocation/loading flags for wait behavior, coherent/zeroed memory, bounce-zone/private allocation behavior, protected calls, page-offset preservation, and uncached mappings.
- Sync operation flags for pre/post read/write.
- Opaque `bus_dma_tag_t` and `bus_dmamap_t`.
- `bus_dma_segment_t` and `bus_dmamem_t`.
- Prototypes for tag create/destroy, map create/destroy, DMA memory allocation/free, loading raw buffers, mbufs, uios, CAM CCBs, segment extraction/defrag, coherent allocation helpers, sync, and unload.
- Callback typedefs for ordinary and size-reporting DMA load completion.
- `bus_dmamap_sync` and `bus_dmamap_unload` macros skip null and `(void *)-1` maps.

Security/reliability notes:
- DMA constraints are security- and correctness-sensitive for device drivers.
- Load callbacks must correctly handle errors and segment counts before programming hardware.
- Sync flags must match device direction to avoid stale cache data or data corruption.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bus_dma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bus_private.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/bus_private.h

Read completely: 148 lines.

This private kernel header defines internal bus/device framework structures.

Key contents:
- Rejects inclusion from userland.
- `driverlink` entries for drivers attached to devclasses.
- TAILQ list typedefs for devclasses, drivers, and devices.
- `struct devclass` with parent, drivers, name, unit-indexed device array, max unit, and sysctl state.
- Config resource/device structures for config-provided integers, strings, and longs.
- `struct bsd_device` implementation with kobj fields, parent/child/global links, driver/devclass/unit/name/description, busy count, state, flags, ivars, softc, and sysctl state.
- Internal device flags for enablement, fixed class, wildcard unit, malloced description, quiet attach, no-match state, external softc, and async probe.
- `struct device_op_desc` method metadata.

Security/reliability notes:
- Internal layout is tightly coupled to `kern/subr_bus.c`-style implementation and kobj dispatch.
- Incorrect manipulation of flags, child lists, or sysctl contexts can break hotplug and driver lifecycle behavior.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bus_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bus_resource.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/bus_resource.h

Read completely: 46 lines.

This header defines generic bus resource type IDs.

Key contents:
- `SYS_RES_IRQ` for interrupt lines.
- `SYS_RES_DRQ` for ISA DMA lines.
- `SYS_RES_MEMORY` for memory-mapped I/O.
- `SYS_RES_IOPORT` for I/O ports.

Security/reliability notes:
- No runtime logic. These constants are part of driver resource allocation ABI.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/bus_resource.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/callout.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/callout.h

Read completely: 149 lines.

This header defines DragonFlyBSD callout/timer structures and API declarations.

Key contents:
- Internal `_callout` with spinlock, existential lock state, queue entry, verifier, flags, debug line/identifier, optional lock, requested callback state, queued callback state, tick values, and waiter count.
- Public `struct callout` containing an opaque internal pointer plus initialization-copied lock/flags.
- Legacy macros to read/set callback argument and function.
- Optional debug arguments for callout initialization.
- Kernel prototypes for active/pending/deactivate, softclock tick, init variants, quick setup/cancel, reset, reset-by-CPU, stop, async stop, terminate, cancel, and drain.
- Public init macros inject file/line metadata when `CALLOUT_DEBUG` is enabled.

Security/reliability notes:
- Callout lifecycle is concurrency-sensitive; callers must choose stop/cancel/drain semantics according to whether callbacks may be running.
- Legacy direct argument/function macros are explicitly marked for old code only.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/callout.h -->