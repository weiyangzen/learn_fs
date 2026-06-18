# Group Research: group_317_dragonflybsd_sources_os_bsd_dragonflybsd_sys_sys_syscall_h_sources_o_92f4d9d54c20

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/syscall.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/syscall.h

Generated DragonFly system-call number table.

Key contents:
- Defines `SYS_*` numeric syscall IDs from `SYS_syscall` `0` through `SYS_futimesat` `555`.
- Defines `SYS_MAXSYSCALL` as `556`.
- Preserves obsolete/reserved slots as comments, keeping ABI numbering stable.
- Covers core process, VFS, sockets, IPC, POSIX realtime, kqueue, modules, jail, TLS, LWP, `*at`, message queue, affinity, random, and modern exec/sync calls.

Important behavior:
- The file is generated from `syscalls.master`; manual edits would be overwritten by `make sysent`.
- Numeric holes are intentional ABI compatibility slots.
- Consumers pair this with `sysproto.h`, `sysunion.h`, `syscall.mk`, and the kernel `sysent` table.

Research notes:
- This is ABI, not logic. Any renumbering would break user/kernel syscall compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/syscall.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/syscall.mk -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/syscall.mk

Generated make fragment listing machine-independent syscall stub object files.

Key contents:
- Defines `MIASM`, a backslash-continued list of syscall `.o` targets.
- Object names mirror syscall names such as `read.o`, `open.o`, `__sysctl.o`, `set_tls_area.o`, `openat.o`, `getrandom.o`, and `futimesat.o`.
- Omits obsolete numeric syscall holes and contains only active/generated stubs.

Important behavior:
- Generated from `syscalls.master` by `make sysent`.
- Must remain aligned with syscall numbering and prototypes even though it does not encode numbers directly.
- Used by build rules for assembling/linking syscall entry stubs.

Research notes:
- This is build metadata for the syscall ABI surface.
- Divergence from `syscall.h`/`sysproto.h` would show up as missing or stale syscall stubs.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/syscall.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysctl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysctl.h

Public and kernel sysctl interface definitions.

Key responsibilities:
- Defines sysctl name hierarchy limits and type encodings:
  - `CTL_MAXNAME`
  - `CTLTYPE_*`
  - `CTLFLAG_*`
  - bitfield type helpers
- Defines top-level MIB identifiers:
  - `CTL_SYSCTL`, `CTL_KERN`, `CTL_VM`, `CTL_VFS`, `CTL_NET`, `CTL_HW`, `CTL_USER`, `CTL_LWKT`, etc.
- Defines many second-level constants under `KERN_*`, `KERN_PROC_*`, `KIPC_*`, `HW_*`, `USER_*`, and `CTL_P1003_1B_*`.
- In kernel builds, defines:
  - `struct sysctl_req`
  - `struct sysctl_oid`
  - sysctl handler prototypes
  - static OID construction macros
  - dynamic OID/context APIs
  - common sysctl root declarations
- In user/virtual-kernel-visible builds, declares:
  - `sysctl`
  - `sysctlbyname`
  - `sysctlnametomib`

Important invariants:
- `CTL_MAXNAME` caps integer MIB depth at 12.
- `OID_AUTO` enables dynamic numbering through linker-set registration.
- `SYSCTL_OID` instances are placed in `DATA_SET(sysctl_set, ...)`.
- Several scalar helpers automatically add `CTLFLAG_NOLOCK`.
- `NO_SYSCTL_DESCR` strips descriptions at compile time.
- Kernel sysctl lock macros use per-CPU `gd_sysctllock`.

Research notes:
- This header is both user ABI and kernel registration framework.
- The macro layer hides most static-tree construction details; dynamic OIDs are tracked with `sysctl_ctx_list`.
- The `FEATURE()` macro standardizes read-only feature booleans under `kern.features`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysent.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysent.h

Kernel syscall dispatch table and executable ABI vector definitions.

