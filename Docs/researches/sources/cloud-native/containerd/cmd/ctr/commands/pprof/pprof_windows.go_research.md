<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof_windows.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof_windows.go

## Purpose
Windows implementation of the pprof dialer using named pipe transport.

## Important APIs, Types, And Functions
Implements `(*pprofDialer).pprofDial` and `getPProfDialer` with `npipe` protocol.

## Control Flow
The dialer stores `npipe` plus address and calls `winio.DialPipe` with no timeout when net/http needs a connection.

## State And Persistence
No persistence; opens a transient named-pipe connection.

## Dependencies And Integration Points
Depends on Microsoft go-winio and is selected by the `windows` build tag.

## Risks And Test Signals
A nil timeout means connection behavior is delegated to named-pipe dialing. Tested only through Windows pprof integration paths. Source size reviewed: 31 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof_windows.go -->
