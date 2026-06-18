# sources/distributed-fs/ceph-client/kernel/time/tick-common.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-common.c` contains the generic periodic tick and clockevent device management core. It owns per-CPU tick device selection, periodic tick handling, `do_timer()` CPU assignment and handoff, replacement policy for clockevent devices, suspend/resume, CPU hotplug shutdown, and system freeze/unfreeze support. The complete 595-line source was read.

## Important APIs, Types, and Functions

Global state includes `DEFINE_PER_CPU(struct tick_device, tick_cpu_device)`, `ktime_t tick_next_period`, and `int tick_do_timer_cpu`. Important functions are `tick_get_device`, `tick_is_oneshot_available`, `tick_handle_periodic`, `tick_setup_periodic`, `tick_install_replacement`, `tick_check_replacement`, `tick_check_new_device`, `tick_broadcast_oneshot_control`, `tick_assert_timekeeping_handover`, `tick_cpu_dying`, `tick_shutdown`, `tick_suspend_local`, `tick_resume_local`, `tick_suspend`, `tick_resume`, `tick_freeze`, `tick_unfreeze`, and `tick_init`. Internal helpers include `tick_periodic`, `tick_setup_device`, `tick_check_percpu`, and `tick_check_preferred`.

## Control Flow

Periodic tick interrupts call `tick_handle_periodic`, which clears forced-next-event state, invokes `tick_periodic`, and, for devices operated in oneshot mode, repeatedly programs the next tick while catching up if timekeeping is valid for high-resolution operation. `tick_periodic` lets only `tick_do_timer_cpu` update jiffies/timekeeping via `do_timer` and `update_wall_time`; all CPUs still perform process accounting and profiling.

When a clockevent device is registered, `tick_check_new_device` compares it with the current per-CPU device using CPU affinity, oneshot support, rating, and current mode. If selected, `tick_setup_device` assigns first-time `do_timer` duty, preserves previous handler/next event on replacement, pins IRQ affinity if needed, asks broadcast logic whether this device should be controlled by broadcast, and configures periodic or oneshot mode. If not selected locally, the device may become the broadcast device. Hotplug and suspend paths shut down or resume per-CPU and broadcast devices while preserving tick mode.

## State and Persistence Behavior

State is kernel-resident. Each CPU has a `tick_device` pointer and mode. `tick_next_period` tracks the next periodic tick under `jiffies_lock`/`jiffies_seq`. `tick_do_timer_cpu` records which CPU updates global jiffies/timekeeping and can be transferred during NO_HZ idle or CPU hotplug. Suspend freeze state is protected by `tick_freeze_lock` and `tick_freeze_depth`.

## Dependencies and Integration Points

Dependencies include clockevents, jiffies/timekeeping, scheduler process accounting, profiling, hrtimers, CPU hotplug, suspend/resume, lockdep, tracepoints, broadcast support, NO_HZ, and high-resolution timer transition code. It integrates with `tick-broadcast.c` for broadcast device decisions, `tick-oneshot.c` for oneshot setup, and `tick-sched.c` for NO_HZ initialization and dying-CPU tick scheduler cleanup.

## Risks and Edge Cases

The `do_timer()` owner must never disappear without handoff or jiffies stall. Device replacement must avoid returning a broadcast device to the clockevents layer incorrectly. A non-per-CPU device may need IRQ affinity pinning, and existing CPU-local devices are preferred even with lower rating. Periodic devices that lack true periodic mode are emulated with oneshot reprogramming and can loop if timekeeping is invalid. Freeze/unfreeze runs in constrained suspend contexts, including PREEMPT_RT lockdep exceptions.

## Test Signals

Strong signals include clockevent registration/replacement tests, boot on systems with per-CPU and global timer devices, highres and lowres tick modes, CPU hotplug with the timekeeping CPU going down, suspend/resume and freeze/unfreeze, NO_HZ handoff tests, and tracing/profiling checks that process accounting still runs on non-timekeeping CPUs.
