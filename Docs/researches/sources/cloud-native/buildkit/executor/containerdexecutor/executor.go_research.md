# Research: sources/cloud-native/buildkit/executor/containerdexecutor/executor.go

## Purpose
Containerd-backed BuildKit executor implementation.

## Important APIs, Types, and Functions
`containerdExecutor`, `ExecutorOptions`, `RuntimeInfo`, `containerState`, `OnCreateRuntimer`, and methods `New`, `Run`, `Exec`, `runProcess`.

## Control Flow
`Run` validates IDs, tracks running state, selects network/proxy provider, prepares rootfs/DNS/hosts, ensures CWD, injects proxy env/CA, creates OCI spec/container/task, runs the task, handles signals/resizes, maps exit codes, and deletes task/container. `Exec` waits for the task and starts an exec process.

## State and Persistence
In-memory `running` map plus transient files under executor root and containerd container/task state.

## Dependencies and Integration Points
Depends on containerd client/task/cio, BuildKit executor/OCI/network/CDI helpers, identity, OpenTelemetry, and gateway exit errors. Selected by workers using containerd as runtime backend.

## Risks and Edge Cases
Cleanup ordering, cancellation/kill semantics, missing IO streams, and proxy CA/rootfs assumptions are high-risk.

## Test Signals
`executor_test.go` asserts interface compatibility; deeper behavior is integration-tested.
