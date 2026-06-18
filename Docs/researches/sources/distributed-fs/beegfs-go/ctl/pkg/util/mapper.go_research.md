# sources/distributed-fs/beegfs-go/ctl/pkg/util/mapper.go

## Purpose
Builds and caches common BeeGFS entity mappings used throughout CTL, including targets, nodes, storage pools, buddy groups, mirrored targets, metadata buddy primaries, and Remote Storage Target configs.

## Important APIs, Types, And Functions
Exports errors (`ErrMappingRSTs`, `ErrMapperNotInitialized`, `ErrMapperNotFound`), `Mappings`, generic `Mapper[T]`, cache functions `GetCachedMappings` and `GetMappings`, mapper methods `Get`, `Len`, `UIDs`, `Aliases`, `LegacyIDs`, and mapping constructors such as `MapNodeToTargets`, `MapTargetToNode`, `MapStoragePoolToConfig`, `MapStorageTargetsToBuddyGroup`, and `MapRstIdToConfig`.

## Control Flow
`GetMappings` fetches targets, pools, node store, buddy groups, and BeeRemote RST config in sequence, building mapper structs after each source. RST mapping is initialized last so callers can choose to ignore `ErrMappingRSTs` while retaining other mappings. `GetCachedMappings` returns an existing clean cache, triggers background refresh if stale, or serializes a blocking refresh when cache is missing, errored, or force-updated.

`Mapper.Get` dispatches by concrete entity ID type and resolves UID, legacy ID, alias, or prioritized fields in `EntityIdSet`. Constructors populate three maps for each supported lookup type.

## State And Persistence
No disk persistence. Global mutable cache state includes cached mappings/error, force-update flag, update-in-progress flag, timestamps, mutexes, and injectable `getMappingsFunc` for tests.

## Dependencies And Integration Points
Central integration point for `ctl/pkg/ctl/target`, `pool`, `buddygroup`, node store, BeeRemote config, protobuf RST config, gRPC status handling, and many entry/RST commands.

## Risks And Edge Cases
`mappingsForceUpdate` is written outside a mutex before lock acquisition, creating a data-race risk under concurrent callers. Cached `Mappings` are mutable and documented as immutable-by-convention only. Background refresh uses the caller's context, so cancellation may poison the cache with an error. RST unavailability is returned as an error with partial mappings, and callers must intentionally tolerate it.

## Test Signals
`mapper_test.go` covers mapper length, cache first call, refresh on error, force update, fresh-cache hit, background update, already-active update, and entity-id-set lookup. Gaps include race tests, mapping constructors for buddy/pool/RST cases, and partial RST failure behavior.
