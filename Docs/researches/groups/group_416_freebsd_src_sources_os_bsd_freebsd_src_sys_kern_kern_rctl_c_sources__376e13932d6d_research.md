# Group Research: FreeBSD sys/kern resource controls, resource accounting, locks, sendfile, and shared page files

Scope source: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_rctl.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_rctl.c

Read completely: 2247 lines.

## Purpose
Implements FreeBSD's RACCT-backed resource control facility (`rctl`): rule parsing, rule storage, enforcement actions, rule inheritance, credential-change relinking, and the `rctl_*` syscalls.

## Main Elements
- Compiles only under `RCTL` and requires `RACCT`; otherwise exports `sys_rctl_*` stubs returning `ENOSYS`.
- Defines string dictionaries for subject types (`process`, `user`, `loginclass`, `jail`), RACCT resource names, and actions including signals, `deny`, `log`, `devctl`, and `throttle`.
- Maintains `struct rctl_rule` objects in UMA storage and attaches them to RACCT containers via `struct rctl_rule_link`, with rule refcounts and delayed freeing through `taskqueue_thread`.
- Implements throttling parameters and sysctls under `kern.racct.rctl`, including minimum/maximum sleep duration and process/container penalty percentages.
- `rctl_enforce()` evaluates every rule linked to a process for a resource, rate-limits log/devctl notifications, sends signals, applies throttling through `racct_proc_throttle()`, and defers final denial until other side effects have run.
- `rctl_get_limit()`, `rctl_get_available()`, and `rctl_pcpu_available()` expose effective resource ceilings for consumers, with special handling for percent-CPU.
- `rctl_string_to_rule()` parses user rule/filter strings in the form `subject:id:resource:action=amount/per`, resolves process, UID, loginclass, and jail subjects, and converts "millions" RACCT resources.
- `rctl_rule_add()` validates deny/throttle compatibility, removes duplicates, links rules to the subject RACCT, and walks all processes to attach applicable inherited rules.
- `rctl_rule_remove()` removes matching rules from process, user, loginclass, jail, and all-process RACCT lists.
- `sys_rctl_get_racct()`, `sys_rctl_get_rules()`, `sys_rctl_get_limits()`, `sys_rctl_add_rule()`, and `sys_rctl_remove_rule()` implement the privileged user ABI with bounded input/output buffers.
- `rctl_proc_ucred_changed()` rebuilds a process rule-link list after credential changes, preserving per-process rules and retrying if global rule lists change during allocation.
- `rctl_proc_fork()` duplicates process-subject rules for children and links inherited non-process rules; `rctl_racct_release()` tears down all rule links for a RACCT.

## Dependencies And Integration
Tightly integrated with RACCT accounting, process and credential structures, UID/loginclass/jail RACCT containers, allproc locking, `devctl_notify()`, signal delivery, taskqueues, UMA, sysctl/tunables, and privilege checks.

## Risk Notes
Correctness depends on RACCT lock coverage, allproc lock expectations during parsing/add/remove paths, avoiding rule-list races during credential changes, preserving rule refcounts across many container links, and keeping deny/throttle semantics aligned with RACCT resource properties. Output buffers are bounded, so large rule sets can return `ERANGE` or `E2BIG`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_rctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_resource.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_resource.c

Read completely: 1843 lines.

## Purpose
Implements process priority syscalls, realtime/idle priority conversion, resource limits, rusage accounting, copy-on-write `plimit` management, UID accounting objects, per-user limit counters, and rlimit-usage reporting.

