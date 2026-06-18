<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/writer_windows.go -->
# sources/cloud-native/containerd/plugins/content/local/writer_windows.go

## Purpose
Windows no-op directory sync helper.

## Important APIs, Types, And Functions
syncDir returns nil.

## Control Flow
Commit calls it but no operation occurs.

## State And Persistence
No state or persistence beyond normal file operations.

## Dependencies And Integration Points
Platform companion for writer.go.

## Risks And Edge Cases
Windows lacks the same directory sync support, so crash-durability differs from Unix.

## Test Signals
Indirect Windows content tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/writer_windows.go -->
