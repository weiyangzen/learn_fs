# sources/storage-engines/foundationdb/fdbserver/datadistributor/DDTeamCollection.actor.cpp lines 6286-7221

## Scope

This chunk is the end of `DDTeamCollection.actor.cpp`. It starts in the tail of the `DDTeamCollectionUnitTest::testTeamCollection(...)` fixture helper, covers the rest of the `DDTeamCollectionUnitTest` class, and ends with the `TEST_CASE` registrations for data-distribution team construction, team selection, storage wiggler ordering, TSS-aware wiggle selection, CPU cutoffs, and shard-count-aware destination preference. The production implementation of `DDTeamCollection`, `TCTeamInfo`, `TCServerInfo`, `StorageWiggler`, and `DDTeamCollectionImpl::getNextWigglingServerID()` is earlier in the file; this chunk exercises those APIs rather than defining their main behavior.

## Purpose

The code builds small synthetic `DDTeamCollection` instances and verifies critical destination-team selection invariants used by FoundationDB data distribution:

- Team construction should respect replication policy, locality, team-size limits, and per-server coverage goals.
- `addTeamsBestOf()` should create enough healthy server teams without duplicating invalid combinations and should still give every server at least one team in constrained clusters.
- `getTeam()` should honor complete-source preference, unhealthy-team avoidance, disk utilization preference, minimum free-space cutoffs, read-bandwidth balancing, paused-wiggle deprioritization, CPU destination cutoffs, and optional shard-count limits.
- `StorageWiggler` should pick storage servers in the intended order based on store type, age, TSS needs, and metadata updates.

The tests serve as a regression net for data movement target choice. Failures here usually imply a behavioral change in data-distribution safety, balance, or recruitment/wiggle logic.

## Important APIs, Types, and Functions

- `DDTeamCollectionUnitTest::testTeamCollection(...)`: creates a test `DatabaseContext`, `DDTxnProcessor`, `DatabaseConfiguration`, and `DDTeamCollection`, then inserts synthetic `StorageServerInterface` objects into `server_info` and `server_status`. In the visible tail of the helper, each server receives `machineid`, `zoneid`, and `data_hall` locality and immediately calls `checkAndCreateMachine()`.
- `DDTeamCollectionUnitTest::testTeamCollection(int, Reference<IReplicationPolicy>, int)`: convenience overload that allocates a fresh `ShardsAffectedByTeamFailure`.
- `DDTeamCollectionUnitTest::testMachineTeamCollection(...)`: fixture variant that derives hierarchical locality from the numeric process id (`dcid`, `data_hall`, `zoneid`, `machineid`, `processid`), populates `server_info` and `server_status`, then calls `constructMachinesFromServers()`.
- `PolicyAcross` and `PolicyOne`: replication-policy fixtures used to require placement across `zoneid` for most multi-replica tests, or no locality constraint for single-replica tests.
- `DDTeamCollection::addBestMachineTeams()`, `addTeamsBestOf()`, `addTeam()`, `sanityCheckTeams()`, `disableBuildingTeams()`, `setCheckTeamDelay()`, `getTeam()`: the primary production APIs under test.
- `GetTeamRequest`: constructed with `TeamSelect` (`WANT_COMPLETE_SRCS`, `WANT_TRUE_BEST`, `ANY`) plus preference flags (`PreferLowerDiskUtil`, `TeamMustHaveShards`, `PreferLowerReadUtil`, `PreferWithinShardLimit`, `ForReadBalance`). The tests fill `completeSources` where source-awareness matters and read results from `req.reply`.
- `GetStorageMetricsReply` and `HealthMetrics::StorageStats`: synthetic server metric inputs for disk capacity, available bytes, storage load, read bandwidth, read ops, and CPU usage.
- `ShardsAffectedByTeamFailure`: injected into one fixture to assign many key ranges to a specific team and verify shard-count avoidance.
- `StorageWiggler`, `StorageMetadataType`, `KeyValueStoreType`, and `DDTeamCollectionImpl::getNextWigglingServerID()`: exercised by the final storage-wiggler tests.
- `TEST_CASE(...)`: Flow test registrations that expose these helpers to the FoundationDB unit-test runner.

## Control Flow

The fixture setup follows two patterns. The simple helper constructs the collection and, for each synthetic server id, installs a `StorageServerInterface`, locality entries, a `TCServerInfo`, and a healthy `ServerStatus`; this chunk includes the final locality and machine creation operations before returning the collection. The machine-aware helper performs the same core setup but derives locality buckets from integer divisions of the process id and builds all machine structures in one pass via `constructMachinesFromServers()`.

The team-building tests first create a policy and collection, then call `addTeamsBestOf()` or `addBestMachineTeams()` with desired and maximum counts derived from `SERVER_KNOBS`. `AddTeamsBestOf_UseMachineID` and `AddTeamsBestOf_NotUseMachineID` validate that machine-aware and prebuilt-machine-team paths can generate sane server teams. `AddAllTeams_isExhaustive` asks for more teams than possible and asserts the exact locality-valid count of 80. `AddAllTeams_withLimit` asks for 10 and accepts any result at or above that limit. The constrained-server tests seed two teams manually, build more, and assert every server is covered; `NotEnoughServers` also asserts exactly 10 machine teams and 8 added server teams after debugging output if the expectations fail.

