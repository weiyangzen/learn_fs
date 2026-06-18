<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts_windows.go -->
# sources/cloud-native/moby/daemon/pkg/opts/hosts_windows.go

## Purpose
Provides Windows-specific daemon host defaults and documents the historical reason for using `127.0.0.1` instead of `localhost` for TCP defaults.

## Important APIs, Types, And Functions
`DefaultHTTPHost` is `127.0.0.1`. `DefaultHost` is `npipe://` plus `DefaultNamedPipe`.

## Control Flow
No functions execute. The Go build selects this file on Windows.

## State, Dependencies, And Integration Points
No state. These constants affect `ParseDaemonHost`, daemon startup defaults, and Windows client/daemon local connection behavior.

## Risks And Test Signals
The long comment records a DNS delay workaround; changing the constant can reintroduce local Windows connection latency. Host parser tests validate expected normalization under Windows builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts_windows.go -->
