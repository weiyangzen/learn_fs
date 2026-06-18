# subset-b-007031 EOS GeoTreeEngine and group balancer research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotreeengine/GeoTreeEngine.cc -->
# sources/distributed-fs/eos/mgm/geotreeengine/GeoTreeEngine.cc

## Purpose
Implements EOS MGM geoscheduling: placing new replicas, selecting access replicas, selecting data proxies/firewall entry points, and maintaining the scheduling trees that back those decisions. It is the runtime companion to `GeoTreeEngine.hh`, wiring filesystem change events, slow-tree mutation, fast-tree double buffering, penalty accounting, configuration persistence, and operator display.

## Important APIs, types, and functions
`GetMaxPlacementAttempts()` reads `EOS_SCATTERED_PLACEMENT_MAX_ATTEMPTS` to retry scattered placement away from a collocated geotag. `GeoTreeEngine::GeoTreeEngine()` initializes defaults, disabled `nogeotag` placement branches, listener state, mutex behavior, penalty windows, pthread TLS cleanup, and the updater semaphore. `forceRefreshSched()` and `forceRefresh()` force all watched filesystem/proxy entries through a rebuild. `insertFsIntoGroup()` and `removeFsFromGroup()` synchronize EOS `FsView` membership with slow/fast geotrees and filesystem listeners. `placeNewReplicasOneGroup()` drives placement for regular and draining cases, including existing replicas, excluded fsids/geotags, booking-size filtering, collocation count, and proxy/firewall output. `accessHeadReplicaMultipleGroup()` selects a best head replica among existing replicas, including legacy multi-group placement. `findProxy()` and `accessProxyFirewall()` schedule data proxies and firewall entry points. `listenFsChange()` is the background updater loop. The two `updateTreeInfo()` overloads update one fs node or process a frame of notifications. `updateAtomicPenalties()` self-estimates per-speed-class penalties. The setters and `setParameter()` mutate geoscheduling config and optionally persist it through `gOFS->mConfigEngine`.

## Control flow
Insertion snapshots the `FileSystem`, derives geotag/host/fsid node info, inserts into a `SlowTree`, subscribes the fs queue to `FsChangeListener`, initializes slow-tree state through `updateTreeInfo()`, marks the group modified, and optionally rebuilds fast structures before publishing the map entry. Removal reverses listener subscription, deletes the slow-tree node, marks the group modified, rebuilds if requested, and defers deleting now-empty `SchedTME` objects until no readers hold them.

Placement and access take read locks on the selected foreground fast structures, copy a fast tree into the per-thread `tlGeoBuffer`, mark existing replicas or exclusions in that working copy, update the copy, and call `findFreeSlot()`/`findFreeSlotsAll()`. Successful placement returns fsids and atomically subtracts upload/download penalties from the foreground fast structures. Access first validates availability in the relevant RO/RW/draining access tree, ranks candidates by geotag proximity and unsaturated status, applies access penalties, then schedules proxies and firewall entry points if requested.

The updater thread fetches filesystem events into per-frame bitfields, periodically pauses collection, copies foreground fast structures to background structures, records and clears per-frame foreground penalties, snapshots changed filesystems from `FsView`, applies state changes to the background fast tree or slow tree, self-updates penalty values, rebuilds/refreshes modified fast structures, swaps foreground/background buffers, clears notification buffers, and advances the frame counter.

## State and persistence
Durable scheduler state is intentionally minimal: parameters, disabled branches, access geotag mappings, and access proxygroup mappings can be written under the `geosched` config prefix. The actual slow/fast scheduling trees are rebuilt from `FsView`, filesystem/node config, and notifications at boot/refresh time. Runtime state includes `pGroup2SchedTME`, `pFs2SchedTME`, `pFsId2FsPtr`, proxy maps, notification buffers, circular penalty and latency windows, pending-deletion lists, and `AccessStruct` mapping trees. Foreground fast structures are read by client threads; background fast structures are modified by the updater and swapped under `doubleBufferMutex`. Per-thread tree working copies live in `tlGeoBuffer` and are freed by a pthread key destructor.

## Dependencies and integration points
Depends on EOS MGM `FsView`, `FileSystem` snapshots, `FsGroup`, `SlowTree` and fast scheduling tree classes from `mgm/geotree`, `mq::FsChangeListener`, `mq::MessagingRealm`, `AssistedThread`/`ThreadAssistant`, `RWMutex`, XRootD atomics, `TableFormatterBase`, `gOFS->mConfigEngine`, and logging macros. It integrates with `FsView` add/remove paths, filesystem shared-object notifications, geosched command display/configuration, data proxy groups, and firewall entrypoint scheduling.

