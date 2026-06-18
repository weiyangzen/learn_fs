<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/socket_windows.go -->
# sources/cloud-native/containerd/pkg/sys/socket_windows.go

## Purpose
Windows local listener helper backed by named pipes.

## Important APIs, Types, And Functions
GetLocalListener calls winio.ListenPipe and ignores uid/gid parameters.

## Control Flow
Single pass-through to Windows named pipe listener creation.

## State And Persistence
Creates a named pipe endpoint managed by Windows.

## Dependencies And Integration Points
Used by daemon service listener setup on Windows.

## Risks And Edge Cases
ACL/ownership are not applied here; security depends on winio defaults or caller path configuration.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/socket_windows.go -->
