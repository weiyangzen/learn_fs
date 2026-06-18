# Group Research: group_1229_netbsd_src_sources_os_bsd_netbsd_src_lib_libpthread_pthread_h_sourc_ecc3e4e1c87e

Scope: `Docs/research_subset_a.md`, limited to the listed NetBSD `libpthread` and `libpuffs` files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread.h

This is the public NetBSD pthread API header. It declares core thread lifecycle calls, attributes, mutexes, condition variables, once control, thread-specific data, cancellation, names, suspend/resume extensions, CPU-clock access, cleanup handler macros, spinlocks, rwlocks, barriers, scheduling, errno access, affinity, and NetBSD-specific inspection helpers.

The header defines POSIX constants and NetBSD extension constants such as `PTHREAD_BARRIER_SERIAL_THREAD`, `PTHREAD_CANCELED`, and `PTHREAD_MAX_NAMELEN_NP`, and maps public initializer macros to the private layout constants in `pthread_types.h`. It also contains the important libc stub remapping layer used when `__LIBPTHREAD_SOURCE__` is not defined: many pthread calls become `__libc_*` symbols so libraries can use synchronization stubs without forcing a libpthread dependency. `pthread_create` is deliberately only weakly redirected under `_NETBSD_PTHREAD_CREATE_WEAK`, preserving link-time detection of programs that forgot to link libpthread.

Integration points: includes `pthread_types.h`, exposes the ABI consumed by all libpthread C files, and coordinates with libc weak/strong aliases. Risks are ABI stability and macro remapping surprises, especially for code that `#undef`s pthread names or depends on process-shared support hidden behind `_PTHREAD_PSHARED`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_attr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_attr.c

This file implements pthread attribute object management and getters/setters for detach state, guard size, inherited scheduling, scheduling parameters, scheduling policy, scope, stack address/size, thread names, create-suspended state, and `pthread_getattr_np`.

The public `pthread_attr_t` stores only magic, flags, and a private pointer. Optional data is lazily allocated by `pthread__attr_init_private`, which initializes defaults from global stack and guard sizes and `SCHED_OTHER`. Destroy frees this private area and poisons the magic. `pthread_attr_get_np` copies live thread state into an attribute object, including flags, stack region, guard size, name argument, and scheduler parameters via `pthread_getschedparam`.

Validation is handled with `pthread__error` checks on magic values. Stack size is checked against `_SC_THREAD_STACK_MIN`; scheduling priorities are passed through `pthread__checkpri`; scheduling policies support `SCHED_OTHER`, `SCHED_FIFO`, and `SCHED_RR`, returning `ENOTSUP` otherwise. `pthread_attr_setname_np` formats into the fixed `PTHREAD_MAX_NAMELEN_NP` buffer and rejects truncation.

Integration points: uses `pthread_int.h` private structures, libc strong aliases for attr init/destroy/detach, and live thread state from `struct __pthread_st`. Main risks are lazy allocation failures, format-string semantics in thread naming, and compatibility of deprecated stack-address APIs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_attr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_barrier.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_barrier.c

This file implements POSIX barriers and barrier attributes. `pthread_barrier_init` validates the optional attribute, rejects a zero count, initializes the waiter queue, stores the configured count, and starts generation and current count at zero. `pthread_barrier_destroy` requires a valid barrier with no current waiters and marks it dead.

`pthread_barrier_wait` uses a hash mutex around the barrier object, a generation counter, and a `PTQ` waiter list. The thread that satisfies the barrier advances the generation, resets the count, unparks all waiters, unlocks, and returns `PTHREAD_BARRIER_SERIAL_THREAD`. Other threads enqueue themselves, set `pt_sleepobj`, and park until generation changes. The implementation explicitly notes that barrier wait is not a cancellation point, simplifying wakeup ownership.

Barrier attributes are minimal: init/destroy only manage magic values. If `_PTHREAD_PSHARED` is enabled, process-private is accepted and process-shared returns `ENOSYS`.

