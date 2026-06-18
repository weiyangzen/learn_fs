# Group Research: FreeBSD sys process, resource, queue, locking, scheduler, and support headers

Scope source: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/proc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/proc.h

Read completely: 1380 lines.

## Purpose
Defines FreeBSD's central process/thread kernel data model and the public/kernel interfaces for process groups, sessions, threads, processes, scheduler-visible state, ptrace/debug flags, process lookup, forking, reaping, suspension, and machine-dependent thread/process hooks.

## Main Elements
- Defines `struct session`, `struct pgrp`, `struct pargs`, `struct rusage_ext`, `struct thread`, `struct thread0_storage`, and `struct proc`.
- Documents extensive locking keys for process, thread, process-group, and session fields.
- Defines thread state machine values, thread flags (`TDF_*`), AST indices (`TDA_*`), debugger flags (`TDB_*`), private thread flags (`TDP_*`, `TDP2_*`), and inhibitor/state macros.
- Defines process state values, process flags (`P_*`, `P2_*`), proctree flags, legacy process status constants, process magic, and switch/reason constants.
- Provides lock macros for process, process spin/stat/itim/prof locks, process group locks, and session locks.
- Provides process hold/release macros (`PHOLD`, `PRELE`) and process copy-on-write generation helpers.
- Exposes PID and process-group hash globals, `allproc`, `proctree_lock`, `proc0`, `thread0`, `vmspace0`, process limits, UMA zones, and process/thread list head types.
- Defines `struct fork_req` and flags for `fork1()` behavior, including process-descriptor and kernel-process creation fields.
- Declares process lookup (`pfind`, `pget`, `tdfind`), process visibility/permission helpers, process-group/session operations, fork/exit/reparent/reap operations, thread allocation/lifecycle/suspension operations, AST scheduling, CPU context hooks, and global stop/resume controls.
- Provides inline helpers for current-thread pflags save/restore, scheduler-private thread storage access, kernel-stack top lookup, and `rusage_ext` reset.
- Declares process and thread eventhandler lists.

## Dependencies And Integration
Integrates nearly every kernel subsystem touching processes: scheduler, signals, credentials, file descriptors, VM spaces, jails, RACCT/RCTL, kqueue, audit, DTrace, ktrace, MAC, procdesc, timers, callouts, turnstiles, sleepqueues, machine-dependent CPU/thread state, and UMA allocation.

## Risk Notes
This is a core ABI/KPI contract. Field ordering, lock annotations, flag meanings, and macro side effects are relied on widely. Changes can break scheduler state, process lifetime rules, ptrace semantics, process reaping, credential checks, or machine-dependent context switching.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/proc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/procctl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/procctl.h

Read completely: 169 lines.

## Purpose
Defines the user/kernel command ABI for `procctl(2)`, including process protection, reaper control, tracing/coredump controls, capability-trap behavior, ASLR/protection policy, no-new-privs, W^X, and signal-exit logging.

## Main Elements
- Reserves machine-dependent command space starting at `PROC_PROCCTL_MD_MIN` and includes `<machine/procctl.h>`.
- Defines command numbers `PROC_SPROTECT` through `PROC_LOGSIGEXIT_STATUS`.
- Defines protected-process operations and inheritance/descendant flags.
- Defines reaper status, descendant PID query, and reaper kill structures with fixed padding for ABI stability.
- Defines reaper, trace, trapcap, ASLR, PROT_MAX, stack-gap, no-new-privs, W^X, and logsigexit control/status constants.
- Declares `procctl(idtype_t, id_t, int, void *)` for userland.

## Dependencies And Integration
Used by `kern_procctl.c`, process reaper state in `struct proc`, security policy toggles in `p_flag2`, machine-dependent procctl extensions, and userland tools controlling process subtrees and hardening policy.

## Risk Notes
Command numbers and structure layouts are syscall ABI. Padding fields preserve forward compatibility; changing constants or layout would affect existing binaries and process-management tools.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/procctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/procdesc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/procdesc.h

Read completely: 145 lines.

## Purpose
Defines process descriptor kernel state and userland process-descriptor syscalls for fd-based process lifecycle control.