Key contents:
- Defines `sy_call_t`, the syscall handler signature:
  - `int (*)(struct sysmsg *, const void *)`
- Defines `struct sysent`:
  - argument count
  - result size
  - start handler
  - optional abort handler for async calls
- Defines `struct sysentvec`, describing an executable ABI’s syscall table, signal mappings, stack fixup, signal delivery, sigcode, coredump hook, image activation hook, and minimum signal-stack size.
- Kernel-only dynamic syscall module support:
  - `struct syscall_module_data`
  - `SYSCALL_MODULE`
  - `SYSCALL_MODULE_HELPER`
  - `syscall_register`
  - `syscall_deregister`
  - `syscall_module_handler`

Important behavior:
- `NO_SYSCALL` is `-1`.
- `SYSCALL_MODULE_HELPER` calculates argument count from the generated args struct minus `struct sysmsg`.
- `struct sysentvec` is the bridge between syscall dispatch and binary compatibility/personality handling.

Research notes:
- This is central to kernel syscall dispatch and loadable syscall modules.
- The ABI vector is broader than syscall dispatch: it also owns signal and core-dump behavior.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysid.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysid.h

Defines DragonFly system resource identifiers.

Key contents:
- Defines `sysid_t` as `u_int64_t`.
- Documents two SYSID classes:
  - physical SYSIDs for routing across a mesh
  - logical SYSIDs for persistent resources such as devices, media, or filesystems

Important concepts:
- Physical SYSIDs can change and can be recalculated.
- Logical SYSIDs can persist in superblocks or other metadata and support migration/multihoming.
- Logical plus physical SYSID validates message targets and drives route refresh.

Research notes:
- This is a small but foundational distributed-resource identity header.
- It is consumed by `sysref.h` for resource registration and lookup.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/syslimits.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/syslimits.h

BSD/POSIX system limit constants.

Key contents:
- Defines fixed limits including:
  - `ARG_MAX` 262144
  - `CHILD_MAX` 40
  - `LINK_MAX` 32767
  - `MAX_CANON`/`MAX_INPUT` 255
  - `NAME_MAX` 255
  - `NGROUPS_MAX` 16
  - `OPEN_MAX` 64
  - `PATH_MAX` 1024
  - `PIPE_BUF` 512
  - `IOV_MAX` 1024
- Warns userland when included directly outside expected headers.
- Leaves `HOST_NAME_MAX` undefined so applications use conservative values or `sysconf()`.

Important behavior:
- Header comments explicitly discourage adding new variables here.
- Some values are conditionally defined only if not already provided.

Research notes:
- This is user-visible ABI/standards surface.
- The intentionally undefined limits are as important as the defined constants.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/syslimits.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/syslink_rpc.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/syslink_rpc.h

Minimal syslink RPC descriptor definitions.

Key contents:
- Defines `struct syslink_desc`:
  - `sd_offset`: offset into an operations structure
  - `sd_name`: debug name

Role:
- Supports syslink protocol abstraction for RPC operations.
- The comment notes this descriptor is also used by vnode operations and device operations.

Research notes:
- This is a small shared metadata contract rather than a full RPC implementation.
- Offset-based descriptors allow generic dispatch/conversion logic to identify operation slots.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/syslink_rpc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/syslog.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/syslog.h

Syslog priority, facility, option, and userland API definitions.

Key contents:
- Defines log socket paths:
  - `/var/run/log`
  - `/var/run/logpriv`
  - legacy `/dev/log`
- Defines priorities `LOG_EMERG` through `LOG_DEBUG`.
- Defines facility constants `LOG_KERN`, `LOG_USER`, `LOG_DAEMON`, `LOG_AUTHPRIV`, `LOG_LOCAL0` through `LOG_LOCAL7`, etc.
- Provides encoding helpers:
  - `LOG_PRI`
  - `LOG_MAKEPRI`
  - `LOG_FAC`
  - `LOG_MASK`
  - `LOG_UPTO`
