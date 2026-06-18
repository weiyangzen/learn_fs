<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_linux.go -->
# sources/cloud-native/containerd/pkg/shim/shim_linux.go

## Purpose
Linux shim server platform behavior.

## Important APIs, Types, And Functions
newServer appends UnixSocketRequireSameUser handshaker; subreaper calls reaper.SetSubreaper(1).

## Control Flow
Shared run calls subreaper before serving unless disabled and creates a ttrpc server with same-user socket authentication.

## State And Persistence
Kernel subreaper flag is process state; no filesystem persistence.

## Dependencies And Integration Points
Depends on pkg/sys/reaper and ttrpc.

## Risks And Edge Cases
Subreaper setup requires prctl support; same-user handshake affects clients over Unix sockets.

## Test Signals
Indirectly covered through shim lifecycle and reaper tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_linux.go -->
