# Group Research: group_316_dragonflybsd_sources_os_bsd_dragonflybsd_sys_sys_resource_h_sources__964b9af50571

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/resource.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/resource.h

This header defines DragonFly BSD user/kernel resource accounting ABI: priorities, resource usage records, resource limits, load averages, CPU state indexes, and public resource syscalls.

Key responsibilities:
- Defines `id_t` and `rlim_t` where not already declared.
- Defines process priority targets and ranges:
  - `PRIO_PROCESS`, `PRIO_PGRP`, `PRIO_USER`
  - BSD-visible `PRIO_MIN`, `PRIO_MAX`, `IOPRIO_MIN`, `IOPRIO_MAX`
- Defines `struct rusage` for user/system time, RSS, page faults, block I/O, messages, signals, and context switches.
- Defines `struct __wrusage` as paired self/children usage under BSD visibility.
- Defines resource limit IDs:
  - POSIX/common: `RLIMIT_CPU`, `RLIMIT_FSIZE`, `RLIMIT_DATA`, `RLIMIT_STACK`, `RLIMIT_CORE`, `RLIMIT_NOFILE`, `RLIMIT_AS`
  - BSD-visible: `RLIMIT_RSS`, `RLIMIT_MEMLOCK`, `RLIMIT_NPROC`, `RLIMIT_SBSIZE`, `RLIMIT_POSIXLOCKS`
- Defines `struct rlimit`, `RLIM_INFINITY`, saved-limit aliases, and optional `_RLIMIT_IDENT` string table.
- Defines BSD-visible `struct loadavg` and `CP_*` CPU state indexes.
- Exposes userland declarations for `getpriority`, `setpriority`, `getrlimit`, `setrlimit`, `getrusage`, and BSD `ioprio_get`/`ioprio_set`.
- Exposes kernel `averunnable` and `dosetrlimit()`.

Important invariants:
- `RLIMIT_CPU` is documented as milliseconds in this ABI.
- `RLIM_INFINITY` is the maximum signed 63-bit `rlim_t` value.
- `RLIM_NLIMITS` is BSD-visible and currently 12.
- `ru_first`/`ru_last` mark the aggregatable counter range inside `struct rusage`.

Research notes:
- This is a stable syscall/user ABI header with visibility-gated BSD additions.
- The `getpriority`/`setpriority` prototypes still take `int` for the id argument, with comments noting XSI would prefer `id_t`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/resource.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/resourcevar.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/resourcevar.h

This header defines kernel-side resource state for profiling, per-process resource limits, per-UID accounting, and UID resource management APIs.

Key responsibilities:
- Defines `struct uprof` for process profiling state:
  - profiling buffer base/size
  - PC offset/scale
  - temporary address/tick fields for AST processing
- Defines `struct krate` for rate-limited kernel printing.
- Defines `struct plimit`, the copy-on-write process limit object:
  - `pl_rlimit[RLIM_NLIMITS]`
  - CPU limit cache in usec
  - cache-aligned spinlock and ref/exclusive word
- Defines `PLIMITF_EXCLUSIVE`, `PLIMITF_MASK`, and CPU-limit test results.
- Defines per-CPU `struct uidcount` with POSIX-lock and open-file counters.
- Defines `PUP_LIMIT` rollup threshold of +/-32 for UID per-CPU counters.
- Defines `struct uidinfo` for per-UID consumption:
  - socket buffer bytes
  - process count
  - POSIX lock and open-file rollups
  - variant symlink set
  - per-CPU counters
  - cache-aligned reference count
- Declares kernel APIs for profiling, rusage aggregation, UID accounting, UID object lifecycle, and process limit lifecycle/modification.

Important invariants:
- `struct plimit` is designed for sharing after fork and copy-on-write modification.
- `p_refcnt` is separated into its own cache-aligned area to avoid cacheline churn on mostly read-only limit data.
- Threaded programs cache `p_limit` in thread state for lockless reads.
- Per-CPU UID counts intentionally allow small slop to avoid cacheline ping-ponging.
- `PLIMIT_TESTCPU_*` distinguishes OK, soft-limit `SIGXCPU`, and hard kill outcomes.

Research notes:
- This header is internal resource-accounting infrastructure rather than user ABI.
- It ties resource limits to DragonFly-specific spinlocks, varsym sets, and per-CPU UID rollups.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/resourcevar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/rman.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/rman.h

This header defines DragonFly BSD's resource manager interface for managing allocatable bus/resource address ranges and exporting resource manager state to userland.

Key responsibilities:
- Defines `RF_*` resource flags:
  - allocated, active, shareable, timeshare, wanted, first-share, prefetchable, optional
  - encoded alignment fields with `RF_ALIGNMENT_*`
- Defines `enum rman_type`:
  - `RMAN_UNINIT`
  - `RMAN_GAUGE`
  - `RMAN_ARRAY`
- Defines user-exported `struct u_resource` and `struct u_rman` with stable text length `RM_TEXTLEN`.
- Defines kernel `struct resource`:
  - resource range start/end
  - flags and optional RID
  - virtual address
  - bus space tag/handle
  - owning device
  - parent `struct rman`
  - links for resource and share lists
- Defines kernel `struct rman`:
  - managed resource list
  - sleep/token lock pointer
  - global rman list link
  - start/end range
  - type, description, owner CPU, destruction interlock
- Declares kernel APIs for initialization, region management, reservation, activation, deactivation, release, finish, and alignment flag construction.
- Provides accessor macros for resource fields.

Important invariants:
- Resources use linked lists instead of bitmaps so huge address spaces can be represented.
- Resource indexes are `u_long`, matching the historical design intent for large resource spaces.
- Resource ranges are inclusive; size is `r_end - r_start + 1`.
- `rm_cpuid` tracks ownership for DragonFly's per-CPU/resource-manager model.

Research notes:
- This is a kernel bus resource allocation contract with a small user-visible reporting ABI.
- `rman_await_resource()` is present only inside `#if 0`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/rman.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/rtprio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/rtprio.h

This header defines the realtime-priority ABI used by `rtprio()` and DragonFly's LWP-specific realtime-priority call.

Key responsibilities:
- Defines priority classes:
  - `RTP_PRIO_REALTIME`
  - `RTP_PRIO_NORMAL`
  - `RTP_PRIO_IDLE`
  - `RTP_PRIO_THREAD`
  - `RTP_PRIO_FIFO`
- Provides helper macros:
  - `RTP_PRIO_BASE()`
  - `RTP_PRIO_IS_REALTIME()`
  - `RTP_PRIO_NEED_RR()`
- Defines priority range:
  - `RTP_PRIO_MIN` is highest priority
  - `RTP_PRIO_MAX` is lowest priority
- Defines syscall operations:
  - `RTP_LOOKUP`
  - `RTP_SET`
- Defines `struct rtprio` with `type` and `prio`.
- Declares userland `rtprio()` and `lwp_rtprio()`.

