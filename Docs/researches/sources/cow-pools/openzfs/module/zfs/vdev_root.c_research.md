# File Research: sources/cow-pools/openzfs/module/zfs/vdev_root.c

## Purpose
Defines the OpenZFS root vdev operations. The root vdev is a synthetic container for top-level vdevs and is responsible for opening/closing children and computing pool-level health from child open/state errors.

## Main Responsibilities
- Counts concrete, non-log, non-hole, non-indirect top-level vdevs as core data-bearing devices.
- Opens every child vdev during root open.
- Determines whether child open failures exceed the pool's allowed missing top-level-vdev budget.
- Reports root vdev state as healthy, degraded, or cannot-open based on faulted/degraded child counts.
- Exposes `vdev_root_ops` for the root vdev type.

## Key Data And State
- No private persistent state is introduced by this file.
- `vdev_root_core_tvds()` excludes holes, log vdevs, and indirect vdevs from the root failure budget.
- `too_many_errors()` compares current errors with `spa_missing_tvds_allowed()`, while always failing when every core top-level vdev is missing.

## Important Functions
- `vdev_root_core_tvds()`: returns the number of core top-level vdevs relevant to missing-device tolerance.
- `too_many_errors()`: central policy helper for deciding whether the root vdev must fail.
- `vdev_root_open()`: opens children, records missing top-level count during load, initializes reported sizes/shifts to zero, and returns failure if too many core devices failed.
- `vdev_root_close()`: closes all child vdevs.
- `vdev_root_state_change()`: maps child fault/degrade counts to root vdev state.
- `vdev_root_ops`: operation vector with root-specific open/close/state handlers and no I/O start/done handlers.

## Control Flow Notes
- The root vdev itself does not issue I/O and does not contribute allocation geometry.
- During pool load, root open records missing top-level vdev count in the SPA so import policies can account for it.
- Indirect vdevs are ignored for root missing-device tolerance because they no longer contain directly allocated pool data.

## Error Handling And Invariants
- A root vdev with no children fails with `VDEV_AUX_BAD_LABEL` and `EINVAL`.
- If too many core top-level children fail to open, root state is `VDEV_AUX_NO_REPLICAS`.
- Assertions ensure the counted error total does not exceed the core top-level vdev count.

## Dependencies
Depends on the vdev operation framework, SPA load state and missing-vdev policy, child vdev open/close helpers, and indirect vdev operation identity.

## Research Notes
This file is small but policy-significant: its exclusions for log, hole, and indirect vdevs affect import behavior and pool health classification after device removal or missing-device imports.
