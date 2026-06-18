<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/gov.h -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/governors/gov.h

## Purpose

`gov.h` defines constants shared by cpuidle governors that reason about short residencies and safe timer ranges.

## Important APIs, Types, And Functions

`RESIDENCY_THRESHOLD_NS` is 15 microseconds and is used to decide when checking the closest timer is worth the overhead. `SAFE_TIMER_RANGE_NS` is two scheduler tick periods and marks a range where the nearest timer is close enough that extra selection adjustment is unnecessary.

## Control Flow

There is no executable control flow. `menu` and `teo` include these thresholds in their selection heuristics.

## State And Persistence Behavior

The constants are compile-time only and store no state.

## Dependencies And Integration Points

It depends on `NSEC_PER_USEC` and `TICK_NSEC` definitions from included kernel headers in the consuming files.

## Risks And Test Signals

Risks are heuristic regressions: changing thresholds can alter tick-stopping behavior and shallow/deep state selection. Test through idle microbenchmarks, timer-heavy workloads, and power/latency comparisons for menu and TEO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/gov.h -->
