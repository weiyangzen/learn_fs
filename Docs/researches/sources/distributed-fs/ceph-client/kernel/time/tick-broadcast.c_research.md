# sources/distributed-fs/ceph-client/kernel/time/tick-broadcast.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-broadcast.c` manages generic tick broadcast support. It selects a broadcast clockevent device, tracks CPUs whose local tick devices stop or are placeholders, broadcasts periodic and oneshot tick events, handles deep-idle enter/exit, supports oneshot wakeup devices, and coordinates CPU hotplug, suspend, and resume. The complete 1248-line source was read.

## Important APIs, Types, and Functions

External APIs include `tick_get_broadcast_device`, `tick_get_broadcast_mask`, `tick_get_wakeup_device`, `tick_install_broadcast_device`, `tick_is_broadcast_device`, `tick_broadcast_update_freq`, `tick_device_uses_broadcast`, `tick_receive_broadcast`, `tick_broadcast_control`, `tick_set_periodic_handler`, `tick_broadcast_offline`, `tick_suspend_broadcast`, `tick_resume_check_broadcast`, `tick_resume_broadcast`, `tick_get_broadcast_oneshot_mask`, `tick_check_broadcast_expired`, `tick_check_oneshot_broadcast_this_cpu`, `__tick_broadcast_oneshot_control`, `tick_broadcast_switch_to_oneshot`, `hotplug_cpu__broadcast_tick_pull`, `tick_broadcast_oneshot_active`, `tick_broadcast_oneshot_available`, and `tick_broadcast_init`. Key state includes `tick_broadcast_device`, `tick_broadcast_mask`, `tick_broadcast_on`, `tick_broadcast_oneshot_mask`, `tick_broadcast_pending_mask`, `tick_broadcast_force_mask`, per-CPU `tick_oneshot_wakeup_device`, and `tick_broadcast_lock`.

## Control Flow

Clockevent registration calls may install a device as either a per-CPU oneshot wakeup device or the global broadcast device if it is not dummy, per-CPU, or C3STOP-affected and has sufficient rating. Periodic broadcast uses `tick_handle_periodic_broadcast`: under the broadcast lock it computes online CPUs in `tick_broadcast_mask`, sends remote broadcast callbacks, optionally handles the local CPU after dropping the lock, and reprograms oneshot-style broadcast devices for the next period.

For oneshot broadcast, idle entry calls `__tick_broadcast_oneshot_control(TICK_BROADCAST_ENTER)`. The code may refuse deep idle if the current CPU owns an hrtimer broadcast event, otherwise it sets the CPU in the oneshot mask, shuts down the local timer if safe, and programs the broadcast device to the earliest sleeping CPU deadline. The broadcast interrupt scans sleeping CPUs for expired local `next_event` values, marks pending remote events, combines forced wakeups, sends broadcast IPIs/callbacks, and arms the next earliest event. Idle exit clears mask state, restores the local device, and either avoids reprogramming when a broadcast IPI is pending or forces the broadcast path to deliver an already expired local event.

## State and Persistence Behavior

All state is in memory and mostly global cpumasks protected by `tick_broadcast_lock`. `tick_broadcast_mask` covers CPUs needing periodic broadcast; `tick_broadcast_on` records explicit broadcast mode requests; oneshot, pending, and force masks track sleeping CPUs and in-flight events. Per-CPU wakeup device pointers persist until replaced or CPU offline. Suspend shuts down the broadcast device but preserves masks; resume reinitializes the device according to the saved mode and masks.

## Dependencies and Integration Points

The file depends on clockevents, cpumasks, SMP broadcast callbacks, IRQ affinity, hrtimers, CPU hotplug, suspend/resume, NO_HZ, and per-CPU `tick_cpu_device` from `tick-common.c`. It integrates with `tick-oneshot.c` for oneshot mode switching, `tick-sched.c` for idle/nohz behavior, and `tick-broadcast-hrtimer.c` for hrtimer pseudo broadcast devices.

## Risks and Edge Cases

Broadcast correctness is sensitive to cpumask races, offline CPUs, hrtimer broadcast ownership, and local handler recursion. Hrtimer broadcast devices cannot let their owning CPU enter deep idle or the broadcast event may never fire. Pending and force masks avoid repeated reprogramming and ping-pong when a CPU wakes just as its local deadline expires. Device replacement during oneshot mode must avoid setting oneshot bits for CPUs that are not actually idle. Missing broadcast function support degrades to a critical warning path where CPUs may become unresponsive.

## Test Signals

Important signals include platforms with C3STOP local timers, systems using hrtimer broadcast fallback, NO_HZ idle and full dynticks tests, CPU hotplug while CPUs are in broadcast masks, suspend/resume with broadcast active, dynamic clockevent replacement, IRQ affinity changes, and lockdep/KCSAN stress around `tick_broadcast_lock` and mask updates.
