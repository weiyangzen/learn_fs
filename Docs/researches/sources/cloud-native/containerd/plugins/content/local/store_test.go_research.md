<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_test.go -->
# sources/cloud-native/containerd/plugins/content/local/store_test.go

## Purpose
Comprehensive tests and benchmarks for the local content store.

## Important APIs, Types, And Functions
memoryLabelStore, TestContent, TestContentRootDir, TestInvalidPermissionRootDir, TestContentWriter, TestWalkBlobs, BenchmarkIngests, helper generators, TestWriterTruncateRecoversFromIncompleteWrite, TestWriteReadEmptyFileTimestamp.

## Control Flow
Tests run content testsuite, create stores under temp dirs, write random blobs with sha256/sha512, resume writers, assert duplicate commit errors, verify readonly permissions and fsverity when available, walk blobs, and recover from truncated ingest.

## State And Persistence
Creates temp content store roots, ingest directories, committed blobs, and optional immutable directory state via chattr in a root-only test.

## Dependencies And Integration Points
Exercises store.go, writer.go, readerat.go, lock behavior via Writer, fsverity integration, and content package helpers.

## Risks And Edge Cases
Some tests are root/tool/fsverity dependent. Benchmarks generate random blob maps for two algorithms, potentially doubling blob count.

## Test Signals
High-signal direct coverage for store correctness and persistence layout.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_test.go -->