Important invariants:
- `RTP_PRIO_FIFO` is represented as realtime with `RTP_PRIO_FIFO_BIT` set.
- `RTP_PRIO_NEED_RR()` treats FIFO as the non-round-robin exception.
- LWP realtime-priority declaration is guarded by `_LWP_RTPRIO_DECLARED`.

Research notes:
- This is a small ABI header for scheduling policy control, not the scheduler implementation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/rtprio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sbuf.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sbuf.h

This header defines the `sbuf` string/binary buffer API used for bounded and auto-extending formatted output.

Key responsibilities:
- Defines opaque `struct sbuf` API plus the concrete structure layout:
  - backing buffer
  - optional drain function and argument
  - error, size, length, flags, section length
- Defines drain callback type `sbuf_drain_func`.
- Defines user-selectable flags:
  - `SBUF_FIXEDLEN`
  - `SBUF_AUTOEXTEND`
  - `SBUF_USRFLAGMSK`
- Defines internal flags:
  - `SBUF_DYNAMIC`
  - `SBUF_FINISHED`
  - `SBUF_DYNSTRUCT`
  - `SBUF_INSECTION`
- Declares construction, mutation, formatting, trimming, finishing, access, and deletion APIs.
- Declares section APIs:
  - `sbuf_start_section()`
  - `sbuf_end_section()`
- Declares kernel-only UIO/copyin helpers:
  - `sbuf_uionew()`
  - `sbuf_bcopyin()`
  - `sbuf_copyin()`

Important invariants:
- `sbuf_new_auto()` constructs a dynamically allocated auto-extending sbuf.
- `sbuf_printf()` and `sbuf_vprintf()` carry format-checking attributes.
- The finished state is explicit; callers generally must call `sbuf_finish()` before treating data as finalized.

Research notes:
- This header is a reusable formatting and incremental-output utility, visible to both kernel and user contexts with kernel-only extensions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sched.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sched.h

This header defines the POSIX scheduling policy ABI and userland scheduling function declarations.

Key responsibilities:
- Defines scheduling policies:
  - `SCHED_FIFO`
  - `SCHED_OTHER`
  - `SCHED_RR`
- Defines `struct sched_param` with `sched_priority`.
- Declares POSIX scheduler APIs:
  - `sched_setparam()`
  - `sched_getparam()`
  - `sched_setscheduler()`
  - `sched_getscheduler()`
  - `sched_yield()`
  - `sched_get_priority_max()`
  - `sched_get_priority_min()`
  - `sched_rr_get_interval()`
- Under BSD visibility, includes CPU mask support and declares affinity APIs:
  - `sched_setaffinity()`
  - `sched_getaffinity()`
  - `sched_getcpu()`
- Defines `cpu_set_t` and FreeBSD-compatible `cpuset_t` as `cpumask_t`.

Important invariants:
- The userland declarations are excluded under `_KERNEL`.
- BSD affinity support depends on `<sys/cpumask.h>` and visibility gates.

Research notes:
- This is a POSIX/BSD user ABI header for scheduler control, not DragonFly's internal scheduler data structure header.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sched.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/select.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/select.h

This header defines the userland `select()`/`pselect()` ABI and pulls in the fd, signal, timeval, and timespec types needed by those interfaces.

Key responsibilities:
- Includes:
  - `sys/_fd_set.h`
  - `sys/_sigset.h`
  - `sys/_timespec.h`
  - `sys/_timeval.h`
- Defines `sigset_t` from `struct __sigset` if not already declared.
- Declares:
  - `select()`
  - `pselect()`

Important invariants:
- The prototypes use `restrict` annotations through `__restrict`.
- `pselect()` takes `const struct timespec *` and `const sigset_t *`.
- `select()` takes a mutable `struct timeval *`, matching traditional timeout modification semantics.

Research notes:
- This is a compact user ABI forwarding header.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/select.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sem.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sem.h

This header defines System V semaphore ABI structures, commands, permissions, kernel metadata, and syscall declarations.

Key responsibilities:
- Includes IPC and machine integer types.
- Defines `pid_t`, `size_t`, and `time_t` if needed.
- Defines public `struct semid_ds`:
  - permission record
  - base semaphore pointer
  - semaphore count
  - operation/change timestamps
  - SV ABI padding fields
- Defines kernel `struct semid_pool` containing a lock, descriptor, and generation number.
- Defines `struct sembuf` for `semop()` operations and `SEM_UNDO`.
- Under BSD visibility:
  - defines `MAX_SOPS`
  - defines `union semun`
  - defines `SEM_STAT`, `SEM_A`, and `SEM_R`
- Defines `semctl()` command constants:
  - `GETNCNT`, `GETPID`, `GETVAL`, `GETALL`, `GETZCNT`, `SETVAL`, `SETALL`
- Defines kernel `struct seminfo` for semaphore limits/tunables.
- Defines internal `SEM_ALLOC` and `SEM_DEST` mode bits.
- Declares kernel `semexit()` and global `seminfo`.
- Declares userland `semctl()`, `semget()`, and `semop()`.

Important invariants:
- The ABI preserves historical SV ABI padding in `struct semid_ds`.
- `union semun` is BSD-visible rather than always exposed.
- `SEM_DEST` marks a semaphore set being destroyed on last detach.

Research notes:
- This is the public and kernel-facing System V semaphore contract.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sensors.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sensors.h

This header defines the OpenBSD-derived hardware sensor ABI and DragonFly kernel sensor registration/task interface.

Key responsibilities:
- Defines `enum sensor_type` for temperature, fan, voltage, resistance, power, current, capacity, boolean indicators, raw integers, percent, illuminance, drive state, timedelta, ECC, frequency, and reserved types.
- Provides `sensor_type_s[]` string names for all sensor types plus `undefined`.
- Defines drive-state values such as empty, ready, online, idle, active, rebuild, powerdown, fail, and predictive fail.
- Defines `enum sensor_status`:
  - unspecified
  - OK
  - warning
  - critical
  - unknown
- Defines user-visible `struct sensor`:
  - description
  - last-change timeval
  - value
  - type/status
  - per-type number
  - flags
- Defines sensor flags:
  - `SENSOR_FINVALID`
  - `SENSOR_FUNKNOWN`
- Defines user-visible `struct sensordev` and `MAXSENSORDEVICES`.
- In kernel builds, defines:
  - `struct ksensor`
  - `struct ksensordev`
  - sensor device/sensor list links
  - sysctl nodes and contexts
- Declares kernel install/deinstall and attach/detach APIs.
- Declares deprecated `sensor_task_register()`/`sensor_task_unregister()` and replacement `sensor_task_register2()`/`sensor_task_unregister2()`.
- Defines inline helpers:
  - `sensor_set_invalid()`
  - `sensor_set_unknown()`
  - `sensor_set()`
  - `sensor_set_temp_degc()`

