<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/writer_unix.go -->
# sources/cloud-native/containerd/plugins/content/local/writer_unix.go

## Purpose
Unix directory sync helper for durable blob commit.

## Important APIs, Types, And Functions
syncDir opens a directory and calls Sync.

## Control Flow
Commit calls syncDir after renaming blob into place.

## State And Persistence
Forces directory metadata to storage on Unix filesystems.

## Dependencies And Integration Points
Used by writer.go.

## Risks And Edge Cases
Directory sync can fail on filesystems that do not support fsync on directories.

## Test Signals
Covered indirectly by writer commit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/writer_unix.go -->