Integration points: depends on `pthread__hashlock`, `pthread__park`, `pthread__unpark_all`, and `PTQ` queues. Risks are misuse during destroy while waiters exist and unsupported process-shared semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_barrier.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_cancelstub.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_cancelstub.c

This file provides libpthread's strong cancellation-aware wrappers around libc syscall stubs for POSIX cancellation points. It declares `_sys_*` entry points that perform raw system calls without cancellation checks, then defines public wrappers that call `TESTCANCEL(self)` before and after the raw call.

Covered wrappers include socket and I/O calls (`accept`, `accept4`, `connect`, `read`, `write`, `readv`, `writev`, `pread`, `pwrite`, `recv*`, `send*`), synchronization and waiting calls (`poll`, `pselect`, `select`, `kevent`, `sigsuspend`, `sigwait`, `wait4`, `nanosleep`, `clock_nanosleep`), filesystem sync and open calls (`close`, `open`, `openat`, `fsync`, `fdatasync`, `fsync_range`, `msync`), message queues, aio suspend, System V messages, and `tcdrain`.

`TESTCANCEL` skips checks when using libc stubs, otherwise reads `pt_cancel` relaxed, issues an acquire barrier when cancelled, and calls `pthread__cancelled`. `sigwait` preserves caller `errno` while translating the signal wait result into the POSIX return convention. Variadic `open`, `openat`, and `fcntl` forward one argument through `va_arg`.

Integration points: tied to libc symbol naming, compat prototypes, weak/strong aliases, and NetBSD versioned syscall names. Risks are ABI drift when libc adds or renames cancellation points, incorrect variadic forwarding for command-specific `fcntl` arguments, and maintaining exact errno/cancellation semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_cancelstub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_compat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_compat.c

This compatibility file supplies libc symbols not present before NetBSD 5.0 and initializes libc threading/atomic support from a constructor. `__pthread_init` calls `__libc_atomic_init` and `__libc_thr_init` before normal program execution.

The rest of the file provides direct syscall-backed implementations for LWP, scheduler, aio, and message queue helper symbols such as `_lwp_kill`, `_lwp_detach`, `_lwp_park`, `_lwp_unpark`, `_lwp_unpark_all`, `_lwp_setname`, `_lwp_getname`, `_lwp_ctl`, `_sched_setaffinity`, `_sched_getaffinity`, `_sched_setparam`, `_sched_getparam`, `_sys_sched_yield`, `_sys_aio_suspend`, and `_sys_mq_*`. `sched_yield` is also implemented as a direct syscall.

Integration points: bridges newer libpthread code to older libc/kernel symbol availability and is used by synchronization, scheduling, cancellation, and affinity code. Risks are compatibility-only path rot and syscall-number or prototype mismatches across NetBSD versions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_cond.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_cond.c

This file implements condition variables and condition-variable attributes. Condition variables use a lock-free waiter stack in `ptc_waiters`, a remembered associated mutex in `ptc_mutex`, and optional private clock storage. It supports libc stub fallback through `__uselibcstub` and exports libc strong aliases.

`pthread_cond_timedwait` validates the condition and mutex, checks for pending cancellation, atomically pushes a stack-allocated waiter with the current LWP id, unlocks the mutex, parks with the selected clock and absolute timeout, then relocks the mutex. If cancellation or timeout/error races with a signal, it broadcasts to ensure any absorbed wakeup is not lost and waits until its waiter record is no longer globally visible. Cancellation exits only after the mutex has been reacquired, matching POSIX requirements.

`pthread_cond_signal` uses a dummy sentinel pointer to lock the waiter list, removes one waiter, and transfers it to the associated mutex through `pthread__mutex_deferwake`. `pthread_cond_broadcast` atomically steals the whole waiter list and similarly defers wakeups to mutex unlock. Attributes support `CLOCK_MONOTONIC` and `CLOCK_REALTIME`; process-shared support returns `ENOSYS` when enabled.

Risks are subtle memory-ordering requirements, stack waiter lifetime, and the single remembered mutex pointer when applications misuse a condition variable with multiple mutexes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_cond.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_getcpuclockid.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_getcpuclockid.c