Important invariants:
- Public structures note that new fields should be appended for backward compatibility.
- Temperature values are represented in microkelvin; `sensor_set_temp_degc()` converts Celsius to microkelvin using `degc * 1000000 + 273150000`.
- Kernel `ksensor` mirrors the public sensor fields and adds list/sysctl linkage.

Research notes:
- This is both the user-visible sensor reporting schema and the kernel provider registration surface.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sensors.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/serial.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/serial.h

This header defines serial-port modem signal bits, delta bits, and kernel interrupt-source bits independent of tty processing.

Key responsibilities:
- Defines modem/control state bits:
  - `SER_DTR`, `SER_RTS`, `SER_STX`, `SER_SRX`
  - `SER_CTS`, `SER_DCD`, `SER_RI`, `SER_DSR`
- Defines `SER_MASK_STATE`.
- Defines `SER_DELTA(x)` and per-signal delta bits such as `SER_DDTR`, `SER_DCTS`, and `SER_DDSR`.
- Defines `SER_MASK_DELTA`.
- In kernel builds, defines interrupt-source flags:
  - `SER_INT_OVERRUN`
  - `SER_INT_BREAK`
  - `SER_INT_RXREADY`
  - `SER_INT_SIGCHG`
  - `SER_INT_TXIDLE`
- Defines interrupt masks:
  - `SER_INT_MASK`
  - `SER_INT_SIGMASK`
- Defines kernel interrupt callback type `serdev_intr_t`.

Important invariants:
- Modem bits are intended to match shifted `TIOCMGET` definitions from `<sys/ttycom.h>`.
- Both state and delta bits must fit in 16 bits.
- Kernel interrupt bits intentionally use upper bits so lower 16 bits remain for signal state/delta.

Research notes:
- This is a small cross-driver serial signal vocabulary, not a full serial driver interface.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/serial.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/serialize.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/serialize.h

This header defines DragonFly's lightweight `lwkt_serialize` synchronization primitive and its kernel API.

Key responsibilities:
- Defines `struct lwkt_serialize`:
  - atomic interrupt interlock
  - last-owning thread pointer
- Defines initializer `LWKT_SERIALIZE_INITIALIZER`.
- Defines ownership assertion helpers:
  - `IS_SERIALIZED()`
  - `ASSERT_SERIALIZED()`
  - `ASSERT_NOT_SERIALIZED()`
- Defines `lwkt_serialize_t`.
- Declares kernel functions:
  - init
  - enter/adaptive enter
  - try
  - exit
  - handler disable/enable/call/try

Important invariants:
- The header explicitly warns the primitive is not recursive and is not deadlock-safe like tokens.
- It is meant to serialize across blocking conditions while being fast in the common case.
- Ownership tracking uses `last_td` and `curthread` for assertions.

Research notes:
- This is a DragonFly-specific low-level serialization primitive used where a full token would be heavier.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/serialize.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/serialize2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/serialize2.h

This kernel-only header defines inline helpers for acquiring and releasing arrays of `lwkt_serialize_t` serializers in a fixed order.

Key responsibilities:
- Rejects userland inclusion with `#error`.
- Includes kernel param/systm and `serialize.h`.
- Defines `lwkt_serialize_array_enter()`:
  - asserts starting index is valid
  - enters serializers from index `_s` through `_arrcnt - 1`
- Defines `lwkt_serialize_array_try()`:
  - tries serializers in ascending order
  - unwinds already acquired serializers in reverse order on failure
- Defines `lwkt_serialize_array_exit()`:
  - exits serializers in reverse order

Important invariants:
- Callers supply a starting index, enabling partial-array locking.
- Enter order is ascending; exit/unwind order is descending.
- KASSERT guards reject empty ranges.

Research notes:
- This header provides correct bulk acquisition patterns for non-recursive serializers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/serialize2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sfbuf.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sfbuf.h

This kernel-only header defines sendfile/lightweight page buffer wrappers around DragonFly `lwbuf`.

Key responsibilities:
- Includes `<cpu/lwbuf.h>`.
- Rejects userland inclusion unless kernel structures are requested.
- Defines `struct sf_buf`:
  - pointer to active `lwbuf`
  - reference count
  - cached embedded `lwbuf`
- Defines access macros:
  - `sf_buf_kva()`
  - `sf_buf_page()`
- Declares kernel APIs:
  - `sf_buf_alloc()`
  - `sf_buf_ref()`
  - `sf_buf_free()`

Important invariants:
- `sf_buf_kva()` and `sf_buf_page()` delegate directly to the active `lwbuf`.
- The structure supports reference counting for page mappings used by sendfile-style paths.

Research notes:
- This is a small compatibility/abstraction layer over DragonFly lightweight buffers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sfbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sglist.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sglist.h

This kernel-only header defines scatter/gather list structures and APIs for physical address ranges.

Key responsibilities:
- Rejects userland inclusion.
- Defines `struct sglist_seg` with physical address and length.
- Defines `struct sglist`:
  - segment array
  - reference count
  - current segment count
  - maximum segment count
- Declares forward references for `mbuf` and `uio`.
- Defines inline helpers:
  - `sglist_init()`
  - `sglist_reset()`
  - `sglist_hold()`
- Declares allocation, append, build, clone, count, join, slice, split, length, free, and UIO consumption APIs.

Important invariants:
- `sglist_init()` initializes refcount to 1 and sets `sg_nseg` to 0.
- `sglist_reset()` clears only the used segment count, retaining storage and max segment capacity.
- `sglist_hold()` increments the reference count and returns the same pointer.

Research notes:
- This API is used for physical scatter/gather descriptions across kernel buffer, mbuf, UIO, and user memory paths.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sglist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/shm.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/shm.h

This header defines System V shared memory ABI structures, flags, tunables, and kernel/user APIs.

Key responsibilities:
- Defines attach flags:
  - `SHM_RDONLY`
  - `SHM_RND`
  - `SHMLBA`
- Under BSD visibility, defines `SHM_R` and `SHM_W`.
- Defines `shmatt_t`, plus `pid_t`, `size_t`, and `time_t` if needed.
- Defines public `struct shmid_ds`:
  - IPC permissions
  - segment size
  - last-op and creator PIDs
  - attach count
  - attach/detach/change times
  - internal pointer
- Defines kernel `struct shminfo` with SysV shared memory limits.
- Declares kernel `shminfo`, `shmexit()`, and `shmfork()`.
- Declares userland `shmget()`, `shmctl()`, `shmat()`, and `shmdt()`.

Important invariants:
- `SHMLBA` is `PAGE_SIZE`.
- Shared memory accounting tracks both creator and last-operation process IDs.
- Kernel VM integration is explicit through `struct vmspace` in `shmexit()`.

Research notes:
- This is the System V shared memory ABI plus process/VM lifecycle hooks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/shm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/signal.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/signal.h