## Main Elements
- Implements `getpriority(2)` and `setpriority(2)` through `kern_getpriority()` and `kern_setpriority()`, supporting process, process-group, and user scopes with Capsicum and visibility/scheduling permission checks.
- `donice()` clamps nice values and requires `PRIV_SCHED_SETPRIORITY` when raising scheduling priority.
- Implements `rtprio(2)` and `rtprio_thread(2)` lookups/updates, translating between `struct rtprio` and scheduler priority classes with `rtp_to_pri()` and `pri_to_rtp()`.
- Supports old 4.3BSD `ogetrlimit()`/`osetrlimit()` compatibility when enabled.
- `kern_proc_setrlimit()` performs privileged hard-limit changes, clamps data/stack/nofile/nproc limits to kernel maxima, updates CPU-limit callouts, updates stack VM protections when soft stack limits change, and uses copy-on-write `struct plimit` replacement.
- `lim_cb()` periodically checks CPU time limits, sends `SIGXCPU` below the hard limit, and kills processes beyond the maximum.
- `getrlimitusage_one()` reports current use for CPU, data, stack, RSS, locked memory, process count, open files, socket buffers, VMEM, ptys, swap, kqueues, umtxs, pipe buffers, and VMM resources.
- Implements `getrusage(2)` via `kern_getrusage()`, with `RUSAGE_SELF`, `RUSAGE_CHILDREN`, and `RUSAGE_THREAD`.
- Maintains precise runtime accounting with `calcru()`, `calccru()`, `calcru1()`, `rufetchtd()`, `rufetch()`, `rufetchcalc()`, `ruxagg()`, and overflow-safe `mul64_by_fraction()`.
- Manages `struct plimit` allocation, hold/free, fork sharing, thread COW synchronization, batch refcount release, and copying.
- Initializes and manages the UID hash table through `uihashinit()`, `uifind()`, `uilookup()`, `uihold()`, and `uifree()`, including per-UID RACCT creation/destruction when `RACCT` is enabled.
- Provides `ui_racct_foreach()` for RACCT/RCTL consumers to iterate UID accounting containers.
- Implements atomic per-user limit counters through `chglimit()` wrappers: process count, socket buffer size, ptys, kqueues, umtxs, pipes, inotify instances/watches, and VMM count.
- Exposes `kern.proc.rlimit_usage` sysctl output for all resources or one selected resource.

## Dependencies And Integration
Integrated with scheduler priority classes, process/session/process-group locking, Capsicum, privilege framework, VM maps and pmaps, file descriptor counting, RACCT, UMTX priority inheritance, callouts, sysctl, and per-UID credential state.

## Risk Notes
This file sits on hot process/resource paths. Risk centers on lock ordering between proc locks, stat locks, thread locks, UID hash locks, and VM references; accurate monotonic runtime conversion across long uptimes; copy-on-write limit lifetimes; and per-user counters staying balanced on all allocation/free paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_resource.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_rmlock.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_rmlock.c

Read completely: 1258 lines.

## Purpose
Implements machine-independent read-mostly locks: classic `rmlock` with per-CPU reader trackers and backing writer lock, plus sleepable read-mostly `rmslock`.

## Main Elements
- Registers lock classes `lock_class_rm` and `lock_class_rm_sleepable`, including generic lock/unlock/assert/owner hooks and optional DDB display support.
- Represents read ownership with caller-supplied `struct rm_priotracker` entries on per-CPU `pc_rm_queue` lists, allowing fast local reader acquisition without taking the writer lock in the common case.
- Uses `rm_writecpus` as a CPU token bitmap. Writers restore tokens for CPUs that have readers by rendezvous/IPI cleanup and gather active readers into `rm_activeReaders`.
- `_rm_rlock()` installs a tracker, pins the scheduler, and usually completes as a fast path; `_rm_rlock_hard()` handles missing CPU tokens, recursive read ownership, trylock failure, and backing writer-lock acquisition.
- `_rm_runlock()` removes the tracker, unpins the scheduler, and `_rm_unlock_hard()` wakes a waiting writer when a signaled active reader exits.
- `_rm_wlock()` takes the backing mutex or sx lock, gathers all outstanding readers, marks active readers for signaling, and waits on the rmlock turnstile until all active readers drain.
- `_rm_wunlock()` releases the backing writer primitive.
- Debug wrappers integrate with WITNESS, lock logging, lock counters, idle-thread checks, destroyed-lock detection, and recursion assertions.
- `_rm_assert()` can compute exact read recursion count for the current thread by walking the current CPU's tracker list.
- DDB support prints write CPU bitmap, per-CPU readers, active readers, and backing write-lock state.
- The second half implements `rmslock`, a sleepable read-mostly primitive with per-CPU reader counters, an `influx` flag for IPI synchronization, a mutex-serialized writer side, and no reader/writer priority propagation.
- `rms_rlock()`/`rms_runlock()` use per-CPU counters in the writer-free fast path; writer presence routes through fallback paths using the global mutex and sleep/wakeup.
- `rms_wlock()` switches all per-CPU reader counts into a global count using `smp_rendezvous_cpus_retry()`, waits for readers, serializes concurrent writers with transient ownership, and records the owning thread.

