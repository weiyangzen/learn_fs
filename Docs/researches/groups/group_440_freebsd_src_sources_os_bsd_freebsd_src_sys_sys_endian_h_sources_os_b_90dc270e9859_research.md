# Group Research: group_440_freebsd_src_sources_os_bsd_freebsd_src_sys_sys_endian_h_sources_os_b_90dc270e9859

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_endian.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_endian.h

Internal endian helper included only through endian-related public headers.

Key elements:
- Maps compiler byte-order constants to BSD names.
- Defines quad high/low word ordering.
- Exposes POSIX/BSD `LITTLE_ENDIAN`, `BIG_ENDIAN`, `PDP_ENDIAN`, and `BYTE_ORDER` under visibility rules.
- Provides byte-swap, network-order, and host/endian conversion macros.

Dependencies:
- Requires `sys/cdefs.h`.
- Depends on integer typedefs such as `uint16_t` and `__uint32_t` from surrounding include context.

Research notes:
- Uses compiler builtins for byte swaps.
- Important for filesystem and disk formats that need stable little/big-endian conversions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_endian.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_eventhandler.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_eventhandler.h

Private eventhandler type definitions.

Key elements:
- Defines `struct eventhandler_entry` with TAILQ linkage, priority, and callback argument.
- Defines `eventhandler_tag`.
- Provides declaration macros for predeclared eventhandler lists and typed eventhandler entries.

Dependencies:
- Includes `sys/queue.h`.

Research notes:
- This header supplies the lightweight shared structure layer for `eventhandler.h`.
- Direct list declarations are intended to avoid global-list lookup overhead for high-frequency events.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_eventhandler.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_exterr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_exterr.h

Kernel-side extended error record definition.

Key elements:
- Defines `struct kexterr` with numeric error, message pointer, two 64-bit parameters, category, and source line.

Dependencies:
- Includes `sys/_types.h`.

Research notes:
- Added for richer kernel error reporting.
- Paired conceptually with `_uexterror.h`, which provides the fixed-size user ABI representation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_exterr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_ffcounter.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_ffcounter.h

Feed-forward clock counter typedef.

Key elements:
- Defines `ffcounter` as `uint64_t`.
- Describes it as a wide monotonic counter accumulating at the selected timecounter rate.

Dependencies:
- Assumes `uint64_t` is visible from including context.

Research notes:
- Minimal ABI/type shim for feed-forward clock consumers.
- Relevant to timestamping paths that may affect I/O accounting or filesystem timing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_ffcounter.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_iovec.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_iovec.h

Scatter/gather vector definition.

Key elements:
- Declares `size_t` if needed.
- Defines `struct iovec` with `iov_base` and `iov_len`.
- Under `_KERNEL`, adds initialization and advancement helper macros.

Dependencies:
- Includes `sys/_types.h`.
- Kernel helpers rely on `strlen()` and `KASSERT()` being available from including context.

Research notes:
- Core ABI for read/write, VFS, socket, and block I/O scatter/gather paths.
- `IOVEC_ADVANCE` bounds-checks advancement before adjusting pointer and length.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_iovec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_lock.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_lock.h

Common lock object and debug macro definitions.

Key elements:
- Defines `struct lock_object` with name, flags, class data, and witness pointer.
- Under `_KERNEL`, derives `LOCK_DEBUG` from module/debug/profiling/tracing options.
- Defines file/line argument macros for debug and non-debug lock builds.

Dependencies:
- Forward-references `struct witness`.

Research notes:
- Shared base embedded by mutexes, rwlocks, sx locks, lockmgr locks, and rmlocks.
- Lock debug mode affects ABI/calling conventions for modules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_lock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_lockmgr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_lockmgr.h

Private lockmgr structure definition.

Key elements:
- Defines `struct lock` containing `lock_object`, volatile `lk_lock`, sleep-failure priority fields, timeout, and optional debug stack.
- Includes stack storage only when `DEBUG_LOCKS` is enabled.

Dependencies:
- Optionally includes `sys/_stack.h`.
- Requires `struct lock_object` to be visible from including context.

Research notes:
- Lockmgr locks are used by older VFS/filesystem paths.
- Structure layout is conditional on lock debugging.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_lockmgr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_maxphys.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_maxphys.h