This header defines the public signal ABI: signal numbers, signal sets, signal actions, alternate stacks, event notification, and signal-related userland declarations.

Key responsibilities:
- Defines `pid_t`, `size_t`, and `uid_t` where needed.
- Defines sigset indexing macros:
  - `_SIG_MAXSIG`
  - `_SIG_IDX`
  - `_SIG_WORD`
  - `_SIG_BIT`
  - `_SIG_VALID`
- Defines standard and BSD signal numbers, including:
  - traditional signals 1-34
  - checkpoint signals `SIGCKPT` and `SIGCKPTEXIT`
  - realtime range `SIGRTMIN` to `SIGRTMAX`
- Defines handler type `__sighandler_t` and sentinel handlers:
  - `SIG_DFL`
  - `SIG_IGN`
  - `SIG_ERR`
- Defines `struct sigevent` and notification types:
  - `SIGEV_NONE`
  - `SIGEV_SIGNAL`
  - `SIGEV_THREAD`
  - BSD `SIGEV_KEVENT`
- Defines `sigset_t` and includes machine signal definitions after it is available.
- Defines POSIX `struct sigaction`, handler/sigaction aliases, and signal action flags.
- Defines BSD `NSIG`, `SI_UNDEFINED`, `sig_t`, and `struct sigvec`.
- Defines alternate signal stack flags and sizes:
  - `SS_ONSTACK`
  - `SS_DISABLE`
  - `MINSIGSTKSZ`
  - `SIGSTKSZ`
- Defines `SIG_BLOCK`, `SIG_UNBLOCK`, and `SIG_SETMASK`.
- Declares `signal()` and BSD `sigblockall()`/`sigunblockall()`.

Important invariants:
- `_SIG_MAXSIG` is 128, while BSD-visible `NSIG` is 64 for historical `sigptbl` sizing.
- `SIGKILL` and `SIGSTOP` are the uncatchable/unignorable signals in later kernel macros.
- `struct sigaction` stores handler and sigaction callback in a union; `SA_SIGINFO` determines which is meaningful.
- `SIG_EINTR` is described in comments as an internal no-delivery interrupt cause, but no public define appears in this header.

Research notes:
- This is a visibility-gated ABI header with POSIX, XSI, and BSD surfaces interleaved.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/signal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/signal2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/signal2.h

This kernel inline header defines signal-delivery helpers, permission tests, pending-signal computation, conditional all-signal blocking, current-signal selection, and signal-processing reference interlocks.

Key responsibilities:
- Includes kernel process, signalvar, and systm headers.
- Defines `CANSIGNAL(q, sig, initok)`:
  - checks credential trespass
  - checks reaper signal rules
  - allows `SIGCONT` within the same session
- Defines `lwp_sigpend()` to combine process and LWP pending signal sets.
- Defines `lwp_delsig()` to clear LWP pending and optionally process pending state.
- Defines `__sig_condblockallsigs()`:
  - checks per-LWP user-mapped `blockallsigs`
  - marks signal-arrival bit 31
  - masks all maskable signals while preserving unmaskable and synchronous trap signals
- Defines `__cursig()` and macros:
  - `CURSIG`
  - `CURSIG_TRACE`
  - `CURSIG_LCK_TRACE`
  - `CURSIG_NOBLOCK`
- Defines generic signal-processing reference helpers:
  - `sigirefs_hold()`
  - `sigirefs_drop()`
  - `sigirefs_wait()`

Important invariants:
- `lwp_delsig()` requires `p->p_token` and `lp->lwp_spin`.
- `__cursig()` may return with `proc->p_token` held through the `ptok` mechanism.
- Userland `blockallsigs` bit 31 is used as a signal-arrival notification bit.
- `sigirefs_wait()` uses the high bit of `p_sigirefs` as a waiter flag and sleeps on the field.

Research notes:
- This file contains concurrency-sensitive signal delivery logic and userland fast-path integration.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/signal2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/signalvar.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/signalvar.h

This header defines kernel signal action state, signal set manipulation macros, and machine-independent/machine-dependent signal function declarations.

Key responsibilities:
- Includes `sys/signal.h`; kernel builds also include process and lock headers.
- Defines `struct sigacts`:
  - per-signal disposition table
  - catch masks
  - source PID/UID info
  - ignored/caught/onstack/intr/reset/nodefer/siginfo/usertramp signal sets
  - refcount and flags
- Defines internal handler sentinels:
  - `SIG_CATCH`
  - `SIG_HOLD`
- Defines kernel `SIGACTION(p, sig)` lookup macro.
- Defines signal set manipulation macros:
  - add/delete
  - atomic add/delete
  - empty/fill
  - member check
  - empty/equality checks
  - OR/AND/NAND operations
  - unmaskable, stop-signal, and continue-signal cleanup helpers
- Defines `sigcantmask`.
- Provides inline `__sigisempty()` and `__sigseteq()`.
- Declares kernel signal functions:
  - process exec/init/kill/group signaling
  - `issignal()`, `iscaught()`, `postsig()`
  - direct process/LWP signal posting
  - trap signal handling
  - machine-dependent `sendsig()` and `sigexit()`
  - checkpoint signal handler hook

Important invariants:
- `SIG_CANTMASK()` removes `SIGKILL` and `SIGSTOP` from a mask.
- Atomic signal-set operations use `atomic_set_int()`/`atomic_clear_int()` on backing words.
- `struct sigacts` is process signal action state, not necessarily resident according to comments.

Research notes:
- This file supplies the macros used by `signal2.h` and kernel signal implementation files.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/signalvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/single_threaded.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/single_threaded.h

This user ABI header declares libc threading-state globals.

Key responsibilities:
- Declares `extern int __isthreaded` once via `__LIBC_ISTHREADED_DECLARED`.
- Declares `extern char __libc_single_threaded`.

Important invariants:
- Comment states zero value of `__libc_single_threaded` indicates the process might be multi-threaded.
- The header uses C linkage guards through `__BEGIN_DECLS`/`__END_DECLS`.

Research notes:
- This header exposes libc runtime state used by optimized single-threaded code paths.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/single_threaded.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/slaballoc.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/slaballoc.h

This kernel-structure header defines DragonFly's slab allocator zone and per-CPU metadata structures.

Key responsibilities:
- Defines slab sizing constants:
  - `ZALLOC_ZONE_LIMIT`
  - `ZALLOC_MIN_ZONE_SIZE`
  - `ZALLOC_MAX_ZONE_SIZE`
  - slab/oversize magic values
  - `ZALLOC_SLAB_SLIDE`
- Defines `NZONES` based on `ZALLOC_ZONE_LIMIT`.
- Defines `SLChunk` free-list node.
- Under `SLAB_DEBUG`, defines allocation source tracking entries.
- Defines `SLZone`, the in-band zone header:
  - magic
  - owner CPU/globaldata
  - zone list linkage
  - free counts and chunk bounds
  - chunk size, zone index, flags
  - local free chunks
  - remote free chunks
  - remote signal/count fields
  - optional debug source arrays
  - optional invariant bitmap
