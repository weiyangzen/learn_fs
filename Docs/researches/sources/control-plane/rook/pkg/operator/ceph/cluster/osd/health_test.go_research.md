# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/health_test.go

## Purpose
This file tests OSD health monitoring behavior in `health.go`: deletion of safe-to-destroy out OSDs, monitor lifecycle setup, interval selection, and periodic require-osd-release convergence logic.

## Important APIs, Types, and Helpers
`TestOSDHealthCheck` uses a mock Ceph executor returning an OSD dump with osd.0 down/out and safe-to-destroy output. It creates a fake Deployment with `ceph-osd-id=0`, runs `checkOSDDump()`, and asserts the Deployment is deleted. `TestMonitorStart` creates a `sync.Map` entry with `ClusterHealth`, starts the monitor goroutine, and cancels the internal context. `TestNewOSDHealthMonitor` compares default and custom interval monitor structs. `TestCheckRequireOSDRelease` uses subtests with mock executor responses for `ceph versions` and `ceph osd require-osd-release`.

## Control Flow Covered
The deletion test covers status parsing, safe-to-destroy command invocation, and Kubernetes Deployment deletion. It uses the default zero creation timestamp, which is older than the one-hour grace time, so deletion proceeds. The require-release tests cover the happy path where a single OSD version maps to `squid`, the cached-release skip path, mixed-version early return, version query failure, and enable failure without cache update.

## State and Persistence Behavior
Fake Kubernetes Deployments represent persistent OSD daemons. The mock executor count confirms Ceph calls are made. `lastRequireOSDRelease` is inspected as in-memory monitor state. The tests do not persist Ceph state; command success is inferred from executor calls and cache changes.

## Dependencies and Integration Points
The file depends on Rook fake clientsets, `exectest.MockExecutor`, Ceph client command wrappers, Kubernetes Deployment labels, and controller health structs. It provides integration-like coverage across monitor logic, Kubernetes helpers, and Ceph command parsing.

## Risks and Gaps
The grace-period branch is only covered through an already-old timestamp; there is no test that a newly created Deployment is retained. `Start()` is only smoke-tested and does not assert map deletion after cancel. Error handling in `checkOSDDump()` for malformed OSD IDs or command failures is not deeply asserted.

## Test Signals
The tests give strong signals for destructive behavior and require-release idempotency. They are especially valuable because health monitoring runs outside the main reconcile loop and can delete Kubernetes objects asynchronously.
