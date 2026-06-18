# Group Research: group_1285_netbsd_src_sources_os_bsd_netbsd_src_sys_sys_ras_h_sources_os_bsd_n_bacf92dc66fb

Scope checked against `Docs/research_subset_a.md`; all listed files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every source file listed for this group was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ras.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ras.h

Read completely: 134 lines.

This header defines NetBSD restartable atomic sequences, or RAS, for userland and kernel consumers. It exposes `struct ras`, control operations `RAS_INSTALL`, `RAS_PURGE`, and `RAS_PURGE_ALL`, plus the userland `rasctl(void *, size_t, int)` interface.

For user code it provides declaration, address, size, and assembly-label macros: `RAS_DECL`, `RAS_START`, `RAS_END`, `RAS_ADDR`, `RAS_SIZE`, and assembly variants including hidden-symbol forms. Kernel code gets `ras_lookup`, `ras_fork`, and `ras_purgeall`.

Important behavior: the C macros emit global labels with compiler memory barriers, but the comments strongly prefer assembly-authored RAS regions because compiler-generated C may not be safely restartable.

Risks: correctness depends on exact instruction ranges and restart-safe machine code. ABI exposure is through symbol labels and `rasctl`, so label visibility and range sizing mistakes can break atomicity.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ras.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rbtree.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/rbtree.h

Read completely: 223 lines.

This header declares NetBSD's intrusive red-black tree API. `rb_node_t` stores left/right child pointers plus parent, color, and side-position bits packed into `rb_info`; `rb_tree_t` stores the root, operation table, cached min/max pointers, and optional debug/statistics fields.

The public API includes tree initialization, insertion, lookup, lower/upper-bound lookup, removal, and iteration through `rb_tree_init`, `rb_tree_insert_node`, `rb_tree_find_node`, `rb_tree_find_node_geq`, `rb_tree_find_node_leq`, `rb_tree_remove_node`, and `rb_tree_iterate`. Convenience macros provide min/max, next/previous, and safe forward/reverse traversal.

Important interactions: callers embed `rb_node_t` at an offset described by `rb_tree_ops_t` and supply node/key comparison functions. Optional `RBDEBUG` adds a TAILQ list of nodes and tree checking; optional `RBSTATS` tracks operation counts.

Risks: the parent/color packing assumes node alignment leaves the low two pointer bits free. Comparison callbacks define tree ordering, so inconsistent callbacks can corrupt lookup/removal semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rbtree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/reboot.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/reboot.h

Read completely: 124 lines.

This header defines reboot and bootloader flag constants. It includes `RB_*` system reboot flags, `AB_*` autoboot verbosity/debug flags, architecture-specific high-bit `RB_MD*` flags, and old boot-device-number encoding macros.

Key macros include `MAKEBOOTDEV`, `B_ADAPTOR`, `B_CONTROLLER`, `B_UNIT`, `B_PARTITION`, and `B_TYPE`. Kernel consumers get the non-returning `kern_reboot(int, char *)` and `cpu_reboot(int, char *)` prototypes.

Risks: this is an ABI/control-plane header. Flag values and boot-device bit layouts must remain stable for bootblocks, kernel initialization, and compatibility code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/reboot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/resource.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/resource.h

Read completely: 164 lines.

This public header defines process priority, resource-usage, and resource-limit ABI. It provides `PRIO_*`, `RUSAGE_*`, `struct rusage`, NetBSD `struct wrusage`, `RLIMIT_*` constants, `RLIM_INFINITY`, `struct rlimit`, and NetBSD `struct loadavg`.

Userland prototypes include `getpriority`, `setpriority`, `getrlimit`, `setrlimit`, and versioned `getrusage`. Kernel code also sees `struct orlimit`, `averunnable`, and `dosetrlimit`.

Important details: NetBSD defines 12 resource limits, including socket buffer, address space, and thread-count limits. `RLIM_INFINITY` is the maximum signed 63-bit quantity in an unsigned type.

