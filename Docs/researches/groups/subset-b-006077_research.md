# subset-b-006077 research

Grouped research for the Ceph client kernel sources in `subset-b-006077`. Each file section is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/watch_queue.c -->
# sources/distributed-fs/ceph-client/kernel/watch_queue.c

## Purpose
`watch_queue.c` implements the kernel watch queue and general notification mechanism backed by pipes. It lets kernel objects expose `struct watch_list` instances, lets users attach `struct watch` objects that point at a `struct watch_queue`, filters notifications, and posts fixed-size notification records into a pipe for userspace to read. The file is generic infrastructure rather than Ceph-specific code; in this source tree it is part of the kernel copy used by the Ceph client source corpus.

## Important APIs, types, and functions
The central types are `struct watch_queue`, `struct watch`, `struct watch_list`, `struct watch_filter`, `struct watch_type_filter`, `struct watch_notification`, `struct watch_notification_filter`, and `struct pipe_inode_info`. The important exported APIs are `__post_watch_notification()`, `put_watch_queue()`, `add_watch_to_object()`, `remove_watch_from_object()`, and `get_watch_queue()`. Non-exported but operationally important helpers include `lock_wqueue()`, `post_one_notification()`, `filter_watch_notification()`, `watch_queue_set_size()`, `watch_queue_set_filter()`, `watch_queue_clear()`, and `watch_queue_init()`.

The file defines a custom `pipe_buf_operations` table, `watch_queue_pipe_buf_ops`, with `watch_queue_pipe_buf_release()` as its release hook. That hook returns a notification slot to `wqueue->notes_bitmap` when the corresponding pipe buffer is consumed. There is intentionally no `try_steal` method, so pipe consumers cannot steal pages from the notification pool.

## Control flow
Queue setup starts with `watch_queue_init()`, which allocates a zeroed `struct watch_queue`, initializes its kref, spinlock, and watch hlist, attaches it to the pipe, and stores the pipe pointer in the queue. Userspace or pipe setup then calls `watch_queue_set_size()` to allocate notification pages and a slot bitmap. The requested note count is rounded up to a whole number of `WATCH_QUEUE_NOTES_PER_PAGE` slots and the pipe ring is resized to a power-of-two ring that can hold the overprovisioned buffers. Per-user pipe buffer accounting is charged for the actual pages.

`watch_queue_set_filter()` optionally installs a userspace-supplied filter. It copies the header, validates count/reserved fields, imports the array of type filters, rejects malformed info masks, ignores unknown notification types, builds a compact internal `struct watch_filter`, and swaps it under the pipe mutex with `rcu_replace_pointer()`. Old filters are freed with RCU.

Adding a watch flows through `init_watch()` and `add_watch_to_object()`. The caller initializes the watch with a queue pointer, then `add_watch_to_object()` takes an RCU read lock, locks the queue, locks the target `watch_list`, and calls `add_one_watch()`. `add_one_watch()` prevents duplicate `(queue,id)` attachments on the same watched object, enforces a per-user watch count limit based on `RLIMIT_NOFILE`, stores the current credentials, takes references on both the queue and watch, and links the watch into both the queue hlist and the watched object's RCU hlist.

Posting flows through `__post_watch_notification()`. The caller supplies a `watch_list`, notification record, triggering credentials, and a watch ID. The function validates nonzero notification length, iterates matching watchers under RCU, injects the watch's info ID into `n->info`, applies the queue filter, asks LSM policy through `security_post_notification()`, and then locks the queue before calling `post_one_notification()`. `post_one_notification()` serializes with pipe readers by taking `pipe->rd_wait.lock`, rejects full rings or exhausted note slots by marking the previous pipe buffer with `PIPE_BUF_FLAG_LOSS`, copies the notification into the preallocated note page with `kmap_local_page()`, publishes the pipe head with release ordering, clears the note bitmap bit, wakes readers, and sends async `SIGIO` notification.

