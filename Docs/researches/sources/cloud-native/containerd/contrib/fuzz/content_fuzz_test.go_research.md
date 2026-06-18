<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/content_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/content_fuzz_test.go

## Purpose
Fuzzes content store walking and archive export with generated blob stores.

## Important APIs, Types, And Functions
Defines blob validation/population helpers plus `FuzzCSWalk` and `FuzzArchiveExport`.

## Control Flow
Generates digest-to-bytes maps, writes blobs to local content store, verifies paths, walks content, and attempts archive export.

## State And Persistence
Uses temp local content stores and blobs.

## Dependencies And Integration Points
containerd content/local store, digest validation, archive export.

## Risks And Test Signals
Digest/path checks defend against malformed content paths; semantic image validity is limited. Fuzzing provides crash/regression signal. Source size reviewed: 163 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/content_fuzz_test.go -->