Risks: layout and constant stability matters for libc, syscalls, core process accounting, and compatibility layers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/resource.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/resourcevar.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/resourcevar.h

Read completely: 133 lines.

This kernel/KMEMUSER-only header defines internal process accounting and resource-limit state. `struct uprof` stores profiling buffers and deferred AST accounting, while `struct pstats` stores per-process usage, child usage, interval timers, profiling state, and process start time.

The kernel-only `struct plimit` stores copy-on-write resource limits, core-file naming state, reference count, lock, writeability marker, and saved limit pointer. APIs cover profiling accounting, runtime usage calculation, limit copying/refcounting/private copies, core name updates, resource subsystem init, usage aggregation, pstats copy/free, and `getrusage1`.

Risks: `plimit` is shared after fork and privatized on mutation, so lock/refcount discipline is central. Profiling uses deferred fields updated from AST paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/resourcevar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rmd160.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/rmd160.h

Read completely: 57 lines.

This header declares the RIPEMD-160 digest interface. It defines digest, string, and block lengths; `RMD160_CTX`; and core routines `RMD160Init`, `RMD160Transform`, `RMD160Update`, and `RMD160Final`.

Userland additionally gets helpers to format or hash streams/files/data: `RMD160End`, `RMD160FileChunk`, `RMD160File`, and `RMD160Data`.

Risks: no logic in the header. The context layout is ABI-visible to code that allocates it directly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rmd160.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rnd.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/rnd.h

Read completely: 52 lines.

This kernel-only header declares the core random-device entry points. It defines minor numbers for blocking `/dev/random` and nonblocking/random-generating `/dev/urandom`, and declares `rnd_init`, `rnd_init_softint`, `rnd_seed`, and `rnd_system_ioctl`.

Risks: the header is small, but it sits on the randomness initialization and ioctl boundary. Correct consumers must include the richer source/ioctl headers for source registration or userspace control structs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rnd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rndio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/rndio.h

Read completely: 173 lines.

This public random-subsystem ioctl header defines userspace-visible save/load, statistics, source description, source-control, and entropy-injection structures. Key types are `rndsave_t`, `rndpoolstat_t`, `rndsource_t`, `rndsource_est_t`, `rndstat_t`, `rndstat_est_t`, name-specific stat wrappers, `rndctl_t`, and `rnddata_t`.

It defines source flags such as collection/estimation controls, fast processing, callbacks, and enable hooks, plus source type IDs for disk, network, tty, hardware RNG, VM, power, and related sources. Ioctls include `RNDGETENTCNT`, source enumeration/name lookups, `RNDCTL`, `RNDADDDATA`, `RNDGETPOOLSTAT`, and entropy-estimate variants.

Risks: this is a privileged entropy-control ABI. `RNDADDDATA` includes caller-supplied entropy estimates, and source control flags can disable collection/estimation, so access control in the implementation is security-sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rndio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rndsource.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/rndsource.h

Read completely: 102 lines.

This kernel-only header defines entropy-source registration and input APIs. It defines `rnd_delta_t` for time/value delta entropy estimation and `struct krndsource`, the driver-allocated per-source state carrying name, type, flags, cold entropy counters, callback pointers, and ABI-preserved unused fields.

Main APIs include `rndsource_setcb`, `rnd_attach_source`, `rnd_detach_source`, legacy `_rnd_add_uint32/_rnd_add_uint64`, and modern `rnd_add_uint32`, `rnd_add_data`, `rnd_add_data_intr`, and `rnd_add_data_sync`.

Risks: source structs are treated as opaque by drivers but contain ABI-preserved fields. Call-context matters: interrupt, sync, and generic data-add paths have different constraints.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rndsource.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rngtest.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/rngtest.h

Read completely: 49 lines.

This header defines a small FIPS 140 random-number generator test state. It sets the test window to 20,000 bits, defines `rngtest_t` with sample bytes, poker/run counters, error count, and source name, and declares `rngtest`.

Risks: no implementation here. Consumers must treat the result as a statistical health check, not proof of cryptographic quality.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rngtest.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rpst.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/rpst.h

