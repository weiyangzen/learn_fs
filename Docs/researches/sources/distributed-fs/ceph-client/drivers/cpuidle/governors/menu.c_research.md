<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/menu.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/governors/menu.c

## Purpose

`menu.c` implements the menu governor, which predicts idle duration from the next timer event and recent interval history, then selects the deepest state satisfying latency and target-residency constraints.

## Important APIs, Types, And Functions

Per-CPU `struct menu_device` stores correction factors, recent intervals, next timer duration, bucket, and pending-update flags. `menu_select()` performs state selection, `menu_reflect()` defers update work, `menu_update()` adjusts prediction factors after wakeup, and `get_typical_interval()` detects repeating wakeup patterns with variance and outlier handling.

## Control Flow

Selection first updates prior metrics if needed. It computes a typical interval from the last eight samples, optionally obtains nohz sleep length and next tick delta, applies a bucketed correction factor, honors latency constraints, and scans enabled states in order. It may retain the tick for polling or short predicted idle, and corrects the selected state downward if the tick will arrive before the selected state's target residency.

## State And Persistence Behavior

Correction factors start at unity on enable and decay with measured wakeups. Interval history persists per CPU. `next_timer_ns` and `bucket` are saved so `menu_update()` can compare measured residency to the prediction.

## Dependencies And Integration Points

It depends on tick/nohz sleep length APIs, cpuidle accounting, PM QoS latency, scheduler tick wakeup detection, and shared governor thresholds in `gov.h`.

## Risks And Test Signals

Risks include bad predictions with irregular interrupts, shallow-state lock-in when the tick is stopped, fallback to polling under tight latency, and arithmetic corner cases in variance/factor updates. Test with periodic timers, interrupt-heavy workloads, nohz enabled/disabled, PM QoS constraints, and residency/miss counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/menu.c -->
