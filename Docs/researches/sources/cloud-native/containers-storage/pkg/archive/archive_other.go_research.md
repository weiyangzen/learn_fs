# sources/cloud-native/containers-storage/pkg/archive/archive_other.go

## Purpose
This non-Linux platform file provides fallback whiteout behavior for archive operations.

## Important APIs
`GetWhiteoutConverter(format, data)` always returns nil on non-Linux builds, meaning no platform-specific whiteout conversion is applied.

## Control Flow and State
There is no state and no conversion. Tar creation and extraction proceed with the generic AUFS-style names or ordinary file entries handled by `archive.go`.

## Dependencies and Integration Points
The file is selected by `//go:build !linux` and shares the same function name as `archive_linux.go`, allowing generic code to call `GetWhiteoutConverter` unconditionally.

## Risks and Edge Cases
Non-Linux platforms do not get overlay whiteout conversion. Callers using overlay-specific formats on non-Linux will effectively get no converter, so tests and features must account for platform capability.

## Test Signals
No direct test in this subset. The behavior is primarily a build-time fallback.