Read completely: 67 lines.

This header declares a priority search tree structure. `struct rpst_tree` holds root and height, `struct rpst_node` stores parent, two children, and `x/y` keys, and `struct rpst_iterator` stores range-iteration state.

APIs include tree initialization, insert, remove, first matching node, and next matching node: `rpst_init_tree`, `rpst_insert_node`, `rpst_remove_node`, `rpst_iterate_first`, and `rpst_iterate_next`.

Risks: callers manage node storage and key values directly. Correct range iteration depends on tree invariants maintained by the implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rpst.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rwlock.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/rwlock.h

Read completely: 120 lines.

This header defines the kernel reader/writer lock type and interface. `krw_t` distinguishes `RW_READER` and `RW_WRITER`, and `struct krwlock` contains the volatile owner word.

When `__RWLOCK_PRIVATE` is set, the file exposes packed owner-word bits for waiters, write-wanted, write-locked, debug disable, reader-count shift/increment, owner/count extraction, and vector fallback functions. Kernel APIs cover init/destroy, enter/exit, tryenter, upgrade/downgrade, ownership tests, lock operation query, and reference-counted lock object allocation/free.

Risks: the private encoding packs owner pointer or reader count with state bits. Architecture stubs and generic vector paths must agree on this layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/rwlock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/scanio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/scanio.h

Read completely: 132 lines.

This legacy scanner ioctl header defines `struct scan_io`, scanner control ioctls, image mode constants, and scanner product IDs. Fields include scan dimensions, resolution, origin, image mode, brightness, contrast, quality/speed, computed window size, line/pixel counts, bits per pixel, and scanner type.

Ioctls include `SCIOCGET`, `SCIOCSET`, `SCIOCRESTART`, and `SCIOC_USE_ADF`. `SCAN_BC` compatibility aliases expose older field and ioctl names.

Risks: this is a user/kernel device ABI. Drivers validate scanner-specific ranges and may round to supported settings, so callers are expected to read back state after setting it.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/scanio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sched.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/sched.h

Read completely: 285 lines.

This header defines POSIX scheduling policy constants, CPU set interfaces, Linux-compatible clone flags, CPU accounting states, and kernel scheduler interfaces. Public pieces include `struct sched_param`, `SCHED_*`, cpuset creation/manipulation wrappers, and internal affinity/parameter syscalls.

For kernel/KMEMUSER it defines `struct schedstate_percpu`, including per-CPU scheduler locks, processor-set data, CPU state counters, runqueue state, priority bitmap, and queue pointers. Kernel APIs cover scheduler initialization, CPU attach, periodic accounting, runqueue enqueue/dequeue, rescheduling, fork/exit hooks, wake/sleep hooks, CPU selection, preemption, context switching, idle, suspend, and scheduling parameter syscalls.

Risks: `schedstate_percpu` fields have explicit lock-domain annotations. Misusing fields outside their lock or CPU ownership can corrupt run queues or accounting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sched.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/scsiio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/scsiio.h

Read completely: 112 lines.

This header defines SCSI command and bus ioctl ABI. `scsireq_t` carries command bytes, data buffer pointer/lengths, sense buffer, status/return status, flags, timeout, and error bits. Flags indicate read/write, iovec, escape, and target operations.

It declares device ioctls for command execution, debugging, identify, deconfigure/reconfigure, and reset. Bus ioctls cover scanning, bus reset, detach, acceleration flags for sync/wide/tags, and low-level scan.

Risks: `SCIOCCOMMAND` passes a user buffer pointer through the request structure; implementation must validate direction, lengths, and copy semantics carefully.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/scsiio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sdt.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/sdt.h

Read completely: 512 lines.

This header implements statically defined tracing macros for userland and kernel code. Userland gets `DTRACE_PROBE*` macros that call external `__dtrace_provider___name` symbols with unsigned-long arguments.

In the kernel, behavior splits on `KDTRACE_HOOKS`. Without hooks, provider/probe declarations and probe macros compile away while consuming arguments to avoid warnings. With hooks, macros create `sdt_provider`, `sdt_probe`, and `sdt_argtype` objects in linker sets and dispatch enabled probes through `sdt_probe_func`.