## Main Elements
- In-kernel `struct procdesc` links one process to one process-descriptor file, caches pid, tracks refcount, exit status, flags, selinfo notification, and a mutex.
- Defines lock macros for process descriptor mutex lifecycle and access.
- Defines descriptor state flags `PDF_CLOSED`, `PDF_EXITED`, and `PDF_DAEMON`.
- Declares kernel helpers for procdesc exit notification, fd lookup, pid retrieval, creation, file initialization, reaping, and allocation.
- Declares userland syscalls `pdfork`, `pdrfork`, `pdkill`, `pdgetpid`, `pdwait`, and `pdrfork_thread`.
- Defines user flags `PD_DAEMON`, `PD_CLOEXEC`, and `PD_ALLOWED_AT_FORK`.

## Dependencies And Integration
Integrates with process lifetime, file descriptors, Capsicum rights, `selinfo`/poll/kqueue notification, proctree locking, and wait/reap behavior.

## Risk Notes
The invariant of one process descriptor per process is central. Lifetime is split between process and file references, so refcounting, close-vs-exit races, and notification state must stay consistent.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/procdesc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/procfs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/procfs.h

Read completely: 120 lines.

## Purpose
Defines procfs/core-dump debugger structures used to expose register and process information to debuggers, especially ELF core consumers.

## Main Elements
- Typedefs machine register sets as `gregset_t`, `fpregset_t`, `prgregset_t`, and `prfpregset_t`.
- Defines stable `prstatus_t` with version, structure/register sizes, OS release, current signal, thread id, and general registers.
- Defines `prpsinfo_t` with version, command name, arguments, and process id.
- Defines `thrmisc_t` for thread name notes and `psaddr_t` for target addresses.
- Provides 32-bit compatibility structures when `__HAVE_REG32` is present.

## Dependencies And Integration
Used by procfs, core dump generation, debuggers, machine register definitions, and 32-bit compatibility core note emission.

## Risk Notes
The file explicitly warns not to change or remove existing structure fields. These layouts are debugger/core-file ABI and must remain backward compatible.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/procfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/protosw.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/protosw.h

Read completely: 183 lines.

## Purpose
Defines the socket protocol switch table KPI used by domains/protocols to plug protocol operations into the socket layer.

## Main Elements
- Declares protocol operation typedefs for attach/detach, bind/connect/listen/accept, send/receive, sendfile readiness, control operations, polling, kqueue, AIO, shutdown, address queries, labels, fd close, and chmod.
- Defines `pr_send_flags_t` including OOB, EOF, more-to-come, not-ready, and IPv6 flags.
- Defines `struct protosw` with socket type, protocol number, flags, domain pointer, and function pointers grouped by cache-line comments.
- Defines protocol behavior flags such as `PR_ATOMIC`, `PR_ADDR`, `PR_CONNREQUIRED`, `PR_WANTRCVD`, `PR_IMPLOPCL`, `PR_CAPATTACH`, and `PR_SOCKBUF`.
- Declares domain/protocol lookup and registration functions plus known `inetdomain` and `inet6domain`.

## Dependencies And Integration
Used by network domains, socket creation and dispatch, sendfile/KTLS readiness callbacks, socket buffer policy, Capsicum attach rules, MAC labeling, AIO, kqueue, and protocol module registration.

## Risk Notes
Function pointer signatures and flag semantics are protocol KPI. Incorrect handler setup can break socket lifecycle, sendfile readiness, address handling, or protocol unload/register safety.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/protosw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ptio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ptio.h

Read completely: 37 lines.

## Purpose
Defines CAM passthrough timeout ioctl numbers.

## Main Elements
- Includes `sys/ioccom.h`.
- Defines `PTIOCGETTIMEOUT` as an integer read ioctl.
- Defines `PTIOCSETTIMEOUT` as an integer write ioctl.

## Dependencies And Integration
Used by passthrough device interfaces that expose timeout configuration via ioctl.

## Risk Notes
The ioctl group/number/type are user ABI; changing them would break existing callers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ptio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ptrace.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ptrace.h

Read completely: 281 lines.

## Purpose
Defines the `ptrace(2)` request ABI, event masks, data structures, and kernel helper prototypes for process/thread debugging, memory/register access, syscall tracing, VM map inspection, coredump requests, and remote syscalls.

## Main Elements
- Defines standard ptrace requests from `PT_TRACE_ME` through `PT_SC_REMOTE`, plus machine-specific ranges and kernel-internal request range.
- Includes machine-specific ptrace extensions from `<machine/ptrace.h>`.
- Defines ptrace event mask bits for exec, syscall entry/exit, fork, LWP, and vfork.
- Defines `struct ptrace_io_desc` and PIOD read/write operation constants.
- Defines `struct ptrace_lwpinfo` and 32-bit variant with event, flags, signal state, thread name, child pid, and syscall metadata.
- Defines syscall return, VM map entry, coredump, and remote syscall argument structures.
- Under `_KERNEL`, defines coredump/syscall request carrier structs and declares register, single-step, machine-dependent, memory I/O, compat32 register, and unsuspend helpers.
- Declares userland `ptrace()` and exposes `allow_ptrace` in-kernel.

