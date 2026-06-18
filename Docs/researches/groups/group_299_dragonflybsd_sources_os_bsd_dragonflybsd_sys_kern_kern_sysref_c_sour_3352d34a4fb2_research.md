# Group Research: group_299_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_kern_sysref_c_sour_3352d34a4fb2

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_sysref.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_sysref.c

Implements DragonFlyBSD’s `sysref` resource reference framework for cluster-addressable kernel resource structures. It combines reference counting, per-CPU sysid allocation, RB-tree lookup storage, and objcache-backed allocation.

Key structures and state:
- Per-CPU `sysref_array[MAXCPU]`, each with an RB tree and spinlock.
- RB tree generated over `struct sysref` keyed by `sysid`.
- `sysref_class` supplies object size, sysref offset, malloc type, objcache settings, optional ctor/dtor, and lifecycle ops.

Important behavior:
- `sysrefbootinit()` initializes per-CPU spinlocks and RB trees during boot.
- `sysref_init()` manually initializes static resources, assigns a CPU-encoded sysid, marks refcount as inactive/initializing, and inserts into the per-CPU RB tree.
- `sysref_alloc()` lazily creates the class objcache, obtains an object, verifies `SRF_PUTAWAY`, sets refcount to the negative initialization state, and zeroes non-sysref parts unless `SRC_MANAGEDINIT` is set.
- `sysref_ctor()` allocates a sysid, inserts the sysref into the per-CPU RB tree, marks `SRF_ALLOCATED | SRF_PUTAWAY`, then runs the class ctor.
- `sysref_dtor()` removes the sysref from its CPU-derived RB tree and runs the class dtor.
- `sysref_activate()` converts initialization refcounts into active positive refcounts.
- `_sysref_put()` handles normal decrements, active-to-terminating transition, termination callback invocation, and final objcache return or destruction depending on `SRF_SYSIDUSED`.
- `allocsysid()` exposes bare per-CPU sysid allocation.

Concurrency model:
- Per-CPU critical sections protect sysid allocation.
- RB tree mutation is protected by per-CPU spinlocks.
- Refcount transitions use atomic compare-and-set loops with `cpu_pause()` retry.
- Termination interlocks through class-provided lock/unlock/terminate operations.

Filesystem relevance:
- Not filesystem-specific, but it is a generic lifetime/identity mechanism that can back major kernel resources. Any VFS or filesystem object using `sysref` inherits this negative-refcount activation and termination lifecycle.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_sysref.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_systimer.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_systimer.c

Implements fine-grained per-CPU system timers on top of the machine `cputimer` abstraction. Timers are MP-safe and are dispatched without the MP lock.

Key APIs:
- `systimer_intr()`
- `systimer_intr_enable()`
- `systimer_add()`
- `systimer_del()`
- `systimer_init_periodic*()`
- `systimer_adjust_periodic()`
- `systimer_init_oneshot()`
- `systimer_changed()`

Important behavior:
- `systimer_intr()` runs ready timers from the current CPU’s sorted `gd_systimerq`; if the head is not due, it reloads the one-shot CPU timer for the remaining delta.
- Timer callbacks may delete or requeue themselves. The `gd_systimer_inprog` pointer detects whether the callback left the timer alone so periodic timers can be automatically requeued.
- Periodic timers preserve phase and can use synchronization flags such as millisecond sync, 100 kHz sync, CPU offset, and half-period offset.
- `SYSTF_NONQUEUED` periodic timers avoid accumulating missed events by advancing in multiples of the period.
- `systimer_add()` inserts into the owning CPU queue. If called from a different CPU, it sends an IPI to add on the owner CPU.
- `systimer_del()` requires the owning CPU and removes queued or in-progress timers safely.
- `systimer_changed()` recalculates timers after `sys_cputimer` changes, locally and via IPIs to other CPUs.

Concurrency model:
- Uses critical sections around queue operations.
- Remote CPU operations are marshaled through `lwkt_send_ipiq()`.
- Queue ordering supports `SYSTF_FIRST` to control ordering of coincident events.

Filesystem relevance:
- Provides the precision timer substrate used by kernel subsystems. Filesystems and VFS code indirectly depend on this through callouts, sleeps, timeouts, and periodic maintenance paths.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_systimer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_threads.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_threads.c