Default maximum physical I/O size definition.

Key elements:
- Defines `MAXPHYS` if not already set.
- Uses `128 KiB` for `__ILP32__`, otherwise `1 MiB`.

Dependencies:
- None.

Research notes:
- Public-domain compatibility shim.
- Directly relevant to block and filesystem I/O sizing defaults.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_maxphys.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_mutex.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_mutex.h

Mutex structure definitions.

Key elements:
- Defines `struct mtx` with common `lock_object` and volatile `mtx_lock`.
- Defines cache-line-aligned `struct mtx_padalign` with mirrored fields.

Dependencies:
- Includes `sys/_types.h`, `sys/_lock.h`, and `machine/param.h`.

Research notes:
- The member name `mtx_lock` is reserved for mutex implementations.
- Pad-aligned form is intended to be API-compatible while avoiding false sharing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_mutex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_null.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_null.h

Portable `NULL` definition.

Key elements:
- Defines `NULL` only if not already defined.
- Uses `((void *)0)` for C.
- Uses `__null` for modern GNU C++, otherwise `0L` on LP64 C++ or `0`.

Dependencies:
- Compiler/language predefined macros.

Research notes:
- Small compatibility header used by other public headers that need `NULL` without pulling larger standard headers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_null.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_nv.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_nv.h

Name-value list forward declaration.

Key elements:
- Includes `sys/nv_namespace.h` outside the kernel.
- Forward-declares `struct nvlist`.
- Defines `nvlist_t` once via `_NVLIST_T_DECLARED`.

Dependencies:
- Userland namespace handling through `sys/nv_namespace.h`.

Research notes:
- Keeps consumers from needing the full nvlist layout.
- Used where typed references to libnv/kernel nvlist objects are enough.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_nv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_offsetof.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_offsetof.h

Minimal `offsetof` provider.

Key elements:
- Defines `offsetof(TYPE, MEMBER)` as `__builtin_offsetof(TYPE, MEMBER)` if not already defined.

Dependencies:
- Compiler builtin support.

Research notes:
- Small standalone helper for code needing offset calculations without including broader headers.
- Copyright notes indicate recent CHERI/DEC-related provenance.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_offsetof.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_param.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_param.h

Small parameter and rounding macro subset.

Key elements:
- Defines `NBBY`, `NBPW`, `nitems`, `howmany`, `rounddown`, `roundup`, `rounddown2`, `roundup2`, and `powerof2`.
- Power-of-two alignment delegates to `__align_down` and `__align_up`.

Dependencies:
- Assumes alignment helpers are available from surrounding headers.

Research notes:
- These macros are foundational in kernel and filesystem sizing, block rounding, array counts, and page calculations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_param.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_pctrie.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_pctrie.h

Compressed radix tree root definition.

Key elements:
- Forward-declares `struct pctrie_node`.
- Defines `struct pctrie` with a root node pointer.

Dependencies:
- None beyond standard struct declarations.

Research notes:
- Provides the shared root type for pctrie users.
- Used by `_rangeset.h`; pctries are common for sparse keyed kernel structures.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_pctrie.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_pthreadtypes.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_pthreadtypes.h

POSIX pthread public type definitions.

Key elements:
- Forward-declares pthread object structs.
- Defines opaque pointer typedefs for pthreads, attrs, mutexes, condvars, rwlocks, barriers, and spinlocks.
- Defines `pthread_key_t`, `pthread_addr_t`, and start routine type.
- Defines `struct pthread_once`.

Dependencies:
- None explicit.

Research notes:
- Mostly opaque ABI boundary for libc/libpthread.
- `pthread_once_t` is not opaque: it stores state plus a mutex pointer.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_pthreadtypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_pv_entry.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_pv_entry.h

Physical-to-virtual page mapping entry structures.

Key elements:
- Defines `pv_entry_t`, representing a virtual mapping of a VM page.
- Defines per-pmap `pv_chunk` storage sized to one page.
- Computes `_NPCPV`, `_NPCM`, `PC_FREEN`, and `PC_FREEL` from page size and word width.
- Provides kernel inline helpers `pc_is_full`, `pc_is_free`, `pv_to_chunk`, and `PV_PMAP`.