## Dependencies And Integration
Integrated with signals, machine registers, proc/thread state, procfs/linprocfs, VM maps, vnode coredump output, syscall argument handling, compat32, and process debug flags from `proc.h`.

## Risk Notes
This is a debugger ABI. Request numbers, structure layouts, flag meanings, and compat32 translations must remain stable. Kernel helpers must preserve stopped-process, thread-suspension, and register-access invariants.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ptrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/qmath.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/qmath.h

Read completely: 638 lines.

## Purpose
Provides macro-based fixed-point “Q” number types and arithmetic/conversion helpers with embedded control bits describing fractional precision.

## Main Elements
- Defines signed/unsigned Q storage typedefs from 8-bit through 64-bit and max aliases.
- Reserves the low 3 bits of each value for precision control, encoding fractional precision as 2, 4, 6, 8, 16, 32, 48, or 64 effective bits subject to storage size.
- Defines macros for type casting, total/control/fractional/integer/sign bit counts, radix shift, sign setting, control masks, integer/fraction masks, and raw/value getters/setters.
- Provides decimal-to-binary fractional conversion, initialization, C-string rendering, max string length calculation, float/double conversion, and debug printf format/data generation.
- Provides comparison and representability checks across Q values and integers.
- Provides value cloning/copying, addition/subtraction, multiplication/division, and fraction creation for Q-to-Q and Q-to-integer operations.
- Returns conventional errors such as `EINVAL`, `EOVERFLOW`, and `ERANGE` from arithmetic macros on invalid input, overflow, or underflow.

## Dependencies And Integration
Depends on integer types, compiler `__typeof`, bit scanning/popcount builtins, and errno values provided by consumers. Intended for low-level fixed-point math without runtime helper functions.

## Risk Notes
This header is macro-heavy and evaluates some arguments multiple times. Precision normalization is explicitly incomplete (`Q_NORMPREC` returns `ERANGE` when precision differs), so callers must understand precision compatibility and side effects.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/qmath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/queue.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/queue.h

Read completely: 1097 lines.

## Purpose
Defines FreeBSD's intrusive linked-list macro library: singly-linked lists, singly-linked tail queues, doubly-linked lists, and tail queues.

## Main Elements
- Documents operation availability and complexity for SLIST, STAILQ, LIST, and TAILQ.
- Supports optional queue macro debug tracing, pointer trashing, and structural assertions; kernel `INVARIANTS` can enable assertions automatically.
- Defines C and C++ head/entry variants for each queue family.
- SLIST supports head/entry declaration, initialization, empty/first/next access, forward and safe iteration, O(n) concatenation/removal, prevptr removal, split, swap, and atomic-empty reads.
- STAILQ supports head/tail insertion, concatenation, last lookup, forward/safe iteration, remove/split/swap/reverse, and tail invariant checks.
- LIST supports O(1) arbitrary removal/replacement via back-pointers, before/after/head insertion, forward/safe iteration, previous lookup, split, swap, and structural checks.
- TAILQ supports head/tail/before/after insertion, forward/reverse/safe iteration, fast last/previous lookup variants, concatenation, removal/replacement, split, swap, tracing, and structural checks.
- Provides `_EMPTY_ATOMIC` helpers using atomic pointer loads for all queue families.

## Dependencies And Integration
Used throughout the kernel and userland headers as the basic intrusive container facility. Depends on `sys/cdefs.h`, `__containerof`, optional atomics, panic/abort behavior for debug assertions, and consumer-provided element fields.

## Risk Notes
Macros assume correct intrusive field ownership and external synchronization. Removing or reusing elements incorrectly can corrupt lists; debug modes help catch bad prev/next/tail links but alter layout when tracing is enabled.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/queue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/queue_mergesort.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/queue_mergesort.h

Read completely: 217 lines.

## Purpose
Adds merge and mergesort macros for the queue types defined in `sys/queue.h`.

