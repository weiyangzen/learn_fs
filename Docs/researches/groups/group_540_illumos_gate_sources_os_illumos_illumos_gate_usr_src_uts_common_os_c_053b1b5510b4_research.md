# Group Research: group_540_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_c_053b1b5510b4

Scope verified against `Docs/research_subset_a.md`: this subset includes `sources/os/illumos/illumos-gate`. Read completely: 12 listed illumos kernel source files, 9,542 total lines.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock.c

This file implements the main illumos kernel clock service: the periodic `clock()` cyclic, NTP/PPS discipline state, wall-clock/TOD synchronization, process tick handling, delay routines, deadman timers, load-average maintenance, and the hybrid `lbolt` implementation.

Core behavior:
- `clock()` runs from `clock_cyclic` every `nsec_per_tick`, skips work during panic, refreshes `freemem`, applies precision-kernel phase adjustments to `timedelta`, samples CPU/partition runnable state, updates lgroup load, schedules per-thread tick accounting via `clock_tick_schedule()`, invokes cluster/cpucap clock callouts, and performs once-per-second VM/system accounting.
- Once-per-second logic handles NTP leap states, `time_maxerror`, PLL/FLL phase/frequency adjustment, PPS watchdog expiry, TOD drift comparison, `hrestime` correction, TOD chip resync, `lbolt_cv` broadcast, swap and run queue accounting, `fsflush` wakeup, `vmmeter()`, load averages, and swapper wakeups.
- `clock_update()` is called under `tod_lock` by `ntp_adjtime()` to update `time_offset`, `time_freq`, and `time_reftime`, and marks the TOD for later sync.
- `ddi_hardpps()` handles external PPS interrupts with median filters for phase and frequency, jitter/wander/error accounting, adaptive calibration interval selection, and PPS-driven `pps_freq` updates.
- `clock_tick()` charges a target LWP/process for pending ticks: scheduler class ticks, user/system tick counters, profiling ASTs, virtual/prof interval timers, process/task CPU-time resource controls, and RSS usage.
- `profil_tick()` drains `lwp_oweupc` and updates old-style profiling counters or PC-sampling buffers in user memory.
- `delay()`, `delay_random()`, and `delay_sig()` implement tick-based sleeps using callouts/CVs when timeouts are available, with spin fallback during panic or devinfo freeze.
- `clkset()` initializes system time from TOD or an approximate filesystem time; `set_hrestime()` resets `hrestime`, clears `timedelta`, increments `timechanged`, and calls callout users.
- `deadman_init()` installs per-CPU high-level cyclics that detect clock inactivity and panic if enabled; during panic the same path can time out crash dumps.
- `tod_fault()`, `tod_status_set()`, `tod_status_clear()`, `tod_set_prev()`, and `tod_validate()` implement TOD health tracking for reversed, stalled, jumped, rate-changed, and read-only TOD states.
- `clock_init()` registers the clock cyclic and lbolt cyclic and allocates cache-aligned per-CPU/global lbolt state.
- `lbolt_event_driven()`, `lbolt_ev_to_cyclic()`, `lbolt_cyclic_driven()`, and `lbolt_cyclic()` switch DDI lbolt reads between computed `gethrtime()/nsec_per_tick` mode and a cyclic-maintained counter under high call pressure.
- `lbolt_debug_entry()` and `lbolt_debug_return()` subtract debugger stop time from lbolt-visible uptime.

Important invariants:
- `tod_lock` protects TOD-facing clock update and validation state; `hr_clock_lock()` protects `hrestime`, `timedelta`, `tod_needsync`, and `timechanged` mutations.
- `clock_tick()` requires the process `p_lock` to be held and assumes a valid LWP.
- Delay callout/CV paths use the current thread’s `t_delay_lock` and `t_delay_cv`; interrupt-context use is diagnosable because `delay(9F)` is not valid there.
- `tod_validate()` is disabled until high-resolution time is usable and does not run after a TOD fault until reset.
- `lbolt_hybrid` mode switches are serialized with `lbi_token`; cyclic reprogramming is deferred to a softint for event-to-cyclic transitions.
- `lbi_debug_time` is subtracted from returned lbolt values so hardware reboot and debugger time do not leak into DDI lbolt semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_highres.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_highres.c