- Defines `SLZF_UNOTZEROD`.
- Defines `SLZoneList`.
- Defines `SLGlobalData`:
  - zone arrays by size class
  - free zone lists
  - free-zone count
  - junk index
  - meta-zone malloc stats

Important invariants:
- Allocations that are exact page-size multiples or `>= ZALLOC_ZONE_LIMIT` fall through to kmem.
- Most `SLZone` fields are CPU-local except `z_RChunks`; remote CPUs free through atomic operations and signal local CPUs as needed.
- `SLAB_DEBUG_ENTRIES` must be a power of two.
- `NZONES` is compile-time constrained to known zone limits.

Research notes:
- This header defines allocator internals and layout, not allocator public allocation functions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/slaballoc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sleepqueue.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sleepqueue.h

This kernel header defines the sleep queue API used by sleep/wakeup, condition variables, pause, sx locks, and lockmgr-style waits.

Key responsibilities:
- Documents the sleep queue usage model:
  - lock a queue chain for a wait channel
  - add the current thread
  - optionally set timeout
  - wait or timed wait
  - signal/broadcast/abort/remove under queue lock
- Defines queue type and behavior flags:
  - `SLEEPQ_SLEEP`
  - `SLEEPQ_CONDVAR`
  - `SLEEPQ_PAUSE`
  - `SLEEPQ_SX`
  - `SLEEPQ_LK`
  - `SLEEPQ_INTERRUPTIBLE`
  - `SLEEPQ_UNFAIR`
  - `SLEEPQ_DROP`
- Declares DragonFly applicable APIs:
  - setup/teardown per thread
  - add, lock, release
  - signal, broadcast
  - timeout setup
  - sleep count
  - timed wait and signal-interruptible timed wait
  - type query
  - wait and signal-interruptible wait
- Keeps several FreeBSD-style APIs in `#if 0` as not applicable to DragonFly.

Important invariants:
- Sleep queue chain must be locked before signal/broadcast according to comments.
- Signal/broadcast return whether at least one swapped-out thread resumed; caller may need to kick proc0 after releasing the lock.
- Timeout macro converts ticks to `sbintime_t` using `tick_sbt` and `C_HARDCLOCK`.

Research notes:
- This header documents the contract around wait-channel queue locking even though many implementation details live elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sleepqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/snoop.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/snoop.h

This header defines ioctl commands and error sentinel values for tty snooping support.

Key responsibilities:
- Includes ioctl command encoding definitions.
- Defines snoop ioctl commands:
  - `SNPSTTY`
  - `SNPGTTY`
- Defines negative `FIONREAD` sentinel returns:
  - `SNP_OFLOW`
  - `SNP_TTYCLOSE`
  - `SNP_DETACH`

Important invariants:
- `SNPSTTY` and `SNPGTTY` use `dev_t` as their ioctl payload type.
- Comments state setting type or unit to `-1` detaches the snoop device from its current tty, though the current command payload is `dev_t`.

Research notes:
- This is a narrow compatibility header for the snoop device interface.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/snoop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sockbuf.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sockbuf.h

This header defines a generic mbuf-chain socket buffer structure and low-level buffer manipulation macros/functions.

Key responsibilities:
- Defines kernel `struct sockbuf`:
  - actual byte count
  - mbuf memory count
  - preallocation byte/memory counts
  - I/O data limit
  - mbuf chain head
  - last mbuf
  - last record
- Defines default `SB_MAX`.
- Defines debug `sbcheck()` behavior.
- Defines counter macros:
  - `sballoc()`
  - `sbprealloc()`
  - `sbfree()`
- Defines inline `sbinit()`.
- Declares append, append-address, append-control, append-record, append-stream, compress, create-control, drop, drop-record, unlink, check, and flush functions.

Important invariants:
- `sballoc()` and `sbfree()` account both mbuf header size and external storage size.
- Preallocation counters are updated atomically.
- `sb_lastrecord` is valid only when `sb_mb` is non-NULL.
- `sbinit()` clears all counters and chain pointers while setting the caller-provided limit.

Research notes:
- `sockbuf.h` is lower-level than `socketvar.h`; `signalsockbuf` embeds it and adds locking/notification state.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sockbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/socket.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/socket.h

This header defines the primary socket user ABI: socket types, options, address families, socket address structures, message and control-message formats, shutdown constants, sendfile header/trailer structure, and socket syscall declarations.

Key responsibilities:
- Defines socket-related types:
  - `sa_family_t`
  - `socklen_t`
  - BSD-visible `gid_t`, `uid_t`, and `off_t`
- Defines socket types and BSD socket creation flags:
  - `SOCK_STREAM`, `SOCK_DGRAM`, `SOCK_RAW`, `SOCK_SEQPACKET`, BSD `SOCK_RDM`
  - `SOCK_CLOEXEC`, `SOCK_NONBLOCK`, `SOCK_CLOFORK`
  - kernel `SOCK_KERN_NOINHERIT`
- Defines socket options:
  - `SO_DEBUG`, `SO_ACCEPTCONN`, `SO_REUSEADDR`, `SO_KEEPALIVE`, `SO_LINGER`, etc.
  - buffer/time/error/type options `SO_SNDBUF`, `SO_RCVBUF`, `SO_ERROR`, `SO_TYPE`
  - DragonFly/BSD additions such as `SO_USER_COOKIE` and `SO_CPUHINT`
- Defines `struct linger` and BSD `struct accept_filter_arg`.
- Defines `SOL_SOCKET`.
- Defines address families and BSD-visible protocol family aliases.
- Defines `struct sockaddr`, `SOCK_MAXADDRLEN`, kernel `sa_equal()`, `struct sockproto`, and `struct sockaddr_storage`.
- Defines network sysctl constants such as `NET_RT_DUMP`, `NET_RT_FLAGS`, and `NET_RT_IFLIST`.
- Defines listen and sockopt limits:
  - `SOMAXCONN`
  - `SOMAXOPT_SIZE`
  - `SOMAXOPT_SIZE0`
- Defines `struct msghdr`, message flags, `struct cmsghdr`, credential ancillary data, and `CMSG_*` macros.
- Defines control message types:
  - `SCM_RIGHTS`
  - BSD `SCM_TIMESTAMP`
  - BSD `SCM_CREDS`
- Defines shutdown constants `SHUT_RD`, `SHUT_WR`, `SHUT_RDWR`.
- Defines BSD `struct sf_hdtr` for `sendfile()`.
- Declares socket syscalls and BSD extensions:
  - standard socket, bind, connect, listen, accept, send, recv, getsockopt, setsockopt, shutdown
  - `accept4`, `extaccept`, `extconnect`, `pfctlinput`, `sendfile`

