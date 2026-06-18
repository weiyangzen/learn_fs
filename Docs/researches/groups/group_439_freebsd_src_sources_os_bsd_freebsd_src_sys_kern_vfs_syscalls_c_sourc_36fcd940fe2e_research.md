# Group Research: group_439_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_vfs_syscalls_c_sourc_36fcd940fe2e

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_syscalls.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_syscalls.c

Primary syscall front-end for FreeBSD VFS operations. It translates user-visible filesystem syscalls into namei lookups, vnode operations, mount operations, Capsicum right checks, MAC/audit hooks, jail visibility rules, and compatibility ABI conversions.

Key responsibilities:
- Filesystem-wide operations: `kern_sync()`, `sys_quotactl()`, `kern_statfs()`, `kern_fstatfs()`, `kern_getfsstat()`, plus FreeBSD 4/11 statfs conversion paths.
- Directory/root context: `kern_chdir()`, `kern_chroot()`, `sys_fchdir()`, `sys_fchroot()`, and `change_dir()`, including `unprivileged_chroot` policy and `NO_NEW_PRIVS` requirement.
- Open/create namespace operations: `kern_openat()`, `kern_openatfp()`, `kern_mknodat()`, `kern_mkfifoat()`, `kern_linkat()`, `kern_symlinkat()`, `kern_funlinkat()`, `kern_frmdirat()`, `kern_renameat()`, `kern_mkdirat()`.
- Metadata syscalls: `kern_statat()`, `kern_accessat()`, `kern_chflagsat()`, `kern_fchmodat()`, `kern_fchownat()`, `kern_utimesat()`, `kern_utimensat()`, `kern_truncate()`, `kern_fsync()`.
- Directory and descriptor helpers: `kern_getdirentries()`, `getvnode_path()`, `getvnode()`, `sys_umask()`, `sys_revoke()`.
- File-handle operations for NFS/lockd-style privileged access: `kern_getfhat()`, `kern_fhopen()`, `kern_fhstat()`, `kern_fhstatfs()`, `kern_fhlinkat()`, `sys_fhreadlink()`.
- Advisory/copy helpers: `kern_posix_fadvise()` stores or applies per-file advice, and `kern_copy_file_range()` validates descriptors, offsets, ranges, and delegates to `vn_copy_file_range()`.

Important patterns:
- `at2cnpflags()` is the central translator from `AT_*` lookup flags to namei flags such as `FOLLOW`, `NOFOLLOW`, `RBENEATH`, and `EMPTYPATH`.
- Most mutating path operations use `NDPREINIT`, `bwillwrite()`, `vn_start_write()`, VOP call, `VOP_VPUT_PAIR()` or explicit releases, `vn_finished_write()`, and retry on `ERELOOKUP`.
- Capsicum rights are passed through `NDINIT_ATRIGHTS()` and descriptor helpers; open flags are converted to descriptor rights by `flags_to_rights()`.
- `O_PATH` is deliberately allowed only through selected paths, mainly `getvnode_path()`, while `getvnode()` rejects it for ordinary vnode file operations.
- MAC and AUDIT hooks are interleaved at syscall boundaries and before sensitive VOPs.
- Jail/prison visibility is enforced for statfs-style reporting with `prison_canseemount()` and `prison_enforce_statfs()`.

Research relevance:
- This file is the best map of FreeBSD's syscall-to-VFS boundary.
- It shows how FreeBSD combines path lookup policy, capability rights, vnode locking, mount write suspension, ABI compatibility, and filesystem-specific VOP dispatch.
- For filesystem implementation work, the expected VOP contracts for create/link/remove/rename/stat/readdir/readlink/fsync/copy-range are visible here through their callers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_vnops.c

Core vnode-backed file operation implementation. This file binds `struct fileops vnops` to vnode methods and supplies the shared helpers that filesystems rely on for open/close, read/write, offset locking, mount write suspension, truncation, mmap, fsync, range copy, allocation/deallocation, directory iteration, and vnode pair locking.