- Under `SYSLOG_NAMES`, defines name-to-code arrays for priorities and facilities.
- Defines `openlog` option flags.
- Userland declarations:
  - `closelog`
  - `openlog`
  - `setlogmask`
  - `syslog`
  - `vsyslog`

Important behavior:
- Priority uses low 3 bits; facility is shifted left by 3.
- `LOG_PRINTF` is kernel-only pseudo-priority for `kprintf` behavior.
- Some historical priority names are kept as deprecated aliases.

Research notes:
- This is both libc API and kernel logging vocabulary.
- Facility/priority encodings must stay compatible with `syslogd`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/syslog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysmsg.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysmsg.h

Kernel syscall message/result carrier.

Key contents:
- Kernel-only `struct sysmsg`.
- `sm_result` union supports pointer, int, long, `size_t`, two file descriptors, 32-bit, 64-bit, `off_t`, and `register_t` results.
- Stores `sm_frame`, the trapframe for saved user context.
- Stores `extargs`, a `union sysunion` used when more than six syscall arguments are needed.
- Provides aliases such as `sysmsg_result`, `sysmsg_fds`, `sysmsg_offset`, and `sysmsg_frame`.

Important behavior:
- The struct is packed.
- File descriptor return storage is `long fds[2]` so it maps to two 64-bit registers on 64-bit architectures.
- `struct sysmsg` usually precedes syscall arguments in `union sysunion`.

Research notes:
- This is the kernel-side ABI carrier tying syscall handlers to machine trap state and generated argument unions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysmsg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysproto.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysproto.h

Generated kernel syscall argument structs and handler prototypes.

Key responsibilities:
- Rejects userland inclusion.
- Includes syscall argument dependencies such as select, signal, ACL, cpumask, mqueue, msgport, and procctl headers.
- Defines `PAD_(t)` to pad each argument field to `register_t` alignment/size.
- Defines one `struct <syscall>_args` for each generated syscall argument layout.
- Declares kernel syscall handlers:
  - `int sys_<name>(struct sysmsg *, const struct <name>_args *)`

Covered syscall families:
- Classic process/file syscalls: `fork`, `read`, `write`, `open`, `close`, `wait4`, `execve`, `chdir`, `chmod`, `chown`.
- VFS/stat/mount syscalls: `mount`, `statfs`, `getfh`, `stat`, `fstat`, `lstat`, `statvfs`, `getvfsstat`.
- Socket syscalls: `socket`, `bind`, `connect`, `accept`, `sendmsg`, `recvmsg`, `accept4`.
- VM syscalls: `mmap`, `munmap`, `mprotect`, `madvise`, `mlock`, `vmspace_*`.
- IPC/POSIX realtime: SysV IPC, AIO, message queues, clocks, nanosleep.
- Signals/scheduling/LWP: `sigaction`, `sigprocmask`, `sched_*`, `lwp_*`, affinity calls.
- Modern namespace APIs: `openat`, `fstatat`, `unlinkat`, `utimensat`, `fexecve`, `posix_fallocate`.

Important invariants:
- Generated from `syscalls.master`; manual edits are not durable.
- Padding fields preserve architecture syscall argument ABI layout.
- Old compatibility names appear in places, e.g. `__getrlimit_args` and `__setrlimit_args`.
- Prototypes use the `struct sysmsg` first argument uniformly.

Research notes:
- This is the authoritative generated contract between trap/syscall dispatch and implementation functions.
- It pairs directly with `sysunion.h`, `sysmsg.h`, and `sysent.h`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysproto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysref.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysref.h

System resource registration and reference-management definitions.

Key contents:
- Defines callback types for terminate, lock, and unlock operations.
- Defines `struct sysref_class`:
  - resource name
  - malloc type
  - RPC protocol id
  - embedded sysref offset
  - object size
  - cache sizing
  - flags
  - object cache hooks
  - resource operation callbacks