This small file implements `pthread_getcpuclockid`. It validates the supplied `pthread_t` magic, saves the caller's `errno`, calls `clock_getcpuclockid2(P_LWPID, thread->pt_lid, clock_id)`, translates failure into the returned errno value, restores the original `errno`, and returns the error code.

Integration points: depends on the internal thread structure's LWP id and on the kernel/libc CPU-clock API. The function follows the pthread convention of returning errors directly rather than leaving them in `errno`.

Risks are limited to stale or invalid thread handles, which are checked only by magic value here, and races with thread exit if callers do not otherwise hold a valid thread reference.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_getcpuclockid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_int.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_int.h

This is the central private header for NetBSD libpthread internals. It defines hidden visibility, core thread structures, private attribute data, lock operation vectors, cancellation flags, magic numbers, global tuning variables, waiter structures, utility function prototypes, inline spinlock helpers, TLS-based `pthread__self`, assertion/error macros, TSD hooks, and rwlock bit layout.

`struct __pthread_st` is the key runtime thread object. It starts with `pt_self`, optional TLS pointer, magic/state/flags/cancellation word, per-thread errno, stack metadata, exit value, name, cached lock ops, start routine and argument, cleanup stack, LWP id, all-thread tree/list links, state mutex, LWP control pointer, rwlock handoff fields, sleep-object tracking, and a flexible array of per-key specific data.

The header defines cancellation bits (`PT_CANCEL_DISABLED`, `PT_CANCEL_ASYNC`, `PT_CANCEL_PENDING`, `PT_CANCEL_CANCELLED`), synchronization constants, and rwlock owner bit packing where low bits are flags and the high aligned pointer/count region stores writer owner or reader count.

Integration points: included by nearly every libpthread implementation file. ABI and memory-layout stability matter because many files assume pointer alignment, cacheline placement, and TLS access. Risks are architecture-specific TLS assumptions and the broad blast radius of changing thread or synchronization layouts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_int.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_lock.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_lock.c

This file implements internal libpthread simple-lock primitives. It provides two `pthread_lock_ops` tables: one using restartable atomic sequences (RAS) and one using machine atomic simple locks. The global `pthread__lock_ops` defaults to RAS for early single-threaded startup safety, then `pthread__lockprim_init` chooses atomic operations on multiprocessor/concurrent execution or installs RAS on uniprocessor systems when available.

`pthread__spinlock_slow` is the contended path used through the lock ops table. It repeatedly checks the lock, pauses with SMT hints for a configured number of spins, tries again when the lock appears free, and yields when spinning is exhausted. The spin count comes from `PTHREAD_NSPINS`, defaults to 64 on concurrent systems, and 1 on single-concurrency systems.

Integration points: underlies public spinlocks and internal per-thread cached lock ops in `struct __pthread_st`. Risks are architecture-specific RAS support, tuning sensitivity of spin/yield behavior, and startup ordering before full threading initialization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_makelwp.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_makelwp.h

This private header declares `pthread__makelwp`, the helper used to create a new NetBSD LWP for a pthread. The function accepts a start routine, argument, private pointer, stack base and size, LWP creation flags, and an output LWP id. It includes `<lwp.h>`, public pthread definitions for `PTHREAD_HIDE`, and `pthread_int.h`.

Integration points: the implementation is in `pthread_makelwp_netbsd.c` and is used by thread creation code outside this listed group. Its interface isolates machine/context setup and `_lwp_create` details from higher-level pthread creation logic.

Risks are ABI expectations around `ucontext_t`, stack pointer direction, private TLS/thread pointer passing, and LWP creation flag semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_makelwp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_makelwp_netbsd.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_makelwp_netbsd.c

This file implements `pthread__makelwp` for NetBSD. It zeroes a `ucontext_t`, initializes user-context flags with `_INITCONTEXT_U`, fills stack fields from the supplied stack base and size, clears `uc_link`, calls `_lwp_makecontext` with the start routine, argument, private pointer, and stack bounds, then calls `_lwp_create` with the requested flags and returns its result.