Tiny syscall implementation file for the general-purpose user yield system call.

Key API:
- `sys_yield()`

Behavior:
- Sets `sysmsg->sysmsg_result` to `0`.
- Calls `lwkt_user_yield()` to yield the current user thread.
- Returns success.

Concurrency model:
- Marked MPSAFE.
- No local locks or complex state.

Filesystem relevance:
- No direct filesystem logic. It is scheduler plumbing that can influence latency and fairness for filesystem-using user processes.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_threads.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_time.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_time.c

Implements kernel time-of-day syscalls, POSIX clock operations, nanosleep, interval timers, NTP adjustment controls, timeval helpers, and rate-limit helpers.

Key areas:
- Clock get/set/resolution: `kern_clock_gettime()`, `sys_clock_gettime()`, `kern_clock_settime()`, `sys_clock_settime()`, `kern_clock_getres()`.
- CPU clock IDs: `kern_getcpuclockid()`, `sys_getcpuclockid()`.
- Sleep: `clock_nanosleep1()`, `nanosleep1()`, `sys_clock_nanosleep()`, `sys_nanosleep()`.
- Time of day: `sys_gettimeofday()`, `sys_settimeofday()`, `settime()`.
- NTP adjustment: `kern_adjtime()`, `kern_reladjtime()`, `kern_adjfreq()`, `sys_adjtime()`, `sysctl_adjtime()`, `sysctl_delta()`, `sysctl_adjfreq()`.
- Interval timers: `sys_getitimer()`, `sys_setitimer()`, `realitexpire()`.
- Helpers: `itimerfix()`, `itimespecfix()`, `itimerdecr()`, `timevaladd()`, `timevalsub()`, `ratecheck()`, `ppsratecheck()`.

Important behavior:
- `settime()` moves execution to CPU 0 if necessary, computes delta, enforces securelevel clamping, calls `set_timeofday()`, then updates the RTC via `resettodr()`.
- `kern_clock_gettime()` supports realtime, monotonic, uptime, fast/precise variants, process CPU time, thread CPU time, and encoded process/LWP CPU clocks.
- `clock_nanosleep1()` combines coarse `tsleep()` with fine-grained one-shot `systimer` sleeps, and may yield or spin for very small intervals controlled by `kern.nanosleep_min_us` and `kern.nanosleep_hard_us`.
- `sys_gettimeofday()` optionally uses coarse `getmicrotime()` when `kern.gettimeofday_quick` is enabled; the sysctl also updates `kpmap->fast_gtod`.
- `sys_setitimer()` stores real timers as absolute uptime and schedules `p_ithandle` callouts; virtual/profiling timers live in process timer arrays.
- `realitexpire()` sends `SIGALRM` and advances periodic real timers without drift, compressing delayed expirations into one signal.
- NTP sysctls expose permanent frequency correction, one-time delta, tick delta state, leap second state, and relative adjustment.

Concurrency and privilege:
- Time setting requires `SYSCAP_NOSETTIME` privilege checks and uses `masterclock_lock`.
- NTP state is protected by `ntp_spin`.
- Process and LWP timing uses process tokens and reference holds.

Filesystem relevance:
- Provides timestamp validation helpers used by time-setting syscalls and filesystem metadata update paths.
- VFS/file code can depend on `itimerfix()`, `itimespecfix()`, realtime/uptime clocks, and rate limiting helpers for event throttling and timestamp correctness.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_timeout.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_timeout.c

Implements DragonFlyBSD’s per-CPU callout facility using hashed timing wheels and per-CPU softclock helper threads.

Key structures:
- `struct wheel`: spinlock plus TAILQ of internal callouts.
- `struct softclock_pcpu`: per-CPU wheel array, running/next pointers, freelist, tick counters, and softclock thread.
- Public `struct callout` is backed lazily by an internal `struct _callout`.

Important flags:
- Frontend/backend state includes `CALLOUT_DID_INIT`, `CALLOUT_ACTIVE`, `CALLOUT_SET`, `CALLOUT_INPROG`, `CALLOUT_RESET`, `CALLOUT_STOP`, `CALLOUT_CANCEL`, `CALLOUT_AUTOLOCK`, `CALLOUT_MPSAFE`, `CALLOUT_PREVENTED`, and `CALLOUT_FREELIST`.

