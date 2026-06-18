# sources/cloud-native/moby/daemon/volume/service/convert_test.go

## Purpose
Unit tests for prune filter normalization.

## Important APIs, Types, And Functions
`TestFilterWithPrune` exercises `withPrune`.

## Control Flow
The test checks that empty filters gain the anonymous-volume label, existing labels are preserved and augmented, `all=1`/`all=true` disables anonymous-only injection, `all=0`/`false` keeps anonymous-only behavior, and invalid or repeated `all` values return invalid filter errors.

## State And Persistence
Only in-memory filter args are mutated.

## Dependencies And Integration Points
Uses daemon filter args and `AnonymousLabel`, feeding behavior used by `VolumesService.Prune`.

## Risks
Does not test `filtersToBy` directly or actual volume deletion; service tests cover those paths.

## Test Signals
Protects Docker prune compatibility: default prune targets anonymous volumes unless the user requests all volumes.