Dependencies:
- Includes `sys/param.h`.
- Requires VM/page types and queue macros from included context.

Research notes:
- Enforces `sizeof(struct pv_chunk) == PAGE_SIZE`.
- Important VM infrastructure for page mappings that back filesystem cache and memory-mapped files.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_pv_entry.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_rangeset.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_rangeset.h

Range-set structure declaration.

Key elements:
- Defines data duplication/free callback types.
- Defines `struct rangeset` backed by a `pctrie`, callback hooks, callback context, and allocation flags.

Dependencies:
- Includes `sys/_pctrie.h`.

Research notes:
- Generic kernel range-tracking primitive.
- Relevant to VM/VFS/block code that tracks sparse offset or address ranges.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_rangeset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_rmlock.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_rmlock.h

Mostly-reader lock structure definitions.

Key elements:
- Defines reader queue structures, `struct rmlock`, `struct rm_priotracker`, and `struct rmslock`.
- `struct rmlock` embeds common lock metadata, writer CPU set state, active reader list, and a union of write-lock representations.
- Provides field aliases for union members.

Dependencies:
- Includes cpuset, lock, mutex, queue, and sx headers.

Research notes:
- Supports read-mostly concurrency patterns common in routing, VFS, and global kernel state.
- `rm_priotracker` keeps per-reader priority/thread tracking.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_rmlock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_rwlock.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_rwlock.h

Reader/writer lock structure definitions.

Key elements:
- Defines `struct rwlock` with common `lock_object` and volatile `rw_lock`.
- Defines cache-line-aligned `struct rwlock_padalign`.

Dependencies:
- Includes `sys/_types.h`, `sys/_lock.h`, and `machine/param.h`.

Research notes:
- The member name `rw_lock` is reserved for rwlock implementations.
- Pad-aligned form mirrors the normal layout for API compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_rwlock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_semaphore.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_semaphore.h

Kernel semaphore user ABI declarations.

Key elements:
- Defines `semid_t` as `intptr_t`.
- Defines `SEM_VALUE_MAX`.
- Outside `_KERNEL`, declares `ksem_*` APIs for close, post, wait, timedwait, init, open, unlink, getvalue, and destroy.

Dependencies:
- Forward-declares `struct timespec`.
- Uses `mode_t` from including context.

Research notes:
- Provides low-level FreeBSD kernel semaphore syscall interface declarations, distinct from higher-level POSIX wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_semaphore.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_seqc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_seqc.h

Sequence counter typedef.

Key elements:
- Defines `seqc_t` as `uint32_t`.

Dependencies:
- Assumes `uint32_t` is visible.

Research notes:
- Minimal public-domain shim for sequence counter users.
- Sequence counters are used for low-overhead consistency checks in concurrent kernel data paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_seqc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_sigaltstack.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_sigaltstack.h

Alternate signal stack definitions.

Key elements:
- Under XSI visibility, defines `stack_t`, `SS_ONSTACK`, `SS_DISABLE`, `MINSIGSTKSZ`, and `SIGSTKSZ`.
- Defines `struct __stack_t` unconditionally for ucontext needs.
- Under BSD visibility, aliases the structure tag as `sigaltstack`.

Dependencies:
- Includes `sys/_types.h`.

Research notes:
- The structure carries stack pointer, size, and flags for signal delivery.
- Needed by `_ucontext.h` even when public typedef visibility is restricted.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_sigaltstack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_sigset.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_sigset.h

Signal set bit layout.

Key elements:
- Defines signal set sizing and bit-indexing macros.
- Defines `_SIG_MAXSIG` as 128 and `_SIG_WORDS` as 4.
- Defines `__sigset_t` as four 32-bit words.
- Under kernel 4.3 compatibility, defines `osigset_t`.

Dependencies:
- Requires `__uint32_t` from included type context.

Research notes:
- Establishes ABI layout for signal masks used in process, thread, and ucontext state.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_sigset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_sigval.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_sigval.h

Signal value union definitions.

Key elements:
- Under POSIX realtime or XSI visibility, defines `union sigval` with integer and pointer payload variants plus FreeBSD 6 compatibility names.
- For 32-bit compatibility contexts, defines `union sigval32`.