Important behavior:
- `swi_softclock_setup()` sizes the wheel per CPU, allocates per-CPU softclock state, initializes wheels, and creates one softclock thread per CPU.
- `hardclock_softtick()` advances per-CPU tick state from hardclock and schedules the softclock thread when due work exists or the CPU is behind.
- `softclock_handler()` walks wheel slots, validates callout ownership via verifier pointers, marks callouts in progress, handles MP lock compatibility, runs callbacks, processes queued reset/stop/cancel operations, and reclaims EXIS-safe internal callouts.
- `_callout_update_spinlocked()` is the central state machine for queued and unqueued callouts; it handles reset, stop, cancel, requeueing to safe future ticks, waiter wakeups, and prevented status.
- `_callout_gettoc()` lazily allocates and attaches an internal `_callout` under EXIS protection.
- `callout_reset()` schedules on current CPU; `callout_reset_bycpu()` schedules on a selected CPU.
- `callout_cancel()`, `callout_drain()`, `callout_stop_async()`, `callout_stop()`, `callout_deactivate()`, and `callout_terminate()` provide varying synchronous/asynchronous stop and teardown semantics.
- `_callout_setup_quick()` and `_callout_cancel_quick()` provide low-overhead internal callouts for `tsleep()`.
- `slotimer_callback()` runs every 10 seconds per CPU and calls `slab_cleanup()`.

Concurrency model:
- Wheel lists are protected by wheel spinlocks.
- Individual callout state is protected by `_callout.spin` plus atomic flag operations.
- EXIS is used to prevent freeing internal callout backing while other CPUs hold or inspect it.
- AUTOLOCK callouts use cancelable `lockmgr()` interlocks.

Filesystem relevance:
- Foundational delayed-work mechanism for kernel subsystems, including VFS/filesystem cache cleanup, delayed writes, timeouts, device timers, and watchdog-like retry paths.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_timeout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_udev.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_udev.c

Implements DragonFlyBSD’s kernel udev interface layered over devfs character devices and proplib dictionaries.

Key data structures:
- `struct udev_event_kernel`: queued event plus TAILQ link.
- `struct udev_softc`: per-open clone state, marker for per-reader event position, unit, device pointer, opened/initiated state.
- Global `udevq` for open instances and `udev_evq` for event stream.
- Global locks: `udev_lk` for event/open state and `udev_dict_lk` for per-device dictionary access.

Dictionary handling:
- `udev_get_dict()` retains a device’s `si_dict` under a global dict lock.
- `udev_put_dict()` releases retained dicts and unlocks.
- Internal helpers set string, signed integer, unsigned integer, and delete keys.
- `udev_init_dict()` creates a per-device dictionary with name, devnum, kernel pointer, devtype, uid, gid, mode, major, minor, and driver.
- `udev_destroy_dict()` releases and clears a device dictionary.

Event handling:
- `udev_init_dict_event()` builds an event dictionary identifying device name, devnum, devtype, kernel pointer, and changed key.
- `udev_dict_set_cstr()`, `udev_dict_set_int()`, `udev_dict_set_uint()`, and `udev_dict_delete_key()` update device properties and queue key update/remove events.
- `udev_event_attach()` queues attach events, handling aliases by copying the base dictionary and changing name/alias state.
- `udev_event_detach()` queues detach events and destroys the device dictionary.
- `udev_event_insert()` queues events only after at least one client has initiated collection; otherwise it bumps sequence state when clients are open.
- `udev_clean_events_locked()` drops old events that all markers have passed.
- `udev_event_externalize()` wraps event type and event dictionary into an XML proplib payload.

Device interface:
- Autoclone `/dev/udev` creates per-open devices under `udevs/<unit>`.
- `udev_dev_open()` allows one open per clone and increments open count.
- `udev_dev_close()` destroys the clone, removes reader marker, cleans old events, returns clone unit, and frees softc.
- `udev_dev_read()` initiates collection on first read, blocks until an event is available unless nonblocking, externalizes one XML event, and advances the reader marker.
- `udev_dev_kqfilter()` supports `EVFILT_READ`; readiness is true if the reader marker has a later real event.
- `udev_dev_ioctl()` supports `UDEVPROP` command dictionaries and `UDEVWAIT` sequence waits.
- `udev_getdevs_ioctl()` enables event collection before scanning devfs, then returns an array of current device dictionaries using `devfs_scan_callback()`.