## Risks and test signals
Concurrency risk is high: map locks, slow-tree locks, double-buffer locks, `fastStructLockWaitersCount`, pending deletions, semaphores, and atomics must stay ordered to avoid stale pointers or deadlocks. Notification bitfields have hazards: `sfgDrain` and `sfgDrainer` share the same bit, and `gNotifKey2EnumSched.at(event.key)` assumes every listener key is known. Placement risks include leaked `existingReplicasIdx`/`excludeFsIdx` on unusual cleanup paths being handled manually, geotag prefix comparisons causing unintended collocation behavior, and `GetMaxPlacementAttempts()` caching its environment value statically. Access risks include null `unavailableFs` defaults being dereferenced, mixed-group legacy behavior, and forced fsid handling that only rejects unavailable forced replicas. Penalty risks include atomic casts on floats, signed `char` saturation/underflow, approximate latency windows, and intentionally lost updates during swaps. Configuration parsing risks include vector string parsing, disabled-branch conflict checks, and persistence side effects through global `gOFS`. Test signals should include filesystem add/remove/refresh races, geotag move updates, listener unknown-key behavior, placement with booking/exclusions/collocation, access under saturated and draining states, proxygroup missing/empty cases, firewall mapping prefix lists, config round trips, updater pause/resume, pending deletion after active readers, and penalty frame recall.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotreeengine/GeoTreeEngine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotreeengine/GeoTreeEngine.hh -->
# sources/distributed-fs/eos/mgm/geotreeengine/GeoTreeEngine.hh

## Purpose
Declares the `GeoTreeEngine` public scheduling API and the private data structures used to maintain EOS geolocation-aware file placement, file access, data proxy scheduling, firewall entrypoint scheduling, background tree updates, and penalty/latency accounting. The large header comment is also the main in-tree design document for geoscheduling.

## Important APIs, types, and functions
`SchedType` classifies regular RO, regular RW, and draining scheduling. `FastStructSched` owns five fast trees for filesystem scheduling: RO access, RW access, draining access, regular placement, and draining placement, plus shared fast tree info, fsid-to-index and geotag-to-index maps, and penalty counters. `FastStructProxy` owns the fast gateway access tree and host/geotag maps for proxy scheduling. `TreeMapEntry<FastStruct>` supplies the slow tree, foreground/background fast structures, modification flags, double-buffer swap, config propagation, and fast rebuild helpers. `SchedTME`, `ProxyTMEBase`, and `DataProxyTME` specialize tree map entries for filesystem groups and data proxy groups. `AccessStruct` stores direct-access and firewall-proxygroup mappings as slow/fast access trees. `PenaltySubSys` and `LatencySubSys` keep circular frame data for atomic score penalties and fs publish latency. Public APIs include forced refresh, fs insertion/removal, formatted introspection, writable-space accounting, replica placement, access head selection, proxy/firewall scheduling, updater lifecycle, fs info lookup, parameter mutation, disabled-branch management, and access mapping management.

## Control flow
The header establishes two scheduling lanes. Client-facing scheduling operations take read access to the foreground fast structures and work on thread-local copies, minimizing contention. The updater and administrative paths mutate slow trees or background fast structures, rebuild snapshots when topology changes, update score/status fields when only state changes, apply disabled branches, clear background penalties, and swap buffers. Proxy scheduling mirrors filesystem scheduling with `FastStructProxy`, while `AccessStruct` uses direct locking because its mappings are rare configuration changes rather than high-frequency state updates.

## State and persistence
The class separates configuration from runtime state. Configuration protected by `configMutex` includes saturated-node skip flags, proxy-distance policy, penalty update rate, fill-ratio and saturation thresholds, timeframe duration, publish-to-penalty delay, and disabled branches. Runtime state includes group-to-tree and fsid-to-tree maps, proxygroup/host maps, notification buffers, pending deletion queues, thread-local fast-tree copy buffer, circular penalties, latency stats, updater state, and access mapping trees. Persistence is only by explicit config writes in setters and mapping/branch methods; tree topology and fast snapshots are not persisted.

## Dependencies and integration points
Includes `mgm/fsview/FsView.hh`, `mgm/geotree/SchedulingSlowTree.hh`, EOS table formatting, timing, filesystem and messaging classes, XRootD atomics/strings, POSIX threading/semaphore facilities, and standard containers. External users should treat the public `GeoTreeEngine` methods as the integration surface; private nested types encode important ownership and locking invariants and are not stable extension points.