This file registers the `CLOCK_HIGHRES` backend. It exposes monotonic high-resolution time from `gethrtime()` and implements high-resolution POSIX timers using the cyclic subsystem.

Core behavior:
- `clock_highres_gettime()` converts `gethrtime()` to `timespec_t`; `clock_highres_getres()` reports `cyclic_getres()`.
- `clock_highres_settime()` always returns `EINVAL`; this clock is not settable.
- Timer creation allocates a `cyclic_id_t` slot in `it->it_arg` and stores the generic timer fire callback.
- `clock_highres_timer_settime()` clamps sub-`clock_highres_interval_min` one-shot or interval values to 200 us for callers without `proc_clock_highres`.
- Existing one-shot timers can be reprogrammed directly with `cyclic_reprogram()` instead of being removed and re-added.
- Nonzero timers are installed as low-level cyclic handlers and then bound to the current thread’s CPU and processor-set binding.
- One-shot timers are represented with `CY_INFINITY` interval so they remain until `timer_settime()` or delete removes them.
- `clock_highres_fire()` atomically records the last fire time in `it_hrtime` before calling `it_fire()`.
- `clock_highres_timer_gettime()` computes remaining time from the original start, interval, current hrtime, and last recorded fire.
- `clock_highres_timer_lwpbind()` rebinds an active cyclic after LWP binding changes.
- `clock_highres_init()` fills the backend vector and registers it with `clock_add_backend(CLOCK_HIGHRES, ...)`.

Important invariants:
- Cyclic add/remove/rebind operations are performed under `cpu_lock`.
- Process binding state is sampled under `p_lock` while `cpu_lock` keeps CPU/partition objects stable.
- Overflow is checked for initial start plus interval; later wrap is accepted as practically unreachable.
- `it_itime.it_value` is converted to an absolute fire time for reporting, even when caller passed a relative timeout.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_highres.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_process.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_process.c

This file registers a read-only `CLOCK_PROCESS_CPUTIME_ID` backend. It reports CPU time consumed by the current process using existing microstate accounting.

Core behavior:
- `clock_process_gettime()` locks `curproc->p_lock`, sums `mstate_aggr_state(p, LMS_USER)` and `mstate_aggr_state(p, LMS_SYSTEM)`, and converts the result to `timespec_t`.
- `LMS_SYSTEM` aggregation includes `LMS_TRAP`, matching `/proc` status behavior.
- `clock_process_getres()` reports `cyclic_getres()`, matching the thread CPU-time backend’s resolution choice.
- `clock_process_settime()` and all timer operations return `EINVAL`; interval timers are not implemented for this clock.
- `clock_process_init()` fills the backend dispatch table and registers `CLOCK_PROCESS_CPUTIME_ID`.

Important invariants:
- The clock is scoped only to the calling process.
- Timer callbacks/default signal metadata are filled for backend completeness but timer creation is deliberately unsupported.
- `p_lock` is required while aggregating process microstate time.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_process.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_realtime.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_realtime.c

This file registers the `CLOCK_REALTIME` backend and the compatibility `__CLOCK_REALTIME0` backend. It wraps wall-clock get/set operations and implements realtime POSIX timers on top of timeout callouts.