Important invariants:
- `struct sockaddr` uses a length byte and family byte, BSD style.
- `struct sockaddr_storage` is 128 bytes and aligned using an `__int64_t` field.
- `CMSG_NXTHDR()` performs bounds checking against `msg_controllen`.
- `MSG_FBLOCKING` and `MSG_FNONBLOCKING` override `FIONBIO`; their mask is `MSG_FMASK`.
- `SOMAXOPT_SIZE0` allows larger root `getsockopt()` payloads.

Research notes:
- This is one of the core network ABI headers and must remain stable for userland compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/socket.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/socketops.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/socketops.h

This kernel-only header declares DragonFly socket protocol-operation wrappers, including synchronous, direct, fast, and asynchronous protocol request paths.

Key responsibilities:
- Rejects userland inclusion.
- Includes protocol switch, socket ABI, and socket kernel state headers.
- Defines inline direct calls for:
  - `so_pru_sosend()`
  - `so_pru_soreceive()`
- Declares protocol request wrappers for:
  - abort, accept, attach, bind, connect, connect2, control, detach, disconnect, listen, peeraddr, rcvd, rcvoob, sync, send, sense, shutdown, sockaddr
- Declares async variants:
  - async abort
  - async connect
  - async rcvd
  - async send
  - async rcvd reply/drop helpers
- Declares protocol control-input/control-output helpers:
  - `so_pr_ctloutput()`
  - `so_pr_ctlport()`
  - `so_pr_ctlinput()`
  - `so_pr_ctlinput_direct()`
- Defines `so_pru_senda()`:
  - uses async send if protocol has `PR_ASYNC_SEND`
  - otherwise sends synchronously

Important invariants:
- Comments state `sosend()` and `soreceive()` can block and call other `pru_usrreq` functions, so they should be called directly from process context rather than dispatched to protocol threads.
- `so_pru_senda()` assumes async send consumes/handles the mbuf path and returns 0 immediately.

Research notes:
- This file is the adapter layer between sockets and protocol switch/user request implementations in DragonFly's message-passing network stack.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/socketops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/socketvar.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/socketvar.h

This header defines DragonFly kernel socket state, signaling socket buffers, socket state bits, sysctl-exported socket records, socket buffer predicates, socket options, accept filters, and socket/file operation declarations.

Key responsibilities:
- Defines `struct signalsockbuf`, embedding `struct sockbuf` and adding:
  - kqueue info
  - pending notification message list
  - atomic flags
  - timeout, low/high water marks, mbuf max
  - frontend/backend token
- Defines `SSB_*` flags:
  - lock/wait/async/upcall/nointr/knote/message event/stop/autosize/autolowat/wakeup/prealloc/stopsupp
- Defines `SSB_CLEAR_MASK` and `SSB_NOTIFY_MASK`.
- Defines kernel `struct socket`:
  - type/options/linger/state
  - protocol PCB and protocol switch pointer
  - accept queue head/back pointer/listing fields
  - message port/original port
  - errors, async I/O, OOB mark
  - receive/send `signalsockbuf`
  - upcall, credentials, emulator data, refs
  - accept filter data
  - close and received netmsgs
  - foreign address
  - socket inode and user cookie
- Defines socket state bits `SS_*`.
- Defines sysctl-exported `struct xsocket` and nested `struct xsockbuf`.
- Defines macros:
  - `sosendallatonce()`
  - `soreadable()`
  - `sowriteable()`
  - `ssb_append*()` wrappers
  - kqueue note insertion/removal
  - `sorwakeup()`/`sowwakeup()`
- Defines inline `ssb_space()` and `ssb_space_prealloc()`.
- Defines inline `ssb_preallocstream()`.
- Defines kernel `struct sockopt` and `enum sopt_dir`.
- Defines `struct accept_filter`.
- Declares socket malloc types, globals, file operations, socket buffer functions, socket lifecycle/state functions, option copy helpers, send/receive variants, wakeup, export, and accept-filter APIs.

Important invariants:
- `SSB_STOP` makes `ssb_space()` report zero regardless of byte/mbuf counters.
- Preallocation-aware space uses the tighter of actual and preallocated availability.
- `soreadable()` considers data, receive shutdown, completed accept queue, and socket errors.
- `sowriteable()` considers send buffer space, connection state/protocol flags, send shutdown, and error.
- `SS_NOFDREF` and `so_pcb` state are explicitly interlocked with `so_refs`.
- `signalsockbuf` partial clearing is sensitive to `sorflush()` and `sowflush()` implementation details.

Research notes:
- This is the central kernel socket object contract and is tightly coupled to DragonFly's netmsg/lwkt token design.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/socketvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/socketvar2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/socketvar2.h

This kernel-only inline header defines locking and atomic state helpers for `signalsockbuf` and sockets.

Key responsibilities:
- Rejects userland inclusion.
- Includes `socketvar.h`, `systm.h`, and machine atomics.
- Defines `ssb_lock()` inline when `MALLOC_DEFINE` is present:
  - spins/CASes `SSB_LOCK`
  - uses `_ssb_lock()` when lock is held and waiting is allowed
  - returns `EWOULDBLOCK` for non-waiting lock failure
  - acquires `ssb_token` on success
- Defines `ssb_unlock()`:
  - releases token
  - clears `SSB_LOCK` and `SSB_WANT`
  - wakes waiters if `SSB_WANT` was set
- Defines atomic socket state helpers:
  - `sosetstate()`
  - `soclrstate()`
- Defines `soreference()` to increment `so_refs`.

Important invariants:
- `ssb_lock()` must acquire both the flag lock and the lwkt token on success.
- `ssb_unlock()` asserts the lock bit is held before releasing.
- `soreference()` allows a 0 to 1 transition for aborted sockets left on accept queues.

Research notes:
- This file keeps fast-path socket locking and state transitions inline while relying on slower contested code elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/socketvar2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sockio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/sockio.h

This header defines socket and network-interface ioctl command numbers.

Key responsibilities:
- Defines generic socket ioctls:
  - high/low water mark get/set
  - OOB mark query
  - process group get/set
- Defines multicast routing counter ioctls:
  - `SIOCGETVIFCNT`
  - `SIOCGETSGCNT`
- Defines interface address, destination, broadcast, netmask, flags, config, metric, alias, capability, index, data, name, description, multicast, MTU, physical/media/generic/status/link address ioctls.
- Defines gif/tunnel physical address ioctls.
- Defines Linux-private compatibility query slots.
- Defines clone interface ioctls:
  - get cloners
  - create/destroy
  - create2
- Defines driver-specific parameter ioctls.
- Defines deprecated polling CPU ioctls.
- Defines TSO length ioctls.
- Defines interface group ioctls.
- Defines extended media query ioctl.

