# sources/cloud-native/containerd/core/snapshots/storage/metastore_bench_test.go

## Purpose
Defines generic benchmarks for snapshot metadata stores.

## APIs, Flow, State, Dependencies, Risks, And Tests
`Benchmarks` registers sub-benchmarks for stat active, stat committed, create active, remove, commit, get active parent chain, writable transaction open/close, and read transaction open/close. `makeBench` creates a metastore, opens one writable transaction for repeated operation benchmarks, and runs the benchmark function. Helper benchmarks create and remove snapshots around timed sections as needed. `getActiveBenchmark` builds a 10-deep committed parent chain and repeatedly resolves an active snapshot's parent IDs.

State is temporary database files and snapshot metadata inside benchmark transactions. Dependencies include testing, context, fmt, and snapshots types.

Risks include long-lived write transactions not representing real concurrent workloads, setup leakage into timing if `StopTimer` is missed, and benchmark keys reused intentionally with cleanup. Signals are ns/op for metadata operations and transaction overhead across implementations.