It defines argument-type registration, 0 through 7 argument SDT probe macros, translated argument variants, `DTRACE_PROBE*` compatibility macros, provider/probe structures, init/exit functions, a stub function, and `SET_ERROR` instrumentation when DTrace hooks are enabled.

Risks: this header emits static objects and link-set entries via macros. Provider/module/function/name tokens become symbol names, and the 6/7-argument probes use function-pointer casts beyond the base five-argument function typedef.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sdt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/select.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/select.h

Read completely: 78 lines.

This header exposes `select` and `pselect` interfaces and kernel select/poll support hooks. Userland gets versioned `pselect` and `select` prototypes, while kernel code gets `selcommon`, `selrecord`, knote registration/removal, `selnotify`, per-CPU select init, and `selinfo` init/destroy.

Important interactions: kernel consumers include `selinfo.h` for wait-state storage and `signal.h` for `sigset_t`. Userland uses `fd_set` from `sys/fd_set.h`.

Risks: select readiness notification depends on callers maintaining `struct selinfo` correctly and calling `selnotify` on state transitions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/select.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/selinfo.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/selinfo.h

Read completely: 83 lines.

This header defines `struct selinfo`, the kernel state object for processes and knotes waiting for I/O readiness. It stores collision CPU masks, a kqueue list, cluster association, first LWP to notify, selected descriptor info, LWP-list linkage, and reserved fields.

Risks: the structure is embedded in device/socket state and is manipulated by select and kqueue paths. Lifetime must outlast registered waiters and knotes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/selinfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sem.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/sem.h

Read completely: 244 lines.

This header defines the System V semaphore ABI and kernel internals. Public types include `struct semid_ds`, `struct sembuf`, semaphore control commands, and userland prototypes for `semctl`, `semget`, `semop`, `semtimedop`, and NetBSD `semconfig`.

Kernel sections define internal `struct __sem`, semaphore limits, permissions, undo structures, configuration defaults, global `seminfo`/`sema`, freeze/thaw commands, sysctl export packing, and implementation functions including `do_semop1`, `do_semop`, `seminit`, `semfini`, `semexit`, and `semctl1`.

Risks: semaphore undo state is per-process and variable-length. ABI structs expose private implementation pointers while sysctl variants handle padding explicitly for 64-bit layouts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/semaphore.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/semaphore.h

Read completely: 44 lines.

This non-public header contains only the POSIX semaphore value limit definition `SEM_VALUE_MAX` as all bits set in an unsigned int. It explicitly tells userland to include `<semaphore.h>` instead.

Risks: no behavior here; the main concern is accidental use as a public API despite the warning.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/semaphore.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sha1.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/sha1.h

Read completely: 38 lines.

This header declares SHA-1 constants, `SHA1_CTX`, and core functions `SHA1Transform`, `SHA1Init`, `SHA1Update`, and `SHA1Final`. Userland additionally gets `SHA1End`, `SHA1FileChunk`, `SHA1File`, and `SHA1Data`.

Risks: SHA-1 is cryptographically weak for collision resistance. The header is ABI-only, but new security-sensitive code should not choose SHA-1 for collision-resistant use.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sha1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sha2.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/sha2.h

Read completely: 127 lines.

This header declares SHA-224, SHA-256, SHA-384, and SHA-512 constants, context structures, and APIs. `SHA224_CTX` aliases `SHA256_CTX`, and `SHA384_CTX` aliases `SHA512_CTX`.

Each algorithm has `Init`, `Update`, and `Final`; userland also gets `End`, `FileChunk`, `File`, and `Data` helpers. `_LIBC_INTERNAL` exposes transform routines for libc internals.

Risks: context layout is public to callers. Transform prototypes under `_LIBC_INTERNAL` expose lower-level block operations that expect correctly formatted internal state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sha2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sha3.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/sha3.h

Read completely: 80 lines.

