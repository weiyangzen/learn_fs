<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_windows.go -->
# sources/cloud-native/containerd/plugins/content/local/store_windows.go

## Purpose
Windows access-time fallback for local content store.

## Important APIs, Types, And Functions
getATime returns FileInfo.ModTime.

## Control Flow
Called by store.info on Windows.

## State And Persistence
No state.

## Dependencies And Integration Points
Keeps store.go portable on Windows where Unix atime fields are unavailable.

## Risks And Edge Cases
UpdatedAt is less precise semantically because it mirrors modification time.

## Test Signals
Indirect Windows content tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_windows.go -->