## Dependencies And Integration
Depends on per-CPU data, scheduler pinning, critical sections, SMP rendezvous/IPI mechanisms, turnstiles, WITNESS, lock profiling/logging, DDB, mutexes, sx locks, and UMA per-CPU allocation for `rmslock`.

## Risk Notes
The fast paths rely on strict interrupt fences, critical-section nesting, and per-CPU queue consistency during local interrupt traversal. Writers depend on correctly transferring readers from per-CPU lists/counters to global wait state. `rmslock` intentionally has no priority propagation and is suitable only for very rare writes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_rmlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_rwlock.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_rwlock.c

Read completely: 1582 lines.

## Purpose
Implements FreeBSD's machine-independent sleepable reader/writer lock core, including adaptive spinning, turnstile blocking, recursive writer support, upgrades/downgrades, lock-class integration, assertions, and DDB inspection.

## Main Elements
- Defines `lock_class_rw` with lock, trylock, unlock, assert, owner, and DDB hooks.
- Stores state in the packed `rw_lock` word: unlocked/read-count state, write owner thread pointer, reader/writer wait flags, writer spinner flag, and writer-recursed bit.
- `_rw_init_flags()` initializes WITNESS/profiling/recursion options; `_rw_destroy()` verifies unlocked/non-recursed state and marks destroyed locks.
- `_rw_wlock_cookie()` fast-acquires an unlocked lock by installing the current thread pointer, otherwise enters `__rw_wlock_hard()`.
- `__rw_try_wlock_int()` attempts nonblocking writer acquisition, including recursive writer acquisition when `LO_RECURSABLE` is set.
- `_rw_wunlock_cookie()` releases write ownership through inline fast unlock or `__rw_wunlock_hard()` for recursion and waiter cases.
- `__rw_can_read()` and `__rw_rlock_try()` implement reader admission policy: ordinary readers can enter only when there is no writer/writer-wait/spinner state, while recursive readers already holding a read lock may enter to avoid self-deadlock.
- `__rw_rlock_hard()` handles contended readers, including adaptive spinning on running writers or active readers, read-waiter flag management, turnstile sleeping, lockstat/KDTRACE accounting, and priority owner tracking.
- `__rw_try_rlock_int()` performs nonblocking reader count increments when the lock is in readable state.
- `__rw_runlock_try()` decrements reader count on the fast path; `__rw_runlock_hard()` handles last-reader release with waiters and wakes either shared or exclusive turnstile queues.
- `__rw_wlock_hard()` handles contended writers, recursive writer entry, adaptive spinning on running owners or reader counts, writer-spinner flag management, write-waiter flag setup, turnstile sleeping, and lock profiling.
- `__rw_wunlock_hard()` unwinds recursive writers or releases a contended write lock, preserving the appropriate waiter flag and broadcasting to either reader or writer waiters.
- `__rw_try_upgrade_int()` atomically upgrades a sole reader to writer, claiming the turnstile when waiter flags are preserved.
- `__rw_downgrade_int()` converts a writer to one reader, wakes compatible readers when no writer waiters are pending, and disowns or unpends the turnstile as needed.
- `__rw_assert()` validates read/write/locked/unlocked/recursive state using WITNESS when available and fallback state checks otherwise.
- DDB support prints unlocked/destroyed/read/write state, writer thread identity, recursion count, and waiter categories.

## Dependencies And Integration
Integrated with turnstiles and priority propagation, scheduler running-state checks, adaptive lock-delay tuning, WITNESS, lockstat/KDTRACE, HWPMC lock-failure hooks, lock profiling, DDB, and per-thread read-lock counters.

## Risk Notes
The packed-state protocol is subtle: waiter bits, spinner bits, reader counts, and owner pointers must be updated with the right acquire/release ordering. Fairness and latency depend on adaptive spinning heuristics and the choice of which turnstile queue to wake. Upgrades only succeed for a single reader and must preserve waiter ownership correctly.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_rwlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_sdt.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_sdt.c

Read completely: 69 lines.

