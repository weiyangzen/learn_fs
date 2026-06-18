# sources/distributed-fs/ceph-client/include/linux/hrtimer_rearm.h

## Purpose
`hrtimer_rearm.h` defines optional deferred hrtimer rearm hooks used when `CONFIG_HRTIMER_REARM_DEFERRED` is enabled. It allows CPU-local timer reprogramming to be deferred until safe exit or scheduling points, reducing expensive clockevent reprogramming in some paths.

## Important APIs, Types, And Functions
Enabled builds declare `__hrtimer_rearm_deferred()` and define inline helpers `hrtimer_test_and_clear_rearm_deferred_tif()`, `hrtimer_rearm_deferred_user_irq()`, `hrtimer_rearm_deferred_tif()`, `hrtimer_rearm_deferred()`, and `hrtimer_test_and_clear_rearm_deferred()`. `TIF_REARM_MASK` combines reschedule and hrtimer rearm thread flags. Disabled builds provide no-op/false stubs.

## Control Flow And State
The current thread's `_TIF_HRTIMER_REARM` flag signals that rearm work is pending. IRQ/user exit and scheduler paths test and clear the flag with interrupts disabled, optionally invoke `__hrtimer_rearm_deferred()`, and avoid entering slower loops when rearm was the only pending work. State is CPU-local and stored in thread flags plus hrtimer CPU-base deferred fields.

## Dependencies And Integration Points
It depends on `linux/thread_info.h` when enabled, thread flag helpers, lockdep IRQ assertions, scheduler exit-to-user paths, irqentry exit, and hrtick/time-slice extension logic.

## Risks
Risks include calling with interrupts enabled, missing rearm when reschedule flags are also present, clearing the wrong thread flag, or making assumptions in disabled configs where helpers are no-ops. Since it participates in scheduler/interrupt return paths, small ordering bugs can cause lost timer interrupts or unnecessary latency.

## Test Signals
Test with `CONFIG_HRTIMER_REARM_DEFERRED` on and off, scheduler hrtick workloads, user/IRQ exit paths, reschedule flag combinations, lockdep IRQ assertions, and virtualized workloads sensitive to clockevent reprogramming.
