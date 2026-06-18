<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/containerd_import_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/containerd_import_fuzz_test.go

## Purpose
Fuzzes containerd image import command paths.

## Important APIs, Types, And Functions
Defines `fuzzContext` and `FuzzContainerdImport`.

## Control Flow
Creates a namespace context, consumes fuzz bytes as import input/options, and invokes import logic against test stores.

## State And Persistence
Test-scoped temp content/metadata state.

## Dependencies And Integration Points
containerd import code, fuzz headers, namespace helpers.

## Risks And Test Signals
Focuses crash resistance; malformed archives are expected. Fuzz build/test signal. Source size reviewed: 65 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/containerd_import_fuzz_test.go -->