Dependencies:
- Uses visibility macros and `__uint32_t`.

Research notes:
- Used by queued signals, timers, AIO notifications, and other sigevent paths.
- Keeps 64-bit kernels able to represent 32-bit userland pointer payloads.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_sigval.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_smr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_smr.h

Safe Memory Reclamation core typedefs and assertions.

Key elements:
- Defines `smr_seq_t`, `smr_delta_t`, and opaque `smr_t`.
- Provides `SMR_ENTERED`, `SMR_ASSERT_ENTERED`, `SMR_ASSERT_NOT_ENTERED`, and `SMR_ASSERT`.

Dependencies:
- Assumes kernel globals/helpers such as `curthread`, `zpcpu_get`, `SMR_SEQ_INVALID`, and `KASSERT`.

Research notes:
- SMR is a lockless read-side reclamation scheme for high-concurrency kernel structures.
- Assertions verify critical-section state.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_smr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_sockaddr_storage.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_sockaddr_storage.h

Protocol-independent socket address storage.

Key elements:
- Defines RFC 2553 storage size and alignment constants.
- Defines `struct sockaddr_storage` with length, family, padding, and alignment field.

Dependencies:
- Requires `sa_family_t` and `__int64_t` from including context.

Research notes:
- Fixed 128-byte socket address container for ABI-safe network address passing.
- Indirect relevance to network filesystems and socket-based filesystem tools.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_sockaddr_storage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_stack.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_stack.h

Kernel stack trace storage definition.

Key elements:
- Defines `STACK_MAX` as 18.
- Defines `struct stack` with depth and an array of program counters.

Dependencies:
- Requires `vm_offset_t` from including context.

Research notes:
- Used by debug/profiling facilities, including optional lock debugging in `_lockmgr.h`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_stack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_stdarg.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_stdarg.h

Compiler-backed variadic argument macros.

Key elements:
- Includes visibility macros.
- Defines `va_list` from `__builtin_va_list` if needed.
- Maps `va_start`, `va_arg`, `__va_copy`, `va_copy`, and `va_end` to compiler builtins.

Dependencies:
- Includes `sys/_visible.h`.

Research notes:
- `va_copy` is exposed for ISO C99 and newer.
- Centralizes stdarg behavior for FreeBSD headers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_stdarg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_stdint.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_stdint.h

Standard fixed-width integer typedef layer.

Key elements:
- Defines `int8_t` through `int64_t`, `uint8_t` through `uint64_t`, `intptr_t`, `uintptr_t`, `intmax_t`, and `uintmax_t`.
- Under BSD visibility, defines `int64ptr_t` and `uint64ptr_t`.

Dependencies:
- Uses internal `__*` integer types from `sys/_types.h` or surrounding include context.

Research notes:
- Provides public names while guarding each typedef with `_DECLARED` macros.
- Pointer-width compatibility typedefs are useful for 32/64-bit ABI translation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_stdint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_sx.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_sx.h

Shared/exclusive lock structure definition.

Key elements:
- Defines `struct sx` with common `lock_object` and volatile `sx_lock`.

Dependencies:
- Includes `sys/_types.h` and `sys/_lock.h`.

Research notes:
- SX locks are sleepable shared/exclusive kernel locks.
- Used by VFS and filesystem code where blocking while locked is acceptable.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_sx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_task.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_task.h

Taskqueue task structure definitions.

Key elements:
- Defines `task_fn_t` and `struct task` with queue link, pending count, priority, flags, handler, and context.
- Defines task flags for enqueued, no-enqueue, and network tasks.
- Defines `struct timeout_task`.
- Under `_KERNEL`, defines `gtask_fn_t` and `struct gtask`.

Dependencies:
- Includes `sys/_callout.h` and `sys/queue.h`.

Research notes:
- Taskqueues are deferred execution infrastructure used throughout drivers, storage, networking, and filesystem-adjacent code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_task.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_termios.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_termios.h

Terminal I/O constants and `struct termios`.