## Risks and test signals
The header exposes several correctness-sensitive contracts: `DeepCopyTo()` must preserve pointer wiring into copied maps/info, `resizePenalties()` must match node count before penalties are copied, `TreeMapEntry::swapFastStructBuffers()` is the narrow publication point, and `updateSlowTreeInfoFromBgFastStruct()` must not propagate derived disabled bits back into the slow tree. Potential bugs include missing deletes (`FastStructProxy` deletes `proxyAccessTree`, `treeInfo`, `penalties`, and `tag2NodeIdx` but not visibly `host2TreeIdx`), unguarded map access assumptions, `char` score/threshold ranges, and default pointer arguments such as `unavailableFs = nullptr` that implementations must validate before use. Tests should exercise copy/rebuild/swap behavior, disabled-branch application per operation tree, access mapping lifecycle, parameter setters that force rebuilds, TLS allocation/free, and public methods with null optional vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotreeengine/GeoTreeEngine.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngine.cc -->
# sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngine.cc

## Purpose
Implements the common, policy-neutral part of the EOS group balancer engine. It stores per-group size information, delegates threshold classification to derived engines, chooses source/target group pairs for transfers, and renders status for humans and monitoring.

## Important APIs, types, and functions
`populateGroupsInfo()` resets current state, moves in a `group_size_map`, then calls virtual `recalculate()` and `updateGroups()`. `clear_threshold()`, `clear_thresholds()`, and `clear()` maintain `BalancerEngineData`. `updateGroups()` reclassifies every known group by calling virtual `updateGroup()`. `pickGroupsforTransfer()` chooses a random over-threshold source and under-threshold target using `common::getRandom()`. `pickGroupsforTransfer(uint64_t index)` does deterministic round-robin selection through `common::pickIndexRR()`. `generate_table()` formats selected groups with used bytes, capacity, and fill value. `get_status_str()` returns either compact monitoring counters or a detailed human report with average fill/range and source/target tables.

## Control flow
The base engine receives a complete group-size snapshot, recalculates engine-specific thresholds, and rebuilds source/target sets. Transfer picking first verifies that both sets are non-empty; empty sets cause debug logging, a threshold recalculation, and an empty pair. Non-empty sets are selected independently, either randomly or by index, so pairing is not tied to relative imbalance magnitude in the base class.

## State and persistence
All state is in-memory inside `BalancerEngineData`: the full `mGroupSizes` map and two sets of group names over and under the active policy threshold. No persistence occurs here; upstream group balancer orchestration is responsible for fetching group sizes and acting on picked pairs.

## Dependencies and integration points
Depends on `BalancerEngine.hh`, `BalancerEngineTypes.hh`, policy helpers from `BalancerEngineUtils.hh`, EOS logging, `TableFormatterBase`, and common container/random utilities. Derived engines such as stddev, minmax, and freespace supply `recalculate()`, `updateGroup()`, and `configure()` implementations while inheriting common status and picking behavior.