Filesystem relevance:
- Directly devfs-facing. This file exposes character device creation/removal/property changes to userland consumers and scans devfs for current devices. It depends on vnode/device interfaces and is important for device-node visibility in the filesystem namespace.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_udev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_umtx.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_umtx.c

Implements userland mutex sleep/wakeup helper syscalls operating on user addresses translated to physical wait addresses.

Key sysctls:
- `kern.umtx_delay` when RDTSC is supported: nanoseconds to spin before sleeping.
- `kern.umtx_timeout_max`: maximum sleep timeout in microseconds, default 2,000,000.

Key APIs:
- `sys_umtx_sleep()`
- `sys_umtx_wakeup()`

Important behavior:
- `sys_umtx_sleep()` validates timeout and alignment, reads the user int, translates the user virtual address to a physical address via `uservtophys()`, and sleeps only if the current value matches the expected value.
- It tolerates temporary translation discontinuities with retry loops and emits diagnostics if retries are exhausted.
- With RDTSC support, it spin-polls briefly before sleeping to avoid sleep/wakeup/IPI overhead on short-lived mutex contention.
- Sleep timeout is capped by `kern.umtx_timeout_max`, converted to ticks, and uses `tsleep_interlock()` plus `tsleep()` in `PDOMAIN_UMTX`.
- Before sleeping, it rechecks that the physical address did not change and rereads the user value to close wakeup races.
- `ERESTART` is converted to `EINTR`.
- `sys_umtx_wakeup()` translates the user pointer similarly and wakes either one waiter or all waiters in `PDOMAIN_UMTX`.

Concurrency model:
- Wait channel is physical address, not user virtual address, to interlock shared mappings.
- Mapping changes are not fully tracked; capped timeout and caller retry are part of the design.
- Critical sections tighten the sleep/wakeup interlock.

Filesystem relevance:
- No direct filesystem logic. It matters indirectly for threaded user programs doing filesystem I/O and for userland libraries using umtx primitives around file/path operations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_umtx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_usched.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_usched.c

Implements user scheduler registration/control plus CPU affinity syscalls for processes and LWPs.

Key global state:
- `usched_list`: registered user schedulers.
- `usched_mastermask`: all-ones CPU mask.

Key APIs:
- `usched_init()`
- `usched_ctl()`
- `usched_schedulerclock()`
- `sys_usched_set()`
- `sys_lwp_getaffinity()`
- `sys_lwp_setaffinity()`
- `setaffinity_lp()`

Important behavior:
- `usched_init()` registers `bsd4`, `dfly`, and `dummy` schedulers during early boot and chooses default from `kern.user_scheduler`, defaulting to `dfly`.
- `usched_ctl()` adds/removes schedulers, invoking optional register/unregister callbacks and disallowing removal of `bsd4`.
- `usched_schedulerclock()` calls each registered scheduler’s clock hook, passing the current LWP only to its owning scheduler.
- `sys_usched_set()` handles scheduler selection and older CPU-affinity commands. Scheduler changes require single-threaded processes and `SYSCAP_NOSCHED`; CPU mask mutation generally requires `SYSCAP_NOSCHED_CPUSET`.
- `sys_lwp_getaffinity()` snapshots the active CPU mask for a selected process/LWP.
- `sys_lwp_setaffinity()` updates one LWP or all LWPs in a process and allows self-affinity changes without privilege otherwise required for other processes.
- `setaffinity_lp()` updates `lwp_cpumask` and immediately migrates the current LWP if its current CPU is no longer allowed.

Concurrency model:
- Process and LWP tokens protect tree lookup and affinity mutation.
- Process references use `PHOLD/PRELE`; LWP references use `LWPHOLD/LWPRELE`.

Filesystem relevance:
- No direct filesystem implementation. Scheduler choice and CPU affinity can materially affect VFS/filesystem workload scheduling, per-CPU cache locality, and latency.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_usched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_uuid.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_uuid.c