Core behavior:
- `clock_realtime_settime()` takes `tod_lock`, writes the TOD with `tod_set()`, and resets high-resolution system time via `set_hrestime()`.
- `clock_realtime_gettime()` calls `gethrestime()`, though libc normally uses a faster path for `CLOCK_REALTIME`.
- `clock_realtime_getres()` reports `nsec_per_tick`.
- Timer creation allocates a `timeout_id_t` slot and records the generic `it_fire()` callback.
- `clock_realtime_timer_settime()` removes any existing timeout under `p_lock`, records the new `it_itime`, converts relative times to absolute `hrestime`, and schedules the first fire through `realtime_timeout()`.
- The first fire uses `clock_realtime_fire_first()` to avoid firing early because `timespectohz()` is based on `hrestime` while callouts are interpreted against lbolt.
- `clock_realtime_fire()` invokes the timer subsystem, clears one-shot timers, or computes the next interval expiration by stepping forward from the previous expected expiration. If the clock moved, it uses exponential stepping and then normal stepping to find the minimum future deadline.
- `clock_realtime_timer_gettime()` snapshots `it_itime` and current time under `p_lock`, returning zero remaining time when expired.
- Deletion cancels outstanding timeouts and frees `it_arg`.

Important invariants:
- `p_lock` protects `it_itime` and the active timeout id.
- `untimeout()` is called with the process lock dropped and then reacquired because timeout removal can block.
- Realtime interval timers preserve cadence from the expected expiration time instead of simply adding interval to current time.
- Wall-clock changes can force recomputation of future interval deadlines.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_realtime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_thread.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_thread.c

This file registers read-only thread CPU-time clock backends for `CLOCK_VIRTUAL` and `CLOCK_THREAD_CPUTIME_ID`.

Core behavior:
- `CLOCK_VIRTUAL` reports only the current thread’s `LMS_USER` microstate time from `lwp_mstate.ms_acct[LMS_USER]`, scaled with `scalehrtime()`.
- `CLOCK_THREAD_CPUTIME_ID` reports current thread user plus system plus trap time through `mstate_thread_onproc_time()`, under `thread_lock()`.
- `clock_thread_getres()` reports `cyclic_getres()` as the closest practical resolution for this subsystem.
- `clock_thread_settime()` and all timer operations return `EINVAL`; interval timers are not implemented.
- `clock_thread_init()` registers two backend structures: one for `CLOCK_VIRTUAL`, one for `CLOCK_THREAD_CPUTIME_ID`.

Important invariants:
- Both clocks always refer to the calling thread, so no cross-process privilege or lifetime lookup is needed.
- `mstate_thread_onproc_time()` is used for the user+system clock because it includes currently executing system time not yet folded into stored microstate counters.
- Timer metadata is initialized but timer support is intentionally absent.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_thread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_tick.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_tick.c

This file implements scalable per-thread tick accounting. It is called by `clock()` every tick and either accounts ticks in the clock path or distributes work across CPUs with softints.

Core behavior:
- `clock_tick_init_pre()` initializes single-threaded mode, cache-line-aligned per-CPU tick structures, a shared softint if available, the global lock, and CPU-set partition descriptors.
- `clock_tick_init_post()` decides at boot whether to remain single-threaded or enable multi-threaded accounting based on CPU count, `clock_tick_threshold`, softint availability, and high-resolution tick settings.
- `clock_tick_mp_init()` populates online CPU tables and registers `clock_tick_cpu_setup()` for CPU online/offline updates.
- `clock_tick_cpu_setup()` maintains `clock_tick_cpus`, set boundaries, online CPU set, and set counts during CPU online/offline. Offline syncs softints where supported before removing a CPU from the online set.
- `clock_tick_schedule()` is called each tick. In single-threaded mode it rotates the scan start for fairness and directly calls `clock_tick_execute_common()`.
- In multi-threaded mode it batches pending ticks if previous softints are still active; otherwise it accounts the clock CPU immediately, schedules one softint per CPU set, rotates the scheduling CPU once per second, and clears the pending count.
- `clock_tick_schedule_one()` fills a target CPU’s per-CPU work descriptor and invokes its softint.
- `clock_tick_execute()` runs in softint context, drains pending work from the per-CPU descriptor, runs common accounting, and decrements `clock_tick_active`.
- `clock_tick_execute_common()` accounts the current CPU first to avoid losing a pinned thread, then scans assigned CPUs in rotating order.
- `clock_tick_process()` safely locates a CPU’s current thread, prevents thread free, avoids offline/quiesced/interrupt/idle threads, takes the persistent process lock pointer, checks migration/exiting races, and calls `clock_tick(t, pending)` once per lbolt.

