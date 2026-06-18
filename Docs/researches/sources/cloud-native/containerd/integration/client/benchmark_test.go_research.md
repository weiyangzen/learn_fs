# sources/cloud-native/containerd/integration/client/benchmark_test.go

## Purpose
This file benchmarks client container creation and task start paths against a running containerd.

## Important APIs, Types, and Functions
`BenchmarkContainerCreate` times `NewContainer` with a pre-generated spec and new snapshots. `BenchmarkContainerStart` pre-creates containers, then times `NewTask` and `Start`.

## Control Flow
Both benchmarks create a client, resolve the test image, generate an OCI spec with `withTrue`, track containers for cleanup, reset timers around the target operation, and stop timers before cleanup.

## State and Persistence
Benchmarks create snapshots, containers, and tasks in the test namespace and clean them with snapshot cleanup.

## Dependencies and Integration Points
Uses the integration client harness, `containerd/client`, OCI spec generation, and test images.

## Risks
Benchmark results depend on daemon state, snapshotter, host performance, and image availability. Cleanup errors are reported after timing.

## Test Signals
Performance-oriented signal for container creation and task start overhead.