Implements kernel UUID generation, formatting, comparison, nil/type checks, endian encoding/decoding, and string parsing.

Key state:
- `uuid_last`: last generated UUID state, including timestamp, sequence, and node.
- `uuid_lock`: serializes generation.

Key APIs:
- `kern_uuidgen()`
- `sys_uuidgen()`
- `snprintf_uuid()`, `printf_uuid()`, `sbuf_printf_uuid()`
- `kuuid_compare()`, `kuuid_is_nil()`, `kuuid_is_ccd()`, `kuuid_is_vinum()`
- `le_uuid_enc()`, `le_uuid_dec()`, `be_uuid_enc()`, `be_uuid_dec()`
- `parse_uuid()`

Important behavior:
- `uuid_node()` attempts to obtain an Ethernet MAC via `if_getanyethermac()`, falls back to random bytes, and sets multicast/local-style low bit behavior.
- `uuid_time()` builds a 60-bit count of 100 ns units since the Gregorian UUID epoch using `nanotime()`.
- `kern_uuidgen()` generates version-1 UUIDs under lock, choosing a new random 14-bit sequence when node changes or state is uninitialized, incrementing sequence if time goes backwards or repeats, and reserving a range for `count`.
- `sys_uuidgen()` limits batch generation to 1..2048 UUIDs, allocates temporary kernel memory, generates, and copies out.
- Formatting prints canonical `8-4-4-4-12` hex groups.
- `kuuid_compare()` treats NULL as nil and orders fields lexicographically.
- `kuuid_is_ccd()` and `kuuid_is_vinum()` compare against DragonFly GPT partition type UUIDs.
- Encoding/decoding routines serialize UUIDs to little-endian and big-endian byte streams.
- `parse_uuid()` accepts empty string as nil, otherwise requires the modern 36-character dashed form and validates variant bits.

Filesystem relevance:
- Relevant for storage/filesystem metadata that uses UUIDs, including GPT partition type checks for DragonFly CCD and Vinum.
- Provides common UUID parsing/encoding helpers usable by filesystem and block-device code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_uuid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_varsym.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_varsym.c

Implements variable storage and substitution for variant symlinks, plus syscalls to set/get/list variable symbols at process, user, system, and prison scopes.

Key structures:
- Global `varsymset_sys`.
- Per-set TAILQ of `varsyment`, each referencing a refcounted `varsym`.
- Each `varsymset` has a lock and set-size accounting.

Key APIs:
- `varsymreplace()`
- `sys_varsym_set()`
- `sys_varsym_get()`
- `sys_varsym_list()`
- `varsymfind()`
- `varsymmake()`
- `varsymdrop()`
- `varsymset_init()`
- `varsymset_clean()`

Important behavior:
- `varsym_sysinit()` initializes the global system varsym set.
- `varsymreplace()` scans a symlink target for `${name}` expressions, looks up variables using `VARSYM_ALL_MASK`, substitutes values in-place, and rejects expansion beyond the target buffer.
- `sys_varsym_set()` copies in name/data, applies privilege checks for system/prison-level variables, maps system-level requests in jail to prison scope, and creates or deletes variables.
- `sys_varsym_get()` resolves a wildcard/name using a mask, copies out the value if the buffer is large enough, and returns `EOVERFLOW` with an empty string when too small.
- `sys_varsym_list()` enumerates a chosen scope using a user-supplied marker, copying name/value NUL-terminated pairs into a buffer and returning bytes copied.
- `varsymfind()` searches scopes in order: process, user, then prison/system depending on jail state, retaining the returned symbol.
- `varsymmake()` creates a new varsym entry or deletes an existing one. The syscall path first deletes any old value before inserting replacement.
- `varsymset_init()` can duplicate references from an existing set without copying string storage.
- `varsymset_clean()` removes all entries and drops refs.

Concurrency model:
- Each varsym set uses `lockmgr` shared/exclusive locking.
- Symbols have atomic refcounts so lookups can safely retain across lock release.

Filesystem relevance:
- Directly filesystem-relevant: `varsymreplace()` is called from namei/path resolution for variant symlink expansion. These variables alter resolved symlink targets based on process/user/system/prison state.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_varsym.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_wdog.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_wdog.c