The `getTeam()` tests all disable background team building and set the check-team delay so the request result reflects the manually constructed test universe. They then populate metrics and call `co_await collection->getTeam(req)`. `WANT_COMPLETE_SRCS` tests verify that a healthy complete-source team is reused when possible and that an unhealthy team is skipped in favor of another team composed only of complete sources. `WANT_TRUE_BEST` tests compare lower-disk-utilization versus higher-utilization selection, reject teams whose members are below minimum space thresholds, and reject near-cutoff teams when the ratio threshold is the controlling limit.

Read balancing and CPU filtering are tested with single-replica teams. The read-bandwidth test issues two requests concurrently: one that prefers low read utilization and one that does not. It expects the low-read request to pick server 4, the high-utilization request to pick server 5, then adds in-flight read penalty to the first selected team and expects the next low-read selection to move to server 2. The CPU cutoff test forces stale pivot values, optionally changes the `cpu_pivot_ratio` knob, creates four single-server teams with combinations of high/low space, high/low read, and low/mid/high CPU, then verifies the best team is server 2 and any random candidate excludes the low-space and high-CPU servers.

The shard-count preference test populates `ShardsAffectedByTeamFailure` with more than `DESIRED_MAX_SHARDS_PER_TEAM` randomly generated adjacent ranges assigned to the first team. With `PreferWithinShardLimit::True`, `getTeam()` must pick the second team regardless of whether the request uses `WANT_TRUE_BEST` or `ANY`.

The final `TEST_CASE` blocks register each helper. Most actor helpers are wrapped in `wait(...)`; synchronous helpers are called directly. The storage-wiggler tests are inline `TEST_CASE` bodies: one checks age/type ordering and future completion after metadata update, and the other checks TSS-sensitive wiggle selection against a one-replica machine-aware collection.

## State and Persistence Behavior

All state in this chunk is synthetic in-memory test state. The fixture creates a `DatabaseContext` and `DDTxnProcessor`, but the tests do not persist user data or commit transactions. Instead, they mutate `DDTeamCollection` internals that model data-distribution state:

- `server_info` maps UIDs to `TCServerInfo` objects carrying interfaces, metrics, storage stats, and team membership.
- `server_status` tracks healthy, desired, non-wiggling server status plus locality.
- `machine_info`, machine teams, and machine locality maps are created incrementally by `checkAndCreateMachine()` or in bulk by `constructMachinesFromServers()`.
- `teams`, `teamsByServerIDs`, and per-server team vectors are populated by `addTeam()` and `addTeamsBestOf()`.
- `machineTeams` is populated by `addBestMachineTeams()` and indirectly used by `addTeamsBestOf()` when constructing server teams.
- `pauseWiggle`, `wigglingId`, and `configuration` fields are directly modified in tests for paused-wiggle and TSS cases.
- `teamPivots` and server CPU stats feed candidate filtering in the CPU cutoff test.
- `ShardsAffectedByTeamFailure` stores key-range-to-team assignments for the shard-count limit test.
- `StorageWiggler` stores server metadata and pending notification state; `getNextWigglingServerID()` waits until an eligible server exists.

The durable behavior being protected is indirect: these tests verify that production data-distribution state transitions would choose safe relocation destinations and storage wiggle candidates under the same metrics and topology conditions.

## Dependencies and Integration Points

- Flow actor/test infrastructure: `Future<Void>`, `co_await`, `wait`, `success`, `trigger`, `delay`, `state`, and `TEST_CASE` integrate with FoundationDB's deterministic simulation test runner.
- Data-distribution types: `DDTeamCollection`, `DDTeamCollectionInitParams`, `DDTxnProcessor`, `MoveKeysLock`, `RelocateShard`, `GetMetricsRequest`, `RebalanceStorageQueueRequest`, `BulkLoadTaskCollection`, `TCServerInfo`, `TCTeamInfo`, and `TCMachineTeamInfo`.
- Locality and replication policy: `LocalityData`, `StorageServerInterface::locality`, `PolicyAcross`, `PolicyOne`, and `IReplicationPolicy` determine whether a team satisfies placement rules.
- Server knobs: `DESIRED_TEAMS_PER_SERVER`, `MAX_TEAMS_PER_SERVER`, `MIN_AVAILABLE_SPACE`, `MIN_AVAILABLE_SPACE_RATIO`, `MAX_DEST_CPU_PERCENT`, `CPU_PIVOT_RATIO`, `DESIRED_MAX_SHARDS_PER_TEAM`, `ENFORCE_SHARD_COUNT_PER_TEAM`, and `DD_STORAGE_WIGGLE_MIN_SS_AGE_SEC` shape expected outcomes.
- Metrics interfaces: `GetStorageMetricsReply` supplies capacity, availability, load bytes, read bandwidth, and read operations; `HealthMetrics::StorageStats` supplies CPU.
- Randomness: `deterministicRandom()` generates keys, chooses between request modes in one test, and decides which CPU cutoff path to exercise.
- Tracing/debugging: `printf`, `fmt::print`, `std::cout`, `traceAllInfo(true)`, and `CODE_PROBE` provide failure diagnostics and simulation coverage signals.

