# sources/control-plane/rook/pkg/operator/ceph/cluster/cephstatus_test.go

Purpose: tests Ceph cluster status conversion, status checker construction, insecure global ID health behavior, and stuck-pod cleanup helpers.

Important APIs/types/functions: `TestCephStatus()` covers `toCustomResourceStatus()` and `formatTime()`. `TestNewCephStatusChecker()` covers interval/external construction. `TestConfigureHealthSettings()` tests `configureHealthSettings()`. `TestForceDeleteStuckRookPodsOnNotReadyNodes()` tests force deletion behavior. `TestGetRookPodsOnNode()` tests Rook pod label filtering.

Control flow: status conversion tests mutate current/new status across health and capacity scenarios. Health-setting tests use a mocked executor to detect whether Ceph config set is attempted. Stuck-pod tests create fake nodes/pods, mark nodes NotReady, and verify only terminating matching pods are deleted. Pod label tests create many app labels and compare sorted expected names.

State and persistence behavior: uses fake Kubernetes clientsets for nodes and pods and in-memory status structs. Some time assertions compare formatted current timestamps rather than fixed clocks.

Dependencies and integration points: relies on Rook operator test clientsets, Ceph client structs, `exectest.MockExecutor`, Kubernetes API objects, and `testify/assert`.

Risks: time-based equality in capacity tests can be fragile around second boundaries. Fake clients may not fully model deletion timestamps and force deletion semantics. `TestNewCephStatusChecker()` does not cover the env var override path.

Test signals: good coverage for conversion edge cases and pod filtering. Periodic `checkCephStatus()` loop and `updateCephStatus()` API persistence are not directly tested.