Key elements:
- Defines control-character indexes, input/output/control/local flag bits, standard baud rates, and `NCCS`.
- Uses visibility gates for BSD, XSI, and POSIX-specific constants.
- Defines `tcflag_t`, `cc_t`, `speed_t`, and `struct termios`.

Dependencies:
- Relies on visibility macros from including context.

Research notes:
- Main ABI contract for terminal and tty behavior.
- Mostly peripheral to filesystem research, but terminal ioctl structures appear in broader kernel/user ABI work.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_termios.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_timespec.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_timespec.h

Nanosecond-resolution time structure.

Key elements:
- Defines `time_t` if not already declared.
- Defines `struct timespec` with seconds and nanoseconds.

Dependencies:
- Includes `sys/_types.h`.

Research notes:
- Common timestamp ABI used by filesystems, timers, semaphores, AIO, and stat-like interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_timespec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_timeval.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_timeval.h

Microsecond-resolution time structure.

Key elements:
- Defines `suseconds_t` and `time_t` if needed.
- Defines `struct timeval` with seconds and microseconds.

Dependencies:
- Includes `sys/_types.h`.

Research notes:
- Used by `gettimeofday(2)` and legacy time interfaces.
- Appears in ABI compatibility helpers and filesystem timestamp/user ABI paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_timeval.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_tls_variant_i.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_tls_variant_i.h

Variant I thread-local storage layout.

Key elements:
- Defines `TLS_VARIANT_I`.
- Defines `struct dtv_slot`, `struct dtv`, and `struct tcb`.
- Defines `TLS_TCB_SIZE`.

Dependencies:
- Requires `uintptr_t` from included type context.
- Forward-declares `struct pthread`.

Research notes:
- TCB layout is shared across architectures using TLS variant I.
- `tcb_dtv` is required by the runtime linker.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_tls_variant_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_types.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_types.h

Core FreeBSD internal type foundation.

Key elements:
- Defines fixed-width internal integer types, pointer-sized types, size/ssize/ptrdiff, VM offset/size, and many system ABI types.
- Includes `machine/_types.h` for target-specific additions.
- Defines filesystem-relevant types including `__blksize_t`, `__blkcnt_t`, `__fflags_t`, `__fsblkcnt_t`, `__fsfilcnt_t`, `__ino_t`, `__mode_t`, `__nlink_t`, `__off_t`, `__dev_t`, and `__daddr_t`.
- Defines ACL internal typedefs, max alignment type, multibyte state, varargs compatibility, and `__INO64`.

Dependencies:
- Compiler width macros and `machine/_types.h`.

Research notes:
- This is the key ABI substrate for almost every other header in the group.
- Comments emphasize preserving exact typedef spellings to avoid ABI and C++ name-mangling breaks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_ucontext.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_ucontext.h

User context structure definition.

Key elements:
- Defines `ucontext_t` as `struct __ucontext`.
- First fields are `uc_sigmask` and `uc_mcontext`, intentionally ordered for compatibility with `sigcontext`.
- Includes link, alternate stack, flags, and spare fields.

Dependencies:
- Requires `__sigset_t`, `mcontext_t`, and `struct __stack_t` from including context.

Research notes:
- Used by signal handling and context switching APIs.
- Field ordering is an explicit compatibility constraint.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_ucontext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_uexterror.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_uexterror.h

User ABI extended error record.

Key elements:
- Defines `struct uexterror` with version, error, category, source line, flags, reserved fields, two 64-bit parameters, and a fixed 128-byte message buffer.

Dependencies:
- Includes `sys/_types.h`.

Research notes:
- Fixed-size representation suitable for copying to userland.
- Complements kernel pointer-based `struct kexterr`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_uexterror.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_uio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_uio.h

UIO direction and segment enums.

Key elements:
- Under BSD visibility, defines `enum uio_rw` with `UIO_READ` and `UIO_WRITE`.
- Defines `enum uio_seg` for user space, system space, and no-copy segments.

Dependencies:
- Visibility macros from including context.

Research notes:
- UIO is central to VFS, device, socket, and filesystem I/O paths.
- This header only exports small enum pieces; full `struct uio` lives elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_uio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_umtx.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_umtx.h

User mutex and synchronization object ABI structures.