Important invariants:
- Multi-threaded mode is chosen at boot only; CPU hotplug updates tables but does not switch accounting modes.
- `clock_tick_active` and `clock_tick_pending` batch missed ticks so busy systems charge multiple pending ticks in one `clock_tick()` call.
- `thread_free_prevent()` is needed because the current thread can otherwise be freed or recycled while inspected.
- `t_plockp` is used instead of dereferencing a possibly freed process to acquire `p_lock`.
- `t_lbolt < mylbolt` prevents double-accounting an LWP that migrates and appears in more than one CPU scan.
- CPU table updates are protected by `clock_tick_lock` and published with memory barriers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_tick.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/compress.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/compress.c

This file provides a standalone LZJB compressor/decompressor and a simple 32-bit rolling checksum. It is compiled into the kernel, boot code, and savecore, so it avoids dependencies on external kernel symbols.

Core behavior:
- `compress()` implements LZJB, a derivative of LZRW1, using 3-byte minimum matches, 6 bits of encoded match length, 10 bits of offset, 256 uninitialized Lempel hash entries, and an 8-item copy bitmap.
- If compression output approaches the original size, `compress()` falls back to copying the original input and returns `s_len`.
- The compressor never intentionally reads past input or writes past an output buffer of original input size.
- `decompress()` copies input directly when compressed length is greater than or equal to destination length, otherwise decodes bitmap-controlled literal/copy items until input or destination ends.
- Copy items use overlapping forward byte copying, matching LZ-style back-reference semantics.
- Corrupt compressed data with an offset before the destination start returns the number of bytes decompressed so far.
- `checksum32()` rotates the accumulated 32-bit sum right by one bit and adds each byte.

Important invariants:
- The Lempel table is intentionally uninitialized, making `compress()` non-deterministic but faster and stack-local/MT-safe.
- `MATCH_MAX` is 66 bytes and offset reach is 1 KiB.
- `decompress()` does not guarantee full output on corrupt or truncated input; callers must compare returned length with expected length.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/condvar.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/condvar.c

This file implements kernel condition variables on top of hashed sleep queues, scheduler sleep-object callbacks, callout-backed timed waits, signal-aware waits, and listener wakeups.

Core behavior:
- `cv_sobj_ops` supplies owner, unsleep, and priority-change hooks for threads blocked on CVs; CVs have no owner.
- `cv_init()` initializes the compact waiter count; `cv_destroy()` asserts no waiters remain.
- `cv_block()` prepares the current thread for sleep, sets `t_wchan`, assigns `cv_sobj_ops`, accounts voluntary context switch/microstate sleep, increments `cv_waiters` up to `CV_MAX_WAITERS`, switches the thread to sleep state, and inserts it into the hashed sleep queue.
- `cv_wait()` blocks non-interruptibly, drops the associated mutex while asleep, switches, and reacquires the mutex.
- `cv_timedwait()`, `cv_reltimedwait()`, and `cv_timedwait_hires()` add callout-based wakeups and return remaining time or `-1` on timeout.
- `cv_wait_sig()` handles signal-interruptible waits for user LWPs, including scheduler-control cancellation, `lwp_asleep`, `lwp_sysabort`, `T_WAKEABLE`, and pending signal processing.
- `cv_timedwait_sig_hires()` combines timeout and signal behavior, with return precedence: signal/sysabort/cancel as `0`, timeout as `-1`, normal wake as positive remaining time.
- `cv_timedwait_sig()`, `cv_timedwait_sig_hrtime()`, and `cv_reltimedwait_sig()` are wrappers for tick-relative, hrtime-absolute, and tick-relative signal-aware waits.
- `cv_wait_sig_swap_core()` allows the sleeping thread to become swappable by clearing `TS_DONT_SWAP`; `cv_wait_sig_swap()` wraps it.
- `cv_signal()` wakes one waiter using the waiter hint if trustworthy, or consults the sleep queue when the hint has saturated.
- `cv_broadcast()` wakes all waiters and clears the waiter count.
- `cv_wait_stop()` periodically wakes to honor process stop/checkpoint/watchpoint/fork/lwp-suspend requests without general signal handling.
- `cv_waituntil_sig()` waits until an absolute wall-clock time and treats abrupt system time changes as a forced timeout so callers can reevaluate.

