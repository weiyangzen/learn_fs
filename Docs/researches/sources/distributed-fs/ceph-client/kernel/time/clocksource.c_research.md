# sources/distributed-fs/ceph-client/kernel/time/clocksource.c

Purpose: core clocksource registry, selection, watchdog verification, suspend-time measurement, sysfs override/unbind, and conversion math. It exports clocksource registration/update helpers and unstable marking used by architecture and driver code.

Important APIs and flow: `clocks_calc_mult_shift()` and `clocks_calc_max_nsecs()` compute scaled conversion limits. `__clocksource_register_scale()` initializes arch state, validates id/VDSO mode, updates frequency scaling, inserts the clocksource by rating, attaches watchdog state, selects current/watchdog/suspend clocks, and notifies timekeeping. `__clocksource_select()` chooses the best clocksource subject to boot/sysfs override and high-res validity. The watchdog timer compares candidate deltas against a continuous watchdog, checks remote CPU skew via async SMP calls, marks unstable clocks, drops their rating to zero in a kthread, and may trigger re-selection. Suspend helpers use a nonstop suspend clocksource to measure slept nanoseconds.

State and persistence: global state includes `curr_clocksource`, `suspend_clocksource`, `clocksource_list`, `override_name`, boot completion, watchdog list/timer/work, and per-CPU watchdog exchange data. Sysfs persists user override until changed or invalidated.

Dependencies and integration: integrated with timekeeping notification, tick high-res/nohz mode, VDSO clock modes, CPU topology/NUMA distances, kthreads/workqueues, sysfs, boot parameters `clocksource=` and deprecated `clock=`, and architecture clocksource hooks.

Risks and test signals: risks include watchdog false positives after long stalls, remote CPU timeout/skew detection, fallback failure when unbinding current/watchdog clocks, overflow in conversion math, and invalid VDSO mode. Test via watchdog unit module, sysfs selection/unbind, suspend/resume deltas, boot overrides, high-res enablement after validation, and unstable-clock re-selection.
