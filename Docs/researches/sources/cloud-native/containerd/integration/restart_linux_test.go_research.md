# sources/cloud-native/containerd/integration/restart_linux_test.go

## Purpose

`restart_linux_test.go` adds Linux restart scenarios around sandbox recovery and large sandbox reload counts.

## Important APIs, Types, and Functions

- `TestContainerdRestartSandboxRecover` verifies ready, stopped, and unknown/failpoint sandbox states after a daemon restart.
- `TestReload100Pods` starts a separate daemon, creates 100 host-network pods, restarts the daemon, and ensures it becomes ready with that state.

## Control Flow

The sandbox recovery test creates a ready sandbox, a stopped sandbox, and a sandbox whose shim `Create` is delayed while the daemon is restarted. After restart it lists sandboxes, validates expected states, and removes them. The reload test uses the release-upgrade process helper to run an isolated daemon, creates many pods through CRI, stops and restarts the process, and checks readiness.

## State and Persistence Behavior

Both tests depend on persisted CRI sandbox metadata and runtime state across daemon restarts. `TestReload100Pods` also checks that volatile runtime state under the daemon work directory can be removed at cleanup without leaks.

## Dependencies and Integration Points

The file uses failpoint annotations from `sandbox_run_rollback_test.go`, process helpers from `release_upgrade_linux_test.go`, CRI runtime helpers, Linux signals, and filesystem cleanup.

## Risks and Edge Cases

The unknown-state path races daemon shutdown against shim creation delay. The 100-pod reload case stresses startup/recovery scaling and cleanup of many sandbox entries. Both tests can expose mount/state leaks if cleanup is incomplete.

## Test Signals

Failures indicate regressions in sandbox recovery state classification, failpoint rollback, daemon restart readiness, or large-pod reload behavior.