Implements kernel watchdog registration, periodic reset, sysctl control, and `/dev/wdog` ioctl reset support.

Key state:
- `wdoglist`: registered watchdog devices.
- `wdogmtx`: spinlock protecting list and periods.
- `wdog_callout`: automatic reset callout.
- `wdog_auto_enable`: whether kernel auto-reset is enabled.
- `wdog_auto_period`: current/minimum period.

Key APIs:
- `wdog_register()`
- `wdog_unregister()`
- `wdog_disable()`
- `wdog_ioctl()`

Important behavior:
- `wdog_register()` initializes device period, inserts into list, immediately resets all watchdogs, and logs registration.
- `wdog_unregister()` removes a watchdog and logs.
- `wdog_reset_all()` calls each watchdog’s callback, tracks the minimum returned period, and if auto mode is enabled schedules the next reset at half that minimum period.
- `wdog_set_period()` applies a period to all registered watchdogs.
- `kern.watchdog.auto` sysctl toggles automatic reset and starts/stops the callout behavior.
- `kern.watchdog.period` sysctl adjusts all watchdog periods and triggers reset.
- `wdog_disable()` stops auto callout, sets all periods to zero, and resets all watchdogs.
- `/dev/wdog` accepts `WDIOCRESET` only when auto mode is disabled.
- `wdog_init()` creates `/dev/wdog`, initializes spinlock and callout.
- `wdog_uninit()` cancels/terminates callout and removes device ops.

Concurrency model:
- Spinlock protects watchdog list and period updates.
- Callout is initialized MP-safe.

Filesystem relevance:
- Creates a character device node through devfs. Not a filesystem implementation, but its device-node lifecycle and ioctl behavior are visible through the filesystem namespace.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_wdog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_xio.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_xio.c

Implements the kernel XIO abstraction: a vmspace-agnostic collection of held `vm_page_t` pages used to pass user or kernel data between threads without permanently mapping it into kernel virtual memory.

Key APIs:
- `xio_init()`
- `xio_init_kbuf()`
- `xio_init_pages()`
- `xio_release()`
- `xio_uio_copy()`
- `xio_copy_xtou()`
- `xio_copy_xtok()`
- `xio_copy_utox()`
- `xio_copy_ktox()`

Important behavior:
- `xio_init()` creates an empty XIO using internal page storage.
- `xio_init_kbuf()` translates a kernel buffer to physical pages with `pmap_kextract()`, converts to `vm_page_t`, holds pages, and records byte count/page offset. Failure releases all held pages and returns `EFAULT`.
- `xio_init_pages()` holds a caller-provided page array and records total bytes.
- `xio_release()` dirties pages if `XIOF_WRITE` is set, unholds pages, clears counters, and marks error `ENOBUFS`.
- `xio_uio_copy()` copies between XIO pages and a `uio` using `uiomove_fromphys()`.
- `xio_copy_xtou()` maps pages one at a time with `lwbuf`, then `copyout()`s to user memory.
- `xio_copy_xtok()` maps pages with `lwbuf` and `bcopy()`s to kernel memory.
- `xio_copy_utox()` maps pages and `copyin()`s user data into XIO pages.
- `xio_copy_ktox()` maps pages and `bcopy()`s kernel data into XIO pages.

Safety notes:
- Comments warn that user memory cannot be mapped directly into XIO unless it uses managed pages, or modifications race pageout/flush.
- TODO notes mention missing busy-page and writable checks for modification paths.

Filesystem relevance:
- Explicitly intended for I/O path and VFS use. It is a page-backed transfer object for moving file data across threads or contexts without tying buffers to the original vmspace.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_xio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/libmchain/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/libmchain/Makefile

Builds the `libmchain` kernel module.

Contents:
- Defines `KMOD= libmchain`.
- Defines `SRCS= subr_mchain.c`.
- Includes `<bsd.kmod.mk>`.

Filesystem relevance:
- No filesystem logic. It packages mbuf chain helper routines as a kernel module, which may support network filesystem or protocol code that serializes/deserializes messages in mbufs.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/libmchain/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/libmchain/subr_mchain.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/libmchain/subr_mchain.c

