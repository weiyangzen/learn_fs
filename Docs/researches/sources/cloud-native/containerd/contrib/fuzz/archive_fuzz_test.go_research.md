<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/archive_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/archive_fuzz_test.go

## Purpose
Fuzzes archive apply/import index paths using synthetic tar streams.

## Important APIs, Types, And Functions
Defines `FuzzApply` and `FuzzImportIndex`.

## Control Flow
Consumes fuzz data to build tar entries/blobs and invokes archive apply/import index logic, checking for panics and path issues.

## State And Persistence
Uses test temp directories/content only.

## Dependencies And Integration Points
go-fuzz-headers, archive/tar helpers, containerd archive import code.

## Risks And Test Signals
Generated tar structures may be invalid by design; useful for robustness, not semantic correctness. Source size reviewed: 138 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/archive_fuzz_test.go -->