Key elements:
- Defines `struct umtx`, `umutex`, `ucond`, `urwlock`, `_usem`, `_usem2`, and `_umtx_time`.
- Includes owner fields, flags, robust linkage, waiter counters, semaphore counts, and timeout metadata.

Dependencies:
- Includes `sys/_types.h` and `sys/_timespec.h`.

Research notes:
- These layouts are user/kernel ABI for FreeBSD thread synchronization primitives.
- 32-bit padding is explicit in `struct umutex`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_umtx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_unrhdr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_unrhdr.h

Unit number allocator header structure.

Key elements:
- Defines `struct unrhdr` with allocation range, busy/allocation counts, first/last free tracking, mutex pointer, main TAILQ, and deferred-free TAILQ.

Dependencies:
- Includes `sys/queue.h`.
- Forward-declares `struct mtx`.

Research notes:
- Used by kernel subsystems that allocate stable numeric IDs.
- Deferred-free queue supports freeing after dropping the allocator lock.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_unrhdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_visible.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_visible.h

Header feature-test visibility policy.

Key elements:
- Normalizes old `_POSIX_C_SOURCE` values.
- Maps `_XOPEN_SOURCE`, `_POSIX_SOURCE`, `_POSIX_C_SOURCE`, `_ANSI_SOURCE`, `_C99_SOURCE`, `_C11_SOURCE`, `_C23_SOURCE`, and glibc-style ISO source macros to internal visibility macros.
- Defines `__POSIX_VISIBLE`, `__XSI_VISIBLE`, `__BSD_VISIBLE`, `__ISO_C_VISIBLE`, and `__EXT1_VISIBLE`.

Dependencies:
- Preprocessor feature-test macros.

Research notes:
- Controls which names public headers expose.
- Default environment exposes POSIX Issue 8, XSI 800, BSD extensions, C23, and Annex K extension visibility.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_visible.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_winsize.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/_winsize.h

Terminal window size structure.

Key elements:
- Defines `struct winsize` with row, column, horizontal pixels, and vertical pixels.

Dependencies:
- None explicit.

Research notes:
- Kernel stores the structure to present a consistent tty ioctl ABI but does not otherwise use the values.
- Peripheral to filesystem scope, but part of shared system ABI headers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/_winsize.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/aac_ioctl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/aac_ioctl.h

Adaptec AAC RAID controller ioctl definitions.

Key elements:
- Defines AAC queue statistics structures and `AACIO_STATS`.
- Defines Linux/Windows-derived `FSACTL_LNX_*` ioctl command numbers.
- Defines native BSD `FSACTL_*` ioctl encodings.
- Under `_KERNEL`, defines structures for revision checks, adapter FIB retrieval, disk queries, and feature reporting.

Dependencies:
- Requires ioctl macros and AAC driver protocol types from including context.

Research notes:
- Storage-management ABI for AAC RAID controllers.
- Includes compatibility support for Linux management applications and 32-bit adapter FIB pointers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/aac_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/abi_compat.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/abi_compat.h

ABI object translation helper macros.

Key elements:
- Defines pointer conversion macros `PTRIN` and `PTROUT`.
- Defines copy helpers for same-name fields, renamed fields, pointer fields, `timeval`, `timespec`, `itimerspec`, fixed 64-bit fields, and bintime-like fields.
- Uses static assertions for fixed 64-bit copies.

Dependencies:
- Includes `sys/abi_types.h`.
- Requires `uintptr_t`, `uint64_t`, and `memcpy` availability from context.

Research notes:
- Intended for syscall and compatibility layers translating structures between ABIs.
- Important for 32/64-bit kernel-user compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/abi_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/abi_types.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/abi_types.h

ABI compatibility scalar type definitions.

Key elements:
- Defines `freebsd32_uint64_t`, represented as two 32-bit words on amd64 and as `uint64_t` elsewhere.
- Defines `time32_t`, 32-bit on amd64/i386 and 64-bit elsewhere.
- Defines `__HAVE_TIME32_T`.

Dependencies:
- Includes `sys/_types.h`.

Research notes:
- Captures FreeBSD-specific 32-bit ABI quirks, especially i386 time and 64-bit alignment behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/abi_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/acct.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/acct.h

Process accounting record layouts.

