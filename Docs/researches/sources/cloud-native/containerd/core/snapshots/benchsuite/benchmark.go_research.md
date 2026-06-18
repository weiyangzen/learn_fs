# sources/cloud-native/containerd/core/snapshots/benchsuite/benchmark.go

## Purpose
Declares the Linux-only `benchsuite` package companion file for snapshotter benchmarks.

## APIs, Flow, State, Dependencies, Risks, And Tests
The file contains only package declaration and license under `//go:build linux`. There are no functions, types, imports, state changes, or persistence.

It integrates with `benchmark_test.go` by establishing the package on Linux. The only risk is accidental build-tag/package drift. Test signal is successful Linux test package compilation.