Removal flows in two directions. `remove_watch_from_object()` removes one matching watch or all watches from an object's watch list, posts a `WATCH_TYPE_META` removal notification to the queue when possible, unlinks from the queue list, invokes an optional object-specific `release_watch()` callback outside RCU if needed, and drops the owned references. `watch_queue_clear()` handles pipe teardown: it nulls `wqueue->pipe` under the queue lock to block future posts, drains the queue's watches, then for each watch drops locks before acquiring the object watch-list lock to avoid lock-order deadlocks.

## State and persistence behavior
All state is runtime kernel memory. `watch_queue` owns the pipe pointer, a spinlock, a watch hlist, notification pages, the free-slot bitmap, counts for pages and notes, a kref, and an RCU-protected optional filter. Each `watch` stores its queue pointer, watched-list pointer, credentials, info ID, ID, hlist nodes, kref, and RCU head. Slot lifetime is tracked by `wqueue->notes_bitmap`: a bit is clear while a note is in a pipe buffer and set again from the pipe buffer release path. The code does not persist state across boot or unmount; teardown frees pages, bitmaps, filters, watches, credentials, and queue memory through kref and RCU callbacks.

## Dependencies and integration points
This file integrates with pipe internals (`pipe_inode_info`, pipe ring resizing, `pipe_buf_operations`, wakeups, fasync), RCU and hlist traversal, krefs, page allocation, bitmap allocation, credential and user accounting, `RLIMIT_NOFILE`, LSM notification permission checks, `copy_from_user()` and `memdup_array_user()`, and watched-object subsystems that own `struct watch_list` and optional `release_watch()` callbacks. The exported APIs are intended for other kernel subsystems that need to expose object notifications through watch queues.

## Risks and test signals
Key risks are concurrency and lifetime bugs: queue teardown races with notification posting, object-side removal racing with queue-side clearing, filter replacement under RCU, and pipe buffer release returning slots after consumers drain the pipe. The locking contract is strict: `post_one_notification()` assumes both RCU and queue lock protection, and `lock_wqueue()` rejects destroyed queues by checking `wqueue->pipe`. Other risks include notification loss when the pipe ring is full or all note slots are in use, incorrect `WATCH_INFO_LENGTH` causing copies of the wrong size, quota/accounting mismatches after pipe ring resizing, and user filter validation errors that could admit unintended notifications.

