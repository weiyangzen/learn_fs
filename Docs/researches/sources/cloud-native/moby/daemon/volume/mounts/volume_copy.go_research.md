# sources/cloud-native/moby/daemon/volume/mounts/volume_copy.go

## Purpose
Shared helpers for volume copy mode parsing.

## Important APIs, Types, And Functions
`copyModes` currently maps `nocopy` to false. `copyModeExists` checks mode membership. `getCopyMode(mode string, def bool) (bool, bool)` returns selected copy behavior and whether it was explicitly set.

## Control Flow
`getCopyMode` splits comma-separated mount mode strings, returns the first recognized copy option, or the caller-provided default with `isSet=false`.

## State And Persistence
No state is persisted.

## Dependencies And Integration Points
Linux and Windows/LCOW raw parsers use this to set `mount.VolumeOptions.NoCopy` and `MountPoint.CopyData`.

## Risks
Adding more copy modes must preserve duplicate-mode validation in platform parsers. Because only the first copy option is returned, parser-side counting remains responsible for rejecting duplicates.

## Test Signals
Linux/Windows parser tests cover `nocopy` rejection in volumes-from and copy default behavior through parsed `MountPoint.CopyData`.
