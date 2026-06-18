<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_windows.go -->
# sources/cloud-native/containerd/pkg/shim/util_windows.go

## Purpose
Windows shim utility implementation for named-pipe dialing and compatibility no-ops.

## Important APIs, Types, And Functions
Defines shimBinaryFormat .exe, nil getSysProcAttr, AnonDialer, AnonReconnectDialer, RemoveSocket, writeSocketDir, and cleanupSockets.

## Control Flow
AnonDialer retries pipe-not-found for up to five seconds for newly starting shims. AnonReconnectDialer fails fast on missing pipes for daemon restart scanning. cleanup reads address but RemoveSocket is a no-op.

## State And Persistence
No filesystem socket state is removed. Named pipe connection state is external to the process.

## Dependencies And Integration Points
Depends on go-winio and Windows build tags. Used by shim Command/Connect paths on Windows.

## Risks And Edge Cases
Retry timing is tuned around Windows SCM startup deadlines and shim startup races. RemoveSocket being no-op means pipe cleanup is owned elsewhere.

## Test Signals
No local tests; behavior is integration/platform-specific.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_windows.go -->