This header declares SHA-3 and SHAKE context types and APIs. The shared `struct sha3` stores the 25-lane Keccak state and remaining buffer byte count; wrapper context types are provided for SHA3-224/256/384/512 and SHAKE128/256.

APIs include init/update/final for fixed-length SHA-3 digests, variable-length finalization for SHAKE, and `SHA3_Selftest`.

Risks: no implementation here. Callers of SHAKE finalization must supply the desired output length explicitly and manage output buffers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sha3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/shm.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/shm.h

Read completely: 205 lines.

This header defines System V shared memory ABI and kernel hooks. Public pieces include attach flags, `SHMLBA`, `shmatt_t`, `struct shmid_ds`, NetBSD lock/unlock command constants, compatibility permission aliases, `struct shminfo`, sysctl export structs, and prototypes for `shmat`, `shmctl`, `shmdt`, and `shmget`.

Kernel code gets internal flags for segment state, global `shminfo`, `shmsegs`, and `shm_nused`, lifecycle functions, fork/exit hooks, `shmctl1`, permission lookup by index, UVM hook pointers, and a sysctl fill macro.

Risks: `SHMLBA` resolves differently in kernel versus userland, with userland calling internal `__sysconf(28)`. Segment removal/linger/wired flags are kernel-only and must be synchronized with attach/detach lifetime.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/shm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/siginfo.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/siginfo.h

Read completely: 286 lines.

This header defines `sigval_t`, the internal `_ksiginfo` payload, public fixed-size `siginfo_t`, kernel `ksiginfo_t`, field accessor macros, and `si_code` constants. The reason union covers realtime values, child status/times, fault addresses/traps, poll band/fd, syscall trace data, and ptrace report state.

Kernel-only helpers define queue flags, initialization macros, copy-without-queue-pointers, trap predicates, and kernel field aliases. Public constants enumerate signal-specific codes for SIGILL, SIGFPE, SIGSEGV, SIGBUS, SIGTRAP, SIGCHLD, SIGIO, and generic origins such as `SI_USER`, `SI_QUEUE`, `SI_TIMER`, and `SI_NOINFO`.

Risks: `siginfo_t` is fixed at 128 bytes for ABI expansion. Field macros alias overlapping union members, so producers must set fields matching the signal code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/siginfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/signal.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/signal.h

Read completely: 342 lines.

This public signal header defines signal numbers 1 through 63, handler sentinel values, signal-set macro remapping for the kernel, `struct sigaction`, signal trampoline version constants, signal action flags, `sigprocmask` commands, alternate stack constants, `struct sigstack`, `struct sigevent`, and userland signal APIs.

It conditionally exposes POSIX/XOpen/NetBSD features according to feature-test macros. It includes architecture signal definitions and documents NetBSD's trampoline ABI versions: historical kernel sigcode, legacy sigcontext, and modern siginfo trampolines.

Userland prototypes include `signal`, `sigqueue`, legacy `bsd_signal` under relevant standards modes, and NetBSD `sigqueueinfo`.

Risks: this is central process ABI. Trampoline version constants must match libc and machine-dependent signal frame code; feature-test gating affects which symbols and types user code sees.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/signal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/signalvar.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/signalvar.h

Read completely: 325 lines.

This kernel signal-internals header defines queued signal lists, shared signal actions, pending-signal state, process signal context, internal action properties, and machine-independent signal APIs. `struct sigacts` contains per-signal `struct sigaction`, trampoline pointer, and version, plus refcount and lock. `sigpend_t` combines a `ksiginfo` queue with a signal set, and `struct sigctx` stores debugger/core-dump signal state and catch/ignore/pass masks.

It declares signal delivery, coredump, process group signaling, trap signaling, signal action/mask/suspend/altstack helpers, pending queue operations, ksiginfo allocation/free, sigtimedwait support, notification helpers, and machine-dependent `sendsig_*` functions. Inline helpers find the first signal in a set and manage ksiginfo queues.

With `SIGPROP`, it defines the default action/property table for all signals; otherwise it declares `sigprop`.