Useful test signals include creating a watch queue with invalid, minimum, and maximum note counts; verifying pipe user accounting and resize behavior; installing, removing, and replacing filters; posting accepted and rejected notification subtypes; forcing pipe-full and slot-exhaustion loss flags; reading notifications and confirming slot reuse through the release hook; attaching duplicate watches; removing one watch and all watches; clearing a queue while watched objects still exist; and checking LSM denial behavior in `security_post_notification()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/watch_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/watchdog.c -->
# sources/distributed-fs/ceph-client/kernel/watchdog.c

## Purpose
`watchdog.c` is the generic kernel lockup detector core. It coordinates soft-lockup detection using per-CPU hrtimers and stopper work, hard-lockup detection through backend hooks, boot parameters, sysctl configuration, CPU hotplug, optional interrupt-storm diagnostics, sysfs counters, panic behavior, and delayed hardlockup backend probing. It supplies the policy and shared timing state used by backend implementations such as the buddy and perf files in this group.

## Important APIs, types, and functions
Important global configuration includes `watchdog_enabled`, `watchdog_user_enabled`, `watchdog_thresh`, `watchdog_cpumask`, `watchdog_cpumask_bits`, `watchdog_hardlockup_miss_thresh`, `hardlockup_panic`, `softlockup_panic`, `hardlockup_si_mask`, and the soft/hard all-CPU-backtrace sysctl variables. Core exported or externally visible functions include `hardlockup_detector_disable()`, `arch_touch_nmi_watchdog()`, `watchdog_hardlockup_touch_cpu()`, `watchdog_hardlockup_check()`, weak backend hooks `watchdog_hardlockup_enable()`, `watchdog_hardlockup_disable()`, `watchdog_hardlockup_probe()`, `watchdog_hardlockup_stop()`, `watchdog_hardlockup_start()`, touch APIs such as `touch_softlockup_watchdog()`, `touch_all_softlockup_watchdogs()`, `touch_softlockup_watchdog_sync()`, CPU hotplug callbacks `lockup_detector_online_cpu()` and `lockup_detector_offline_cpu()`, `lockup_detector_reconfigure()`, `lockup_detector_soft_poweroff()`, `lockup_detector_retry_init()`, and `lockup_detector_init()`.

The soft-lockup implementation uses per-CPU `watchdog_touch_ts`, `watchdog_report_ts`, `watchdog_hrtimer`, `softlockup_completion`, and `softlockup_stop_work`. When `CONFIG_HARDLOCKUP_DETECTOR_COUNTS_HRTIMER` is enabled, hard-lockup state is based on per-CPU `hrtimer_interrupts`, saved counters, missed counts, warned flags, and touched flags. With `CONFIG_SOFTLOCKUP_DETECTOR_INTR_STORM`, the file also tracks sampled CPU time groups and IRQ snapshots to identify hard IRQ storms.

## Control flow
Boot-time setup parses command-line controls such as `nmi_watchdog=`, `softlockup_panic=`, `nowatchdog`, `nosoftlockup`, and `watchdog_thresh=`. `lockup_detector_init()` initializes `watchdog_cpumask` from timer housekeeping CPUs, probes the hardlockup backend, records whether delayed retry is allowed, and calls `lockup_detector_setup()`. Setup computes enabled bits with `lockup_detector_update_enable()`, starts or reconfigures detectors under `watchdog_mutex`, and marks softlockup infrastructure initialized. A late init check flushes delayed probe work and registers `/proc/sys/kernel` watchdog sysctls.

The soft-lockup detector starts per CPU in `watchdog_enable()`. It initializes a completion, starts a pinned hard hrtimer at `sample_period`, updates timestamps, and then enables the hardlockup backend if the hard bit is active. The hrtimer callback `watchdog_timer_fn()` is the main loop. It exits when detectors are disabled or panic is already in progress, kicks the hardlockup path, schedules `softlockup_fn()` on the current CPU through `stop_one_cpu_nowait()` when the previous stopper pass completed, advances the timer, gets an approximate running-clock timestamp, handles KVM guest pause false positives, updates optional CPU utilization samples, honors `SOFTLOCKUP_DELAY_REPORT`, and calls `is_softlockup()` to determine whether the CPU has failed to reschedule for longer than the threshold.

On a soft lockup, the callback increments the sysfs counter when enabled, serializes all-CPU backtrace reporting with `soft_lockup_nmi_warn`, updates the report timestamp for the next warning period, prints the stuck task, optional CPU utilization and IRQ storm data, loaded modules, IRQ trace state, registers or stack, triggers all-but-current CPU backtraces if configured, taints the kernel, prints selected `sys_info()`, and panics if `softlockup_panic` is configured and the duration has crossed the required number of soft thresholds.

The hard-lockup hrtimer-counting path increments `hrtimer_interrupts` in `watchdog_hardlockup_kick()` and delegates cross-CPU checking to the buddy backend when present. `watchdog_hardlockup_check()` looks for CPUs whose hrtimer interrupt count has stopped advancing, honors explicit touch/reset requests, suppresses repeated reports per CPU, handles `scx_hardlockup()` mitigation for BPF scheduler failures, prints diagnostics, optionally triggers all-CPU backtraces, emits selected system information, and calls `nmi_panic()` when configured.

Reconfiguration flows through sysctl handlers or `lockup_detector_reconfigure()`. `__lockup_detector_reconfigure()` holds CPU read lock, stops backend hardlockup detection, stops all softlockup hrtimers, updates `watchdog_thresh` only after softlockup timers are stopped when the threshold changed, recomputes `sample_period`, recomputes enable bits, restarts softlockup timers if enabled and threshold is nonzero, and restarts the hardlockup backend. CPU hotplug callbacks enable or disable the detector only for CPUs present in `watchdog_allowed_mask`.

## State and persistence behavior
The detector state is runtime-only and rebuilt at boot. Global sysctl/module-parameter state controls whether watchdogs are enabled, the threshold, panic behavior, CPU mask, all-CPU backtrace behavior, and system-information masks. Per-CPU state records last successful watchdog touch, last warning period, hrtimer object, completion/stopper work, hardlockup counters, and diagnostic sampling history. Sysfs counters `softlockup_count` and `hardlockup_count` expose the number of detections since boot when sysfs support is compiled in. No persistent storage is used.

The key timing relation is that the soft threshold is twice `watchdog_thresh`, and `sample_period` is one fifth of the soft threshold in nanoseconds. This gives the hrtimer several opportunities to feed the soft detector and advance the hardlockup heartbeat before a hardlockup backend fires. The timestamp code intentionally uses coarse `running_clock() >> 30` seconds-like values to avoid expensive division in hot paths.

## Dependencies and integration points
`watchdog.c` integrates with CPU hotplug and CPU masks, housekeeping/nohz-full isolation, hrtimers, `stop_one_cpu_nowait()`, completions, scheduler clocks, KVM guest pause detection, panic state, printk CPU synchronization, backtrace helpers, IRQ tracing, module printing, sysctl, sysfs, workqueues for delayed backend init, BPF sched-ext lockup mitigation (`scx_softlockup()` and `scx_hardlockup()`), `sys_info()` diagnostic masks, perf/NMI or architecture-specific hardlockup backends through weak symbols, and optional interrupt accounting via `kstat_snapshot_irqs()` and `kstat_get_irq_since_snapshot()`.

## Risks and test signals
Primary risks are false positives during CPU bring-up/offline, VM pauses, nohz-full isolation, threshold reconfiguration, delayed stopper execution, long printk/backtrace stalls, or interrupt storms. The code has multiple mitigations, including KVM pause checks, touch APIs, stopping timers before threshold updates, CPU mask filtering, and per-CPU warned flags. Another risk is backend availability: sysctl writes to `nmi_watchdog` return `-ENOTSUPP` when hardlockup probing failed, and delayed probing must finish before init memory is freed. Panic and taint behavior are high-impact and require exact threshold semantics.

Useful test signals include boot parameter parsing for watchdog enable, panic, threshold, and raw NMI options; sysctl reads that reflect current enabled state without permanently changing backing variables; sysctl writes that reconfigure CPU masks and thresholds; CPU hotplug start/stop behavior; nohz-full default mask exclusion; KVM pause suppression; softlockup touch APIs from scheduler and generic callers; interrupt-storm reporting when hard IRQ utilization exceeds the threshold; hardlockup backtrace serialization; sysfs counter increments; and backend delayed-probe success/failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/watchdog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/watchdog_buddy.c -->
# sources/distributed-fs/ceph-client/kernel/watchdog_buddy.c

## Purpose
`watchdog_buddy.c` implements a hard-lockup backend that uses hrtimer progress on one CPU to check a neighboring CPU. Instead of relying on a local perf NMI event per CPU, each active watchdog CPU periodically checks whether the next active CPU's hrtimer interrupt counter is advancing. This file plugs into the weak hardlockup hooks declared by `watchdog.c`.

## Important APIs, types, and functions
The file owns a static `cpumask_t watchdog_cpus`, the set of CPUs participating in buddy checking. The key helper is `watchdog_next_cpu()`, which uses `cpumask_next_wrap()` to find the next CPU in that mask and returns `nr_cpu_ids` when the current CPU would only find itself. Backend entry points are `watchdog_hardlockup_probe()`, `watchdog_hardlockup_enable()`, `watchdog_hardlockup_disable()`, and `watchdog_buddy_check_hardlockup()`.

## Control flow
Probe is simple: `watchdog_hardlockup_probe()` sets the shared `watchdog_hardlockup_miss_thresh` to 3 and returns success. Raising the miss threshold is important because buddy checking observes another CPU's hrtimer count and needs enough grace periods to avoid transient false positives around CPU hotplug or startup.

When a CPU is enabled, `watchdog_hardlockup_enable()` first touches that CPU's hardlockup state through `watchdog_hardlockup_touch_cpu(cpu)` so other CPUs do not report it before its hrtimer has run. It then computes the next currently participating CPU and touches that CPU too, because this CPU may soon begin checking it. A write memory barrier ensures these touch operations are visible before the CPU is added to `watchdog_cpus`, then the CPU bit is set.

When disabling, `watchdog_hardlockup_disable()` finds the next CPU before clearing the current CPU from the mask. If such a next CPU exists, it touches that CPU to avoid a false positive from the CPU before this one, which will begin checking a different buddy after the mask changes. Another write memory barrier orders the touch before the mask removal.

The periodic check is driven by the generic hrtimer code in `watchdog.c`. `watchdog_hardlockup_kick()` increments the local hrtimer interrupt counter and calls `watchdog_buddy_check_hardlockup()`. This file finds the next CPU in `watchdog_cpus`; if there is no other CPU, it returns. Otherwise it executes a read memory barrier paired with the enable/disable write barriers and calls `watchdog_hardlockup_check(next_cpu, NULL)`.

## State and persistence behavior
The only local persistent-in-memory state is `watchdog_cpus`. Hardlockup counters, touch flags, warned flags, and panic/report behavior live in `watchdog.c`. State is runtime-only and changes as CPUs are enabled or disabled for lockup detection. No userspace-visible settings are stored in this file directly.

## Dependencies and integration points
This backend depends on the generic hrtimer-counting hardlockup path in `watchdog.c`, including `watchdog_hardlockup_miss_thresh`, `watchdog_hardlockup_touch_cpu()`, and `watchdog_hardlockup_check()`. It also depends on CPU masks and SMP memory ordering. It is compiled as a backend selected by kernel configuration and supplies strong definitions that override the weak generic hardlockup hooks.

## Risks and test signals
The main risk is false hardlockup reporting during CPU hotplug, especially when a newly online CPU has been added to scheduler-visible masks before its watchdog hrtimer fires, or when removing a CPU changes which buddy another CPU checks. The explicit touch operations and memory barriers are the main safeguards. Another risk is single-CPU behavior: when only one CPU participates, there is no next CPU and no buddy check can be performed.

Useful test signals include enabling the first CPU and verifying no self-check occurs; enabling multiple CPUs and confirming each checks the next wrapped CPU; CPU online/offline churn without false positives; correct miss threshold of 3 after probe; memory-order-sensitive tests where a buddy observes mask changes only after touch state is visible; and integration with `watchdog_hardlockup_check()` reports when a buddy CPU's hrtimer counter stops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/watchdog_buddy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/watchdog_perf.c -->
# sources/distributed-fs/ceph-client/kernel/watchdog_perf.c

## Purpose
`watchdog_perf.c` implements a hard-lockup detector backend using perf events, typically NMI-capable hardware PMU events. It creates a pinned per-CPU perf counter whose overflow callback runs in an NMI-like context and asks the generic watchdog core to check for a hard lockup on that same CPU. It also supports timestamp filtering to reduce false positives caused by PMU frequency behavior, raw perf-event configuration from the boot command line, and global stop/restart hooks for architecture quirks.

## Important APIs, types, and functions
The file owns per-CPU `struct perf_event *watchdog_ev` and an atomic count of enabled watchdog CPUs. The main event attributes are `wd_hw_attr` and `fallback_wd_hw_attr`, both defaulting to pinned `PERF_TYPE_HARDWARE` / `PERF_COUNT_HW_CPU_CYCLES` counters. Important functions are `watchdog_overflow_callback()`, `hardlockup_detector_event_create()`, `watchdog_hardlockup_enable()`, `watchdog_hardlockup_disable()`, `hardlockup_detector_perf_adjust_period()`, `hardlockup_detector_perf_stop()`, `hardlockup_detector_perf_restart()`, weak `arch_perf_nmi_is_available()`, `watchdog_hardlockup_probe()`, and `hardlockup_config_perf_event()`.

When `CONFIG_HARDLOCKUP_CHECK_TIMESTAMP` is enabled, timestamp-related state includes per-CPU `last_timestamp`, per-CPU `nmi_rearmed`, and global `watchdog_hrtimer_sample_threshold`. The exported-to-core function `watchdog_update_hrtimer_threshold()` updates that threshold when the generic sample period changes.

## Control flow
The generic watchdog core first probes this backend by calling `watchdog_hardlockup_probe()`. Probe checks whether the architecture reports perf NMI availability, verifies that `hw_nmi_get_sample_period(watchdog_thresh)` returns a usable period, then tries to create a temporary kernel perf counter on the current CPU. Success releases the temporary event and returns zero; failure logs that the perf NMI watchdog is disabled and returns the perf error.

Enabling a CPU through `watchdog_hardlockup_enable()` asserts the target CPU is local, creates a perf event with `hardlockup_detector_event_create()`, logs a one-time PMU counter consumption message when the first CPU is enabled, warns if an old per-CPU event pointer leaked, stores the event in `watchdog_ev`, initializes timestamp filtering state, and enables the perf event. Event creation first tries `wd_hw_attr` with a sample period derived from `watchdog_thresh`; if that fails, it retries with `fallback_wd_hw_attr`.

When the perf counter overflows, `watchdog_overflow_callback()` resets `event->hw.interrupts` to prevent perf throttling, exits if panic is in progress, applies optional timestamp filtering, and calls `watchdog_hardlockup_check(smp_processor_id(), regs)`. The generic core decides whether to print diagnostics or panic based on hrtimer/touch state and configured policy.

Disabling a CPU through `watchdog_hardlockup_disable()` disables and releases the per-CPU perf event, clears `watchdog_ev`, and decrements the enabled CPU count. `hardlockup_detector_perf_adjust_period()` changes the active event period after CPU frequency changes when the hard watchdog is enabled and the current period differs. `hardlockup_detector_perf_stop()` and `hardlockup_detector_perf_restart()` iterate online CPUs under the CPU hotplug read lock and disable or re-enable existing events; these are special x86-facing hooks for perf hyperthreading issues.

`hardlockup_config_perf_event()` parses a hexadecimal raw event ID from the `nmi_watchdog=r...` boot option path. It accepts either a plain raw event string or a comma-terminated component, converts it with `kstrtoull()`, and changes `wd_hw_attr` to `PERF_TYPE_RAW` with that config.

## State and persistence behavior
State is runtime-only. Each participating CPU may own one kernel perf event pointer in `watchdog_ev`; the atomic `watchdog_cpus` tracks how many CPUs currently have active events and gates the informational message. Timestamp filtering state is per CPU and is reset whenever the event is enabled. Attribute changes from `hardlockup_config_perf_event()` affect runtime boot configuration but are not persisted beyond the running kernel.

The timestamp filter is specifically defensive. The generic hrtimer should run faster than the NMI watchdog, but CPU-cycle PMU events can overflow sooner than nominal under turbo or frequency effects. `watchdog_check_timestamp()` suppresses samples that arrive before `watchdog_hrtimer_sample_threshold`, but after repeated rearming it allows progress so stale time bases do not suppress real lockups forever.

## Dependencies and integration points
This backend integrates with the perf event subsystem, hardware PMU/NMI support, `hw_nmi_get_sample_period()`, generic hardlockup policy in `watchdog.c`, panic state, architecture availability hooks, CPU hotplug locking, and architecture-specific callers that stop/restart perf events or adjust periods. It also shares the boot command parser path in `watchdog.c` for `nmi_watchdog=r...` raw event selection.

## Risks and test signals
Risks include inability to allocate a pinned PMU counter, architectures without NMI-capable perf events, event creation success during probe but later per-CPU failures, leaked per-CPU events, false positives from PMU overflow timing, and period-adjustment failures during CPU frequency changes. The overflow callback runs in a sensitive context, so it must avoid blocking and must keep diagnostics delegated to the generic hardlockup path.

Useful test signals include backend probe success and failure; fallback attribute creation after primary event failure; enable/disable cycles across CPU hotplug; one-time PMU consumption logging; no `watchdog_ev` leak warnings; raw event parsing from `nmi_watchdog=r...`; timestamp filter suppression and eventual rearm escape; period adjustment after frequency changes; perf stop/restart under CPU lock; and hardlockup reports generated from a perf overflow with valid register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/watchdog_perf.c -->
