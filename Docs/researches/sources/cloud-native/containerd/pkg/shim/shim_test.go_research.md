<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_test.go -->
# sources/cloud-native/containerd/pkg/shim/shim_test.go

## Purpose
Unit tests for shim runtime tuning and context option storage.

## Important APIs, Types, And Functions
Tests setRuntime behavior with and without GOMAXPROCS and OptsKey context value retrieval.

## Control Flow
Each test mutates env/context, invokes helper, and asserts GOMAXPROCS or Opts.Debug.

## State And Persistence
Mutates process GOMAXPROCS and restores in the empty-env test; no persistence.

## Dependencies And Integration Points
Depends on runtime and testing. Exercises shim.go helpers.

## Risks And Edge Cases
The non-empty GOMAXPROCS test assumes runtime.NumCPU matches the runtime-set default in that environment.

## Test Signals
Direct coverage for setRuntime and Opts context use.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_test.go -->
