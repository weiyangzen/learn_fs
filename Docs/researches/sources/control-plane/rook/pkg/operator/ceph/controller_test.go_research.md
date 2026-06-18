# sources/control-plane/rook/pkg/operator/ceph/controller_test.go

## Purpose
This test file validates the top-level Ceph operator configuration reconciler behavior around operator settings. It exercises `ReconcileConfig.Reconcile` through fake Kubernetes clients and confirms that environment/config-map-driven settings are applied without requeueing.

## Important APIs, Types, and Functions
The only test entry point is `TestOperatorController`. It builds `clusterd.Context` values with fake core and Rook clientsets, uses controller-runtime fake clients with either the Rook scheme or the client-go scheme, and constructs `ReconcileConfig` with `controller.OperatorConfig`. It asserts effects on `exec.CephCommandsTimeout`, `controller.LoopDevicesAllowed()`, and discovery daemonset creation.

## Control Flow, State, and Persistence
Each subtest creates an isolated fake clientset and reconciler, then calls `Reconcile` with a request targeting `rook-ceph-operator-config` in `rook-ceph`. State is process-local except for environment variables like `ROOK_CEPH_COMMANDS_TIMEOUT_SECONDS`, `ROOK_ENABLE_DISCOVERY_DAEMON`, and `ROOK_CEPH_ALLOW_LOOP_DEVICES`, plus fake API objects created during reconciliation.

## Dependencies and Integration Points
The test integrates top-level operator config reconciliation with `pkg/operator/ceph/controller`, `pkg/util/exec`, discovery daemon handling, and Kubernetes version probing through `test.SetFakeKubernetesVersion`.

## Risks
Several subtests mutate package globals and environment variables, so test isolation depends on `t.Setenv` or explicit cleanup. The fake schemes differ by case, which is useful coverage but can mask scheme-registration dependencies in real managers.

## Test Signals
Coverage confirms normal reconciliation, command timeout from env/config, discovery daemon enablement, and loop-device allowance. It does not validate failure paths or real config-map content because fake clients often start empty.
