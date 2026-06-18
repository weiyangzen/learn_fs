# sources/distributed-fs/ceph-client/kernel/sched/sched-pelt.h

## Purpose
Provides generated constants for PELT decay math. It is produced from `Documentation/scheduler/sched-pelt` and included by `pelt.h`/`pelt.c` to avoid recalculating decay coefficients at runtime.

## APIs, Control Flow, and State
The header defines `runnable_avg_yN_inv[]`, `LOAD_AVG_PERIOD`, and `LOAD_AVG_MAX`. There are no functions or branches. `decay_load()` indexes the 32-entry table to apply the inverse decay coefficient for the sub-period remainder after accounting for whole PELT periods. `LOAD_AVG_PERIOD` fixes the half-life relationship at 32 periods, and `LOAD_AVG_MAX` is the maximum geometric-series sum used for normalization.

## Dependencies and Integration Points
Depends only on Linux fixed-width types. It integrates directly with `pelt.c` decay calculations and indirectly with every scheduler user of PELT load/utilization averages. The "do not modify" comment means the authoritative source is the generator/documentation, not manual edits here.

## Risks and Test Signals
Risks include hand-edited constants drifting from the intended PELT curve, table length mismatches with `LOAD_AVG_PERIOD`, and overflow/precision regressions in consumers. Test signals are successful scheduler builds, PELT trace comparisons before/after regeneration, running the documented generator, and workload tests that validate expected utilization half-life and convergence.