The comment notes some setup is also performed by `_lwp_makecontext`, but the code preserves explicit machine-dependent context initialization for safety.

Integration points: sits between pthread creation code and kernel LWP creation. It relies on `pthread_int.h` context macros, `<lwp.h>`, and the architecture's `_lwp_makecontext` behavior. Risks are architecture-specific context requirements and stack/TLS correctness for newly created threads.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_makelwp_netbsd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_misc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_misc.c

This file implements miscellaneous pthread operations for scheduling, affinity, signals, and thread-directed signals. `pthread_getschedparam`, `pthread_setschedparam`, `pthread_getaffinity_np`, `pthread_setaffinity_np`, `pthread_setschedprio`, and `pthread_kill` all validate thread magic, check that the thread is still findable with `pthread__find`, then call NetBSD LWP or scheduler syscalls using the thread's LWP id.

`pthread_sigmask` wraps `__sigprocmask14` and returns errno-style errors. `pthread__sched_yield` dispatches either to the libc stub or `_sys_sched_yield`.

Integration points: uses scheduler compatibility functions from `pthread_compat.c`, libc strong aliases for `pthread_sigmask` and yield, and private thread lookup state. Risks include races with thread termination, scheduler-policy differences from POSIX expectations, and preserving errno-return conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_mutex.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_mutex.c

This file implements pthread mutexes and mutex attributes. Mutex ownership is held in `ptm_owner`, using pointer low bits for recursive and priority-protect flags. Waiters are tracked with lock-free lists of stack waiter records and parked with LWP primitives, avoiding userspace spinlocks around waiter queues.

Fast-path lock is a CAS from `NULL` to `self`. The slow path handles recursive/errorcheck semantics, priority protection via `_sched_protect`, adaptive spinning while the owner is running according to `lwpctl`, enqueueing the waiter, timeout handling, and wakeup races. Unlock validates ownership, handles recursive depth, releases priority protection, clears owner state, and wakes any waiters through `pthread__mutex_wakeup`. Wakeups batch LWP ids up to `pthread__unpark_max`.

Attributes encode type, protocol, and priority ceiling in `ptma_private`. Supported mutex types are normal, errorcheck, and recursive; supported protocols are none and priority-protect, while priority-inherit returns `ENOTSUP`. Process-shared support returns `ENOSYS` if compiled.

`pthread__mutex_deferwake` lets condition variables transfer waiters onto a mutex so they are woken when the mutex owner unlocks. Risks are subtle memory ordering, stack waiter lifetime, timeout removal races, and complexity around encoded owner bits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_mutex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_once.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_once.c

This file implements `pthread_once`. It uses the mutex embedded in `pthread_once_t` to serialize initialization and `pto_done` as the completion flag. If `pto_done` is clear, it locks the mutex, pushes a cleanup handler to unlock on cancellation/unwind, checks `pto_done` again, calls the routine, issues a release barrier, sets `pto_done`, and pops cleanup with execute. If already done, it issues an acquire barrier before returning.

The implementation falls back to libc stub behavior when `__uselibcstub` is set and exports a strong alias to `__libc_thr_once`.

Integration points: depends on mutexes and pthread cleanup macros. Risks are routine cancellation or nonlocal exit before setting `pto_done`, for which the cleanup handler at least releases the mutex, and correct release/acquire visibility for initialized data.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_once.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_queue.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_queue.h

This header defines the private `PTQ` intrusive queue macro family used throughout libpthread. It is modeled after BSD tail queues but designed for static initializability. It provides head and entry declarations, initializers, insert-at-head/tail/after/before, removal, empty/first/next/last/prev accessors, and forward/reverse iteration.

The key implementation detail is `ptqh_last`, which may be `NULL` in static initializers and is repaired by `PTQ_INSERT_TAIL` before first insertion. This supports objects like statically initialized synchronization primitives.

Integration points: used for thread cleanup stacks, barrier waiters, rwlock wait queues, all-thread lists, and TSD key lists. Risks are typical intrusive-macro hazards: double insertion/removal, stale prev pointers, and lack of type safety.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_queue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_rwlock.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_rwlock.c

