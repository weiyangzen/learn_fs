# sources/cloud-native/moby/daemon/volume/safepath/safepath.go

## Purpose
Defines the `SafePath` handle returned by platform-specific safe join implementations.

## Important APIs, Types, And Functions
`SafePath` stores the usable path, cleanup callback, mutex, and immutable source base/subpath. Methods are `Close`, `IsValid`, `Path`, and `SourcePath`.

## Control Flow
`Close` serializes with the mutex, logs and no-ops if already closed, clears the path before calling cleanup, and returns cleanup errors. `IsValid` reports whether the path is still usable. `Path` panics on use after close. `SourcePath` returns immutable origin data without locking.

## State And Persistence
State is in-memory path validity plus cleanup-owned platform resources such as bind mounts or Windows handles.

## Dependencies And Integration Points
`MountPoint.Setup` stores safe paths and calls cleanup callbacks; `MountPoint.Cleanup` closes any leftover safe paths.

## Risks
Clearing `path` before cleanup means cleanup failures still invalidate the object, which avoids reuse but can hide leaked resources. `Path` panic is intentional but must not be reached from user-controlled cleanup paths.

## Test Signals
`join_test.go` verifies `Close` invalidates `SafePath`; mount cleanup logs unclosed safe paths.
