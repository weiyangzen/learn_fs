# sources/cloud-native/moby/daemon/volume/service/opts/opts.go

## Purpose
Functional option types for volume create, get, and remove operations.

## Important APIs, Types, And Functions
`CreateConfig` with `WithCreateLabel`, `WithCreateLabels`, `WithCreateOptions`, and `WithCreateReference`; `GetConfig` with `WithGetDriver`, `WithGetReference`, and `WithGetResolveStatus`; `RemoveConfig` with `WithPurgeOnError`.

## Control Flow
Each option mutates a config struct later consumed by `VolumesService` or `VolumeStore`. Label options initialize maps when needed, bulk setters assign map references directly, and reference options protect volumes from cleanup races.

## State And Persistence
No direct persistence. Options flow into store metadata labels/options and in-memory references.

## Dependencies And Integration Points
Used throughout service and store APIs and tests to attach labels/options/references, select drivers, request status, and purge stale metadata.

## Risks
Bulk label/options setters do not deep-copy maps at option application time; callers mutating maps later can affect stored values until copied/wrapped. `WithGetResolveStatus` has an unusual direct function signature matching `GetOption`.

## Test Signals
Store/service tests cover create labels/options/references, get driver/reference/status, and remove purge behavior.