This file implements pthread read/write locks and attributes. The lock owner field packs state flags and either a writer thread pointer or reader count. Reader acquisition increments the owner count when no writer or waiting writer is present; writer acquisition CASes from no owner to `self | RW_WRITE_LOCKED`. Both paths prefer writers once `RW_WRITE_WANTED` is set.

Contended readers and writers use a hash interlock mutex and `PTQ` sleep queues. Writers are queued tail-first; readers are inserted at the head of the reader queue. Unlock releases reader or writer ownership and, when waiters exist and the lock becomes unowned, directly hands off to the first waiting writer or all waiting readers. Handoff marks target threads' `pt_rwlocked` state and unparks them through helper functions. Timed waits use `pthread__park`; `pthread__rwlock_early` repairs queue and waiter bits if a timed waiter wakes before handoff.

Try-locks return `EBUSY` without sleeping, timed lock calls validate absolute timeout fields, and NetBSD `_np` helpers inspect held/read/write-held state. Attribute support is minimal; process-shared code appears guarded and unsupported.

Risks are complex flag packing, direct handoff correctness, writer preference fairness tradeoffs, and guarded `_PTHREAD_PSHARED` code referencing `ptr` instead of `attr`, which would matter if compiled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_rwlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_specific.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_specific.c

This file implements the fast public accessors for pthread thread-specific data and current CPU reporting. `pthread_setspecific` falls back to libc stubs when active, otherwise gets `pthread__self` and delegates to `pthread__add_specific`. `pthread_getspecific` directly indexes the current thread's `pt_specific[key].pts_value`, making reads very cheap and unsynchronized. `pthread_curcpu_np` reads the current CPU from the thread's `lwpctl` area and asserts it is valid.

It also overrides `setcontext` through `pthread_setcontext` to preserve the pthread private pointer: when `_UC_TLSBASE` is set in the incoming context, it copies the context, clears that flag, and calls `_sys_setcontext`.

Integration points: pairs with key allocation/destruction in `pthread_tsd.c`, libc strong aliases, and machine TLS/LWP control state. Risks are unchecked key indexing in `pthread_getspecific`, relying on valid key use by callers, and architecture-specific context/TLS preservation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_specific.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_spin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_spin.c

This file implements public POSIX spinlocks. `pthread_spin_init` validates `pshared`, sets the spinlock magic, stores the flag, and initializes the underlying `pthread_spin_t` through internal lock initialization. The comment notes process-shared is not otherwise used because CPU simple locks have the desired properties here.

Destroy validates magic and returns `EBUSY` if the simple lock is not unlocked, then marks the object dead. Lock repeatedly calls the internal trylock and `pthread__smt_wait` until successful. Trylock maps failure to `EBUSY`; unlock releases via cached lock ops and calls `pthread__smt_wake`.

Integration points: depends on `pthread_lock.c` lock primitives and private magic values. Risks are CPU-burning behavior under contention, lack of ownership checking on unlock, and process-shared semantics being accepted but not explicitly coordinated beyond simple-lock behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_spin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_tsd.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_tsd.c

This file implements pthread key lifecycle and thread-exit destruction for thread-specific data. `pthread_tsd_init` registers atfork handlers, reads `PTHREAD_KEYS_MAX` from the environment with a POSIX minimum clamp, computes per-thread TSD storage size, and uses `mmap` rather than malloc for early initialization. It allocates global per-key lists and destructor arrays in one arena.

`pthread_key_create` searches from `nextkey` for an unused destructor slot, uses an internal no-op destructor when the requested destructor is `NULL`, initializes the key's global list expectation, advances `nextkey`, and returns the key. `pthread__add_specific` records a non-null value in the current thread and inserts the per-thread key entry into the global per-key list the first time it is used. `pthread_key_delete` implements the standard's no-destructor rule by removing all entries for that key, setting values to `NULL`, clearing link state, and freeing the key slot.

