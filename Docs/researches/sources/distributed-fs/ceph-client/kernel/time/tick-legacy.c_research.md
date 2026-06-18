# sources/distributed-fs/ceph-client/kernel/time/tick-legacy.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-legacy.c` provides the timer tick function for architectures that have not converted to generic clockevents. The complete 37-line source was read.

## Important APIs, Types, and Functions

The file exposes one function, `legacy_timer_tick(unsigned long ticks)`. It uses `jiffies_lock`, `jiffies_seq`, `do_timer`, `update_wall_time`, `update_process_times`, `profile_tick`, and `get_irq_regs`.

## Control Flow

Architectural timer interrupt code calls `legacy_timer_tick` with the number of elapsed ticks. If `ticks` is nonzero, the function updates jiffies under the jiffies lock and sequence counter, then updates wall time. Regardless of whether this CPU advanced timekeeping, it performs process time accounting and profiling for the interrupted context.

## State and Persistence Behavior

The function updates global timekeeping state (`jiffies`, wall time) only when `ticks` is nonzero. It owns no persistent state of its own.

## Dependencies and Integration Points

This file integrates legacy architecture timer interrupt paths with the common scheduler accounting and timekeeping code. It depends on low-level IRQ register state, profiling, and `timekeeper_internal.h`.

## Risks and Edge Cases

Callers must invoke it with interrupts disabled. A zero `ticks` argument means the current CPU is not responsible for global timekeeping but still needs process accounting; losing that distinction could double-advance jiffies or skip accounting.

## Test Signals

Boot and timer interrupt tests on non-generic-clockevent architectures, jiffies progression checks, process CPU accounting, profiling tick behavior, and lockdep validation around interrupt-disabled calls are the relevant signals.