## Main Elements
- Provides shims to normalize differing queue macro signatures across SLIST, LIST, STAILQ, and TAILQ.
- Defines `SYSQUEUE_MERGE()` to pull entries from one sorted list into another using a `qsort_r`-style comparator.
- Defines `SYSQUEUE_MERGE_SUBL()` to merge sorted sublists inside a working list.
- Defines `SYSQUEUE_MERGESORT()` using bottom-up power-of-two sorted-run invariants, moving all elements into a working list and then concatenating sorted output back.
- Exposes `SLIST_MERGESORT`, `LIST_MERGESORT`, `STAILQ_MERGESORT`, `TAILQ_MERGESORT`, and corresponding `*_MERGE` macros.

## Dependencies And Integration
Depends on queue head/entry operations from `sys/queue.h` and caller-provided comparator signature `cmp(a, b, thunk)`.

## Risk Notes
The macros mutate list heads and element links in place. Comparator consistency and correct queue type/field arguments are required; macro expansion can be large and has no type-safe wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/queue_mergesort.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/racct.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/racct.h

Read completely: 282 lines.

## Purpose
Defines FreeBSD resource accounting identifiers, resource properties, accounting container structure, and RACCT kernel API/stubs.

## Main Elements
- Defines RACCT resource IDs for CPU, data, stack, core, RSS, memlock, process/file/VM counts, IPC resources, wallclock, percent CPU, and I/O rate resources.
- Defines resource property bits for million-scaled values, reclaimable usage, inheritable usage, deniable allocations, sloppy per-credential accounting, and decaying resources.
- Provides macros to query resource properties and whether resource usage can drop.
- Defines `struct racct` with resource counters, linked RCTL rule links, runtime, and timestamp.
- Declares RACCT sysctl node and global enable/type state.
- Under `RACCT`, declares global lock macros and APIs for add/set/subtract, credential accounting, buffer I/O accounting, limits/availability, create/destroy, fork/exit/credential-change handling, moving accounting, and throttling.
- Without `RACCT`, supplies no-op or permissive inline stubs returning success or `UINT64_MAX`.

## Dependencies And Integration
Used by process, credential, jail, UID, and RCTL code to account and enforce resources. Integrates with `struct proc`, `struct ucred`, buffers, sysctl, and global RACCT locking.

## Risk Notes
Resource property classification drives enforcement semantics. Stub behavior means consumers must tolerate RACCT-disabled kernels where accounting calls succeed but do not enforce limits.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/racct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/random.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/random.h

Read completely: 172 lines.

## Purpose
Defines kernel random-device interfaces, entropy source identifiers, harvest helpers, and the userland `getrandom(2)` API flags/prototype.

## Main Elements
- Supports loadable random implementations through function pointers for `read_random`, `read_random_uio`, and `is_random_seeded`; non-loadable builds declare normal functions.
- Enumerates environmental and hardware/pure entropy sources, with a static assertion limiting source count to a word-sized bitset assumption.
- Defines boot entropy module names.
- Declares harvest source mask and queued/fast/direct harvest backends.
- Provides inline harvest wrappers that check `hc_source_mask` before submitting entropy.
- Provides compile-time feature wrappers for UMA and Ethernet entropy harvesting.
- For userland, includes fortified random declarations when enabled.
- Defines `GRND_NONBLOCK`, `GRND_RANDOM`, and `GRND_INSECURE`, and declares `getrandom()`.

## Dependencies And Integration
Integrated with randomdev, entropy harvest queues, hardware RNG drivers, UMA/network entropy hooks, boot entropy modules, `uio`, and userland random APIs.

## Risk Notes
Entropy source numbering is mirrored by descriptive strings elsewhere and constrained to fit a bitmask. Loadable-random kernels rely on proper initialization before function-pointer use.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/random.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/rangelock.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/rangelock.h

Read completely: 105 lines.

## Purpose
Defines range-lock state and kernel APIs for read/write locking byte ranges with overlap-aware compatibility.

## Main Elements
- Defines read/write lock type bits and type mask.
- Defines `struct rangelock` with packed head, sleeper state, and reserved fields intended for embedding consumers.
- Documents compatibility: non-overlapping ranges can coexist; overlapping readers can coexist; overlapping writers conflict.
- Declares initialization, destruction, unlock, blocking and try read/write lock operations, recursion allowance, and invariant cookie assertions.
- Defines assertion flags for locked/read-locked/write-locked cookies.

## Dependencies And Integration
Used by kernel consumers needing byte-range exclusion, notably vnode/file-style range coordination. Depends on VM offset types and invariant support.

## Risk Notes
The returned cookie represents lock ownership and must be released exactly once. Embedded reserved fields are intentionally available to consumers, so structure layout is part of an internal KPI.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/rangelock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/rangeset.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/rangeset.h

Read completely: 94 lines.