Implements `libmchain`, a set of mbuf chain construction and decoding helpers with endian-aware scalar helpers and UIO integration.

Build/module:
- Declares `MODULE_VERSION(libmchain, 1)`.

mbchain write-side APIs:
- `m_fixhdr()`
- `mb_init()`, `mb_initm()`, `mb_done()`, `mb_detach()`, `mb_fixhdr()`
- `mb_reserve()`
- `mb_put_uint8()`, `mb_put_uint16be/le()`, `mb_put_uint32be/le()`, `mb_put_int64be/le()`
- `mb_put_mem()`
- `mb_put_mbuf()`
- `mb_put_uio()`

mdchain read-side APIs:
- `md_init()`, `md_initm()`, `md_done()`
- `md_append_record()`, `md_next_record()`
- `md_get_uint8()`, `md_get_uint16()`, `md_get_uint16be/le()`
- `md_get_uint32()`, `md_get_uint32be/le()`
- `md_get_int64()`, `md_get_int64be/le()`
- `md_get_mem()`
- `md_get_mbuf()`
- `md_get_uio()`

Important behavior:
- `m_fixhdr()` recomputes packet header length across an mbuf chain.
- `mb_init()` creates a header mbuf and initializes chain cursors.
- `mb_reserve()` reserves contiguous space in the current mbuf, allocating another mbuf if needed; sizes greater than `MLEN` panic.
- `mb_put_mem()` copies data into an mbuf chain from system memory, user memory, inline byte loops, zero-fill, or a custom callback.
- `mb_put_uio()` drains a `uio` scatter/gather list into an mbchain and updates `uio_offset`, `uio_resid`, iovec base, and length.
- `md_initm()` initializes a decoder over an existing mbuf chain.
- Record helpers use `m_nextpkt` to chain independent records.
- `md_get_mem()` advances through mbufs, copying out to user/system/inline targets or skipping when target is NULL; incomplete chains return `EBADRPC`.
- `md_get_mbuf()` copies a segment of the current chain with `m_copym()` and advances the decoder.
- `md_get_uio()` copies decoded data into a `uio`.

Filesystem relevance:
- Mostly network/protocol support rather than local filesystem code. It can be relevant to network filesystems or filesystem-related kernel protocols that marshal requests and responses through mbufs and UIOs.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/libmchain/subr_mchain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/link_elf.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/link_elf.c

Implements ELF kernel linker support for executable/dynamic-style KLD images and preloaded ELF modules.

Key data structures:
- `struct elf_file`: base relocation address, dynamic section pointers, SysV hash metadata, string/symbol tables, relocation tables, PLT relocation tables, preload module pointer, and debugger symbol/string tables.

Key registration:
- `link_elf_init()` registers `elf32` or `elf64` linker class, creates the kernel linker file from `_DYNAMIC`, parses dynamic metadata, processes preload symbol metadata, and marks the kernel linked.
- SYSINIT runs at `SI_BOOT2_KLD`.

Load paths:
- `link_elf_preload_file()` locates preloaded modules by name, validates type `"elf<N> module"` or `"elf module"`, obtains address/size/dynamic metadata, creates a linker file, parses dynamic metadata, and performs local relocations.
- `link_elf_preload_finish()` performs external relocations and parses module symbols.
- `link_elf_load_file()` searches linker path, opens the vnode with `nlookup`/`vn_open`, reads the first page, validates ELF identity/class/data/version/type/machine, expects two `PT_LOAD` segments and one `PT_DYNAMIC`, allocates kernel memory, reads text/data segments with `vn_rdwr()`, zeroes BSS, parses dynamic metadata, handles dependencies, performs relocations, and optionally loads section symbol/string tables for debugging.

Relocation and symbol behavior:
- `parse_dynamic()` processes `DT_HASH`, string/symbol tables, GOT, REL/RELA, JMPREL, PLT sizes, and PLT relocation type.
- `relocate_file()` runs `elf_reloc()` over REL, RELA, PLT REL, and PLT RELA entries, resolving via `elf_lookup()`.
- `link_elf_reloc_local()` performs local relocations first using `elf_reloc_local()`.
- `link_elf_lookup_symbol()` uses the SysV hash table first, then falls back to full debugger symbol table if present.
- `link_elf_symbol_values()` returns name, relocated value, and size.
- `link_elf_search_symbol()` finds nearest symbol at or below a given address.
- `link_elf_lookup_set()` resolves linker sets using `__start_set_<name>` and `__stop_set_<name>` symbols.
- `elf_hash()` implements the System V ABI hash algorithm.
- `elf_lookup()` resolves local symbols directly and otherwise delegates to `linker_file_lookup_symbol()`.

