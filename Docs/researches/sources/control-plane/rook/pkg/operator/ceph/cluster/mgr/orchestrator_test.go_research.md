# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/orchestrator_test.go

## Purpose

This file tests Rook's Ceph manager orchestrator-module setup, especially the retry path for selecting the `rook` orchestrator backend after enabling the manager module.

## Important APIs and Test Flow

`TestOrchestratorModules` installs a mock executor with two command paths. `MockExecuteCommandWithOutput` recognizes `ceph mgr module enable rook` and records that the rook module was enabled. `MockExecuteCommandWithTimeout` recognizes `ceph orch set backend rook`, fails the first five calls, then succeeds.

The test creates a minimal `Cluster` with `ClusterInfo`, `clusterd.Context`, a Squid Ceph version, and an overridden `exitCode` hook. It sets `orchestratorInitWaitTime = 0` to avoid real sleeps. The first call to `configureOrchestratorModules()` is expected to fail because the retry budget is exhausted. A direct call to `setRookOrchestratorBackend()` then succeeds once the mock's error counter has reached the success threshold. Later calls verify the success path remains clean once the backend command no longer fails.

## State, Dependencies, and Integration

State is entirely in local booleans and the `backendErrorCount` counter. The test depends on Rook's `exectest.MockExecutor`, Ceph client command wrappers, and the global `exec.CephCommandsTimeout`.

## Risks and Test Signals

The test is a good signal for backend command retry semantics and exact Ceph CLI arguments. It also has global-state risk: it modifies `orchestratorInitWaitTime` and `exec.CephCommandsTimeout` without restoring them. Changes to retry count, command construction, or module setup order will be caught by the command assertions.