- Defines embedded `struct sysref`:
  - per-CPU RB-tree node
  - machine-wide `sysid_t`
  - reference count
  - flags
  - resource class pointer
- Defines flags:
  - `SRC_MANAGEDINIT`
  - `SRF_SYSIDUSED`
  - `SRF_ALLOCATED`
  - `SRF_PUTAWAY`
- Defines `SYSREF_PROTO_*` protocol numbers for vmspace, vnode, process, LWP, fd, socket, mount, device, and related resources.
- Declares `allocsysid()` for kernel builds.

Important behavior:
- Resources are backed by `objcache`.
- The owning CPU is encoded through the SYSID/RB-tree association.
- Negative refcounts represent construction/deconstruction states.
- Reusing SYSIDs can avoid RB-tree relocation when resources are not looked up via syslink.

Research notes:
- This header establishes the generic identity/reference substrate for major kernel resources.
- `sysref2.h` supplies the inline refcount operations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysref.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysref2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysref2.h

Inline sysref reference-count helpers.

Key contents:
- Kernel-only header.
- Declares slow path `_sysref_put`.
- Defines inline:
  - `sysref_get`
  - `sysref_put`
  - `sysref_isactive`
  - `sysref_isinactive`
  - `sysref_islastdeactivation`
- Declares kernel APIs:
  - `sysref_init`
  - `sysref_alloc`
  - `sysref_activate`

Important behavior:
- `sysref_get` asserts the object is not put away, then atomically increments.
- `sysref_put` fast-paths normal decrements with compare-and-set.
- `sysref_put` falls back to `_sysref_put` for 1-to-0, negative, or racing transitions.
- Negative refcounts mark deletion/deactivation.
- `-0x40000000` identifies the last deactivation reference.

Research notes:
- This is deliberately small and hot-path oriented.
- Correctness depends on callers respecting `SRF_PUTAWAY` and the negative-refcount lifecycle.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysref2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/systimer.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/systimer.h

Kernel system timer, CPU timer, interrupt timer, and CPU counter interfaces.

Key contents:
- Defines `sysclock_t` and `ssysclock_t`.
- Defines `struct systimer` for per-CPU queued/nonqueued timers:
  - queue linkage
  - absolute next time
  - periodic interval/frequency
  - callback
  - flags
  - owning timer and CPU globaldata
- Defines `SYSTF_*` flags for queue state, IPI running, nonqueued timers, synchronization offsets, and coincident ordering.
- Declares systimer operations for add/delete/init/adjust/intr.
- Defines `struct cputimer` for monotonic free-running counters.
- Defines CPU timer type and priority constants.
- Defines `struct cputimer_intr` for one-shot interrupt timers.
- Defines interrupt timer priorities/capabilities and register/select helpers.
- Defines `struct cpucounter` and lookup/register APIs.

Important invariants:
- `cputimer->count()` must be MP synchronized, stable through power-saving, and monotonically increasing.
- `count()` returns a full-width wrapping counter.
- Frequency conversion uses precomputed 64-bit factors and `muldivu64`.
- Interrupt timer implementations expose `reload`, `enable`, `config`, `restart`, `pmfixup`, `initclock`, and optional per-CPU handler hooks.
- `cputimer_intr_deregister()` cannot remove the currently selected interrupt timer.

Research notes:
- This header separates timebase selection from interrupt delivery.
- It documents hardware/platform requirements more explicitly than most kernel headers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/systimer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/systm.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/systm.h

Central kernel system declarations and utility API surface.

Key responsibilities:
- Exposes boot/runtime globals:
  - `securelevel`, `cold`, `panicstr`, `dumping`, `boothowto`, `bootverbose`, `ncpus`, `physmem`, root/dump devices, release/version data
