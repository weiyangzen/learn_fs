# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_quota_goal.py

## Purpose

`damos_quota_goal.py` verifies user-input quota goals dynamically tune effective DAMOS quotas in the expected direction.

## Important APIs, Types, and Functions

It uses `_damon_sysfs.DamosQuotaGoal`, `DamosQuota`, `commit_schemes_quota_goals()`, and `update_schemes_effective_quotas()`. The goal metric is `user_input`.

## Control Flow

The script starts a vaddr stat scheme with one quota goal and reset interval 100 ms. While the workload runs, it cycles current values `[0, 15000, 5000, 18000]`, commits the quota goal, samples effective bytes before and after 0.5 seconds, and checks whether effective quota increased when current value is below target and decreased when above target, except when already at minimum 1 byte.

## State and Persistence Behavior

It mutates the quota goal's `current_value` in sysfs and stores `effective_bytes` in the goal object. It runs a short-lived memory workload.

## Dependencies and Integration Points

It depends on DAMOS quota goal sysfs support and the kernel's effective quota tuner.

## Risks and Edge Cases

The test assumes effective quota changes within 0.5 seconds and that initial effective bytes are nonzero. It is sensitive to tuner implementation details.

## Test Signals

It prints score and effective quota transitions. Failures indicate no change or a change opposite to expectation.
