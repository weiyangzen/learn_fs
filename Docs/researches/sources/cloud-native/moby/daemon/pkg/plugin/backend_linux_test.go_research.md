<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/backend_linux_test.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/backend_linux_test.go

## Purpose
Tests `atomicRemoveAll`, the plugin directory removal helper used by Linux backend removal and cleanup recovery.

## Important APIs, Types, And Functions
`TestAtomicRemoveAllNormal`, `TestAtomicRemoveAllAlreadyExists`, and `TestAtomicRemoveAllNotExist` exercise rename-and-remove behavior.

## Control Flow
Each test creates temporary directories, calls `atomicRemoveAll`, then asserts both the original directory and `-removing` path are absent.

## State, Dependencies, And Integration Points
State is limited to temporary directories. It validates the cleanup pattern used by plugin removal and daemon reload cleanup of interrupted removals.

## Risks And Test Signals
The tests do not simulate permission errors, mount points, or rollback on failed `EnsureRemoveAll`, but they cover normal, pre-existing marker, and missing-origin cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/backend_linux_test.go -->
