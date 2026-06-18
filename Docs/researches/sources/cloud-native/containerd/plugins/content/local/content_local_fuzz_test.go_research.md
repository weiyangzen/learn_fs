<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/content_local_fuzz_test.go -->
# sources/cloud-native/containerd/plugins/content/local/content_local_fuzz_test.go

## Purpose
Fuzzes resumable local content writer behavior over arbitrary byte slices.

## Important APIs, Types, And Functions
FuzzContentStoreWriter and checkCopyFuzz.

## Control Flow
The fuzz target opens a store, creates and closes a writer, reopens it with same ref, copies fuzz data, computes expected digest, and commits.

## State And Persistence
Uses temp content store directories and ingest/blob files cleaned by test tempdir.

## Dependencies And Integration Points
Exercises NewStore, Writer resume, Write, and Commit for arbitrary data.

## Risks And Edge Cases
Commit errors are tolerated for some fuzz inputs/conditions, so the target primarily catches panics and copy failures.

## Test Signals
Fuzz coverage for writer resume and digest commit path.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/content_local_fuzz_test.go -->