Important invariants:
- CV waits are invalid during quiesce and return immediately during panic.
- Callout wakeup is synchronized with actual blocking through `t_wait_mutex` to avoid wake-before-sleep races.
- `cv_waiters` is a bounded hint; when it reaches `CV_MAX_WAITERS`, signal paths must verify the sleep queue.
- Signal or timeout paths that observe they consumed a `cv_signal()` reissue `cv_signal(cvp)` so another waiter can receive it.
- `cv_signal()` and `cv_broadcast()` assert they are not running on interrupt stack.
- Associated mutexes are dropped only after the thread is fully queued for sleep.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/condvar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/console.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/console.c

This file implements common kernel console I/O helpers for early boot, panic, PROM fallback, and normal asynchronous `/dev/console` output.

Core behavior:
- Global state includes `console_vnode`, `console_taskq`, and the current polled I/O vector `cons_polledio`.
- `console_hold()`/`console_rele()` serialize direct console rendering with a writer rwlock, recursion depth, framebuffer power management, and optional framebuffer/specfs/devinfo lock checks.
- `console_enter()`/`console_exit()` are used around PROM rendering so platform code can stop other CPUs if framebuffer mappings are busy.
- `console_get_size()` reads screen rows/columns/pixel dimensions from terminal-emulator or root-node properties, clamps values to supported defaults/ranges, and handles pre-DDI fallback.
- `console_vprintf()` normally formats into a heap message and dispatches `console_putmsg()` on `console_taskq` when `/dev/console` is ready and the system is not panicking.
- `console_putmsg()` writes to `console_vnode` with `vn_rdwr(FAPPEND)`; if unavailable or failing, it falls back to PROM printing under console hold/enter protection.
- `console_printf()` wraps `console_vprintf()`.
- `console_puts()` writes a byte string directly through PROM and is intended only for the wscons driver legacy path.
- `console_putc()` writes one character directly to PROM, expanding newline to carriage-return/newline.
- `console_gets()` and `console_getc()` read from PROM only during early boot before `rconsvp` is initialized; `console_gets()` handles erase, kill-line, newline, and buffer-full bell behavior.

Important invariants:
- Panic paths assume exclusive access and avoid changing console lock state.
- Recursive console holds increment `console_depth` and release only at the outermost exit.
- Firmware framebuffer locking is conditional on firmware console mode, multiprocessor systems, and framebuffer vnode availability.
- Asynchronous console taskq output is skipped during panic or when allocation/dispatch fails.
- Synchronous console input is asserted to occur only before the real console stream exists.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/console.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/contract.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/contract.c

This file implements the core Solaris/illumos contracts framework. Contract types provide resource-specific behavior, while this file handles common contract identity, ownership, reference counts, templates, type registration, global/type/process lookup, event queues, listeners, visibility, and event delivery.

