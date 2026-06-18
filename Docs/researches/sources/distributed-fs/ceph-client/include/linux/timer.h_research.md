<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timer.h -->
# sources/distributed-fs/ceph-client/include/linux/timer.h

## Purpose
declares the classic jiffies-based `timer_list` API, initialization macros, flag layout, add/modify/reduce/delete/shutdown functions, and CPU hotplug hooks.

## Important APIs, Types, and Functions
The file is 201 lines and exports these visible symbol families: types/enums `hrtimer`; macros/constants `TIMER_CPUMASK`, `TIMER_MIGRATING`, `TIMER_BASEMASK`, `TIMER_DEFERRABLE`, `TIMER_PINNED`, `TIMER_IRQSAFE`, `TIMER_INIT_FLAGS`, `TIMER_ARRAYSHIFT`, `TIMER_ARRAYMASK`, `TIMER_TRACE_FLAGMASK`, `TIMER_NEXT_MAX_DELTA`, `timers_prepare_cpu`, `timers_dead_cpu`; function-like macros `__TIMER_LOCKDEP_MAP_INITIALIZER`, `__TIMER_INITIALIZER`, `DEFINE_TIMER`, `__timer_init`, `__timer_init_on_stack`, `timer_setup`, `timer_setup_on_stack`, `timer_container_of`; inline helpers `timer_init_key_on_stack`, `timer_destroy_on_stack`, `timer_pending`, `tmigr_isolated_exclude_cpumask`; external prototypes `__TIMER_INITIALIZER`, `timer_init_key_on_stack`, `timer_init_key`, `DEFINE_TIMER`, `add_timer_on`, `mod_timer`, `mod_timer_pending`, `timer_reduce`, `add_timer`, `add_timer_local`, `add_timer_global`, `timer_delete_sync_try`, `timer_delete_sync`, `timer_delete`, and 13 more.

## Control Flow
Callers initialize timers with `timer_setup()` or DEFINE_TIMER, arm them with add/mod/reduce helpers, callbacks run from timer softirq context, and teardown uses delete or shutdown variants. Pinned/deferrable/irqsafe flags influence CPU placement, idle behavior, and callback locking expectations.

## State and Persistence Behavior
`timer_list` stores callback, expiry, flags/base encoding, and lockdep map. The timer wheel and per-CPU bases maintain queued state; `timer_pending()` checks whether the hlist node is unhashed.

## Dependencies and Integration Points
It depends on timer types, debugobjects, lockdep, workqueues/cpumasks, hrtimer for real-time interval hook, and CPU hotplug. Direct includes are `linux/list.h`, `linux/ktime.h`, `linux/stddef.h`, `linux/debugobjects.h`, `linux/stringify.h`, `linux/timer_types.h`.

## Risks and Edge Cases
Deleting a timer while its callback can rearm or holds locks is subtle; shutdown variants prevent rearming and are safer for teardown. Flag bitfields encode CPU/base state and must not collide. IRQ-safe timers need callback discipline.

## Test Signals
Run timer selftests, debugobjects coverage, module unload teardown tests using delete vs shutdown, CPU hotplug with pinned timers, deferrable idle behavior, and race tests for mod/delete/rearm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timer.h -->