Unload behavior:
- `link_elf_unload_file()` frees loaded image memory and optional symbol/string bases.
- `link_elf_unload_module()` frees preload-private state and deletes preload metadata by pathname.

Filesystem relevance:
- Directly uses VFS/vnode operations to load kernel modules from the filesystem.
- Important for filesystem modules: this is one path by which filesystem KLDs can be loaded, linked, relocated, and have linker sets discovered.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/link_elf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/link_elf_obj.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/link_elf_obj.c

Implements ELF relocatable-object kernel linker support for ET_REL KLD object modules.

Key data structures:
- `Elf_progent`: loaded program/NOBITS section address, size, flags, original section index, section name.
- `Elf_relent` and `Elf_relaent`: relocation table pointer/count/target section.
- `struct elf_file`: preload flag, mapped address/size, VM object, section headers, progtab, REL/RELA tables, debugger symbol/string tables, section string table, and optional CTF-related storage.

Key registration:
- `link_elf_obj_init()` registers `elf32` or `elf64` linker class with object-module loader hooks.
- SYSINIT runs at `SI_BOOT2_KLD`.

Preload path:
- `link_elf_obj_preload_file()` locates a preloaded `"elf<N> obj module"` or `"elf obj module"`, validates ET_REL header metadata, uses preloaded section headers, counts PROGBITS/NOBITS/SYMTAB/REL/RELA sections, builds tracking tables, relocates saved section addresses to runtime address, binds symbols to loaded section addresses, records relocation tables, performs local relocations, and returns the linker file.
- `link_elf_obj_preload_finish()` performs external relocations.

Filesystem load path:
- `link_elf_obj_load_file()` searches linker path, opens a vnode with `nlookup`/`vn_open`, reads ELF header, validates class/data/version/type/machine, reads section headers, validates one symbol table and associated string table, loads symbol and string tables, optionally loads section name strings, sizes all PROGBITS/NOBITS sections with alignment, allocates a VM object and kernel mapping, wires pages, loads PROGBITS from vnode with `vn_rdwr()`, zeroes NOBITS, loads REL/RELA sections, adjusts symbol values to loaded addresses, performs local relocations, loads dependencies, then performs external relocations.

Relocation and symbol behavior:
- `findbase()` maps a relocation section’s target section index to its loaded base address.
- `relocate_file()` processes all REL/RELA entries except local symbols, calling `elf_reloc()` with `elf_obj_lookup()`.
- `link_elf_obj_reloc_local()` first fixes linker-set start/stop symbols, then applies only local REL/RELA relocations using `elf_reloc_local()`.
- `elf_obj_lookup()` resolves defined symbols directly from adjusted `st_value`; undefined globals are delegated to `linker_file_lookup_symbol()`. Undefined locals and weak symbols fail.
- `link_elf_obj_lookup_symbol()` linearly searches the symbol table for defined symbols by name.
- `link_elf_obj_symbol_values()` returns symbol name, absolute value, and size.
- `link_elf_obj_search_symbol()` finds nearest symbol for address lookup.
- `link_elf_obj_lookup_set()` finds sections named `set_<name>` and returns start/stop/count.
- `link_elf_obj_fix_link_set()` resolves undefined `__start_<section>` and `__stop_<section>` symbols to matching loaded section bounds.

Unload behavior:
- `link_elf_obj_unload_file()` frees relocation tables, progtab, CTF storage, loaded VM mapping/object, section headers, symbols, string tables, and preload metadata. Preloaded modules do not reclaim module memory here.

Filesystem relevance:
- Directly loads ET_REL kernel modules from the filesystem through vnode reads.
- Critical for filesystem drivers built as relocatable KLDs: it allocates executable kernel memory, resolves dependencies, applies relocations, and exposes linker sets used by module registration machinery.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/link_elf_obj.c -->