Important invariants:
- Many ioctl numeric slots are preserved with comments for ABI compatibility.
- `SIOCSDRVSPEC` and `SIOCGDRVSPEC` intentionally share command number 123 with different directions.
- Deprecated poll CPU ioctls remain defined for compatibility.

Research notes:
- This is a stable networking control-plane ABI header; structures referenced are defined by networking headers such as `if.h`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/sockio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/soundcard.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/soundcard.h

This large header defines the OSS/VoxWare/FreeBSD soundcard compatibility ABI: audio formats, sound device IDs, DSP/sequencer/mixer/MIDI/coprocessor ioctls, event formats, convenience sequencer macros, and OSSv4 metadata structures.

Key responsibilities:
- Defines `SOUND_VERSION` and legacy VoxWare marker.
- Defines legacy sound card IDs such as AdLib, SoundBlaster, GUS, MPU401, MSS, OPL, and related devices.
- Defines newer FreeBSD audio ioctls:
  - `AIONWRITE`
  - `AIOGSIZE`/`AIOSSIZE`
  - `AIOGFMT`/`AIOSFMT`
  - mixer/sync/capability ioctls
- Defines audio format bitmasks:
  - mu-law, A-law, ADPCM, signed/unsigned 8/16/24/32-bit, MPEG, AC3
  - native-endian and opposite-endian aliases
  - stereo, weird hardware, full-duplex capabilities
- Defines `snd_chan_param`, `snd_mix_param`, `snd_sync_parm`, and `snd_capabilities`.
- Defines legacy `/dev/sequencer` ioctl set, timer ioctls, and sequence event records.
- Defines patch/sample upload structures:
  - `patch_info`
  - `sysex_info`
  - `sbi_instrument`
  - `patmgr_info`
- Defines patch manager status, command, event, and data payload constants.
- Defines sequencer event codes, MIDI controller constants, MIDI event types, timer event types, local events, and multiple compatibility aliases.
- Defines synth, timer, and MIDI info structures:
  - `synth_info`
  - `sound_timer_info`
  - `midi_info`
  - `mpu_command_rec`
- Defines `/dev/dsp` and `/dev/audio` ioctls for reset/sync/speed/stereo/format/buffer/fragments/nonblock/caps/triggers/pointers/mmap/syncro/duplex/delay.
- Defines `audio_buf_info`, `count_info`, and buffer mapping structures.
- Defines PCM/DSP capability bits and compatibility aliases between `PCM_CAP_*` and `DSP_CAP_*`.
- Defines coprocessor buffer/debug/message structures and coprocessor ioctls.
- Defines legacy mixer device indexes, names, labels, masks, read/write ioctl macros, and `mixer_info`.
- Defines sequencer convenience macros for building output buffers and events:
  - buffer declaration/use
  - patch loading
  - MIDI voice/common/sysex events
  - controller/bender/timer/local/audio events
- Defines ioctl alias names such as `SOUND_PCM_WRITE_BITS`, `SOUND_PCM_GETOSPACE`, etc.
- Defines OSSv4 additions:
  - long-name/label/devnode typedefs
  - `audio_errinfo`
  - sync groups
  - cooked mode, silence/skip, input/output halt, low-water, 64-bit counters
  - recording/playback target routing controls
  - channel ordering and peak metering
  - channel binding flags
  - `oss_sysinfo`, `oss_mixext`, `oss_mixer_value`, `oss_mixer_enuminfo`
  - `oss_audioinfo`, `oss_mixerinfo`, `oss_midi_info`, `oss_card_info`
  - system/mixer/audio/MIDI/card/engine info ioctls
  - song/name/label ioctls

Important invariants:
- The file warns that ioctl commands and ABI types must not be changed incompatibly without coordinating with OSS upstream.
- Mixer IDs use a bitmask space where bit 31 is reserved.
- Sequencer level-1 events are 4 bytes; many level-2 and extended events are 8 bytes.
- `SEQ_FULLSIZE` patch/sample uploads must be written as exactly one write call without mixed events.
- OSSv4 `SOUND_VERSION` is redefined to `0x040000` if already defined.
- Many structs contain large filler arrays for ABI extension without changing size.

Research notes:
- This is primarily compatibility ABI surface rather than DragonFly-specific implementation.
- It intentionally preserves obsolete names and misspellings, for example `SNDCTL_SEQ_TRESHOLD`, to match historical applications.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/soundcard.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/spinlock.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/spinlock.h

This header defines the basic DragonFly spinlock structure and shared/exclusive bit layout.

Key responsibilities:
- Defines `struct spinlock`:
  - `lock` count/flags word
  - `update` counter
- Defines `SPINLOCK_INITIALIZER`.
- Defines spinlock bit constants:
  - `SPINLOCK_SHARED`
  - `SPINLOCK_EXCLWAIT`
  - `SPINLOCK_EXCLWAIT_MASK`
  - `SPINLOCK_EXCLWAIT_SHIFT`

Important invariants:
- The structure is retained for both SMP and UP builds, preserving embedded-structure size.
- DragonFly spinlocks use a count/flag system.
- Shared spinlocks are supported.
- There is no description field; wait descriptions are pulled from `__func__` in acquisition wrappers.

Research notes:
- This is the structural/bit-definition half of spinlocks; inline behavior is in `spinlock2.h`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/spinlock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/spinlock2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/spinlock2.h

This kernel-only inline header implements fast-path DragonFly spinlock operations, shared spinlocks, upgrades, initialization, and update-counter read/retry support.

Key responsibilities:
- Rejects userland inclusion.
- Includes kernel systm/thread/globaldata and machine atomic/cpufunc headers.
- Declares global `pmap_spin`.
- Declares contested-path helpers:
  - `spin_trylock_contested()`
  - `_spin_lock_contested()`
  - `_spin_lock_shared_contested()`
- Defines public macros that pass `__func__` as the wait/identity string.
- Defines `spin_trylock()`:
  - enters critical section
  - increments per-CPU spinlock count
  - CASes lock from 0 to 1
  - falls back to contested trylock
  - records debug lock stack if enabled
- Defines `spin_held()`.
- Defines exclusive lock/unlock fast paths:
  - `_spin_lock_quick()`
  - `_spin_lock()`
  - `spin_unlock_quick()`
  - `spin_unlock()`
  - `spin_unlock_any()`
- Defines shared lock/unlock fast paths:
  - `_spin_lock_shared_quick()`
  - `_spin_lock_shared()`
  - `spin_unlock_shared_quick()`
  - `spin_unlock_shared()`
- Defines `spin_lock_upgrade_try()`.
- Defines `spin_init()` and `spin_uninit()`.
- Defines update-counter access API:
  - `spin_access_start()`
  - `spin_access_end()`
  - `spin_lock_update()`
  - `spin_unlock_update()`
- Defines non-lock-integrated update-counter API:
  - `spin_access_start_only()`
  - `spin_access_check_inprog()`
  - `spin_access_end_only()`
  - `spin_lock_update_only()`
  - `spin_unlock_update_only()`