- Defines assertion macros:
  - `KASSERT`
  - `KKASSERT`
  - `KKASSERT_UNSPIN`
  - `__assert_unreachable`
- Defines data placement/cacheline annotations.
- Declares initialization, CPU, VM, trap, TLS, CRC, logging/printing, scanning, string conversion, memory, copyin/out, user-access, delay, profiling, environment, startup/shutdown, clock, sleep/wakeup, device number, unit-number, and bit-count helpers.
- Maps common memory functions to compiler builtins while preserving underscore-prefixed real implementations.

Important behavior:
- Kernel-only header; userland inclusion errors out.
- Builtin memory macros use `__DEQUALIFY` and can affect compiler assumptions.
- `copyin/copyout` and `fuword/suword/casu/swapu` declarations define user-kernel memory access primitives.
- Sleep APIs cover bare channels and variants tied to spinlocks, lockmgr locks, mutexes, and serializers.
- Wakeup APIs include per-CPU, domain, one-shot, and delayed wakeup variants.
- `muldivu64` uses a 128-bit intermediate and emits diagnostics on overflow.

Research notes:
- This is a broad dependency hub used to avoid including heavier subsystem headers everywhere.
- The header mixes stable kernel contracts with low-level machine hooks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/systm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysunion.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysunion.h

Generated union of all syscall argument structs.

Key contents:
- Kernel-only generated header.
- Includes `sys/sysproto.h`.
- Defines `union sysunion` with one member per generated syscall argument struct.
- Member names correspond to syscall names, including `__sysctl`, `__getcwd`, `vmspace_*`, `lwp_*`, `mq_*`, `*at`, and modern additions.

Important behavior:
- Used by `struct sysmsg` as `extargs` for syscalls needing more than the register argument path can carry.
- Must remain layout-compatible with generated syscall argument structs.
- Generated from `syscalls.master`; manual edits are not durable.

Research notes:
- This is a space-efficient carrier for syscall argument alternatives.
- It is tightly coupled to `sysproto.h` and `sysmsg.h`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sysunion.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/taskqueue.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/taskqueue.h

Kernel deferred task queue API.

Key contents:
- Defines task callback type `task_fn_t(context, pending)`.
- Defines enqueue notification callback type.
- Defines `struct task`:
  - queue linkage
  - current queue
  - pending count
  - priority
  - handler
  - context
- Defines `struct timeout_task`, combining a `task`, `callout`, and flag.
- Declares queue creation, thread startup, enqueue, cancel, drain, lookup, free, block, and unblock APIs.
- Provides initializer macros:
  - `TASK_INITIALIZER`
  - `TASK_INIT`
  - `TIMEOUT_TASK_INIT`
- Provides declaration/definition macros:
  - `TASKQUEUE_DECLARE`
  - `TASKQUEUE_DEFINE`
  - `TASKQUEUE_DEFINE_THREAD`
- Declares common queues:
  - `taskqueue_swi`
  - `taskqueue_swi_mp`
  - per-CPU `taskqueue_thread[]`

Important behavior:
- `pending` tells a task handler how many enqueue attempts accumulated before execution.
- `TASKQUEUE_DEFINE` creates the queue during `SYSINIT` at `SI_SUB_PRE_DRIVERS`.
- Thread-backed queues use `taskqueue_thread_enqueue` and daemon priority.

Research notes:
- This is FreeBSD-derived deferred execution infrastructure adapted for DragonFly priorities and per-CPU queues.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/taskqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/tbridge.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/tbridge.h

DragonFly test bridge ioctl and kernel testcase module interface.

Key contents:
- Defines ioctl commands:
  - `TBRIDGE_LOADTEST`
  - `TBRIDGE_GETRESULT`
- Kernel-only result constants matching `dfregress.h`.
- Defines testcase callback types:
  - abort callback
  - run callback
- Defines `struct tbridge_testcase`.
- Declares:
  - `tbridge_printf`
  - `tbridge_test_done`
  - safe-memory allocation/free/check helpers
  - `tbridge_testcase_modhandler`
