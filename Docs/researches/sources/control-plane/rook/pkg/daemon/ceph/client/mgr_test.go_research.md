# sources/control-plane/rook/pkg/daemon/ceph/client/mgr_test.go

Purpose: validates manager module retry behavior, command construction, balancer control, and balancer compatibility version decisions.

Important test cases: `TestEnableModuleRetries` sets `moduleEnableWaitTime = 0`, forces invalid module failures, and asserts five retries while valid modules and balancer skip do not retry. `TestEnableModule` covers module enable/disable with force and invalid actions. `TestEnableDisableBalancerModule` verifies `balancer on/off`. `TestSetBalancerMode` verifies `balancer mode upmap`. `TestGetMinCompatClientVersion` verifies `read` and `upmap-read` require Ceph major 19 and return `reef`, while `upmap` returns `luminous`.

Control flow and dependencies: tests use `exectest.MockExecutor`, `AdminTestClusterInfo()`, and `cephver.CephVersion`. They mutate `moduleEnableWaitTime`, which speeds tests but is package global.

Risks and coverage gaps: no tests cover `CephMgrMap()`, `CephMgrStat()`, JSON parse failures, `ConfigureBalancerModule()` full flow, set-min-compat command construction, or `mgrSetBalancerMode()` retry failures. Because `moduleEnableWaitTime` is not restored, parallel or subsequent tests could inherit the zero duration.
