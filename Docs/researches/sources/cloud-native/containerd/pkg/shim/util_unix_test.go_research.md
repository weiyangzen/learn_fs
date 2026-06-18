<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_unix_test.go -->
# sources/cloud-native/containerd/pkg/shim/util_unix_test.go

## Purpose
Unix socket creation tests for shim utilities.

## Important APIs, Types, And Functions
TestNewSocket verifies nested-directory and existing-directory filesystem socket cases.

## Control Flow
Each subtest creates a temp dir, calls NewSocket with unix:// path, dials the socket, and closes resources.

## State And Persistence
Creates temporary directories and socket files cleaned at test end.

## Dependencies And Integration Points
Exercises NewSocket and socket.path from util_unix.go.

## Risks And Edge Cases
Uses /tmp explicitly for temp dirs; platform build tag excludes Windows.

## Test Signals
Direct coverage for directory creation and socket connectivity.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_unix_test.go -->
