<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/stdio/stdio.go -->
# sources/cloud-native/containerd/pkg/stdio/stdio.go

## Purpose
Small value type describing process stdio FIFO paths and terminal mode.

## Important APIs, Types, And Functions
Stdio has Stdin, Stdout, Stderr, Terminal; IsNull reports whether all three paths are empty.

## Control Flow
No control flow beyond IsNull.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by task/process creation and shim IO setup.

## Risks And Edge Cases
Terminal can be true even when paths are empty; IsNull only checks path fields.

## Test Signals
No direct tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/stdio/stdio.go -->