Core behavior:
- `contract_init()` creates the global ID space and AVL tree, initializes process and device contract types, and initializes process 0 contract state.
- `contract_ctor()` initializes a new contract, allocates an ID, creates its per-contract event queue, tests/increments `project.max-contracts`, inserts the contract into owner, global, and type AVL namespaces, and stores it as the LWP’s latest contract for that type.
- `contract_rele()` drops a reference; the last release removes the contract from global/type trees, frees its ID, decrements project contract accounting, destroys common state, and calls the type-specific free op.
- `contract_hold()`, `contract_getzuniqid()`, and `contract_setzuniqid()` provide reference and zone-unique-id helpers.
- `contract_abandon()` removes ownership, optionally inherits to a regent process contract when terms allow it, calls type-specific abandon when not inherited, trims the old process bundle queue, and drops references.
- `contract_adopt()` lets a process adopt an inherited contract from its process contract, transfers ownership, inserts it into `p_ct_held`, and copies critical events to the new owner’s process bundle queue.
- `contract_ack()`, `contract_qack()`, and invalid/notsupported helpers handle critical and negotiation event acknowledgements and delegate negotiation-specific ACK/NACK/QACK to type operations.
- `contract_orphan()` marks a contract orphaned and ACKs all outstanding critical events.
- `contract_destroy()` marks a contract dead, drains its contract event queue, trims type bundles, calls type-specific destroy, and releases the owner reference.
- Contract vnode helpers track ctfs vnodes associated with contract directories without holding permanent vnode references.
- `contract_exit()` abandons all contracts held by an exiting process and drains process bundle queues.
- `contract_status_common()` fills common `ct_status` fields, including zone virtualization of holder/state visibility.
- `contract_owned()` and `contract_checkcred()` implement event visibility by owner, creator zone/uid, effective zone, and observer privilege rules.
- `contract_type_init()`, `contract_type_count()`, `contract_type_max()`, `contract_max()`, lookup, pointer, time, bundle, and process-bundle helpers expose type/global indexing and queue allocation.
- `ctparam_copyin()` and `ctparam_copyout()` copy contract parameter ioctl payloads safely outside process-lock regions.
- Template helpers initialize, copy, duplicate, free, set/get common terms, activate/clear active LWP templates, and invoke type-specific create/set/get/free operations.
- Event queue internals manage queue creation/destruction, event holds/releases, listener movement, queue reference releases, credential checks, readable-event selection, tail-listener wakeups, event copying, trimming, draining, publishing, and reliable delivery.
- `cte_publish_all()` initializes an event, assigns an event ID, holds the generating contract, delivers the event in contract queue, type bundle queue, and owner process bundle queue order, and serializes per-contract delivery with `ct_evtlock`.
- Listener APIs add/remove/reset listeners, advance past an event, read/copy out events and nvlist payloads, and enable reliable delivery with `PRIV_CONTRACT_EVENT`.

Important invariants:
- Lock order is explicitly documented: `ct_evtlock`, regent `ct_lock`, member `ct_lock`, `pidlock`, `p_lock`, queue locks/`contract_lock`, `cte_lock`, then `ct_reflock`.
- Global contract lists do not own references; contracts are removed from namespaces atomically with last-reference release.
- A contract is owned by a process, inherited by a regent process contract, orphaned, or dead; `ct_owner`/`ct_regent` are protected by `ct_lock`, while holder AVL linkage is protected by the holder lock.
- Event references include queue holds, listener queue-position references, copyout holds, and the event’s hold on the generating contract.
- Process bundle queues are dynamically allocated and refcount-like through `CTQ_REFFED`; they can outlive the process if listeners remain.
- `cte_trim()` removes informative/ACKed events only when unreferenced or marks contract-specific events trimmed until reliable readers release them.
- `cte_get_event()` holds the event while copying to userland and uses `CTLF_COPYOUT`/`CTLF_RESET` to avoid racing listener movement/reset with partial copyout.
- Critical events increment `ct_evcnt` until ACKed; orphan/dead paths must clear or ACK outstanding critical events.
- Zone visibility uses both creator-zone unique ID and mutable effective-zone unique ID for global-zone-created contracts visible in non-global zones.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/contract.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/copyops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/copyops.c