Risks: signal actions can be shared between processes and must be unshared before mutation. Queue flags and pending sets must remain consistent or delivery, masking, and debugger behavior diverge.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/signalvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sigtypes.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/sigtypes.h

Read completely: 125 lines.

This header defines signal-related base types and signal-set manipulation macros. `sigset_t` is four 32-bit words, supporting up to 128 bit positions, and macros implement mask, word selection, add, delete, membership, empty/fill, equality, union, subtraction, and intersection.

Under POSIX/XOpen/NetBSD feature modes it also defines `stack_t`/`struct sigaltstack` with stack pointer, size, and flags.

Risks: the macros do not validate signal numbers. Out-of-range signal values can index beyond the intended words if callers do not check first.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sigtypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sleepq.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/sleepq.h

Read completely: 94 lines.

This kernel synchronization header declares generic sleep queue operations. It exposes `sleepq_t` and APIs for init, remove, enter, enqueue, transfer, uncatch, unsleep, timeout, wake, abort, priority change/lending, and blocking.

Kernel code also gets `sleepqlock_t`, a cache-line-sized lock wrapper, and `sleepq_dontsleep`, which prevents sleep during cold startup or shutdown/panic/idle conditions. It includes `sleeptab.h` for hash table and turnstile definitions.

Risks: sleep queue operations coordinate LWP state, wait channels, locks, timeouts, and signal interruptibility. Callers must pass the right interlocks and sync object metadata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sleepq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sleeptab.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/sleeptab.h

Read completely: 140 lines.

This header defines the hashed sleep table and turnstile structures. The sleep table has 128 queues selected by `SLEEPTAB_HASH(wchan)`, and kernel inline helpers acquire the corresponding spin lock while returning the queue or lock.

It also defines `turnstile_t`, specialized sleep queues for kernel locks, with reader/writer queues, waiter counts, priority inheritance state, and hash-chain/free-list links. Kernel APIs include turnstile init, lookup, constructor, exit, block, wakeup, print, unsleep, priority change, and pool globals.

Risks: wait-channel hashing shifts pointer values and maps many wait objects onto shared locks. Turnstiles carry priority inheritance state, so queue and inheritor updates must be serialized.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sleeptab.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/socket.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/socket.h

Read completely: 661 lines.

This public socket ABI header defines socket types, socket creation flags, socket options, address/protocol family constants, socket address structures, message/control-message layouts, ancillary-data macros, shutdown constants, and libc socket prototypes.

Major types include `struct linger`, `struct accept_filter_arg`, `struct sockaddr`, kernel `struct sockproto` and `sockaddr_big`, `struct sockaddr_storage`, NetBSD `struct sockcred`, `struct kinfo_pcb`, `struct msghdr`, NetBSD `struct mmsghdr`, and `struct cmsghdr`.

It defines AF/PF families through `AF_MAX`, routing sysctl levels, `SOMAXCONN`, message flags, internal-only message flags, CMSG alignment/navigation macros, socket-level control messages, and prototypes for accept/bind/connect/send/receive/socketpair plus NetBSD `sendmmsg`/`recvmmsg`.

Kernel-only declarations add sockaddr allocation, copying, formatting, comparison, and generic address helpers.

Risks: this header is wide ABI surface. Control-message macros depend on alignment constants matching kernel runtime layout, and address-family constants are persistent values used across userland and kernel protocols.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/socket.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/socketvar.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/socketvar.h

Read completely: 611 lines.

This kernel socket-internals header defines socket buffer state, socket objects, state flags, accept filters, socket option transport, core socket/file operations, syscall helpers, and inline readiness/accounting helpers.

`struct sockbuf` stores select state, mbuf owner, back pointer, condition variable, byte/mbuf counters, watermarks, mbuf chain pointers, flags, timeout, and overflow count. `struct socket` stores locking, type/options/state, protocol PCB/switch, accept queues, errors, process group, OOB mark, send/receive buffers, upcall and protocol send/receive hooks, mbuf/uid/credential ownership, and accept-filter state.