- Provides `TBRIDGE_TESTCASE_MODULE` macro for registering testcase modules with dependency on `testbridge`.

Important behavior:
- The result constants must stay synchronized with external regression tooling.
- Safe-memory wrappers capture file/line at allocation/free sites.
- Testcase modules are normal kernel modules with declared dependency/version metadata.

Research notes:
- This is test infrastructure, not production syscall/VFS logic.
- The ABI is small but fragile because it matches out-of-file regression constants.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/tbridge.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/thread.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/thread.h

Architecture-independent LWKT thread, token, IPI, and CPU-sync definitions.

Key responsibilities:
- Defines LWKT pointer typedefs and run-queue type.
- Documents and defines LWKT tokens:
  - soft serialization
  - shared/exclusive modes
  - collision tracking
  - per-thread token reference stack
- Defines `struct lwkt_ipiq`, a per-CPU IPI FIFO with 256 slots.
- Defines `struct lwkt_cpusync`.
- Defines per-thread file descriptor cache structures.
- Defines the main `struct thread`, including:
  - queue links
  - message port
  - LWP/proc/PCB/globaldata associations
  - wait channel/domain/message
  - priority, flags, critical count
  - stack and switch function
  - accounting ticks
  - locks/limits/refs
  - credentials
  - token stack
  - migration target
  - fd cache
  - compatibility sleepqueue/Linux/FreeBSD fields
  - debug arrays
  - machine-specific thread state
- Defines thread flags, MP flags, thread types, priorities, and stack size.
- Declares global tokens and LWKT scheduling/token/IPI/CPU-sync/thread lifecycle APIs.

Important invariants:
- A thread is owned by the CPU in `td_gd`; foreign CPU manipulation must use CPU/IPI messaging.
- Threads stay on per-CPU LWKT run queues while running.
- `TDF_RUNNING` can clear temporarily during preemption, so users must also consider `TDF_PREEMPT_LOCK`.
- Tokens are reacquired after blocking and are designed to avoid deadlock across arbitrary ordering.
- `LWKT_MAXTOKENS` caps beneficially held token refs at 32.
- `MAXCPUFIFO` is 256 and must remain a power of two.

Research notes:
- This is one of DragonFly’s core scheduler/concurrency headers.
- It encodes the design distinction between per-CPU LWKT scheduling and user process scheduling.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/thread.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/thread2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/thread2.h

Inline LWKT critical-section, token-test, CPU-sync, and IPI helper routines.

Key contents:
- Kernel-only header including `systm.h`, `globaldata.h`, `cpumask.h`, and machine CPU functions.
- Defines raw critical count adjustment helpers with CPU compiler fences:
  - `crit_enter_raw`
  - `crit_exit_raw`
- Defines token ownership tests:
  - `_lwkt_token_held_any`
  - `_lwkt_token_held_excl`
- Provides debug and non-debug critical-section macros.
- Implements debug critical enter/exit tracking when `DEBUG_CRIT_SECTIONS` is enabled.
- Defines inline critical-section entry/exit variants:
  - normal
  - quick
  - hard
  - no-yield
- Defines helpers:
  - `crit_test`
  - `lwkt_runnable`
  - `lwkt_getpri`
  - `lwkt_getpri_self`
  - `lwkt_passive_recover`
  - `lwkt_cpusync_init`
  - IPI wrapper variants for one/two/three args, masks, passive sends, and by-CPU sends
  - `lwkt_need_ipiq_process`

Important behavior:
- Critical count increments/decrements are fenced because compiler reordering would break preemption semantics.
- Normal critical sections defer preemption but permit explicit blocking/switching.
- Hard critical sections also disallow blockable operations and raise interrupt nesting level.
- Non-debug `crit_exit()` intentionally wraps in a function to avoid inline code bloat.
- IPI wrappers cast simpler callback signatures to the full three-argument IPI function type.