Important invariants:
- All successful lock acquisitions enter a raw critical section and increment `gd_spinlocks`.
- Unlock paths decrement `gd_spinlocks` and exit the critical section after clearing the lock.
- Shared spinlocks cache `SPINLOCK_SHARED` when count reaches zero for faster subsequent shared locks.
- Exclusive conflict handling can convert multiply-held shared locks to exclusive waiting state; shared unlock comments warn about this.
- Update counter uses odd values to mark modification in progress and even values for stable snapshots.
- `spin_access_start()` acquires a shared spinlock if an update is in progress, avoiding dirtying cachelines in the normal read path.

Research notes:
- This is a highly concurrency-sensitive header; memory barriers and atomic operations are integral to correctness.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/spinlock2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/stat.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/stat.h

This header defines file status ABI: `struct stat`, file mode/type bits, file flag bits, timestamp macros, POSIX stat-related constants, and userland filesystem metadata function declarations.

Key responsibilities:
- Defines filesystem-related types if needed:
  - `blkcnt_t`, `blksize_t`, `dev_t`, `gid_t`, `ino_t`, `mode_t`, `nlink_t`, `off_t`, `time_t`, `uid_t`
- Defines `struct stat`:
  - inode, link count, device, mode, owner/group, rdev
  - access/modify/change `timespec`
  - size, blocks, legacy blocksize field
  - flags, generation, spare fields
  - current `st_blksize`
- Defines time aliases:
  - `st_atime`, `st_mtime`, `st_ctime`
  - BSD `st_atimespec`, `st_mtimespec`, `st_ctimespec`
- Defines permission bits and aliases:
  - setuid/setgid/sticky
  - owner/group/other rwx masks
  - BSD read/write/exec aliases
- Defines file type bits and test macros:
  - fifo, char, dir, block, regular, symlink, socket
  - BSD DB and whiteout
- Defines POSIX `S_TYPEISMQ`, `S_TYPEISSEM`, and `S_TYPEISSHM` as zero.
- Defines BSD mode constants:
  - `ACCESSPERMS`
  - `ALLPERMS`
  - `DEFFILEMODE`
  - `S_BLKSIZE`
- Defines user and superuser file flags:
  - `UF_NODUMP`, immutable, append, opaque, nounlink, nohistory, cache, xlink
  - `SF_ARCHIVED`, immutable, append, nounlink, nohistory, nocache, xlink
- Defines kernel shorthand flags:
  - `OPAQUE`
  - `APPEND`
  - `IMMUTABLE`
  - `NOUNLINK`
- Defines POSIX.1-2008 timestamp constants `UTIME_NOW` and `UTIME_OMIT`.
- Declares userland APIs:
  - chmod/fchmod/fchmodat
  - futimens/utimensat
  - fstat/lstat/stat/fstatat
  - mkdir/mkdirat
  - mkfifo/mkfifoat
  - mknod/mknodat
  - umask
  - BSD chflags/fchflags/lchflags/chflagsat/lchmod

Important invariants:
- `struct stat` preserves `__old_st_blksize` for old ABI compatibility while using `st_blksize` later.
- File mode constants must remain consistent with `<fcntl.h>`.
- POSIX IPC object type test macros return zero because these are not implemented as distinct file types.
- `UF_SETTABLE` and `SF_SETTABLE` partition owner-changeable and superuser-changeable flag spaces.

Research notes:
- This is a stable filesystem metadata ABI header and directly relevant to VFS/stat syscall compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/stat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/statvfs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/statvfs.h

This header defines POSIX `statvfs` filesystem capacity/status ABI plus DragonFly UUID extensions.

Key responsibilities:
- Defines `fsblkcnt_t`, `fsfilcnt_t`, and `uid_t` if needed.
- Under BSD visibility, forward-declares `struct fhandle` and `struct statfs`.
- Defines `struct statvfs`:
  - block size and fragment size
  - total/free/available block counts
  - total/free/available file counts
  - filesystem ID
  - mount flags
  - maximum filename length
  - mount owner UID
  - filesystem type
  - synchronous/asynchronous read/write counters
  - DragonFly filesystem UUID and owner UUID fields
- Defines flags:
  - `ST_RDONLY`
  - `ST_NOSUID`
  - BSD `ST_FSID_UUID`
  - BSD `ST_OWNER_UUID`
- Declares:
  - `fstatvfs()`
  - `statvfs()`
  - BSD `fhstatvfs()`
  - BSD `getvfsstat()`

Important invariants:
- Comments distinguish free blocks from blocks available to unprivileged users.
- DragonFly extensions add full UUID FSID and owner identity beyond the scalar `f_fsid`/`f_owner` fields.
- `ST_FSID_UUID` and `ST_OWNER_UUID` indicate validity of the UUID extension fields.

Research notes:
- This is the filesystem-capacity counterpart to `stat.h`, with DragonFly-specific UUID extensions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/statvfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/stdarg.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/stdarg.h

This header provides DragonFly's `stdarg` proxy definitions using machine/compiler varargs primitives.

Key responsibilities:
- Includes `<machine/stdarg.h>`.
- Defines `va_list` from `__va_list` if not already declared.
- Defines:
  - `va_start`
  - `va_arg`
  - `va_copy`
  - `va_end`
- Defines legacy `__va_copy` as `___va_copy`.

Important invariants:
- `va_copy` is exposed for kernel, C99 or newer, C++11 or newer, or non-strict ANSI compatibility.
- The implementation delegates all mechanics to machine/compiler builtins.

Research notes:
- This is a small compatibility wrapper around machine-level varargs support.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/stdarg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/stdint.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/stdint.h

This header is a kernel proxy for fixed-width integer, boolean, max-width, pointer, and offset types, while forwarding userland to standard `<stdint.h>`.

Key responsibilities:
- Includes `sys/cdefs.h` and `machine/stdint.h`.
- Documents that userland should use `<stdint.h>` instead.
- In kernel builds:
  - includes machine integer limits
  - defines `boolean_t`
  - defines `bool`, `true`, and `false` when C/C++ conditions permit
  - defines `offsetof`
  - defines `ptrdiff_t`
  - defines signed fixed-width types `int8_t`, `int16_t`, `int32_t`, `int64_t`
  - defines unsigned fixed-width types with declaration guards
  - defines `intptr_t` and `uintptr_t`
  - defines `intmax_t` and `uintmax_t`
- In non-kernel builds, includes `<stdint.h>` if needed.

Important invariants:
- Kernel `boolean_t` is `_Bool` for C99/GCC-capable environments and `int` otherwise.
- Userland inclusion is tolerated but delegated to the normal userland `<stdint.h>`.
- The header explicitly warns it is not a placeholder for non-integer types.

Research notes:
- This file bridges kernel headers that need C99 integer types without exposing the full userland stdint implementation path.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/stdint.h -->