## Risks and Edge Cases

- The chunk begins inside `testTeamCollection(...)`; the constructor arguments and first locality entries are just before the requested start line. Research for this chunk therefore depends on that small boundary context to explain the helper correctly.
- Several tests assume exact team counts despite comments about randomness in team discovery. Deterministic simulation should make this reproducible, but changes to replica selection or machine-team balancing can legitimately alter expected counts.
- `AddTeamsBestOf_NotUseMachineID` calls `sanityCheckTeams()` without asserting the result. That makes it weaker as a regression signal than the machine-id variant.
- `GetTeam_ServerUtilizationNearCutoff` is tightly coupled to knob values and floating-point ratio behavior. If `MIN_AVAILABLE_SPACE_RATIO` or available-space cutoff semantics change, the test may fail for threshold math rather than team-selection ordering.
- `GetTeam_CutOffByCpu` mutates `cpu_pivot_ratio` on one branch and does not restore it locally. This is probably acceptable in FoundationDB knob-test infrastructure, but it is a shared-state risk if tests are reordered or run outside the expected simulation isolation.
- Tests call `disableBuildingTeams()` and `setCheckTeamDelay()` to make selection deterministic. If future `getTeam()` behavior performs additional asynchronous checks or team construction despite these controls, these tests may become flaky or stop isolating the intended behavior.
- The read-bandwidth test depends on in-flight read penalty changing the next selected team. Changes to penalty scaling, read-load comparison, or tie-breaking can invalidate the exact expected UID.
- Storage-wiggler tests use `now()`, min-age delays, and future readiness. They are simulation-friendly, but wall-clock-like behavior or altered min-age rules could make assertions fragile.
- The TSS storage-wiggler test directly edits `configuration.usableRegions` and `desiredTSSCount`; changes to `reachTSSPairTarget()` semantics can alter which server is eligible before normal min age.

## Test Signals

- `DataDistribution/AddTeamsBestOf/UseMachineID`: `addTeamsBestOf()` can build teams from machine locality and pass `sanityCheckTeams()`.
- `DataDistribution/AddTeamsBestOf/NotUseMachineID`: prebuilt machine teams plus server team building complete without null collection failure and run the sanity checker.
- `DataDistribution/AddAllTeams/isExhaustive`: across-zone replication with 10 processes and team size 3 yields exactly 80 valid teams after filtering same-zone combinations.
- `/DataDistribution/AddAllTeams/withLimit`: bounded team construction can satisfy at least the requested lower limit.
- `/DataDistribution/AddTeamsBestOf/SkippingBusyServers`: seeded busy/covered servers do not prevent adding at least 8 teams, and every server ends with at least one team.
- `/DataDistribution/AddTeamsBestOf/NotEnoughServers`: constrained five-server topology still builds all 10 machine teams, covers every server, and finds the expected 8 additional teams.
- `/DataDistribution/GetTeam/NewServersNotNeeded`: `WANT_COMPLETE_SRCS` maintains the healthy complete-source team instead of moving to higher-availability new servers.
- `/DataDistribution/GetTeam/HealthyCompleteSource`: an unhealthy complete-source team is skipped in favor of another healthy complete-source team.
- `/DataDistribution/GetTeam/TrueBestLeastUtilized` and `TrueBestMostUtilized`: the disk-utilization preference flag controls whether lower or higher utilized teams are selected.
- `/DataDistribution/GetTeam/ServerUtilizationBelowCutoff` and `ServerUtilizationNearCutoff`: teams below absolute or ratio free-space cutoffs are rejected.
- `/DataDistribution/GetTeam/TrueBestLeastReadBandwidth`: read-balancing selection honors read load and in-flight read penalty.
- `/DataDistribution/GetTeam/DeprioritizeWigglePausedTeam`: a team containing the paused wiggling server is deprioritized even when otherwise attractive.
- `/DataDistribution/StorageWiggler/NextIdWithMinAge`: storage-wiggler ordering accounts for store type, min age, special metadata flags, and asynchronous metadata updates.
- `/DataDistribution/StorageWiggler/NextIdWithTSS`: TSS target state changes eligibility and allows a younger server to be selected before the normal age deadline.
- `/DataDistribution/GetTeam/CutOffByCpu`: CPU and space candidate filtering excludes high-CPU and low-space teams for best and random selection paths.
- `/DataDistribution/GetTeam/PreferWithinShardRange`: when shard-count enforcement is enabled, selection avoids the team already above the desired shard limit.