This small file provides compatibility/default wrappers for physical I/O and per-thread copy operation hooks.

Core behavior:
- `physio()` delegates directly to `default_physio()`.
- `install_copyops()` asserts the target thread has no copyops installed and sets `t_copyops`.
- `remove_copyops()` asserts copyops are installed and clears `t_copyops`.
- `copyops_installed()` returns whether a thread currently has copyops.

Important invariants:
- Copyops installation is single-owner per thread; assertions catch double-install and remove-without-install misuse.
- The file does not manage copyops object lifetime; callers own the referenced `copyops_t`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/copyops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/core.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/core.c

This file implements core dump orchestration: selecting per-process/per-zone/global core destinations, safely creating files, expanding core filename patterns, temporarily adjusting credentials for privileged dump locations, invoking executable-format core writers, and writing process memory segments.

Core behavior:
- Core destinations are classified as `CORE_PROC`, `CORE_ZONE`, or `CORE_GLOBAL`.
- `core_log()` emits zone-scoped syslog messages for global/zone core dumps when `CC_GLOBAL_LOG` is enabled.
- `remove_core_file()` is a private unlink path that can operate relative to the process root, zone root, or global root; it refuses directories, read-only filesystems, unwritable files, and files with conflicting NBMAND share reservations.
- `create_core_file()` creates a new core with `FWRITE | FTRUNC | FEXCL | FCREAT | FOFFMAX`, using special lookup for zone/global locations that may be inaccessible under chroot or zone path limits.
- Created core files must be owned by the dumping credential’s uid; otherwise they are closed, removed, and rejected.
- `set_cred()` swaps a held credential into the process, updates per-user process counts if real uid changes, calls `crset()` for all threads, and returns a held old credential.
- `do_core()` determines applicable content and rlimit, rejects zero rlimit, enforces set-id/SNOCD core policy, temporarily switches to zone `kcred` for global/zone or set-id dumps, removes any existing target, creates the new target with exclusive create, restores original process credentials, and calls the executable format’s `exec_core()` method.
- Existing core files are removed before exclusive creation to avoid symlink/hardlink attacks, dumping into a mapped old core file, and concurrent clobbering.
- `expand_string()` expands core path tokens such as `%p`, `%u`, `%g`, `%f`, `%d`, `%n`, `%m`, `%t`, `%z`, `%Z`, and `%%`, with length checks and special `%d` pathname lookup.
- `dump_one_core()` expands a zone/global core pattern, calls `do_core()`, logs success and common failure cases, invokes core rctl actions on `EFBIG`, and optionally returns the allocated path string.
- `core()` is the main entry point. It checks whether any core paths are enabled, blocks most signals while preserving termination signals, marks `SDOCORE`, frees watched pages, moves current signal info aside, dumps per-process, per-zone, and global-zone cores as configured, restores the signal mask, and notifies process contracts via `contract_process_core()`.
- `core_seg()` writes a process memory range in chunks, skipping holes/non-memory via `as_memory()`, capping each write to `core_chunk * PAGESIZE`, and aborting on real signals.
- `core_write()` wraps `vn_rdwr()` so callers get complete-write-or-errno behavior, retrying partial writes and returning `ENOSPC` if no progress is made.

Important invariants:
- Core dumping may temporarily use zone `kcred` for filesystem access but restores process credentials before `exec_core()` records process credential information.
- Set-id or `SNOCD` processes dump only when global/process set-id core options allow it.
- Zone/global core paths deliberately bypass ordinary chroot/zone path restrictions using selected root/start vnodes.
- `core()` clears the current signal while doing file I/O because pending signal state can interfere with network filesystem writes.
- Offset arithmetic in `core_seg()` and `core_write()` is checked against `OFF_MAX` and wraparound.
- `core_write()` treats zero-progress successful `vn_rdwr()` as `ENOSPC`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/core.c -->