## Purpose
Declares the kernel rangeset API for maintaining non-overlapping or managed integer ranges with caller-embedded elements.

## Main Elements
- Includes private `_rangeset` definitions under `_KERNEL`.
- Defines predicate callback type `rs_pred_t`.
- Defines `struct rs_el`, which must be embedded at the start of application data and stores start/end range keys.
- Declares init/fini, empty checks, insert, remove all, remove by range, remove by predicate, containing lookup, range-empty query, beginning lookup, and copy operations.
- Documents that remove may need to split elements and can fail with `ENOMEM` without modifying the set.
- Documents copy failure leaves destination empty.

## Dependencies And Integration
Used by kernel range-tracking subsystems and backed by the private rangeset implementation, including pctrie-style start keys and caller-provided duplication/free callbacks.

## Risk Notes
Caller data layout must start with `struct rs_el`. Removal and copy have transactional guarantees that implementation and callbacks must preserve.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/rangeset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/rctl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/rctl.h

Read completely: 171 lines.

## Purpose
Defines FreeBSD resource-control rule structures, subject/action constants, kernel enforcement APIs, and userland `rctl_*` syscall interfaces.

## Main Elements
- Describes rule linking through RACCT containers rather than a global rule list.
- Defines immutable-after-link `struct rctl_rule` with subject union, per/resource/action/amount fields, refcount, and delayed task.
- Defines subject types for process, user, loginclass, and jail.
- Maps signal actions to signal numbers and defines non-signal actions `DENY`, `LOG`, `DEVCTL`, and `THROTTLE`.
- Declares kernel APIs for rule allocation/duplication/refcounting, add/remove, enforcement, throttle decay, percent-CPU availability, effective limits/availability, resource names, credential change, fork, and RACCT release.
- Declares userland syscalls for querying RACCT usage, rules, limits, adding rules, and removing rules via input/output buffers.

## Dependencies And Integration
Tied to RACCT, process/user/loginclass/jail subjects, signal delivery, taskqueue-delayed rule freeing, and the rctl syscall ABI.

## Risk Notes
Rules are immutable after linking and refcounted through rule links. Subject/action/resource constants are ABI/KPI; malformed changes can break enforcement or userland rule parsers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/rctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/reboot.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/reboot.h

Read completely: 70 lines.

## Purpose
Defines reboot/boot flags passed through reboot paths, boot programs, and init.

## Main Elements
- Defines `RB_AUTOBOOT` and flags for asking root name, single-user boot, no sync, halt, default root, debugger, read-only root, crash dump, verbose boot, serial/CD-ROM console/root options, poweroff, GDB, muted console, pause, reroot, powercycle, kexec, console probing, multiple consoles, and bootinfo argument presence.
- Includes reserved/unused placeholders for compatibility.

## Dependencies And Integration
Used by kernel reboot/shutdown paths, boot loader/boot blocks, init behavior, console selection, dump handling, and root filesystem behavior.

## Risk Notes
Flag values are cross-component ABI. Reserved and unused values should not be casually repurposed because boot components may pass them through.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/reboot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/refcount.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/refcount.h

Read completely: 220 lines.

## Purpose
Provides atomic unsigned reference count helpers with saturation protection and acquire/release memory ordering.

## Main Elements
- Defines saturated refcount detection and saturation value.
- On overflow/underflow, panics under `INVARIANTS` or stores saturation to prefer leaks over premature object destruction.
- Provides initialization, load, acquire, acquire-n, checked acquire, acquire-if-greater-than, and acquire-if-not-zero helpers.
- Provides release-n/release helpers with release fence before decrement and acquire fence on last reference.
- Defines conditional release helper generators for greater-than and equal-to cases.
- Provides public conditional release helpers for `release_if_gt`, `release_if_last`, and `release_if_not_last`.

## Dependencies And Integration
Used throughout kernel lifetime management. Depends on machine atomic operations, kassert/panic behavior, and C bool support outside kernel/standalone.

## Risk Notes
Correct destructor visibility depends on the release/acquire fences. Saturation avoids use-after-free on wraparound but can leak objects; callers must check result-use annotations where required.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/refcount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/reg.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/reg.h

Read completely: 91 lines.

## Purpose
Wraps machine register definitions and declares kernel register-set infrastructure for ptrace/core/debug consumers.