## Purpose
Provides the base Statically Defined Tracing (SDT) provider symbols and probe trampolines used by DTrace-enabled kernels/modules.

## Main Elements
- Defines the `sdt` provider with `SDT_PROVIDER_DEFINE(sdt)`.
- Exposes `sdt_probe_func`, initially set to `sdt_probe_stub`, for the SDT provider module to replace with the real DTrace probe function.
- Exposes `sdt_probes_enabled` as a frequently-read global flag.
- `sdt_probe_stub()` reports unexpected probe execution and emits a kernel debugger backtrace.
- `sdt_probe()` forwards five explicit arguments plus a zero sixth argument.
- `sdt_probe6()` forwards six probe arguments.

## Dependencies And Integration
Used by SDT probe call sites and loadable DTrace/SDT provider code. Depends on `sys/sdt.h`, kernel printf, and `kdb_backtrace()` for unexpected stub execution.

## Risk Notes
This file is intentionally small. Probe sites rely on `sdt_probes_enabled` and provider setup to avoid calling the stub in unsupported configurations; an unexpected call is treated as diagnostic evidence and backtraced.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_sdt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_sema.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_sema.c

Read completely: 175 lines.

## Purpose
Implements kernel counting semaphores backed by a mutex and condition variable.

## Main Elements
- `sema_init()` zeroes the semaphore, initializes the backing mutex and condition variable, validates a nonnegative initial value, and stores the count.
- `sema_destroy()` asserts no waiters remain, then destroys the mutex and condition variable.
- `_sema_post()` increments the count and signals one waiter when waiters exist and the count is positive.
- `_sema_wait()` sleeps in a loop while the count is zero, tracks waiter count around `cv_wait()`, then decrements the count.
- `_sema_timedwait()` waits with a timeout, treats the timeout as a lower bound in the presence of spurious wakeups, and consumes a count on success.
- `_sema_trywait()` consumes a count only if immediately available.
- `sema_value()` returns the current count under the semaphore mutex.
- All operations emit KTR lock tracing with file/line data for wrapped internal calls.

## Dependencies And Integration
Uses kernel mutexes, condition variables, KTR lock tracing, and the public `sys/sema.h` API wrappers.

## Risk Notes
Semaphores do not model a single owner, so priority propagation generally cannot raise a useful owner priority. Destroying with waiters is invalid, and consumers must balance posts and waits to avoid leaked capacity or permanent sleepers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_sema.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_sendfile.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_sendfile.c

Read completely: 1322 lines.

## Purpose
Implements `sendfile(2)` and `vn_sendfile()`, moving file or shared-memory VM object pages to stream sockets with minimal copying, optional headers/trailers, asynchronous page-in, not-ready mbufs, readahead, `SF_NOCACHE`, and KTLS integration.

## Main Elements
- Defines `struct sf_io` to track one sendfile batch: in-flight I/O refcount, error state, socket, mbuf chain, VM object, base page index, pages, and optional KTLS state.
- Allocates and exports `sfstat` counters under `kern.ipc.sfstat`, with writable sysctl reset support.
- Provides mbuf external free callbacks for mapped `sf_buf` mbufs and unmapped `M_EXTPG` mbufs, releasing pages and optionally trying to free them for `SF_NOCACHE`.
- `xfsize()`, `vmoff()`, and `fixspace()` calculate per-page payload lengths, object offsets, and socket-space adjustments after page or `sf_buf` allocation failures.
- `sendfile_iowait()` waits for async page-ins to drain before unwiring pages on failure paths.
- `sendfile_iodone()` is the async pager completion callback and final completion path: restores bogus-page placeholders, unbusies pages, handles I/O errors by aborting the socket, notifies protocol readiness with `pr_ready()`, or queues software KTLS encryption work.
- `sendfile_swapin()` grabs and wires needed object pages, validates cached pages, zero-fills sparse/no-page regions, launches async pager reads for invalid runs, uses bogus pages for already-valid pages inside pager runs, records readahead stats, and recovers pages on I/O setup failure.
- `sendfile_getobj()` accepts only vnode regular files and shared-memory descriptors with VM objects, obtains object size safely, rejects dead objects, and takes a temporary VM object reference.
- `sendfile_getsock()` resolves the target descriptor with send rights, requires a connected stream socket, and rejects SCTP one-to-one sockets.
- `sendfile_wait_generic()` checks send-buffer state, adjusts auto low-water marks, handles nonblocking `EAGAIN`, waits for space, and reports socket errors/closed connection.
- `vn_sendfile()` is the core loop: gets source object and socket, performs MAC send checks, locks socket sending, holds KTLS session state, copies optional headers into mbufs, revalidates vnode size, computes socket-space-sized page batches and readahead, swaps pages in, builds either mapped `EXT_SFBUF` mbufs or unmapped `M_EXTPG` chains, marks not-ready pages when I/O is pending, frames TLS records, sends through protocol `pr_send()`, and updates byte counts.
- Handles trailers by releasing the socket send lock and delegating to `kern_writev()`.
- `sendfile()` copies in user `sf_hdtr`, handles FreeBSD 4 header-size compatibility, obtains the source fd with `CAP_PREAD`, calls fileops `fo_sendfile()`, and copies out `sbytes`.
- `sys_sendfile()` and optional `freebsd4_sendfile()` provide syscall entry points.

