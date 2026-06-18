<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/diff_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/diff_fuzz_test.go

## Purpose
Fuzzes diff apply and compare operations.

## Important APIs, Types, And Functions
Defines `FuzzDiffApply` and `FuzzDiffCompare`.

## Control Flow
Builds fuzzed mount/content/archive inputs and invokes diff service paths looking for crashes.

## State And Persistence
Uses temp directories/content stores; may create snapshot-like filesystem trees during tests.

## Dependencies And Integration Points
containerd diff/archive/mount helpers and fuzz headers.

## Risks And Test Signals
Requires OS filesystem behavior; malformed inputs are expected. Fuzz signal is panic resistance. Source size reviewed: 104 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/diff_fuzz_test.go -->