## Main Elements
- Includes `<machine/reg.h>`.
- Under `_KERNEL`, defines `regset_get` and `regset_set` callback types.
- Defines `struct regset` with ELF note id, size, get callback, and set callback.
- Declares linker sets for native and compat32 ELF register sets.
- Declares native register/fpreg/dbreg fill and set functions.
- Declares compat32 register accessors when `COMPAT_FREEBSD32` is enabled, with macro-guarded declarations for optional machine overrides.

## Dependencies And Integration
Integrated with ELF core note generation, ptrace register access, machine-dependent register layouts, linker sets, and compat32 support.

## Risk Notes
Register-set note IDs, sizes, and callbacks are consumed by debuggers and core dump code. Machine headers control actual layout, so compatibility must be preserved per architecture.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/reg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/regression.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/regression.h

Read completely: 38 lines.

## Purpose
Declares regression-testing-only syscall support for userland.

## Main Elements
- For non-kernel builds, declares `__setugid(int)` as a kernel regression testing syscall interface.
- Contains no kernel declarations.

## Dependencies And Integration
Used by regression tests that need to manipulate or test setugid-related kernel behavior.

## Risk Notes
Small ABI surface. It should remain isolated to testing use; exposing or relying on it in production paths would be inappropriate.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/regression.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/resource.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/resource.h

Read completely: 201 lines.

## Purpose
Defines user/kernel resource usage, priorities, resource limits, load average, CPU state, and related syscall prototypes.

## Main Elements
- Defines `id_t` and `rlim_t` typedefs when needed.
- Defines priority range and `PRIO_PROCESS`, `PRIO_PGRP`, `PRIO_USER`.
- Defines `RUSAGE_SELF`, `RUSAGE_CHILDREN`, `RUSAGE_THREAD`, and `struct rusage`.
- Under BSD visibility, defines `struct __wrusage`.
- Defines resource limit IDs from CPU/file/data/stack/core through socket buffers, VMEM/AS, ptys, swap, kqueues, umtx, pipe buffers, and VMM.
- Defines `RLIM_NLIMITS`, `RLIM_INFINITY`, saved limit aliases, optional `rlimit_ident[]`, `struct rlimit`, old 32-bit `struct orlimit`, `struct loadavg`, CPU state indices, and `GETRLIMITUSAGE_EUID`.
- Kernel side declares `averunnable` and `read_cpu_time`; userland side declares `getpriority`, `getrlimit`, `getrusage`, `setpriority`, `setrlimit`, and BSD `getrlimitusage`.

## Dependencies And Integration
Used by process accounting, resource limit enforcement, scheduler/load reporting, libc syscall ABI, RACCT/RCTL mapping, and compatibility limit code.

## Risk Notes
Resource IDs and structure layouts are stable ABI. Adding limits requires synchronized updates across kernel enforcement, userland names, RACCT/RCTL mapping, and compatibility handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/resource.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/resourcevar.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/resourcevar.h

Read completely: 205 lines.

## Purpose
Defines kernel-private resource accounting/statistics structures and APIs for process stats, copy-on-write resource limits, UID resource counters, profiling, rusage aggregation, and limit updates.

## Main Elements
- Defines `struct pstats` with child rusage, interval timers, profiling parameters, and process start time, with zero/copy range markers.
- Defines `struct plimit` as shareable copy-on-write array of `struct rlimit` plus refcount.
- Defines `struct limbatch` helpers for batched limit reference release.
- Defines `struct uidinfo` with per-UID atomic counters for VM/swap reservations, socket buffers, processes, ptys, kqueues, umtxs, pipes, inotify, VMM, refcount, UID, and optional RACCT container.
- Declares profiling update functions, runtime accounting conversion, per-UID counter change functions, `kern_proc_setrlimit`, plimit allocation/copy/fork/free/hold/COW sync, current/max limit accessors, rusage aggregation/fetch, and UID hash/refcount helpers.
- Provides optimized `lim_cur` macro for constant non-VM/data/stack limits.

## Dependencies And Integration
Tied to `resource.h`, `proc.h`, UID credential state, RACCT, process timers/profiling, rusage accounting, and kernel limit enforcement.

## Risk Notes
Plimit COW and UID counters are shared hot paths. Counter increments/decrements must stay balanced, and limit access must account for VM/data/stack dynamic handling rather than only static array reads.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/resourcevar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/rman.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/rman.h

Read completely: 165 lines.

## Purpose
Defines the kernel resource manager interface for reserving, activating, adjusting, and exporting bus/device resource ranges.

