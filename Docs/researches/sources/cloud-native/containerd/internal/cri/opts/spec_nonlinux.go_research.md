# sources/cloud-native/containerd/internal/cri/opts/spec_nonlinux.go

## Purpose

This non-Linux file supplies no-op or false-returning Linux capability helpers so shared spec code can compile outside Linux.

## Important APIs, Types, and Functions

`isHugetlbControllerPresent`, `SwapControllerAvailable`, and `IsCgroup2UnifiedMode` return false. `WithCDI` returns a no-op spec option.

## Control Flow

All functions return immediately without reading host state or mutating specs.

## State and Persistence Behavior

No state is stored, read, or persisted.

## Dependencies and Integration Points

It is selected by `//go:build !linux` and satisfies references from cross-platform spec code.

## Risks and Edge Cases

CDI and Linux cgroup capabilities are unavailable on non-Linux targets through this path. Callers should avoid assuming these features work outside Linux.

## Test Signals

Non-Linux builds and tests should assert these helpers are harmless no-ops and do not mutate specs.
