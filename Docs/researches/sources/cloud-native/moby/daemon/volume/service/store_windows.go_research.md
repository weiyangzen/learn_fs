# sources/cloud-native/moby/daemon/volume/service/store_windows.go

## Purpose
Windows volume-name normalization hook.

## Important APIs, Types, And Functions
`normalizeVolumeName(name string) string` lowercases names.

## Control Flow
The function delegates to `strings.ToLower`.

## State And Persistence
No state, but normalized names become lock keys, cache keys, and metadata keys.

## Dependencies And Integration Points
Used by `VolumeStore` operations to make Windows volume names case-insensitive.

## Risks
Lowercasing can collapse distinct names if external drivers preserve case differently. Metadata compatibility depends on consistent normalization.

## Test Signals
Windows store behavior is indirectly covered by platform test runs; no direct test in this subset.