## Main Elements
- Defines resource flags for allocated, active, shareable, first-share, prefetchable, optional, unmapped, and encoded alignment.
- Defines `enum rman_type`, `RM_TEXTLEN`, maximum resource end, and default-range test macro.
- Defines userspace-exported `struct u_resource` and `struct u_rman` snapshots.
- Under `_KERNEL`, defines public ABI-sensitive `struct resource` with opaque implementation pointer plus bus tag/handle fields.
- Defines `struct rman` with resource list, mutex, global list linkage, managed start/end, type, and description.
- Declares resource activation/deactivation, adjustment, free-region lookup, bus tag/handle/device/flag/rid/type/virtual/mapping accessors, init/fini/manage-region, reserve/release, alignment flag creation, and setters.
- Declares global `rman_head`.

## Dependencies And Integration
Used by bus/device drivers, machine bus space/resource definitions, resource sysctl/debug export, and device resource allocation/activation paths.

## Risk Notes
`struct resource` field offsets are explicitly device-driver ABI. Resource range and sharing flags must remain consistent with bus allocation/activation semantics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/rman.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/rmlock.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/rmlock.h

Read completely: 184 lines.

## Purpose
Declares read-mostly lock and sleepable read-mostly lock kernel APIs, wrappers, sysinit helpers, and assertions.

## Main Elements
- Includes mutex, sx, lock, and private `_rmlock` definitions.
- Defines `RM_NOWITNESS`, `RM_RECURSE`, `RM_SLEEPABLE`, `RM_NEW`, and `RM_DUPOK` init flags.
- Declares `rm_init`, `rm_init_flags`, `rm_destroy`, `rm_wowned`, sysinit, debug and non-debug read/write lock operations, runlock operations, and invariant assertions.
- Requires `LOCK_DEBUG` from `sys/lock.h` and maps public macros to debug or non-debug implementations.
- Provides `rm_sleep` wrapper against the lock object.
- Defines `RM_SYSINIT_FLAGS` and `RM_SYSINIT`.
- Defines assertion aliases mapping to generic lock assertion constants.
- Declares `rmslock` APIs for sleepable read-mostly locks and inline ownership/assertion helpers.

## Dependencies And Integration
Used by read-mostly synchronization consumers, WITNESS/lock debugging, lock objects, sleep, SYSINIT/SYSUNINIT, and the implementation in `kern_rmlock.c`.

## Risk Notes
Callers must provide per-read `rm_priotracker` storage and include lock headers in the correct order. Sleepable and non-sleepable variants have different behavior and must not be substituted casually.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/rmlock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/rtprio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/rtprio.h

Read completely: 94 lines.

## Purpose
Defines realtime/idle/normal priority classes and syscall ABI for `rtprio(2)` and `rtprio_thread(2)`.

## Main Elements
- Maps RTP priority classes to kernel priority classes from `sys/priority.h`.
- Exposes FIFO-related priority macros and helpers.
- Defines realtime priority numeric range, where 0 is highest and 31 is lowest.
- Defines syscall function selectors `RTP_LOOKUP` and `RTP_SET`.
- Defines `struct rtprio` with scheduling class type and priority.
- Kernel side declares conversion helpers between `struct rtprio` and thread priorities.
- Userland side declares `rtprio()` and `rtprio_thread()`.

## Dependencies And Integration
Used by scheduler priority conversion, resource/priority syscalls, userland realtime tools, and POSIX FIFO/RR priority mapping.

## Risk Notes
Class and range semantics must stay aligned with `priority.h` and scheduler implementations; userland ABI depends on `struct rtprio`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/rtprio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/runq.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/runq.h

Read completely: 124 lines.

## Purpose
Declares kernel run queue structures and helper APIs used by scheduler implementations.

## Main Elements
- Kernel-only header; rejects non-kernel inclusion.
- Defines maximum priority, priorities per queue, number of queues, and priority-to-queue-index mapping.
- Defines status word type and bit/word helper macros for finding non-empty run queues.
- Defines `TAILQ_HEAD(rq_queue, thread)`, `struct rq_status`, and `struct runq`.
- Declares initialization, empty test, add by priority/index, remove, non-empty test, choose, choose-with-fuzz, range first-thread, and generic predicate-based queue search helpers.

## Dependencies And Integration
Used by scheduler implementations to manage runnable thread queues. Depends on thread `td_runq` linkage, `sys/queue.h`, priority values, and bit-scan helpers.

## Risk Notes
Run queue bitmaps must match queue contents. Scheduler locking must protect queue operations; stale status bits can lead to missed runnable threads or invalid selections.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/runq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/rwlock.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/rwlock.h

Read completely: 299 lines.