Key responsibilities:
- Fileops table: `vnops` maps file-layer operations to vnode-backed implementations: read/write via `vn_io_fault`, truncate, ioctl, poll, kqueue, stat, close, chmod/chown, sendfile, seek, mmap, fallocate, fspacectl, compare.
- Open/close path: `vn_open_cred()` drives name lookup and optional creation; `vn_open_vnode()` checks vnode type, access, MAC, `O_PATH`, FIFO locking, `VOP_OPEN()`, advisory locks, and writecount accounting; `vn_close1()` pairs close and writecount decrement.
- I/O path: `vn_rdwr()`, `vn_read()`, `vn_write()`, `vn_rdwr_inchunks()`, `vn_read_from_obj()`, and write-ioflag helpers manage VOP read/write calls, page-cache reads, direct/sync/dsync flags, sequential heuristics, and `posix_fadvise` state.
- Deadlock avoidance: `vn_io_fault1()`, `vn_io_fault_uiomove()`, and `vn_io_fault_pgmove()` avoid vnode lock order reversals caused by page faults during VOP read/write into userspace buffers.
- Offset synchronization: `foffset_lock()`, `foffset_unlock()`, `foffset_lock_pair()`, and UIO helpers serialize file offset updates with atomic or mutex-backed implementations depending on platform word size.
- Write suspension: `vn_start_write()`, `vn_start_secondary_write()`, `vn_finished_write()`, `vfs_write_suspend()`, `vfs_write_resume()`, and unmount suspension helpers coordinate writes against filesystem suspension.
- Metadata/file helpers: `vn_truncate_locked()`, `vn_statfile()`, `vn_ioctl()`, `vn_poll()`, `vn_chmod()`, `vn_chown()`, `vn_utimes_perm()`, `vn_mmap()`, `vn_fsync_buf()`, `vn_fsid()`.
- Copy and space management: `vn_copy_file_range()` chooses filesystem-specific or generic copy; `vn_generic_copy_file_range()` handles sparse copying, holes, zero scanning, timeouts, and output growth; `vn_fallocate()`, `vn_deallocate()`, and `vn_fspacectl()` wrap allocation/deallocation VOPs.
- Directory helpers: `vn_dir_next_dirent()` provides robust buffered directory iteration; `vn_dir_check_empty()` uses it to detect non-dot entries while ignoring whiteouts.
- Locking helpers: `_vn_lock()` handles doomed vnode behavior and delayed size updates; `vn_lock_pair()` avoids lock order reversal for two vnodes; `vn_lktype_write()` selects shared/exclusive write locking.

Important patterns:
- Range locks protect split I/O, truncation, copy-range, and no-page-fault I/O windows.
- Vnode writecount is carefully paired with opens, truncation, mmap, and failed-open cleanup.
- Generic copy-range preserves sparse files when possible by using `FIOSEEKDATA/FIOSEEKHOLE` or block zero detection.
- Mount write suspension is reference-counted and has special primary/secondary write accounting.
- Many helpers are exported for filesystem code, not just syscall code.

Research relevance:
- This is the primary file for understanding FreeBSD's common vnode operation semantics and the expectations imposed on filesystem VOP implementations.
- It complements `vfs_syscalls.c`: syscalls enter there, then common file/vnode mechanics are performed here.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_align.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_align.h

Small alignment macro header.

Defines:
- `_ALIGNBYTES` as `sizeof(void *) - 1`.
- `_ALIGN(p)` as `__align_up((p), _ALIGNBYTES + 1)`.

Important note:
- The header explicitly documents these interfaces as obsolete/ambiguous and recommends `alignof(type)` plus `__align_up()` for new code.
- CHERI/provenance concerns are called out: `_ALIGN()` preserves type and provenance, which matters for kernel file descriptor passing.

Research relevance:
- Foundational ABI-style macro used by old interfaces needing pointer-sized alignment.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_align.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_atomic64e.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_atomic64e.h

Kernel-only declarations for emulated 64-bit atomic operations on platforms that lack native support.

Defines:
- `HAS_EMULATED_ATOMIC64`.
- Prototypes for add, cmpset, fcmpset, clear, fetchadd, load, readandclear, set, subtract, store, and swap on `u_int64_t`.
- Acquire/release variants are aliases to the base emulated functions.

Constraints:
- Must be included through `<machine/atomic.h>`; direct inclusion triggers `#error`.
- Exposed only under `_KERNEL`.

Research relevance:
- Architecture abstraction layer for FreeBSD atomic APIs, preserving a common kernel atomic interface across weaker platforms.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_atomic64e.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_atomic_subword.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_atomic_subword.h

Fallback implementation for 8-bit and 16-bit atomic operations on platforms that only support word-sized atomics.

Defines:
- Word alignment and endian-dependent shift macros for byte/halfword positions.
- `_atomic_cmpset_masked_word()` and `_atomic_fcmpset_masked_word()` to update subword fields inside a 32-bit word using masks.
- Fallback `atomic_cmpset_8`, `atomic_fcmpset_8`, `atomic_cmpset_16`, `atomic_fcmpset_16`.
- Fallback `atomic_load_acq_8`, `atomic_load_acq_16`.
- Fallback looping `atomic_set_16` and `atomic_clear_16`.

Important behavior:
- Compare-and-set loops distinguish failures caused by the target subword from unrelated changes in the same aligned word.
- `fcmpset` intentionally permits one-shot/spurious failure behavior consistent with `atomic(9)`.
- Direct inclusion is blocked; it must come from `machine/atomic.h`.

