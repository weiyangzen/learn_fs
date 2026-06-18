<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup_linux_test.go -->
# sources/cloud-native/containers-storage/internal/dedup/dedup_linux_test.go

## Purpose
This Linux unit test validates the in-memory inode visitation logic used to avoid redundant dedupe work.

## Important APIs, Types, And Functions
`wasVisited` inspects `dedupFiles.visitedInodes` under lock. `TestRecordAndCheckInode` exercises `newDedupFiles` and `recordInode`.

## Control Flow
The test creates a dedup state, verifies an inode is initially unvisited, records it, verifies repeat detection, and checks different inode/device pairs remain unvisited.

## State And Persistence
No filesystem dedupe is performed; state is in-memory.

## Dependencies And Integration Points
The test uses testify assertions and the Linux dedup implementation.

## Risks And Test Signals
It does not test `IoctlFileDedupeRange`, checksum hashing, mmap reads, or walking behavior, but it covers the concurrency-protected visited map basics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup_linux_test.go -->
