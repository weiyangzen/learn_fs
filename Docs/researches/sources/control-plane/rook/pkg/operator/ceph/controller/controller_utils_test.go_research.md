# sources/control-plane/rook/pkg/operator/ceph/controller/controller_utils_test.go

## Purpose
`controller_utils_test.go` verifies global operator setting parsers and CephCluster readiness gating.

## Important APIs, Types, and Functions
`CreateTestClusterFromStatusDetails()` builds health-status fixtures. Tests cover `canIgnoreHealthErrStatusInReconcile`, `SetCephCommandsTimeout`, `SetAllowLoopDevices`, `SetEnforceHostNetwork`, `SetRevisionHistoryLimit`, `IsReadyToReconcile`, and `SetObcAllowAdditionalConfigFields`/`ObcAdditionalConfigKeyIsAllowed`.

## Control Flow, State, and Persistence
Tests set and unset environment variables to drive operator settings and mutate package-level globals. `TestIsReadyToReconcile` uses controller-runtime fake clients with CephCluster objects in different deletion/cleanup states. No persistent cluster resources are created outside the fake client.

## Dependencies and Integration Points
The tests depend on Ceph API scheme registration, controller-runtime fake client, `exec.CephCommandsTimeout`, Kubernetes metav1 deletion timestamps, and the process environment.

## Risks
Because tested functions mutate globals, test isolation depends on careful env cleanup and value resets. Some subtests use shared variables and global scheme, which can hide order-sensitive issues. Readiness tests do not cover `HEALTH_OK`, `HEALTH_WARN`, initialization error messages, or ignored health-error details even though those branches are important.

## Test Signals
Signals are strong for parsing defaults and invalid inputs. Missing signals include concurrent setting changes, panic recovery, multi-cluster namespace behavior, and full health-status readiness outcomes.
