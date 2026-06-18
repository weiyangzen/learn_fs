# sources/cloud-native/moby/daemon/volume/service/convert.go

## Purpose
Converts internal volume objects and API filter args to public API volume representations and store filters.

## Important APIs, Types, And Functions
Defines conversion options `useCachedPath` and `calcSize`, `pathCacher`, `volumesToAPI`, `volumeToAPIType`, `filtersToBy`, and `withPrune`.

## Control Flow
`volumesToAPI` loops with context cancellation checks, converts each volume, optionally uses cached mountpoint, and optionally calculates directory size plus reference count. `volumeToAPIType` fills name, driver, RFC3339 created time, labels/options/scope for `DetailedVolume`, and cached mountpoint when supported. `filtersToBy` validates accepted filters and builds `By` combinators for driver, name, label, and dangling. `withPrune` adds the anonymous-volume label filter unless `all=true`.

## State And Persistence
No persistent writes. Size calculation reads filesystem data, and reference counts are read from the store.

## Dependencies And Integration Points
Used by `VolumesService.Get`, `List`, `Prune`, and `LocalVolumesSize`. Depends on directory size helper, filter args, API volume types, and store reference counting.

## Risks
`CreatedAt` errors are ignored. Size calculation may be expensive or fail; failures return `-1` size. `withPrune` mutates the provided filter args.

## Test Signals
`convert_test.go`, service tests, and Linux local-size tests cover prune filter mutation, API status/size behavior, and filter conversion effects.