Research notes:
- This header is hot-path inline support for `thread.h`.
- The comments distinguish software preemption control from physically disabling interrupts.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/thread2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/time.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/time.h

BSD time structures, arithmetic macros, interval timers, kernel clock APIs, and userland time prototypes.

Key contents:
- Includes canonical `_clock_id`, `_timespec`, `_timeval`, and select definitions.
- Defines conversion macros:
  - `TIMEVAL_TO_TIMESPEC`
  - `TIMESPEC_TO_TIMEVAL`
- Defines `struct timezone` and DST constants.
- Defines timespec/timeval clear, set, compare, add, and subtract macros.
- Defines interval timer IDs and `struct itimerval`.
- Defines `struct clockinfo`.
- Kernel-only declarations include:
  - time globals and NTP adjustment globals
  - uptime/current-time accessors
  - interval timer validation/decrement
  - rate checking
  - time setting/adjustment
  - timeval/timespec-to-hz conversions
  - nanosleep helpers
  - FAT timestamp conversion
  - TSC target/delay helpers
- Userland declarations include `adjtime`, `gettimeofday`, `settimeofday`, `utimes`, `futimes`, `futimesat`, `lutimes`, `getitimer`, and `setitimer`.

Important behavior:
- Kernel exposes both approximate/simple second counters and precise micro/nano accessors.
- Userland exposes BSD/XSI APIs according to visibility macros.
- `HAVE_FUTIMESAT` is defined with the userland `futimesat` prototype.

Research notes:
- This header is shared ABI plus kernel clock API surface.
- It intentionally duplicates some conversion macros also available in `timespec.h`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/time.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/timeb.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/timeb.h

Legacy `ftime(2)` time structure and prototype.

Key contents:
- Ensures `time_t` is declared.
- Defines deprecated `struct timeb`:
  - seconds since epoch
  - milliseconds
  - timezone minutes west of UTC
  - DST flag
- Userland-only legacy prototype:
  - `ftime(struct timeb *)`

Important behavior:
- `ftime` is exposed only under BSD visibility or old XSI visibility.
- The header is retained for source compatibility.

Research notes:
- This is a legacy ABI compatibility header.
- New code should use `clock_gettime`/`gettimeofday` style APIs instead.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/timeb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/timepps.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/timepps.h

Pulse-per-second timing API definitions and ioctl wrappers.

Key contents:
- Defines PPS API version 1.
- Defines PPS handle and sequence types.
- Defines NTP fixed-point timestamp type `ntp_fp_t`.
- Defines `pps_timeu_t`, carrying either `timespec` or NTP fixed-point time.
- Defines `pps_info_t` and `pps_params_t`.
- Defines PPS capture, offset, echo, wait/poll, timestamp format, and kernel-consumer constants.
- Defines ioctl payload structs:
  - `pps_fetch_args`
  - `pps_kcbind_args`
- Defines ioctl commands:
  - create/destroy
  - set/get params
  - get capabilities
  - fetch
  - kernel-consumer bind
- Kernel side:
  - defines `struct pps_state`
  - declares `pps_event`, `pps_init`, `pps_ioctl`, and `hardpps`
- User side:
  - inline wrappers `time_pps_create`, `destroy`, `setparams`, `getparams`, `getcap`, `fetch`, and `kcbind`

Important behavior:
- `time_pps_create` stores the file descriptor itself as the handle.
- `time_pps_fetch` uses `(-1, -1)` timeout when caller passes `NULL`.
- Kernel PPS state stores parameter/current info, kernel consumer mode, capabilities, and recent sysclock counts.

Research notes:
- This header bridges userland PPS consumers, device ioctl implementations, and kernel hard-PPS discipline.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/timepps.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/timers.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/timers.h

Basic timers compatibility header.

Key contents:
- Includes `sys/time.h`.