`pthread__destroy_tsd` runs exit-time destructors up to `PTHREAD_DESTRUCTOR_ITERATIONS`, clearing values before invocation. `pthread__copy_tsd` migrates libc TSD slots into pthread storage during initialization.

Risks are undefined behavior under concurrent key deletion/use, deliberate unsynchronized fast `pthread_getspecific`, and destructor loops that can reestablish values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_tsd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_types.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_types.h

This public/private ABI header defines pthread object types, object layouts, magic constants, and static initializers. It maps `pthread_t` to `struct __pthread_st *`, defines opaque-looking structs for attributes, mutexes, condition variables, once objects, spinlocks, rwlocks, barriers, and associated attributes, and defines `pthread_key_t` as `int`.

Important layouts include `__pthread_mutex_st` with magic, errorcheck simple lock, optional padding, priority ceiling, volatile owner, volatile waiter list, recursive count, and spare field; `__pthread_cond_st` with magic, unused lock/spare fields, volatile waiter pointer, associated mutex, and private clock pointer; `__pthread_rwlock_st` with reader and writer queues, reader count, owner field, and spare private field; and `__pthread_barrier_st` with waiter queue and generation/count fields.

The header includes C++ accommodations for non-volatile simple-lock typedefs and designated-initializer compatibility macros. It preserves old SA pthread layout compatibility in mutex comments and spare fields.

Integration points: included by `pthread.h` and internal code. Risks are ABI breakage from any layout change, initializer compatibility across C standards and C++, and volatile/padding assumptions across architectures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/res_state.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/res_state.c

This file provides thread-safe resolver state handling for multi-threaded programs. It maintains a global singly-linked free list of `_res_st` objects protected by `res_mtx`. `__res_get_state` checks out an existing resolver state or allocates a new one, initializes it with `res_ninit` when needed, and returns a `res_state`. Allocation or initialization failures set `h_errno = NETDB_INTERNAL`.

`__res_put_state` casts the state back to `_res_st` and returns it to the free list. `__res_state`, which corresponds to global `_res` macro usage, deliberately writes an error message to stderr and aborts because shared `_res` is not supported in multi-threaded programs.

Integration points: uses pthread mutexes, resolver library structures, and NetBSD resolver APIs. Risks are pooled state lifetime management, no cleanup of the global free list in this file, and hard abort for incompatible global resolver state access.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/res_state.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/thrd.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/thrd.c

This file implements C11 `<threads.h>` thread functions as thin wrappers over pthreads. `thrd_create` allocates a small trampoline cookie holding the C11 start function and argument, creates a pthread running `__thrd_create_tramp`, and maps `pthread_create` errors to `thrd_success`, `thrd_nomem`, or `thrd_error`. The trampoline calls the C11 function, frees the cookie, and returns the integer result through a pointer-sized cast.

Other wrappers are direct: current/equal/detach/join/exit map to pthread equivalents, `thrd_join` translates the returned pointer-sized integer back to `int`, `thrd_sleep` uses `clock_nanosleep(CLOCK_MONOTONIC, TIMER_RELTIME, ...)` and maps interrupt/other errors to C11 return conventions, and `thrd_yield` calls `sched_yield`.

Integration points: paired with `threads.h`, `mtx.c`, `cnd.c`, `tss.c`, and pthread lifecycle APIs. Risks are pointer/integer result casting portability, cookie allocation failure, and C11 return-code translation losing detailed pthread errno values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/thrd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/threads.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/threads.h

This header exposes NetBSD's C11 thread API in terms of pthread types. It defines `thread_local` when needed, maps `ONCE_FLAG_INIT` to `PTHREAD_ONCE_INIT`, maps `TSS_DTOR_ITERATIONS` to `PTHREAD_DESTRUCTOR_ITERATIONS`, and typedefs C11 `cnd_t`, `thrd_t`, `tss_t`, `mtx_t`, `once_flag`, `tss_dtor_t`, and `thrd_start_t`.