## Dependencies And Integration
Highly integrated with VM objects, vnode pager state, shared memory objects, `vm_page_grab_pages_unlocked()`, async pager I/O, socket send-buffer locking, protocol `pr_sendfile_wait`/`pr_send`/`pr_ready`, mbuf external storage, `sf_buf`, KTLS, MAC checks, Capsicum rights, audit, inotify access events, TCP logging, and VNET context switching.

## Risk Notes
Risk is concentrated around page lifetime and async I/O: pages must stay wired until mbufs free them, bogus-page substitution must be restored correctly, vnode/object size changes must not expose beyond EOF, and socket abort/error paths must free not-ready mbufs. Header/trailer accounting, KTLS references, and `SF_NODISKIO`/`SF_NOCACHE` partial-progress cases require careful byte-count and cleanup behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_sendfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_sharedpage.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_sharedpage.c

Read completely: 391 lines.

## Purpose
Initializes and manages the kernel-populated user shared page used for signal trampoline/VDSO data, fast userspace timekeeping, and optional FXRNG seed generation metadata.

## Main Elements
- Creates a one-page physical VM object at exec SYSINIT time, grabs and validates its page, maps it into kernel virtual address space, and exposes `shared_page_mapping`.
- Serializes allocations from the page with `shared_page_alloc_sx`, `shared_page_alloc_locked()`, `shared_page_alloc()`, and `shared_page_fill()`.
- `shared_page_write()` copies kernel data into the shared page at an allocated offset.
- `timehands_update()` writes native `vdso_timehands` data into a rotating slot, uses generation counters and release fences for lockless readers, updates the current slot, and records whether VDSO timekeeping is enabled.
- `timehands_update32()` mirrors the same scheme for 32-bit compatibility when `COMPAT_FREEBSD32` is enabled.
- Maintains singleton native and compat32 `struct vdso_sv_tk` pointers so hardclock-context `timekeep_push_vdso()` can update shared-page timekeeping without iterating sysentvec lists.
- `alloc_sv_tk()` and `alloc_sv_tk_compat32()` allocate shared-page timekeep regions, write VDSO timekeep version fields, and trigger an initial push.
- Optional `RANDOM_FENESTRASX` support allocates a cache-line-aligned shared-page FXRNG generation record and updates its 32-bit generation with release ordering via `fxrng_push_seed_generation()`.
- `exec_sysvec_init()` initializes a sysentvec's shared-page object, copies signal trampoline or VDSO signal code, registers native/compat32 timekeeping offsets, and assigns optional FXRNG generation offsets.
- `exec_sysvec_init_secondary()` copies initialized shared-page offsets and objects from a primary sysentvec to a secondary ABI-compatible sysentvec.

## Dependencies And Integration
Depends on VM pager/object/page primitives, kernel virtual mapping, pmap quick mappings, sysentvec ABI metadata, VDSO timecounter filling, exec initialization order, optional compat32 ABI support, and optional random/Fenestra SX support.

## Risk Notes
The shared page is size-limited and allocation failures are treated as panics for required ABI data. Lockless userspace timekeeping depends on generation-counter ordering and release fences. Singleton native/compat32 registration assumes sysentvec initialization order and ABI compatibility are correct.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_sharedpage.c -->