# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/orchestrator.go

## Purpose

This file configures Ceph's manager orchestrator integration so Rook can be selected as the Ceph orchestrator backend. It is a small bridge between Rook manager reconciliation and Ceph's `mgr/orchestrator` command surface.

## Important APIs and Control Flow

`configureOrchestratorModules()` first enables the Ceph manager module named `rook` with `client.MgrEnableModule(..., force=true)`. It then calls `setRookOrchestratorBackend()`.

`setRookOrchestratorBackend()` executes `ceph orch set backend rook` through `client.NewCephCommand(...).RunWithTimeout(exec.CephCommandsTimeout)` inside `client.ExecuteCephCommandWithRetry`. The retry count is five and the wait interval is `orchestratorInitWaitTime`, defaulting to five seconds. This exists because enabling a mgr module does not mean the module is immediately ready to accept orchestrator commands.

## State and Persistence

No Kubernetes object is persisted by this file. The durable state is inside Ceph's mgr module configuration: the rook module is enabled and the orchestrator backend is set to `rook`. Failures are wrapped with context so upper reconciliation can report whether module enablement or backend selection failed.

## Dependencies and Integration Points

The code depends on `pkg/daemon/ceph/client` for mgr module and Ceph command execution, `pkg/util/exec` for command timeout, and the `Cluster`'s `context`/`clusterInfo`. It integrates with manager startup after the manager daemon is available.

## Risks and Test Signals

The main risk is timing: a newly enabled mgr module may reject orchestrator commands until initialized. The retry wrapper mitigates that. Another risk is that Ceph command semantics or module names change. `orchestrator_test.go` explicitly exercises retry behavior and error wrapping around simulated command failures.