It declares C11 condition variable, mutex, thread, once, and thread-specific-storage functions. It defines mutex type bits `mtx_plain`, `mtx_recursive`, `mtx_timed` and thread result constants `thrd_timedout`, `thrd_success`, `thrd_busy`, `thrd_error`, and `thrd_nomem`.

Integration points: depends on `pthread.h` for all underlying object representations and constants. Risks are API conformance gaps because the C11 ABI is intentionally layered on pthread semantics and return-code mappings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/threads.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/tss.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/tss.c

This file implements the C11 thread-specific storage functions as wrappers over pthread TSD. `tss_create` validates the output pointer with `_DIAGASSERT`, calls `pthread_key_create`, and maps success to `thrd_success` and failure to `thrd_error`. `tss_delete` calls `pthread_key_delete` and discards the result because C11 specifies no return value. `tss_get` returns `pthread_getspecific`, and `tss_set` maps `pthread_setspecific` success or failure to C11 return codes.

Integration points: paired with `threads.h` and `pthread_tsd.c`. Risks are minimal, mostly loss of detailed pthread error values and the C11 no-return-value delete behavior hiding invalid-key failures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/tss.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/Makefile

This makefile builds the NetBSD `libpuffs` library. It includes `bsd.own.mk`, enables `_FORTIFY_SOURCE` by default through `USE_FORT?= yes`, sets `WARNS?= 5`, names the library `puffs`, lists implementation sources, installs manual pages, and installs `puffs.h` and `puffsdump.h` under `/usr/include`.

The source list includes the files in this group plus broader library components such as `puffs.c`, `null.c`, `opdump.c`, `paths.c`, `pnode.c`, `requests.c`, `subr.c`, and `suspend.c`. Lint flags suppress some warnings, and `callcontext.c` receives a GCC 12-specific `-Wno-dangling-pointer` because it intentionally manipulates stack/context pointers in ways that confuse the compiler warning.

Integration points: defines build membership for the userspace filesystem support library. Risks are warning suppression hiding real context-lifetime bugs and the source list being the authoritative compilation boundary for libpuffs behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/callcontext.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/callcontext.c

This file implements libpuffs call contexts, which are stackful user-level contexts used to dispatch filesystem requests and yield back to the main loop. Each `puffs_cc` normally lives at the base of an mmap-allocated, aligned stack region with a guard page. `puffs_fakecc` disables real context switching for a volatile single-context mode.

`puffs__cc_create` either reuses a context from the per-mount magazine or allocates one with `slowccalloc`, initializes `ucontext_t` state, assigns stack bounds, and uses `makecontext` to start a supplied `puffs_ccfunc`. `puffs_cc_continue`, `puffs_cc_yield`, `puffs__cc_cont`, and `puffs__goto` coordinate `swapcontext`/`setcontext` transitions among request contexts, borrowed contexts, and the main loop. `puffs_cc_schedule` queues a context for later dispatch.

The file also stores caller pid/lid metadata, recovers the current context by masking the current stack address to the aligned stack base, saves/restores the main context, caches destroyed contexts up to `PUFFS_CCMAXSTORE`, and unmaps extras at exit.

Risks are high: stack alignment assumptions, guard-page placement, context lifetime, borrowed-context races if made multithreaded, and nonportable pointer passing through `makecontext`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/callcontext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/creds.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/creds.c

This file implements PUFFS credential inspection and generic access checks. It distinguishes user credentials (`PUFFCRED_TYPE_UUC`) from internal credentials (`PUFFCRED_TYPE_INTERNAL`). Accessors return uid, gid, and group lists for regular user credentials, or `EOPNOTSUPP` for unsupported credential types. Predicates check uid equality, group membership, regular/kernel/filesystem credentials, and "juggernaut" privilege, meaning root, kernel, or filesystem credential.

`puffs_access` mirrors kernel `vaccess` behavior: kernel/filesystem credentials bypass checks; root bypasses except for non-directory execute when no execute bit is set; ordinary users are checked against owner, group, or other permission bits according to requested read/write/execute access.

`puffs_access_chown`, `puffs_access_chmod`, and `puffs_access_times` enforce common ownership, group, sticky/setgid, and timestamp permission rules using the credential helpers.

