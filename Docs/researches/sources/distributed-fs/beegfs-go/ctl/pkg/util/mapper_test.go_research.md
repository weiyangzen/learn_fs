# sources/distributed-fs/beegfs-go/ctl/pkg/util/mapper_test.go

## Purpose
Tests the generic mapper and cached mapping refresh behavior.

## Important APIs, Types, And Functions
Tests `Mapper.Len`, `GetCachedMappings`, `updateCachedMappingsInBackground` behavior through public calls, and `Mapper.Get` with `beegfs.EntityIdSet` against `MapTargetToNode`.

## Control Flow
Tests mutate package globals (`cachedMappings`, `cachedMappingsErr`, `cachedMappingsLastModified`, `activeCachedMappingsUpdate`, `getMappingsFunc`) to simulate cache states. Assertions verify immediate refresh, retry after previous error, forced refresh, no background update for fresh cache, background update for stale cache, suppression while an update is active, and UID/legacy/alias lookup from an `EntityIdSet`.

## State And Persistence
No persistence, but tests share and mutate global package state. They do not restore `getMappingsFunc` to the production function at the end of each test, which is acceptable inside package test order only if no later tests depend on default behavior.

## Dependencies And Integration Points
Uses `testify/assert` and `require`, common BeeGFS entity types, and `ctl/pkg/ctl/target` result structs.

## Risks And Edge Cases
The stale-cache test uses a very short sleep to wait for a goroutine and may be timing-sensitive on slow systems. The expression `time.Now().Add(-cachedMappingsUpdateDelay * time.Second)` multiplies a duration by `time.Second`, making the intended stale duration much larger than necessary but still stale. No tests run with the race detector assumptions around unsynchronized force-update state.

## Test Signals
Provides meaningful coverage for happy-path cache behavior and mapper lookup. Missing coverage includes constructor maps beyond target-to-node, concurrent callers, error from background refresh, and RST mapping error tolerance.