Key elements:
- Defines `AC_COMM_LEN`.
- Defines current `struct acctv3`, older `struct acctv2`, and legacy `struct acctv1`.
- Defines accounting flags such as `AFORK`, `ACOMPAT`, `ACORE`, `AXSIG`, and `ANVER`.
- Defines legacy `comp_t` and `AHZV1`.
- Under `_KERNEL`, declares `acct_process()`.

Dependencies:
- Userland includes `sys/types.h`; kernel temporarily maps `float` to `uint32_t` for encoded accounting fields.

Research notes:
- Accounting records include command, CPU time, elapsed time, start time, uid/gid, memory, I/O block count, tty, and flags.
- Filesystem relevance comes from persistent accounting logs and encoded I/O counts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/acct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/acl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/acl.h

POSIX.1e and NFSv4 access control list ABI/API header.

Key elements:
- Defines ACL scalar typedefs, maximum entry count, tags, entry types, ACL types, permissions, flag bits, text flags, and mode override/preserve masks.
- Under kernel/private builds, defines old and current ACL entry/layout structures, including `struct oldacl`, `struct acl_entry`, `struct acl`, and libc-private `struct acl_t_struct`.
- Declares kernel ACL conversion, allocation, validation, NFSv4 inheritance/sync, and old/new ACL copy helpers.
- In userland, declares POSIX.1e and FreeBSD `_np` ACL APIs; private mode also declares raw syscall interfaces.

Dependencies:
- Includes `sys/types.h` and `sys/_null.h`; kernel includes `sys/malloc.h`.

Research notes:
- Central filesystem permission metadata header.
- Comments preserve compatibility constraints for old POSIX.1e on-disk layout and 4 KiB current ACL allocation sizing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/agpio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/agpio.h

AGP GART ioctl and mode definitions.

Key elements:
- Defines fixed AGP page size/shift.
- Provides AGP mode word get/set macros for rate, sideband addressing, fast writes, aperture request size, and related capabilities.
- Defines `AGPIOC_*` ioctl commands.
- Defines `agp_version`, `agp_info`, `agp_setup`, `agp_allocate`, `agp_bind`, and `agp_unbind`.

Dependencies:
- Requires ioctl macros and standard kernel/user types from including context.

Research notes:
- Hardware-memory aperture management ABI.
- Filesystem relevance is indirect through memory mapping and device infrastructure.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/agpio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/aio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/aio.h

POSIX asynchronous I/O public and kernel definitions.

Key elements:
- Defines AIO cancellation results, LIO opcodes/modes, vectored and file-offset extensions, and `AIO_LISTIO_MAX`.
- Defines public `struct aiocb` and `aiocb_t`, with aliases for vectored I/O.
- Under `_KERNEL`, defines worker pool tunables, backend function types, `struct kaiocb`, and AIO backend lifecycle/cancellation APIs.
- Userland declares `aio_read`, `aio_write`, `lio_listio`, `aio_error`, `aio_return`, `aio_cancel`, `aio_suspend`, `aio_mlock`, `aio_fsync`, and BSD extensions.

Dependencies:
- Includes `sys/types.h` and `sys/signal.h`; kernel includes queue, event, signalvar, and uio headers.

Research notes:
- Directly relevant to asynchronous filesystem and block I/O.
- `struct kaiocb` stores copied user control block, UIO/iovec storage, credentials, file pointer, notification state, and backend-specific state.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/aio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/alq.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/alq.h

Kernel asynchronous logging queue API.

Key elements:
- Kernel-only header defining opaque `struct alq`, global logging daemon thread pointer, and `struct ale`.
- Defines flags for wait behavior, activation, and ordered writes.
- Declares queue open, write, flush, close, get/post APIs.
- Provides inline `alq_post()` wrapper.

Dependencies:
- Kernel-only; uses `struct thread` and `struct ucred`.

Research notes:
- ALQ writes queued log entries to files asynchronously.
- Useful for low-overhead tracing/accounting paths that must avoid synchronous disk writes in hot code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/alq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/apm.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/apm.h

Compatibility include wrapper.

Key elements:
- Public-domain file that includes `sys/disk/apm.h`.