Role:
- Provides the historical `<sys/timers.h>` include path for code expecting it.
- Contains no additional types or functions beyond what `sys/time.h` provides.

Research notes:
- This is a compatibility shim.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/timers.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/times.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/times.h

Process CPU accounting structure and `times(3)` declaration.

Key contents:
- Ensures `clock_t` is declared.
- Defines `struct tms`:
  - user CPU time
  - system CPU time
  - terminated children user CPU time
  - terminated children system CPU time
- Userland-only declaration:
  - `clock_t times(struct tms *)`

Research notes:
- This is standard POSIX process accounting ABI.
- Kernel builds receive only the type definitions, not the libc prototype.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/times.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/timespec.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/timespec.h

Timespec compatibility and POSIX interval timer structure definitions.

Key contents:
- Includes `sys/_timespec.h`.
- Under BSD visibility, defines `TIMEVAL_TO_TIMESPEC` and `TIMESPEC_TO_TIMEVAL`.
- Defines `struct itimerspec` with:
  - `it_interval`
  - `it_value`

Role:
- Supplies POSIX.1b timer structure used by `timer_*()` APIs.
- Provides a lighter include path than full `sys/time.h`.

Research notes:
- The conversion macros duplicate the definitions in `time.h` under visibility control.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/timespec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/timex.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/timex.h

NTP precision time discipline ABI.

Key contents:
- Defines `NTP_API` version 4.
- Includes `sys/syscall.h` and `sys/time.h`.
- Defines NTP discipline bounds:
  - `MAXPHASE`
  - `MAXFREQ`
  - `MINSEC`
  - `MAXSEC`
  - `NANOSECOND`
  - `SCALE_PPM`
  - `MAXTC`
- Defines `MOD_*` control bits for `timex.modes`.
- Defines `STA_*` status bits for PLL/FLL, PPS, leap second, sync, resolution, mode, and clock source.
- Defines read-only status mask `STA_RONLY`.
- Defines clock state constants `TIME_OK` through `TIME_ERROR`.
- Defines `struct ntptimeval` for `ntp_gettime`.
- Defines `struct timex` for `ntp_adjtime`.
- DragonFly-specific declarations:
  - kernel `ntp_update_second`
  - userland `ntp_adjtime`
  - userland `ntp_gettime`

Important behavior:
- Time offset/precision/jitter fields are interpreted as microseconds or nanoseconds depending on `STA_NANO`.
- Read-only PPS fields are present regardless of kernel PPS configuration for portability.
- Frequency is expressed as scaled PPM.

Research notes:
- This is public ABI for NTP daemons and kernel clock discipline.
- The comments document the historical microsecond-to-nanosecond transition and compatibility expectations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/timex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/tls.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/tls.h

Thread-local storage syscall ABI.

Key contents:
- Defines `struct tls_info`:
  - base pointer
  - signed size
- Declares:
  - `set_tls_area`
  - `get_tls_area`
- On x86_64, defines selectors:
  - `TLS_WHICH_FS`
  - `TLS_WHICH_GS`

Important behavior:
- `size` is explicitly signed.
- APIs take an `infosize` argument for structure-size/version checking.

Research notes:
- This is small user/kernel ABI for architecture TLS register areas.
- The x86_64 definitions map TLS selection to FS/GS.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/tls.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/tprintf.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/tprintf.h

Kernel terminal/session printf interface.

Key contents:
- Kernel-only header.
- Defines `tpr_t` as `struct session *`.
- Forward-declares `struct proc`.
- Declares:
  - `tprintf_open(struct proc *)`
  - `tprintf_close(tpr_t)`
  - `tprintf(tpr_t, const char *, ...)`

Role:
- Provides a typed handle for printing kernel messages to a process/session-associated terminal.
- Uses printf format checking on `tprintf`.

Research notes:
- This is a narrow kernel output helper API, separate from generic `kprintf`/`log`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/tprintf.h -->