Research relevance:
- Shows how FreeBSD keeps fine-grained atomic APIs portable even when hardware lacks byte/halfword atomic instructions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_atomic_subword.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_bitset.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_bitset.h

Base bitset type-definition macros.

Defines:
- `_BITSET_BITS` as bits per `unsigned long`.
- `__howmany()`, `__bitset_words()`.
- `__BITSET_DEFINE(type, size)` producing a struct with an `unsigned long __bits[]` array sized for the requested bit count.
- `__BITSET_DEFINE_VAR()` workaround for variable-size declarations.
- Under `_KERNEL` or `_WANT_FREEBSD_BITSET`, defines a default `struct bitset` and public `BITSET_DEFINE` wrappers.

Research relevance:
- Common substrate for CPU/domain sets and other kernel bit-vector types.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_bitset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_blockcount.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_blockcount.h

Minimal block count type and reader.

Defines:
- `blockcount_t` with a single unsigned integer field.
- High-bit waiter flag `_BLOCKCOUNT_WAITERS_FLAG`.
- `_BLOCKCOUNT_COUNT()` and `_BLOCKCOUNT_WAITERS()` helpers.
- `blockcount_read()` using `atomic_load_int()` and masking off the waiter flag.

Research relevance:
- Compact atomic counter representation where count and waiter state share one word.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_blockcount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_bus_dma.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_bus_dma.h

Opaque bus DMA type declarations.

Defines:
- `bus_dmasync_op_t` as an integer operation type.
- Opaque pointer typedefs `bus_dma_tag_t` and `bus_dmamap_t`.
- `bus_dma_lock_op_t` enum with `BUS_DMA_LOCK` and `BUS_DMA_UNLOCK`.
- Callback type `bus_dma_lock_t(void *, bus_dma_lock_op_t)`.

Research relevance:
- Small public/kernel ABI header separating driver-visible DMA handles from machine-dependent implementation details.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_bus_dma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_callout.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_callout.h

Core callout timer structure definitions.

Defines:
- Queue heads for `callout` in list, slist, and tailq forms.
- `callout_func_t(void *)`.
- `struct callout` fields for queue linkage, scheduled time, precision, argument, callback, associated lock object, public/internal flags, and target CPU.

Research relevance:
- Foundational kernel timer/callback data layout shared by timeout scheduling code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_callout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_clock_id.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_clock_id.h

Shared clock and timer constant definitions for `time.h` and `sys/time.h`.

Defines:
- POSIX-visible clocks such as `CLOCK_REALTIME`, `CLOCK_MONOTONIC`, `CLOCK_THREAD_CPUTIME_ID`, `CLOCK_PROCESS_CPUTIME_ID`.
- BSD-visible clocks such as `CLOCK_VIRTUAL`, `CLOCK_PROF`, uptime/realtime/monotonic precise/fast variants, `CLOCK_SECOND`, and `CLOCK_TAI`.
- Linux-compatible aliases: `CLOCK_BOOTTIME`, `CLOCK_REALTIME_COARSE`, `CLOCK_MONOTONIC_COARSE`.
- Timer flags `TIMER_RELTIME` and `TIMER_ABSTIME`.

Important note:
- Comments document intentional glibc compatibility around POSIX visibility levels, and a temporary visibility exception for `CLOCK_UPTIME_FAST`.

Research relevance:
- User/kernel ABI constant header for time APIs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_clock_id.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_cpuset.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_cpuset.h

CPU set type declaration.

Defines:
- In kernel builds, `CPU_SETSIZE` as `MAXCPU`.
- `CPU_MAXSIZE` as 1024 and default `CPU_SETSIZE` to that outside kernel-specific definition.
- `cpuset_t` as a bitset-backed `_cpuset`.

Research relevance:
- Small ABI/type bridge between generic bitset machinery and CPU affinity/set APIs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_cpuset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_decls.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_decls.h

C/C++ linkage helper header.

Defines:
- `__BEGIN_DECLS` as `extern "C" {` under C++ and empty under C.
- `__END_DECLS` as `}` under C++ and empty under C.

Research relevance:
- Common public header utility for making C declarations safe in C++ translation units.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_decls.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_domainset.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_domainset.h

NUMA memory-domain set type declaration.

Defines:
- In kernel builds, `DOMAINSET_SETSIZE` as `MAXMEMDOM`.
- `DOMAINSET_MAXSIZE` as 256 and default `DOMAINSET_SETSIZE` to that if not otherwise defined.
- `domainset_t` as a bitset-backed `_domainset`.
- Forward declaration `struct domainset`.
- `struct domainset_ref`, embedding a volatile policy pointer and per-object round-robin iterator.

Research relevance:
- Type substrate for NUMA domain policies and per-object domainset references.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_domainset.h -->