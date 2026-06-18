<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts_unix.go -->
# sources/cloud-native/moby/daemon/pkg/opts/hosts_unix.go

## Purpose
Provides Unix/non-Windows defaults for daemon host parsing.

## Important APIs, Types, And Functions
`DefaultHTTPHost` is `localhost`. `DefaultHost` is `unix://` plus `DefaultUnixSocket`.

## Control Flow
There is no executable flow; build tags select this file on non-Windows platforms.

## State, Dependencies, And Integration Points
No state. The constants are consumed by `hosts.go`, daemon defaults, and tests that normalize TCP and Unix listener addresses.

## Risks And Test Signals
The behavior differs from Windows, especially default listener transport and TCP host. `hosts_test.go` indirectly validates the constants in expected output strings under non-Windows builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts_unix.go -->
