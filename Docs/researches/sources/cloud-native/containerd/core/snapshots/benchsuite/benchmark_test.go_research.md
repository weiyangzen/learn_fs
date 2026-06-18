# sources/cloud-native/containerd/core/snapshots/benchsuite/benchmark_test.go

## Purpose
Provides Linux benchmarks comparing native, overlay, and devmapper snapshotters across repeated layered writes, updates, deletes, prepares, mounts, and commits.

## APIs, Flow, State, Dependencies, Risks, And Tests
Package flags configure root paths and devmapper thin-pool device. `BenchmarkNative`, `BenchmarkOverlay`, and `BenchmarkDeviceMapper` create the selected snapshotter, defer cleanup, and call `benchmarkSnapshotter`. The benchmark builds 16 layers of 1 MiB file operations. For each benchmark iteration and layer, it prepares a snapshot, applies the layer through `mount.WithTempMount`, commits it, and accumulates durations for prepare, write, and commit. Extra timing lines are printed to stdout. `makeApplier`, `applierFn`, and `updateFile` generate random file operations and partial overwrites.

State includes benchmark root directories, snapshotter metadata/data, devmapper pools, and committed layer chains. Dependencies include native/overlay/devmapper snapshotters, mount helpers, fstest, crypto random, flags, atomic counters, logging, and testing.

Risks include destructive cleanup of configured roots, requiring real devmapper setup, accumulating snapshots across `b.N`, non-deterministic random data and time-based seeds, and stdout formatting coupling. Test signals are benchmark completion, per-phase timings, bytes/sec, and cleanup without leaked mounts/devices.
