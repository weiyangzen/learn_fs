# sources/cloud-native/moby/daemon/volume/service/store_unix.go

## Purpose
Unix volume-name normalization hook.

## Important APIs, Types, And Functions
`normalizeVolumeName(name string) string` returns the input unchanged.

## Control Flow
No conditional logic.

## State And Persistence
No state.

## Dependencies And Integration Points
Called by `VolumeStore.Create`, `Get`, and `CountReferences` before locking/cache access.

## Risks
Unix volume names are case-sensitive. Any future normalization would affect persisted metadata keys and compatibility.

## Test Signals
Store tests on Unix implicitly validate unchanged names.
