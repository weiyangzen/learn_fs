# sources/cloud-native/containers-storage/drivers/btrfs/dummy_unsupported.go

## Purpose
`dummy_unsupported.go` keeps the `btrfs` package buildable on non-Linux or non-cgo targets where the real Btrfs driver is excluded.

## Important APIs, Types, And Functions
The file contains only the package declaration under the `!linux || !cgo` build constraint.

## Control Flow
There is no runtime control flow. Build tags select this file when `btrfs.go` and version files are unavailable.

## State And Persistence
No state is defined or persisted.

## Dependencies And Integration Points
It integrates at the package/build level only, allowing imports of `drivers/btrfs` to compile on unsupported platforms.

## Risks
No driver registration occurs on unsupported platforms, so callers must handle driver unavailability through graphdriver selection errors.

## Test Signals
Build-only signal on unsupported platforms; no unit tests are attached.