Integration points: used by userspace filesystem implementations that want kernel-like access decisions. Risks are semantic drift from kernel `vaccess`, special treatment of internal credentials, and caller responsibility to pass correct vnode type/mode/owner/group data.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/creds.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/dispatcher.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/dispatcher.c

This is the central PUFFS request dispatcher. It takes kernel request frames, decodes `preq_opclass` and `preq_optype`, invokes the corresponding filesystem operation callback in `struct puffs_ops`, fills reply fields, records errors in `preq_rv`, and sends replies back when required.

`puffs__ml_dispatch` dispatches within the main-loop context, then either enqueues the reply frame to the kernel fd or destroys no-reply frames. `puffs_dispatch_create` and `puffs_dispatch_exec` expose semi-supported manual dispatch through call contexts.

The main `dispatch` function handles VFS operations such as unmount, statvfs, sync, filehandle-to-node, node-to-filehandle, and extattr control. It handles many vnode operations: lookup, create, mknod, open/close, access, getattr/setattr with optional filesystem TTL support, mmap, fsync, seek, remove, link, rename, mkdir/rmdir, symlink, readdir, readlink, reclaim, inactive, pathconf, advisory locking, print, abortop, read/write, poll, extended attributes, fallocate, and fdiscard. It also handles PUFFS error notifications.

It integrates path building and pnode cookies when enabled, updates lookup counts, adjusts path objects on create/lookup/rename, reserves max message space for variable-size read/readdir/vptofh responses, and supports operation dump hooks plus pre/post operation callbacks.

Risks are broad dispatch complexity, optional callback defaults that sometimes return success and sometimes `EOPNOTSUPP`/`EIO`, path and lookup-count consistency, variable reply buffer sizing, and old comments noting return-value and kernel synchronization audit needs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/dispatcher.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/flush.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/flush.c

This file implements public helpers for asking the PUFFS kernel side to invalidate or flush namecache and pagecache state. The shared helper `doflush` allocates a frame buffer, obtains a typed window for `struct puffs_flush`, fills the embedded request header with buffer length, `PUFFSOP_FLUSH`, and a new request id, sets operation, cookie, start, and end offsets, then enqueues it through `puffs_framev_enqueue_cc` on the current call context and selectable fd.

Public wrappers issue directory/all namecache invalidation, whole-node pagecache invalidation, ranged pagecache invalidation, whole-node pagecache flush, and ranged pagecache flush.

Integration points: depends on framebuf construction, request ids from `puffs__nextreq`, current call context lookup, and frame-vector send/yield behavior. Risks are needing a valid call context, allocation failure, and offset semantics for ranged operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/flush.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/framebuf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/framebuf.c

This file implements libpuffs frame buffers and frame-vector I/O scheduling. A `puffs_framebuf` stores callback or call-context continuation state, an expandable byte buffer, cursor/max offsets, completion errno, internal state flags, and queue links. Basic APIs allocate, destroy, recycle, duplicate, reserve space, put/get data at current or explicit offsets, seek, expose windows, and return the raw data pointer.

The enqueue APIs place buffers on per-fd send queues in blocking call-context mode, callback mode, just-send mode, direct receive, direct send, or event-wait mode. Blocking APIs mark buffers non-destroyable while queued and yield the current call context until completion. Error notification resumes a context, calls a callback, or destroys the frame.

`puffs__framev_input` reads frames via a supplied frame controller, matches responses to outstanding request buffers with `cmpfb`, moves buffer ownership from internal read buffers to app buffers, calls `gotfb` for unsolicited frames, and resumes contexts/callbacks. `puffs__framev_output` writes queued frames, moves reply-waiting frames to the response queue, destroys no-reply frames, or resumes direct senders. The file also manages kqueue registration, fd enable/disable, read/write close notification, fd removal, and frame-controller initialization/exit.

Risks are high due to queued ownership flags, partial I/O, response matching, direct-buffer paths, context resumption during list iteration, and fd close races.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/framebuf.c -->