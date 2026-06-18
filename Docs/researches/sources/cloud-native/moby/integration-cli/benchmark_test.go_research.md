# sources/cloud-native/moby/integration-cli/benchmark_test.go

## Purpose
Legacy integration benchmarks for daemon/container concurrency and log rotation/follow behavior.

## Important APIs and Types
Defines `DockerBenchmarkSuite`, `BenchmarkConcurrentContainerActions`, and `BenchmarkLogsCLIRotateFollow`.

## Control Flow, State, and Persistence
The suite cleans containers after tests and dumps daemon info on timeout. The concurrent benchmark starts containers, performs parallel daemon actions, and measures end-to-end behavior. The log benchmark creates containers with log rotation settings and follows logs while rotation occurs.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on integration-cli helpers, daemon/client binaries, and a local daemon. It stresses container lifecycle state, log driver persistence, and concurrent API interactions. Risks include benchmark flakiness, timing sensitivity, and environmental daemon load. Benchmark pass and performance trends are the signals rather than unit assertions.
