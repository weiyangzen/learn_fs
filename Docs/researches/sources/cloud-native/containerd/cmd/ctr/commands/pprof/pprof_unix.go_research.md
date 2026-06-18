<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof_unix.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof_unix.go

## Purpose
Unix implementation of the pprof dialer for containerd debug sockets.

## Important APIs, Types, And Functions
Implements `(*pprofDialer).pprofDial` and `getPProfDialer`.

## Control Flow
`getPProfDialer` records `unix` plus socket address; `pprofDial` ignores the HTTP pseudo host and dials the configured Unix socket.

## State And Persistence
No persistence; opens a transient Unix-domain socket connection.

## Dependencies And Integration Points
Uses Go net package and is selected by `!windows` build tag.

## Risks And Test Signals
Requires the debug socket path to exist and be accessible. Covered indirectly by `ctr pprof` behavior. Source size reviewed: 29 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof_unix.go -->
