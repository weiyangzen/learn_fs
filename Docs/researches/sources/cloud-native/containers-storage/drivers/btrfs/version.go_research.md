# sources/cloud-native/containers-storage/drivers/btrfs/version.go

## Purpose
`version.go` exposes Btrfs build and library version information from btrfs-progs headers for driver status output.

## Important APIs, Types, And Functions
The cgo preamble includes `btrfs/version.h` and defines fallback `BTRFS_LIB_VERSION` and `BTRFS_BUILD_VERSION` values when headers omit them. `btrfsBuildVersion()` returns the build version string; `btrfsLibVersion()` returns the integer library version.

## Control Flow
`Driver.Status` calls these helpers and includes non-placeholder values in the diagnostic status list.

## State And Persistence
The values are compile-time constants from headers. No persistent or mutable runtime state exists.

## Dependencies And Integration Points
The file requires Linux+cgo and Btrfs development headers. It feeds the graphdriver status API.

## Risks
Header compatibility varies by btrfs-progs version, hence the fallback macros. Incorrect header values would affect diagnostics but not layer data directly.

## Test Signals
`version_test.go` asserts the library version is positive on supported builds.