## Purpose
Defines FreeBSD kernel reader/writer lock state encoding, fast-path macros, public lock API wrappers, sysinit helpers, and assertions.

## Main Elements
- Documents packed `rw_lock` word layout: read/write bit, waiter bits, write-spinner bit, writer-recursed bit, writer owner pointer or reader count.
- Defines lock flag masks, owner/read-count extraction, one-reader increment, unlocked, and destroyed encodings.
- Provides atomic fast-path macros for write lock/unlock and inline non-debug write acquisition/release.
- Declares internal initialization, destruction, sysinit, ownership, read/write lock/unlock, trylock, upgrade, downgrade, hard-path, and assertion functions.
- Maps public macros to debug/no-debug and inline/non-inline implementations depending on `LOCK_DEBUG` and `RWLOCK_NOINLINE`.
- Provides `rw_unlock`, `rw_sleep`, `rw_initialized`, `RW_SYSINIT_FLAGS`, and `RW_SYSINIT`.
- Defines init option flags and invariant assertion aliases.

## Dependencies And Integration
Used throughout the kernel for sleepable reader/writer synchronization. Integrates with lock objects, WITNESS, lockstat, PCPU/current-thread state, atomic operations, sleep, and `kern_rwlock.c`.

## Risk Notes
The packed-state protocol is subtle. Waiter bits, recursive writer state, reader counts, and owner pointers must be manipulated only through the lock API; callers must include `sys/lock.h` first so `LOCK_DEBUG` is defined.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/rwlock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sbuf.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sbuf.h

Read completely: 123 lines.

## Purpose
Defines the `sbuf` dynamic/fixed string buffer API used for safe formatted string construction and draining.

## Main Elements
- Declares opaque `struct sbuf` and drain callback type.
- Defines `struct sbuf` fields for buffer pointer, drain function/argument, error, size, length, flags, section length, and record offset.
- Defines flags for fixed length, autoextend, include-NUL accounting, drain-to-EOR, nonblocking extend, dynamic buffer/structure, finished state, in-section, and drain-ended-at-EOL.
- Defines hexdump formatting flags if not already present.
- Declares creation, flag access, clear/setpos, binary/string copy/append, printf/vprintf, newline termination, putc, drain setup/drain, trim, error, finish, data/length/done, delete, section start/end, hexdump, drain helpers, and putbuf.
- Kernel side declares uio-backed sbuf creation and copyin helpers plus DDB drain helper.

## Dependencies And Integration
Used by kernel and userland code that builds bounded or dynamically extending strings, sysctl output, diagnostics, hexdumps, and user-copying paths.

## Risk Notes
Consumers must respect `sbuf_finish()` before reading final data and handle sticky error state. Drain callbacks affect buffering semantics and can impose allocation/sleeping constraints.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sched.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sched.h

Read completely: 380 lines.

## Purpose
Defines the scheduler KPI, scheduler instance dispatch table, scheduler stats/probes, CPU binding/pinning helpers, and POSIX scheduling user ABI.

## Main Elements
- Kernel side declares general scheduler load/runnable/round-robin interval queries.
- Declares process and thread scheduler hooks for fork, exit, class/nice changes, priority lending, sleep/switch/throw, user priority, wakeup, preemption, run-queue add/remove/choose, CPU affinity, and accounting.
- Provides `sched_userret()` inline fast path and slowpath call for restoring user priority on return to userland.
- Defines temporary CPU pin/unpin inline helpers with interrupt fences.
- Defines `SRQ_*` flags for scheduler add/wakeup circumstances and lock-retention behavior.
- Provides optional `SCHED_STATS` per-CPU sysctl statistic macros and declares scheduler SDT probes.
- Declares DTrace virtual-time hooks when enabled.
- Declares scheduler initialization, AP initialization, timer-accounting query, and L2-neighbor lookup.
- Defines `struct sched_instance`, a full scheduler method table, active scheduler pointer, scheduler selection linker-set entry, `DECLARE_SCHEDULER`, and selection routine.
- Userland/POSIX side defines `SCHED_FIFO`, `SCHED_OTHER`, `SCHED_RR`, `struct sched_param`, and scheduling syscall prototypes.

## Dependencies And Integration
Connects process/thread code to concrete scheduler implementations such as ULE, run queues, DTrace/SDT probes, per-CPU stats, linker sets, priority definitions, and POSIX scheduling syscalls.

## Risk Notes
Scheduler implementations must fill the instance table coherently. Pin/unpin must be balanced, priority lending must be unwound correctly, and userland policy constants are ABI.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sched.h -->