## Risks and test signals
`GroupSizeInfo::filled()` returns a ratio, while status labels and average text print `%`; tests should confirm whether downstream helpers expect 0..1 or 0..100. `pickGroupsforTransfer()` recalculates on empty sets but does not re-run `updateGroups()` before returning `{}`, so callers must tolerate a no-op cycle. Selection from `std::set` is stable by lexicographic ordering for round-robin but random selection depends on the shared random helper. Tests should cover empty source/target sets, single-source/single-target behavior, deterministic index wrapping, status output in monitoring/detail modes, groups erased from `mGroupSizes`, and derived-engine classification after `populateGroupsInfo()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngine.hh -->
# sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngine.hh

## Purpose
Declares the group balancer engine interface and the reusable base class for engines that classify filesystem groups as sources or targets for balancing transfers.

## Important APIs, types, and functions
`IBalancerEngine` defines the virtual contract: `recalculate()`, `clear()`, `updateGroup()`, `updateGroups()`, transfer-pair picking, `configure()`, `get_group_sizes()`, and status rendering. `BalancerEngineData` groups the over-threshold set, under-threshold set, and group-size map. `BalancerEngine` implements common population, clearing, status, random/round-robin picking, `canPick()`, `sourceGroupCount()`, `targetGroupCount()`, and exposes `get_data()` for tests. Derived classes are expected to implement policy-specific recalculation, single-group classification, and configuration.

## Control flow
A concrete engine is configured, populated with group sizes, recalculates its threshold model, classifies groups, and then callers repeatedly ask for transfer pairs. The base class owns state transitions around complete refreshes and pair selection; subclasses only decide whether a specific group belongs in `mGroupsOverThreshold`, `mGroupsUnderThreshold`, or neither.

## State and persistence
The header defines only in-memory state. `mGroupSizes` stores the latest snapshot, while threshold sets store derived source/target classifications. `get_data()` intentionally exposes this state for unit tests and validation, not for persistence.

## Dependencies and integration points
Depends on STL maps/sets/random-related headers and `BalancerEngineTypes.hh`. It is consumed by concrete engines and factory code, and by higher-level group balancer orchestration that fetches group sizes, configures engines, invokes `pickGroupsforTransfer()`, and schedules actual transfers.

## Risks and test signals
Because `IBalancerEngine` has no virtual `populateGroupsInfo()` despite the base class providing it, callers that store only an interface pointer cannot use that helper unless they downcast or know the concrete base. The base class is abstract only because `recalculate()`, `updateGroup()`, and `configure()` remain pure; tests should instantiate concrete engines. Test signals include lifecycle sequencing (`clear`, populate, recalculate, update), `canPick()` semantics, source/target count consistency, and ensuring subclasses call `clear_threshold(group_name)` before reclassifying an individual group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngine.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngineFactory.hh -->
# sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngineFactory.hh

## Purpose
Provides header-only helpers for mapping a configured engine name to a `BalancerEngineT` enum and constructing the corresponding concrete balancer engine.

## Important APIs, types, and functions
`get_engine_type(std::string_view name)` maps `"minmax"` to `BalancerEngineT::minmax`, `"freespace"` to `BalancerEngineT::freespace`, and defaults every other name to `BalancerEngineT::stddev`. `make_balancer_engine(BalancerEngineT engine_t)` returns a raw `new` `MinMaxBalancerEngine`, `FreeSpaceBalancerEngine`, or default `StdDevBalancerEngine`.

## Control flow
Configuration code can parse a name into an enum, then construct an engine. Unknown names silently select stddev, making stddev the compatibility/default policy. Construction is unconditional and transfers ownership of a raw pointer to the caller.

## State and persistence
No state is stored in the factory. Persistence is external, usually the configuration string that eventually reaches `get_engine_type()`.

## Dependencies and integration points
Includes `StdDevBalancerEngine.hh`, `MinMaxBalancerEngine.hh`, and `FreeSpaceBalancerEngine.hh`, so including this header pulls all concrete engine definitions. It is the factory boundary between operator/configured engine names and concrete balancing policies.

## Risks and test signals
The functions are non-`inline` definitions in a header, which can create ODR/linker issues if the header is included in multiple translation units without compiler/linker allowances. Raw pointer ownership is another risk; callers must delete or wrap the result. Silent fallback for typos can mask misconfiguration. Tests should cover name mapping, unknown-name default behavior, each enum construction, ownership cleanup through a base pointer, and multi-translation-unit builds that include the factory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngineFactory.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngineTypes.hh -->
# sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngineTypes.hh

## Purpose
Defines shared types for EOS group balancing: group lifecycle status, size/capacity records, maps/sets used by engines, engine configuration maps, engine type enum, and a helper for deciding whether an engine should average fill levels.

## Important APIs, types, and functions
`GroupStatus` models `ON`, `OFF`, `DRAIN`, `DRAINCOMPLETE`, and `DRAINFAILED`. `getGroupStatus(std::string_view)` parses status text. `GroupStatusToStr()` formats a status. `GroupSizeInfo` stores status, used bytes, and capacity, with `swapFile()`, `usedBytes()`, `capacity()`, `filled()`, `draining()`, and `on()`. Type aliases define `group_size_map`, `threshold_group_set`, `groups_picked_t`, and `engine_conf_t`. `BalancerEngineT` selects stddev, minmax, freespace, or `total_count`. `engine_should_average()` returns false for freespace and true for the other engines.

## Control flow
Fetchers and orchestration code create `GroupSizeInfo` objects, concrete engines classify them, and selected transfer pairs are represented as `groups_picked_t`. Simulated or planned transfers can call `swapFile()` to update two group sizes in memory before reclassification.

## State and persistence
`GroupSizeInfo` is a small value object and does not persist directly. The aliases define the shape of in-memory snapshots and configuration maps. `std::less<>` on maps enables heterogeneous lookup by `std::string_view` or `std::string` without allocations when used carefully.

## Dependencies and integration points
Depends only on standard integer/string/map/set headers. It is included by base and concrete balancer engines, factories, group-size fetchers, and code that interprets engine status/configuration.

## Risks and test signals
`getGroupStatus("drainfailed")` returns `GroupStatus::DRAINCOMPLETE`, which conflicts with the declared `DRAINFAILED` enum and `GroupStatusToStr()` branch; this is a likely bug. `GroupStatusToStr(DRAINCOMPLETE)` returns `"drained"` while parsing expects `"draincomplete"`, so round trips are asymmetric. `GroupSizeInfo::filled()` divides by capacity without a zero guard and returns a fraction, not a percent. `swapFile()` can underflow used bytes if asked to move more than the source contains and ignores target capacity. Tests should cover status parse/format round trips, zero-capacity groups, transfer underflow/overflow, heterogeneous map lookup, and `engine_should_average()` for each enum including `total_count`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngineTypes.hh -->