Dependencies:
- `sys/disk/apm.h`.

Research notes:
- Keeps older include path `sys/apm.h` working while real disk partition definitions live under `sys/disk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/apm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/arb.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/arb.h

Array-backed red-black tree macro library.

Key elements:
- Defines array RB tree heads and entries for 8-, 16-, and 32-bit indexes.
- Maintains root, free-list, min, max, current count, and maximum count indexes.
- Provides allocation-size, initialization, node/index accessor, free-list, rotation, insert-color, remove-color, insert, remove, find, nearest-find, next/prev, min/max, reinsert, and traversal macros.
- Supports optional `ARB_AUGMENT` hooks.

Dependencies:
- Includes `sys/cdefs.h`.
- Uses integer typedefs, `intptr_t`, `uint8_t`, and `__DECONST` from context.

Research notes:
- Designed for preallocated arrays rather than pointer-allocated nodes.
- Useful when kernel structures need bounded allocation and stable compact indexes.
- The implementation caches min/max indexes and recycles removed nodes through an internal free list.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/arb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/asan.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/asan.h

Kernel address sanitizer interface.

Key elements:
- Under `KASAN`, defines shadow scale constants and stack/redzone poison byte values.
- Declares KASAN initialization, shadow mapping, poisoning, and thread allocation functions.
- Without `KASAN`, defines no-op macros for the same operations.

Dependencies:
- Under `KASAN`, includes `sys/types.h` and uses `vm_offset_t`, `size_t`, `uint8_t`, and `struct thread`.

Research notes:
- Imported from NetBSD KASAN heritage.
- Useful for detecting memory bugs in kernel subsystems, including filesystem and storage code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/asan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/assym.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/assym.h

Assembly symbol/offset generation macros.

Key elements:
- Defines `ASSYM_BIAS`, `ASSYM_ABS`, and `ASSYM()` to encode numeric values into array sizes.
- Defines `OFFSYM()` to emit offset-sized symbols and assert member type compatibility.
- Optional `OFFSET_TEST` enables layout offset assertions against `_lite` structures.

Dependencies:
- Requires `offsetof`, `CTASSERT`, and compiler type builtins from context.

Research notes:
- Used to generate constants consumed by assembly code.
- Helps keep assembly offsets synchronized with C structure layouts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/assym.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ata.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ata.h

ATA/ATAPI protocol, identify data, log, and ioctl definitions.

Key elements:
- Defines packed `struct ata_params`, mapping ATA IDENTIFY DEVICE words and many capability/status bits.
- Defines dataset management, device/status/error register bits, HPA feature codes, transfer modes, ATA commands, NCQ commands, ZAC zone-management commands, security commands, and ATAPI command opcodes.
- Defines ATA channel/device ioctl structures and ioctl codes.
- Defines packed `struct atapi_sense`.
- Defines Extended Power Conditions constants and power condition log structures.
- Defines ATA general-purpose log directory, identify log page, capacity page, supported capabilities page, and zoned device information page structures.
- Defines `struct ata_ioc_request`, `struct ata_security_password`, and ATA RAID config/status ioctl structures and command codes.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Research notes:
- Core storage protocol ABI header for ATA disks, ATAPI devices, and legacy ATA RAID management.
- Highly relevant to block storage and filesystem layers because it exposes capacity, sector size, trim support, write cache, flush, FUA, NCQ, sanitize, security, power, and zoned-device capabilities.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/atomic_common.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/atomic_common.h

Common atomic load/store helper macros for machine atomic headers.

Key elements:
- Refuses direct inclusion unless `_MACHINE_ATOMIC_H_` is defined.
- Defines relaxed volatile load/store helpers for bool, char, short, int, long, and fixed-width 8/16/32/64-bit types.
- Uses C11 `_Generic` when available for type checking.
- Defines public `atomic_load_*`, `atomic_store_*`, pointer load/store, consume pointer load, and interrupt fence helpers.

Dependencies:
- Includes `sys/types.h`.
- Depends on architecture-provided acquire pointer load and compiler memory barrier macros.

Research notes:
- Shared implementation layer behind architecture atomic APIs.
- 64-bit scalar helpers are exposed only on LP64.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/atomic_common.h -->