APIs cover socket file operations, sockbuf append/drop/flush/reserve/wait, socket init/create/connect/listen/accept/send/receive/shutdown/close, option get/set, sockname/control-message copyout, syscall helper entry points, locking/refcount helpers, and accept-filter management. Inline functions implement `sb_notify`, `sbspace`, `soreadable`, `sowritable`, buffer accounting, wakeups, and socket locking.

Risks: most operations assert the socket lock. Buffer counters are unsigned and overflow-aware in `sbspace`, while manual `sballoc`/`sbfree` updates must track mbuf external storage. Accept queues, abort references, upcalls, and lock pointer replacement make lifetime and locking subtle.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/socketvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sockio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/sockio.h

Read completely: 158 lines.

This header defines socket and network-interface ioctl command numbers. It covers socket high/low watermarks, OOB mark, process group, SCTP peeloff, route add/delete, interface address/flags/broadcast/netmask/metric/configuration, aliases, multicast, media, generic driver data, tunnel physical addresses, MTU, clone interface management, data-link type, capabilities, CARP, interface data/stat zeroing, link strings, ether capabilities, interface index/description, MBIM/UMB, pfsync, and neighbor info.

Risks: command numbers are persistent ABI. Several ioctl numbers are intentionally reused for get/set pairs or reserved by subsystem-specific headers, so new additions must avoid collisions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/sockio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/spawn.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/spawn.h

Read completely: 109 lines.

This header defines NetBSD's internal POSIX spawn attribute and file-action layouts. `struct posix_spawnattr` stores flags, process group, scheduling parameter/policy, default signal set, and signal mask. File actions support open, dup2, close, chdir, and fchdir entries through `posix_spawn_file_actions_entry_t`.

It defines POSIX spawn flags for reset IDs, set process group, set scheduling parameters/policy, set signal defaults, and set signal mask. NetBSD adds `POSIX_SPAWN_RETURNERROR`, which forces parent-side waiting for child setup errors, mainly for testing.

Risks: action entries contain owned path pointers. The return-error extension changes synchronization/error-reporting behavior and should not be assumed by portable callers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/spawn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/specificdata.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/specificdata.h

Read completely: 69 lines.

This header declares a generic kernel specific-data facility. It defines key, destructor, domain, container, and reference types; `specificdata_reference` stores a container pointer and lock.

APIs cover domain create/delete, key create/delete with destructor, per-object init/fini, locked and unlocked getspecific, setspecific, and nonblocking setspecific.

Risks: object lifetime must coordinate domain/key deletion, per-object finalization, destructors, and reference locking. The unlocked getter requires external synchronization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/specificdata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/spl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/spl.h

Read completely: 63 lines.

This kernel/KMEMUSER-only header is intended for machine-dependent headers. It generates inline `spl*` interrupt-priority raisers from IPL constants using `splraiseipl(makeiplcookie(IPL_*))`.

It conditionally emits soft interrupt variants for available IPLs and always emits `splvm`, `splsched`, and `splhigh`.

Risks: it assumes `makeiplcookie` is reasonably fast and that machine-dependent IPL names exist. Ports with slow generic IPL construction should provide optimized MD functions instead.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/spl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/spldebug.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/spldebug.h

Read completely: 41 lines.

This header declares SPL debugging hooks: `spldebug_start`, `spldebug_stop`, `spldebug_lower`, and `spldebug_raise`.

Risks: declaration-only. Use depends on the platform/debug implementation tracking interrupt-priority transitions consistently.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/spldebug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/stat.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/stat.h

Read completely: 299 lines.

This public filesystem metadata header defines `struct stat`, file mode bits, type-test macros, file flags, special timestamp constants, and file-status/manipulation prototypes. `struct stat` includes device, mode, inode, link count, uid/gid, rdev, access/modify/change/birth times, size, block count/size, flags, generation, and spare fields.

