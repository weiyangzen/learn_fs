<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/teo.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/governors/teo.c

## Purpose

`teo.c` implements the timer-events-oriented cpuidle governor. It emphasizes timer wakeup patterns, using per-state bins of timer "hits" and non-timer "intercepts" to select states and decide whether to stop the scheduler tick.

## Important APIs, Types, And Functions

Per-CPU `struct teo_cpu` stores sleep length, `state_bins`, totals, tick intercepts, short-idle metrics, and tick wakeup state. `teo_update()` decays and updates metrics after each wakeup. `teo_select()` chooses the next state. `teo_find_shallower_state()` caps selections by expected duration. `teo_reflect()` records the entered state and tick wakeup flag.

## Control Flow

On selection, TEO updates metrics for the previous state, finds the deepest enabled state and the latency-constrained state, examines shallower intercept totals to detect early wakeup dominance, applies latency constraints, and avoids reading nohz sleep length when a shallow choice is already clear. If needed, it gets the next timer duration, adjusts for stopped ticks, caps by target residency, and may keep the tick running for short selected states.

## State And Persistence Behavior

Metrics decay by shifting and grow by `PULSE`, so recent behavior dominates while old history persists for smoothing. `sleep_length_ns` is saved to classify the next wakeup. `last_state_idx` is reset after update to avoid duplicate accounting.

## Dependencies And Integration Points

It integrates with tick/nohz, scheduler clock residency, cpuidle accounting, PM QoS latency, and shared thresholds in `gov.h`.

## Risks And Test Signals

Risks include misclassifying timer versus non-timer wakeups, over-stopping or under-stopping the tick, and biased bins when target residencies are close. Test with timer-dominated and interrupt-dominated workloads, nohz-stopped scenarios, PM QoS constraints, polling state timeouts, and deep-state residency counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/teo.c -->
