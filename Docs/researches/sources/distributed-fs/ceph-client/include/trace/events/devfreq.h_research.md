# sources/distributed-fs/ceph-client/include/trace/events/devfreq.h

## Purpose
`devfreq.h` traces device frequency scaling decisions and monitor samples.

## Important APIs, types, and functions
Events are `devfreq_frequency` and `devfreq_monitor`. They record device name, selected or previous frequency, busy time, total time, and polling interval where applicable.

## Control flow
Devfreq governors/core emit monitor events when sampling device load and frequency events when frequency changes. Print formatting computes load as `100 * busy_time / total_time`, guarding zero total time.

## State and persistence behavior
The header owns no state. Event records snapshot values from `struct devfreq`, including `last_status`, `previous_freq`, and profile polling interval.

## Dependencies and integration points
It depends on `<linux/devfreq.h>` and tracepoints. It integrates with power-management diagnostics, governor tuning, and performance analysis.

## Risks and test signals
Risks include stale `last_status` data if drivers do not update it consistently, zero total-time samples reporting load 0, and event volume from short polling intervals. Test signals are devfreq governor tests that force load changes and frequency transitions with expected load percentages.