It conditionally exposes timespec fields for POSIX.1-2008/XPG7/NetBSD modes and compatibility second/nanosecond fields otherwise. It defines permission masks, file-type constants, `S_IS*` tests, NetBSD access/default permission masks, user/superuser file flags, kernel shorthand flags, `UTIME_NOW`, and `UTIME_OMIT`.

Userland prototypes include chmod/mkdir/mkfifo/stat/fstat/lstat/fchmod/mknod, NetBSD chflags/lchmod variants, and `*at`/utimens APIs under modern feature modes.

Risks: `struct stat` is a core ABI with versioned syscall names. Feature-test macros change visible field names and prototypes, so compatibility code must include the correct mode.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/stat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/statvfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/statvfs.h

Read completely: 184 lines.

This public VFS statistics header defines `struct statvfs`, mount flag aliases, kernel helpers, and userland statvfs APIs. The structure stores mount flags, block sizes, block/file counts and reservations, sync/async read/write counters, fs IDs, name max, owner, spare fields, filesystem type, mount point, source, and source label.

It maps `ST_*` flags onto `MNT_*` flags, including access controls, logging, extended attributes, export flags, locality/quota/root flags, and wait/nowait modes. Kernel code gets helpers to set/copy/stat filesystem info plus allocation macros. Userland gets versioned `getmntinfo`, `statvfs`, `fstatvfs`, `getvfsstat`, and NetBSD file-handle/statvfs1 variants.

Risks: path/source buffers are large fixed-size ABI fields. Mount flag aliases must remain synchronized with `sys/fstypes.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/statvfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/stdalign.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/stdalign.h

Read completely: 55 lines.

This C/C++ compatibility header defines `alignas` and `alignof` for pre-C++11 modes by mapping them to `_Alignas` and `_Alignof`, and sets `__alignas_is_defined` and `__alignof_is_defined`.

Risks: no runtime behavior. It relies on compiler support for C alignment keywords when not in modern C++.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/stdalign.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/stdarg.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/stdarg.h

Read completely: 68 lines.

This header defines `va_list` and standard varargs macros through compiler builtins. It has lint stubs, compatibility mapping to `__builtin_stdarg_start` for older GCC combinations, and exposes `va_start`, `va_arg`, `va_end`, `__va_copy`, and C99/NetBSD `va_copy`.

Risks: highly compiler-dependent. The fallback logic is constrained to specific GCC/Clang feature checks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/stdarg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/stdbool.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/stdbool.h

Read completely: 47 lines.

This header defines C99 boolean macros for non-C++ compilation: `bool` as `_Bool`, `true` as `1`, `false` as `0`, and `__bool_true_false_are_defined`.

Risks: no runtime behavior. It intentionally avoids redefining C++ built-in bool values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/stdbool.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/stddef.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/stddef.h

Read completely: 156 lines.

This C common-definitions header declares `ptrdiff_t`, `size_t`, `max_align_t`, `wchar_t`, C23 `nullptr_t`, `NULL`, C23 `unreachable`, and `offsetof`. It also defines `__STDC_VERSION_STDDEF_H__` for NetBSD/C23 modes.

`max_align_t` is a union aligned for pointer, long double, and long long. `offsetof` uses `__builtin_offsetof` for modern GCC, a C null-pointer member address fallback otherwise, and a C++ reinterpret-cast fallback for older compilers.

Risks: type exposure depends on machine-provided `_BSD_*` macros and language standard mode. The fallback `offsetof` forms are compatibility paths for older compilers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/stddef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/stdint.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/stdint.h

Read completely: 102 lines.

This header defines fixed-width and pointer-width integer typedefs from machine headers: `int8_t`, `uint8_t`, `int16_t`, `uint16_t`, `int32_t`, `uint32_t`, `int64_t`, `uint64_t`, `intptr_t`, and `uintptr_t`.

It then includes machine headers for minimum-width/greatest-width types, limits, integer constants, and wchar limits, with C++ gating for `__STDC_LIMIT_MACROS` and `__STDC_CONSTANT_MACROS`.

Risks: no runtime behavior. Correctness depends on machine `int_types`, limits, and constant headers matching the architecture ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/stdint.h -->