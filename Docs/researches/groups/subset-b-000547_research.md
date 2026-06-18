# subset-b-000547 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeCapacityPools.cpp -->
# sources/distributed-fs/beegfs/common/source/common/nodes/NodeCapacityPools.cpp

## Purpose
Implements `NodeCapacityPools`, a thread-safe three-pool selector for numeric node IDs. BeeGFS reuses this class for metadata-server capacity pools and buddy-group IDs, where only plain membership and random/round-robin selection are needed.

## Important APIs, Types, And Functions
`addOrUpdate()`, `addIfNotExists()`, `remove()`, `syncPoolsFromLists()`, `syncPoolsFromSets()`, `getPoolsAsLists()`, `chooseStorageTargets()`, `chooseStorageTargetsRoundRobin()`, `getPoolAssignment()`, `getStateAsStr()`, and `poolTypeToStr()` are the public behavior implemented here. Private helpers remove IDs from other pools and choose targets with or without preferences.

## Control Flow
Writes take the `RWLock` in write mode and maintain the invariant that one ID appears in at most one `CapacityPoolType`. `addIfNotExists()` uses a read-lock fast path, then rechecks under write lock before inserting. `chooseStorageTargets()` prefers normal, then low, then emergency pools; with preferred targets, it first tries preferred normal/low entries, then non-preferred normal/low entries, then emergency. Non-preferred selection divides the sorted set into ranges and picks one random element from each range. Round-robin selection uses `lastRoundRobinTarget` and requires a write lock.

## State, Persistence, And Dependencies
State is in-memory: `pools`, `lastRoundRobinTarget`, dynamic-pool flags/limits, and a `RandomReentrant`. Serialization only covers `pools`; round-robin position and dynamic limit values are constructor-owned runtime configuration. Dependencies include `RWLockGuard`, `DynamicPoolLimits`, `CapacityPoolType`, and common BeeGFS UInt16 containers.

## Integration Points
`StoragePool` uses this class for buddy capacity pools. `NodeStoreServers` can attach a `NodeCapacityPools` and removes node IDs from it on node deletion. Management and metadata placement code consume `getPoolsAsLists()` and `chooseStorageTargets()`.

## Risks
Callers must pass a correctly sized `UInt16ListVector`/`UInt16SetVector`; there are no explicit bounds checks before indexing by pool type. The chooser can return fewer than requested targets, so callers must honor `minNumRequiredTargets`. Round-robin state is not persisted and is intentionally global across pools. Preferred-target fallback stops early once any preferred target is found in some paths, which can produce fewer than the requested count.

## Test Signals
Tests should cover pool movement uniqueness, fast-path duplicate insert, list/set sync, empty pools, normal-to-low-to-emergency fallback, preferred target filtering, duplicate preferred IDs, round-robin wraparound, serialization of pools, and concurrent add/remove/select under lock instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeCapacityPools.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeCapacityPools.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/NodeCapacityPools.h

## Purpose
Declares the node-oriented capacity pool abstraction used to track IDs in normal, low, and emergency capacity classes and select IDs for allocation-like workflows.

## Important APIs, Types, And Functions
The class exposes mutation, synchronization, list export, random and round-robin selection, pool lookup, state formatting, and serialization. It stores `UInt16SetVector pools`, `DynamicPoolLimits` for space and inodes, `RandomReentrant randGen`, and `lastRoundRobinTarget`.

## Control Flow
The header defines iterator ring helpers used by the implementation to walk sorted containers with wraparound and to choose a random starting point. The public serialization template emits only `pools`.

## State, Persistence, And Dependencies
The class owns an `RWLock`, pool membership, dynamic-pool configuration, random generator, and volatile round-robin cursor. It depends on `TargetCapacityPools.h` for shared capacity pool/container types, `DynamicPoolLimits`, and `RandomReentrant`.

## Integration Points
Included by `StoragePool.h` and `NodeStoreServers.h`. It mirrors `TargetCapacityPools` but lacks per-node target grouping.

## Risks
The class serializes less state than it holds; this is intentional for runtime-only cursors but important for restart behavior. Static helpers assume non-empty collections at call sites. The type accepts `uint16_t targetID` names although it may hold node IDs, which can confuse callers.

## Test Signals
Compile-time users should verify serialization compatibility and ensure client/server pool-count assumptions match `CapacityPool_END_DONTUSE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeCapacityPools.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeConnPool.cpp -->
# sources/distributed-fs/beegfs/common/source/common/nodes/NodeConnPool.cpp

## Purpose
Implements per-node stream connection pooling for TCP and RDMA internode communication. It caps concurrent connections, reuses idle pooled sockets, chooses NIC routes, authenticates channels, and invalidates stale or failed sockets.

## Important APIs, Types, And Functions
Key methods are the constructor/destructor, `setLocalNicList()`, `loadIpSourceMap()`, `acquireStreamSocketEx()`, `releaseStreamSocket()`, `invalidateStreamSocket()`, `invalidateSpecificStreamSocket()`, `invalidateAllAvailableStreams()`, `disconnectAndResetIdleStreams()`, `updateInterfaces()`, `getFirstPeerName()`, socket option helpers, `authenticateChannel()`, and `makeChannelIndirect()`.

## Control Flow
`acquireStreamSocketEx()` waits on `changeCond` when all connections are busy and waiting is allowed. If an available pooled socket exists, it marks it unavailable and returns it. Otherwise it increments `establishedConns`, releases the mutex, iterates known NICs, filters by net/tcp-only settings, creates RDMA or TCP sockets, binds an optional source IP, connects, applies options, sends auth/directness control messages, and then re-locks to append the socket or roll back the count. Releases either mark a socket available and signal waiters or invalidate expired/close-on-release sockets. Invalidation collects available sockets under lock, closes them outside the lock, and decrements stats through `invalidateSpecificStreamSocket()`.

## State, Persistence, And Dependencies
State is in-memory: NIC lists, source-IP map, `connList`, available/established counters, max connection limit, fallback expiration, direct-channel flag, stats, error-log suppression state, mutex, and condition variable. It depends on `AbstractApp`/common config, `PThread`, net filters, `RoutingTable`, `StandardSocket`, `RDMASocket`, `PooledSocket`, `MessagingTk`, and control messages.

## Integration Points
Each `Node` owns a pool. `NodeStoreServers` and `NodeStoreClients` set channel directness and local NIC capabilities. Messaging paths acquire sockets for request/response traffic. Internode sync uses `disconnectAndResetIdleStreams()` for idle cleanup.

## Risks
The pool relies on correct accounting of `establishedConns` versus `connList.size()`, especially across exceptions. `invalidateSpecificStreamSocket()` searches with a loop that dereferences the iterator before checking `end()`; empty or corrupted lists would be dangerous. Route restriction needs `ipSrcMap` freshness. Filters can silently skip all NICs. Authentication is one-way send here; failures surface as socket errors later. Fallback sockets expire only after release.

## Test Signals
Exercise TCP, RDMA, mixed NIC ordering, filter rejection, source-interface restriction, max-connection blocking and nonblocking acquire, failed-all-routes logging suppression, close-on-release after interface changes, idle disconnect, auth hash enabled, indirect channel mode, destructor cleanup, and concurrent acquire/release stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeConnPool.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeConnPool.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/NodeConnPool.h

## Purpose
Declares the per-node connection pool and its lightweight stats/error-state helpers.

## Important APIs, Types, And Functions
`NodeConnPoolStats` counts established TCP and RDMA sockets. `NodeConnPoolErrorState` tracks last successful peer/NIC and whether the prior attempt failed on all routes to suppress repetitive logs. `NodeConnPool` exposes socket acquire/release/invalidate, interface update, peer-name lookup, local NIC capability setting, max-connection override, stats export, and source-map reload.

## Control Flow
The public API separates normal socket lifecycle from interface updates. Private helpers handle invalidation, idle flag reset, socket options, auth/directness messages, stats, and route source-map loading.

## State, Persistence, And Dependencies
All fields are volatile runtime state. The class owns a `Mutex` and `Condition`, raw `PooledSocket*` list, NIC data, app pointer, parent node reference, and accounting counters. It is non-copyable and non-movable.

## Integration Points
Included by `Node`, and through `Node` by the stores and messaging toolkit. Configuration comes from `ICommonConfig`.

## Risks
Raw socket ownership means all acquire/release/invalidate paths must be paired. Direct setters such as `setChannelDirect()` are not locked, so callers should set them before concurrent use. Stats are counters, not historical telemetry.

## Test Signals
Header-level tests should confirm API overrides in test subclasses, lock-protected getters, and error-state logging decisions after success, partial failure, and complete failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeConnPool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeOpStats.cpp -->
# sources/distributed-fs/beegfs/common/source/common/nodes/NodeOpStats.cpp

## Purpose
Serializes per-client or per-user operation counters into the `uint128_t` vector layout consumed by `fhgfs-ctl`, with cookie-based pagination.

## Important APIs, Types, And Functions
`mapToUInt128Vec()` is the core API. `getMaxIPsPerVector()` calculates how many map entries fit in a response buffer, and `reserveVector()` preallocates output capacity.

## Control Flow
The method selects either `userCounterMap` or `clientCounterMap`, positions after a cookie unless the cookie is all-bits-one, reserves header plus per-IP data, writes metadata fields (`num ops`, `more data`, layout version), appends each key and its `OpCounter` values until the buffer-derived limit is reached, and sets the more-data flag if entries remain.

## State, Persistence, And Dependencies
The function reads in-memory maps under `SafeRWLock`. It depends on `OpCounter`, `Common.h` integer helpers, and constants from `NodeOpStats.h`. There is no disk persistence.

## Integration Points
Derived metadata and storage op-stat classes populate the maps; management/ctl message handlers call `mapToUInt128Vec()` to stream stats to users.

## Risks
If `bufLen` is too small, `maxNumIPs` can be zero and the method may return an empty data vector with `more data` semantics that callers must handle. Layout changes require bumping `OPCOUNTER_VEC_LAYOUT_VERS`. Cookie ordering follows map key ordering, so clients must use the last returned key.

## Test Signals
Validate empty maps, all-bits-one cookie, mid-map cookie, zero/very small buffer, exact-fit buffer, multi-page responses, user versus client maps, and layout version compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeOpStats.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeOpStats.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/NodeOpStats.h

## Purpose
Defines the common base for per-client and per-user operation statistics and the wire-vector layout for exporting counters.

## Important APIs, Types, And Functions
Constants define per-IP and metadata vector positions, reserved header size, layout version, and safety length. `NodeOpCounterMap` maps `uint128_t` IP/user keys to `OpCounter`. `NodeOpStats` exposes `mapToUInt128Vec()` and `removeClientFromMap()`.

## Control Flow
The header establishes that vectors begin with metadata, then repeated key plus counters. Derived classes are expected to update `clientCounterMap` and `userCounterMap` under `lock`.

## State, Persistence, And Dependencies
State is in-memory and protected by `RWLock`. It depends on `OpCounter`, `Node`, and common vector typedefs.

## Integration Points
Used by metadata and storage node operation-stat subclasses and management tooling.

## Risks
Adding operation counters changes the number of elements per key and must be compatible with consumers. Removing only client keys does not affect user counters.

## Test Signals
Static checks should confirm reserved position math and that derived counter counts match exported names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeOpStats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeStore.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/NodeStore.h

## Purpose
Provides a migration typedef from the old unified `NodeStore` name to `NodeStoreServers`.

## Important APIs, Types, And Functions
Only `typedef class NodeStoreServers NodeStore;` is exported.

## Control Flow
There is no runtime control flow.

## State, Persistence, And Dependencies
No state is owned. The header includes `NodeStoreServers.h`.

## Integration Points
Legacy code can include this file while the codebase transitions to explicit client/server stores.

## Risks
New code should avoid it because it hides the server-specific semantics of the aliased type.

## Test Signals
Build coverage of legacy includes is sufficient; no runtime tests are needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreClients.cpp -->
# sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreClients.cpp

## Purpose
Implements the client-node store: a mutex-protected map from numeric client node IDs to `NodeHandle`s with add/update/delete/reference/sync operations.

## Important APIs, Types, And Functions
`addOrUpdateNode()`, `addOrUpdateNodeEx()`, `referenceNode()`, `referenceFirstNode()`, `deleteNode()`, `referenceAllNodes()`, `isNodeActive()`, `getSize()`, and `syncNodes()` are implemented.

## Control Flow
Adds generate an ID if absent via virtual `generateID()`, update existing nodes only if aliases match, update heartbeat/interface data, set client channels indirect, insert new nodes, and broadcast `newNodeCond`. `syncNodes()` assumes ordered active/master maps, computes added and removed IDs while locked, then unlocks and applies removals/adds to preserve virtual override behavior.

## State, Persistence, And Dependencies
State is the inherited store type plus `activeNodes`, `mutex`, and `newNodeCond`. It depends on `AbstractNodeStore`, `Node`, `NumNodeID`, and BeeGFS logging. No disk persistence.

## Integration Points
Used by management or server components tracking connected clients. It differs from `NodeStoreServers` by keeping alias collision rejection strict and not attaching capacity/target/state side stores.

## Risks
`generateID()` returns invalid by default, so only subclasses that implement ID generation can accept nodes without numeric IDs. `syncNodes()` relies on sorted `masterList`. Alias mismatches invalidate output ID but still return `Unchanged`, so callers must inspect `outNodeNumID` when provided.

## Test Signals
Test add, update, alias collision, generated-ID subclass behavior, delete, reference-all snapshot, sync add/remove ordering, and unsorted master-list failure modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreClients.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreClients.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreClients.h

## Purpose
Declares the client-node store specialization of `AbstractNodeStore`.

## Important APIs, Types, And Functions
The class declares add/update, delete, reference, enumeration, active check, size, and `syncNodes()`. It keeps `activeNodes`, `mutex`, `newNodeCond`, and a virtual `generateID()` hook.

## Control Flow
The API mirrors server stores but omits local-node and attached mapper/capacity-store behavior.

## State, Persistence, And Dependencies
All state is process-local. Dependencies are `Mutex`, `Condition`, `Node`, `StorageErrors`, and `AbstractNodeStore`.

## Integration Points
Used anywhere client nodes must be tracked separately from metadata/storage/management servers.

## Risks
Condition variable is broadcast on add but no wait API is exposed in this class. Subclasses must provide ID generation if zero-ID client registration is valid.

## Test Signals
Compile and subclass tests should verify virtual hooks and overrides match `AbstractNodeStore`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreClients.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreServers.cpp -->
# sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreServers.cpp

## Purpose
Implements the server-node store for metadata, storage, and management nodes. It tracks active nodes, handles alias updates, synchronizes from management lists, and propagates node removals to capacity pools, target mappers, and target state stores.

## Important APIs, Types, And Functions
Core functions include `addOrUpdateNodeEx()`, `addOrUpdateNodeUnlocked()`, `referenceNode()`, `referenceFirstNode()`, `referenceNodeByTargetID()`, `deleteNode()`, `referenceAllNodes()`, `waitForFirstNode()`, `syncNodes()`, attachment setters, `retrieveNumIDFromStringID()`, and node-ID formatting helpers.

## Control Flow
Adds reject empty aliases, generate numeric IDs if a subclass supports it, update local-node alias only, update remote aliases and interfaces, enforce store/node type compatibility, set connection-pool directness, and broadcast waiters on new nodes. Deletes refuse the local node and forward removal to optional side stores. `syncNodes()` performs an ordered diff under lock, unlocks, deletes removed IDs, sets local NIC capabilities on incoming nodes, and then add/updates them.

## State, Persistence, And Dependencies
State is `activeNodes`, optional `localNode`, channel directness default, and optional pointers to `NodeCapacityPools`, `TargetMapper`, and `TargetStateStore`. It depends on `MirrorBuddyGroupMapper` only indirectly through includes, plus logging, boost formatting, mutexes, and node/network types.

## Integration Points
Storage target resolution uses `referenceNodeByTargetID()` with `TargetMapper`. Internode sync and heartbeat handling feed `addOrUpdateNodeEx()` and `syncNodes()`. Attached stores keep capacity/target/state data consistent when nodes disappear.

## Risks
`setLocalNode()` is documented as pre-threading and mutates without locking. `syncNodes()` requires an ordered master list. Alias updates from stale heartbeats can temporarily roll back aliases as noted in comments. `stateStore->removeTarget(id.val())` assumes node IDs correspond to state IDs for that store type, which is valid only for node-style state stores.

## Test Signals
Cover local-node alias update, remote alias update, empty alias rejection, type mismatch exception, target-ID reference errors, deletion side effects, wait timeout/signal behavior, sync ordering, and local node preservation during sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreServers.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreServers.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreServers.h

## Purpose
Declares the server-node store and its integration hooks for capacity pools, target mappings, and target state data.

## Important APIs, Types, And Functions
The class exposes add/update/delete/reference/sync APIs, `referenceNodeByTargetID()`, wait-for-first-node, side-store attachment, and log-format helpers. It stores `localNode`, `channelsDirectDefault`, active nodes, and optional side-store pointers.

## Control Flow
The header documents that `setLocalNode()` is intended before multithreading and inserts the local node into `activeNodes`, also adding it to attached capacity pools as low capacity.

## State, Persistence, And Dependencies
State is in memory under `Mutex` except pre-threading local-node setup. Dependencies include `Node`, `NodeCapacityPools`, `TargetMapper`, `TargetStateStore`, and `AbstractNodeStore`.

## Integration Points
Used by server registries and target resolution paths; legacy `NodeStore.h` aliases this type.

## Risks
The `generateID()` default returns invalid, so only management subclasses can assign IDs. `localNode` is owned by the app, not by the store.

## Test Signals
Subclass build tests should verify override behavior, side-store attachment ordering, and local-node insertion assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreServers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeType.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/NodeType.h

## Purpose
Defines BeeGFS node service types and their stream formatting.

## Important APIs, Types, And Functions
`NodeType` values are invalid, metadata, storage, client, and management. `operator<<` formats them as service names such as `beegfs-meta` and `beegfs-storage`.

## Control Flow
Formatting saves/restores stream flags and writes decimal names or an unknown marker.

## State, Persistence, And Dependencies
No state. Depends on iostreams and Boost ios state saver.

## Integration Points
Used in logs, node IDs, connection endpoint strings, and store type validation.

## Risks
Numeric enum values are protocol-visible in practice; changes require compatibility review.

## Test Signals
Verify stream output for known and unknown values and keep service names aligned with tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NodeType.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NumNodeID.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/NumNodeID.h

## Purpose
Defines the strongly typed numeric node ID used across BeeGFS node, target, and store code.

## Important APIs, Types, And Functions
`NumNodeID` is `NumericID<uint32_t, NumNodeIDTag>`. The header also defines list/vector typedefs and iterators.

## Control Flow
No runtime logic.

## State, Persistence, And Dependencies
No owned state. It depends on `NumericID.h`. The comment requires sync with the client module.

## Integration Points
Used by node stores, target maps, root info, capacity pools, and serialization contracts.

## Risks
Changing underlying width or semantics breaks on-wire and client-kernel compatibility.

## Test Signals
Serialization, ordering, zero-invalid semantics, and client-module ABI consistency should be checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/NumNodeID.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/OpCounter.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/OpCounter.h

## Purpose
Defines atomic filesystem operation counters and concrete metadata/storage counter classes.

## Important APIs, Types, And Functions
`OpCounter` stores an `AtomicUInt64Vector` with element zero as the total sum. `increaseOpCounter()`, `increaseStorageOpBytes()`, `getOpCounter()`, `getNumCounter()`, and `addCountersToVec()` are the key APIs. `MetaOpCounter` and `StorageOpCounter` size the base by their enum sentinel.

## Control Flow
Incrementing validates the operation index, increments the specific counter, and increments the sum. Storage read/write byte accounting first increments the read/write op counter and then updates the corresponding byte counter.

## State, Persistence, And Dependencies
State is atomic counters only. Dependencies include `Atomics`, `LogContext`, `OpCounterTypes`, and common vector typedefs.

## Integration Points
Used by `NodeOpStats` maps and operation handlers in metadata/storage services.

## Risks
Passing the sum element as an operation is rejected only under debug for that specific case, while out-of-range is always rejected. Directly incrementing READBYTES/WRITEBYTES through `increaseOpCounter()` would skew op counts, so callers should use `increaseStorageOpBytes()`.

## Test Signals
Validate sum increments, invalid operation logging, byte counter coupling, vector export order, and enum-count compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/OpCounter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/OpCounterTypes.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/OpCounterTypes.h

## Purpose
Defines metadata and storage operation counter enums plus short string mappings for display/export tools.

## Important APIs, Types, And Functions
`MetaOpCounterTypes`, `StorageOpCounterTypes`, and `OpToStringMapping::mapMetaOpNum()`/`mapStorageOpNum()` are the key exports. Sentinel values determine counter vector lengths.

## Control Flow
Mapping functions switch over known enum values and return the numeric value as a string for unknown inputs.

## State, Persistence, And Dependencies
No mutable state. It depends on `StringTk`.

## Integration Points
Used by `OpCounter`, `NodeOpStats`, server operation accounting, and `fhgfs-ctl` presentation.

## Risks
New enum values must be inserted immediately before the sentinel and added to the mapping to preserve compatibility and usability. Byte counters are not intended as independent operation counters.

## Test Signals
Tests should verify every enum except sentinel has a stable nonnumeric mapping and that counter array sizes match sentinel values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/OpCounterTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/RootInfo.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/RootInfo.h

## Purpose
Stores the current filesystem root owner node ID and whether the root is buddy mirrored.

## Important APIs, Types, And Functions
`getID()`, `getIsMirrored()`, `set()`, and `setIfDefault()` are the complete API.

## Control Flow
Every operation locks a `std::mutex`. `setIfDefault()` writes only when `id` is still invalid/zero.

## State, Persistence, And Dependencies
State is `NumNodeID id` and `bool isMirrored`. No serialization is defined here; persistence is external. Depends on `NumNodeID` and `<mutex>`.

## Integration Points
Used by management/metadata code that needs root ownership and mirroring status.

## Risks
`set()` can overwrite established root info unconditionally. Callers relying on first-writer-wins must use `setIfDefault()`.

## Test Signals
Concurrent get/set, first-writer behavior, mirrored flag propagation, and zero-ID initialization should be validated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/RootInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/StoragePoolStore.cpp -->
# sources/distributed-fs/beegfs/common/source/common/nodes/StoragePoolStore.cpp

## Purpose
Implements the storage-pool registry that owns `StoragePool` objects and enforces one-pool membership for storage targets and buddy groups.

## Important APIs, Types, And Functions
Defines constants for default/invalid/max pool IDs and implements `createPool()`, `moveTarget()`, `moveBuddyGroup()`, `setPoolDescription()`, `addTarget()`, `removeTarget()`, `addBuddyGroup()`, `removeBuddyGroup()`, `findFreeID()`, pool getters, `syncFromVector()`, and `getSize()`.

## Control Flow
Construction creates the default pool unless skipped. `createPool()` chooses an ID if requested, inserts a new pool, then moves requested buddy groups and targets from the default pool only. Move operations resolve source/destination pools, remove from the old pool, and add to the new pool, moving buddy-group member targets as well when a buddy mapper is present. Adds scan all pools to prevent duplicate membership. Removal scans pools and returns the pool ID from which an item was removed.

## State, Persistence, And Dependencies
State is `storagePools` protected by `RWLock`, plus pointers to `MirrorBuddyGroupMapper` and `TargetMapper`. Serialization/deserialization is declared in the header and stores pool values. Dependencies include `StoragePool`, `FhgfsOpsErr`, buddy group mapping, target mapping, and logging.

## Integration Points
`TargetMapper` auto-adds/removes targets when mappings change. `StoragePool` capacity pools are used by placement. Management operations create/move/query pools.

## Risks
`addBuddyGroup()` returns `FhgfsOpsErr_EXISTS` after a successful new add, which looks like a bug and can make callers treat success as failure. `moveTarget()` takes only a read lock on the pool map while mutating individual pools; the pool map is stable but lock-order interactions matter. Pool creation can partially succeed and return `INVAL` after the pool has been inserted with only successful moves. Target node lookup during moves may return zero if `TargetMapper` is stale.

## Test Signals
Cover default pool creation, generated IDs, duplicate IDs, create with valid/invalid target sets, partial failure semantics, target and buddy moves, buddy target movement, duplicate add behavior, the `addBuddyGroup()` return code, serialization/deserialization, and concurrent add/move/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/StoragePoolStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/StoragePoolStore.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/StoragePoolStore.h

## Purpose
Declares the storage-pool registry and its serialization hooks.

## Important APIs, Types, And Functions
Static IDs define default and invalid pools. Public APIs create pools, move targets/buddy groups, set descriptions, add/remove/query items, sync from vectors, and export pool vectors. Protected hooks include `makePool()` for subclasses and map-value serialization/deserialization.

## Control Flow
The serialization helpers write only pool values and rebuild keys from each pool ID during deserialization, using virtual `initFromDesBuf()` so derived pool types can participate.

## State, Persistence, And Dependencies
`storagePools` is protected by `RWLock`. Pointers to buddy and target mappers are non-owning integration hooks. Serialized state includes pool contents and capacity-pool data via `StoragePool`.

## Integration Points
The store sits between target mapping, mirror buddy mapping, capacity-pool selection, and management pool operations.

## Risks
Non-owning mapper pointers must outlive the store. No explicit default-pool invariant check exists after `syncFromVector()` or deserialization.

## Test Signals
Subclass serialization, missing default pool after sync, non-owning pointer lifetime in fixtures, and pool ID key reconstruction should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/StoragePoolStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/TargetCapacityPools.cpp -->
# sources/distributed-fs/beegfs/common/source/common/nodes/TargetCapacityPools.cpp

## Purpose
Implements target capacity pools with both plain target membership and target grouping by owning node, enabling random placement as well as inter-domain and intra-domain placement choices.

## Important APIs, Types, And Functions
Implements add/update/remove/sync/list export, `chooseStorageTargets()`, `chooseStorageTargetsRoundRobin()`, `chooseTargetsInterdomain()`, `chooseTargetsIntradomain()`, grouping helpers, pool lookup, state formatting, and pool-type string conversion.

## Control Flow
Mutation updates `pools`, `groupedTargetPools`, and `targetMap` under write lock. Sync builds temporary plain and grouped pools outside the write-lock section and swaps them in. Normal target selection tries normal, low, then emergency pools, with optional preferred-target stages. Interdomain selection chooses one random target from each selected node group and strips already-used nodes when falling through to lower pools. Intradomain selection chooses one random node group and then targets within that same group. Round-robin uses `lastRoundRobinTarget`.

## State, Persistence, And Dependencies
State is `pools`, `groupedTargetPools`, `targetMap`, dynamic pool limits, random generator, and round-robin cursor. Serialization includes `pools`, `groupedTargetPools`, and `targetMap`, but not the cursor or dynamic-limit config. It depends on `TargetMapper` types, `RWLockGuard`, `MinMaxStore`, `DynamicPoolLimits`, `NumNodeID`, and common containers.

## Integration Points
`StoragePool` owns one for its targets. `TargetMapper` and storage-pool management feed target-to-node mappings. File placement and mirror selection can request ordinary, interdomain, or intradomain target sets.

## Risks
Targets without node mappings are omitted from grouped pools, so inter/intra-domain selectors can see fewer targets than plain selectors. A condition in preferred selection reads `if (!outTargets->empty() >= minNumRequiredTargets)`, comparing a boolean with the threshold and likely not doing what the comment intends. Inter/intra-domain methods note they do not try hard to satisfy `minNumRequiredTargets`. Round-robin state is not persisted. Callers must avoid `numTargets == 0` before helpers compute `activeTargetsSize / numTargets`.

## Test Signals
Test target movement between pools and nodes, grouped map cleanup, sync with missing target mappings, preferred target fallback, the suspicious boolean comparison, interdomain uniqueness, intradomain same-node behavior, round-robin wraparound, empty/zero target requests, and serialization round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/TargetCapacityPools.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/TargetCapacityPools.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/TargetCapacityPools.h

## Purpose
Declares the target capacity-pool model, including plain target pools and node-grouped pools for failure-domain-aware selection.

## Important APIs, Types, And Functions
Defines `TargetMap`, `GroupedTargets`, `GroupedTargetsVector`, and class `TargetCapacityPools`. Public APIs cover mutation, sync, selection, inter/intra-domain placement, pool lookup, state dump, string conversion, and serialization.

## Control Flow
Private helpers implement unlocked add/update, removal from other pools, plain/preferred selection, interdomain/intradomain selection, grouping by node, stripping used nodes, and target-to-node lookup.

## State, Persistence, And Dependencies
The class owns an `RWLock`, dynamic config, plain pools, grouped pools, target map, random generator, and round-robin cursor. Serialization covers placement-critical membership and mapping state.

## Integration Points
Used by `StoragePool` and storage target placement. Shares `CapacityPoolType`/`DynamicPoolLimits` concepts with `NodeCapacityPools`.

## Risks
The header documents that not all targets may be in grouped pools if mapping is unknown. Selection helpers assume caller-held locks and non-empty inputs.

## Test Signals
Compile-time and serialization tests should ensure grouped types remain stable and that client/server capacity pool counts align.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/TargetCapacityPools.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/TargetMapper.cpp -->
# sources/distributed-fs/beegfs/common/source/common/nodes/TargetMapper.cpp

## Purpose
Implements the mapping from storage target IDs to owning node IDs and coordinates related state in storage pools, target states, and quota stores.

## Important APIs, Types, And Functions
`mapTarget()`, `unmapTarget()`, `unmapByNodeID()`, `syncTargets()`, `getMappingAsLists()`, `getTargetsByNode()`, and attachment methods are implemented.

## Control Flow
`mapTarget()` writes the mapping and detects new targets by size change. New targets are added to the storage-pool store, initial target state is created as probably-offline/good, and quota stores are initialized. If storage-pool add fails, the target mapping is rolled back. Unmap paths remove targets and cascade to attached stores. `syncTargets()` swaps a whole target map and then ensures attached state/quota stores know every target.

## State, Persistence, And Dependencies
State is `targets` under `RWLock` plus non-owning pointers to `TargetStateStore`, `StoragePoolStore`, and `ExceededQuotaPerTarget`. No disk persistence here.

## Integration Points
Node stores use `unmapByNodeID()` on server deletion. Storage-pool management uses target mappings for node association. Request routing resolves target IDs to nodes.

## Risks
Remapping an existing target to a new node does not update storage-pool membership node metadata because side-store initialization runs only for new targets. `syncTargets()` does not remove stale attached state/quota entries that are no longer present. Attached store calls happen while holding this mapper lock, so lock ordering must be consistent.

## Test Signals
Cover new map success/failure rollback, remap existing target, unmap cascade, unmap-by-node multi-remove, sync with added/removed targets, list ordering, and attached-store lock-order stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/TargetMapper.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/TargetMapper.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/TargetMapper.h

## Purpose
Declares the target-to-node mapping service and its side-store attachment hooks.

## Important APIs, Types, And Functions
Public APIs map/unmap/sync/query targets and attach target-state, storage-pool, and quota stores. Inline getters provide node lookup, size, existence, and full mapping copy.

## Control Flow
The API promises `NumNodeID{}` for unknown targets and `std::pair<FhgfsOpsErr,bool>` for mapping outcomes.

## State, Persistence, And Dependencies
`targets` is protected by `RWLock`. Attached store pointers are non-owning. Depends on `StoragePoolStore`, `TargetCapacityPools` type aliases, `TargetStateStore`, and quota stores.

## Integration Points
Central integration point for target routing, state initialization, pool membership, and quota tracking.

## Risks
Non-owning side stores must outlive the mapper. Copying full mappings can be expensive for large clusters.

## Test Signals
Verify unknown target zero semantics, map copy consistency under concurrent mutation, and side-store attachment sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/TargetMapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/TargetStateInfo.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/TargetStateInfo.h

## Purpose
Defines target reachability and consistency state types, their combined representation, and timestamped internal state records.

## Important APIs, Types, And Functions
`TargetReachabilityState`, `TargetConsistencyState`, `CombinedTargetState`, and `TargetStateInfo` are exported. Serialization maps state enums to `uint8_t`. `TargetStateInfo` extends combined state with `Time lastChangedTime`.

## Control Flow
Assignment from `CombinedTargetState` updates `lastChangedTime`; comparison with combined state ignores timestamp.

## State, Persistence, And Dependencies
State is value-object data. The comment requires enum sync with the client. Depends on `Time` and serialization helpers.

## Integration Points
Used by `TargetStateStore`, `TargetMapper`, storage target info, mirror buddy synchronization, and network messages.

## Risks
Enum order is protocol-visible. Timestamp is relative and not synchronized across nodes, so it is for local freshness only.

## Test Signals
Serialization width, default state offline/good, timestamp update on assignment, and client enum alignment should be checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/TargetStateInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/TargetStateStore.cpp -->
# sources/distributed-fs/beegfs/common/source/common/nodes/TargetStateStore.cpp

## Purpose
Implements a thread-safe map of target IDs to reachability/consistency state and coordinated atomic synchronization with mirror buddy groups.

## Important APIs, Types, And Functions
Implements `addIfNotExists()`, `removeTarget()`, `syncStatesAndGroups()`, `syncStatesFromLists()`, `getStatesAndGroups()`, `getStatesAsLists()`, `getStatesAsListsUnlocked()`, and string conversion helpers.

## Control Flow
Bulk sync builds a temporary `TargetStateInfoMap`, then swaps it under write lock. `syncStatesAndGroups()` also locks the buddy-group mapper write lock and swaps group mappings under the same critical section, updating the local group ID if a group contains the local node. Reads of states plus groups take both locks in read mode to avoid observing split-brain transitions.

## State, Persistence, And Dependencies
State is `statesMap` protected by `RWLock` and the `NodeType` used for logs. Persistence is external via serialized lists/messages. Dependencies include `MirrorBuddyGroupMapper`, `ZipIterator`, and `TargetStateInfo`.

## Integration Points
`TargetMapper` creates/removes entries. Management state sync and mirror buddy group messages use the atomic group/state APIs. Node stores may attach a state store for cleanup.

## Risks
All callers must use the combined state/group APIs when mirror groups are involved; otherwise observers can see inconsistent failover state. `syncStatesFromLists()` zips lists and silently stops at shortest input if list lengths differ. Lock ordering with buddy groups must stay consistent.

## Test Signals
Cover add-if-not-exists idempotence, list sync with mismatched lengths, atomic state/group swap, local group detection, read consistency under concurrent sync, and string conversion of invalid enums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/TargetStateStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/TargetStateStore.h -->
# sources/distributed-fs/beegfs/common/source/common/nodes/TargetStateStore.h

## Purpose
Declares the target-state store used for reachability and consistency tracking.

## Important APIs, Types, And Functions
Public APIs add/remove targets, sync states alone or with buddy groups, export states as maps/lists, convert states to strings, and inline get/set individual or all states.

## Control Flow
Inline setters update entries by assigning `CombinedTargetState`, which refreshes `TargetStateInfo` timestamps. `getStateUnlocked()` and `getStateInfoUnlocked()` are private helpers behind locked public APIs.

## State, Persistence, And Dependencies
`statesMap` is protected by `RWLock`. `NodeType` is retained for logging/context. Depends on `TargetStateInfo` and mirror buddy group map declarations.

## Integration Points
Attached by `TargetMapper` and node stores; consumed by state sync messages and mirror buddy workflows.

## Risks
Inline `setState()` with an unknown ID will create a new state entry through map indexing. The `setAllStates()` helper changes reachability while preserving consistency.

## Test Signals
Verify unknown-ID behavior for each setter, timestamp updates, list export order, and lock-free helper usage only under locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/TargetStateStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/pch.h -->
# sources/distributed-fs/beegfs/common/source/common/pch.h

## Purpose
Provides a precompiled-header include set for common C/C++ standard library headers used across BeeGFS common code.

## Important APIs, Types, And Functions
No project APIs are defined. It includes assertions, errno, C stdlib/string/integer headers, algorithms, chrono, memory, mutex/condition variables, thread, vector, set, map, unordered containers, and utility.

## Control Flow
No runtime control flow.

## State, Persistence, And Dependencies
No state. It reduces compile overhead when PCH is enabled.

## Integration Points
Included by build configuration rather than normal source logic.

## Risks
Adding project headers here can increase rebuild blast radius or hide missing direct includes; currently it stays limited to common standard headers.

## Test Signals
Build with and without PCH should produce the same diagnostics for source files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/pch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/ChunksBlocksVec.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/ChunksBlocksVec.h

## Purpose
Stores per-stripe-target block counts for chunk files, mainly to support sparse-file stat accounting.

## Important APIs, Types, And Functions
`setNumBlocks()`, `getNumBlocks()`, `getBlockSum()`, serialization, equality, and constructors are exported.

## Control Flow
The vector lazily resizes on first set using the caller-provided stripe target count. Out-of-range get/set logs an error and backtrace, returning or doing nothing.

## State, Persistence, And Dependencies
State is `UInt64Vector chunkBlocksVec`. It serializes directly and is embedded in `StatData` for disk metadata. Depends on serialization helpers, logging, and `<numeric>`.

## Integration Points
`StatData` uses it to track exact block usage per chunk when sparse files are detected.

## Risks
The vector size is determined by the first `setNumBlocks()` call; later stripe-pattern size changes need careful handling. Bounds errors are logged but not fatal.

## Test Signals
Test lazy initialization, per-target set/get, sum, sparse `StatData` serialization, and out-of-range logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/ChunksBlocksVec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/EntryInfo.cpp -->
# sources/distributed-fs/beegfs/common/source/common/storage/EntryInfo.cpp

## Purpose
Implements equality for `EntryInfo`.

## Important APIs, Types, And Functions
`EntryInfo::operator==()` compares owner node, parent entry ID, entry ID, file name, entry type, and feature flags.

## Control Flow
No branching beyond chained equality.

## State, Persistence, And Dependencies
No extra state. Includes serialization/logging headers through the implementation unit.

## Integration Points
Equality is used by metadata operations, tests, and message handlers that compare file-entry identity.

## Risks
Equality includes `fileName`, so renamed entries with the same entry ID compare different. It ignores any subclass fields such as `EntryInfoWithDepth::entryDepth`.

## Test Signals
Verify equality changes on each field and that base comparisons do not accidentally include derived state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/EntryInfo.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/EntryInfo.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/EntryInfo.h

## Purpose
Defines the metadata needed to locate or operate on an inode or chunk files: owner metadata node, parent ID, entry ID, file name, type, and feature flags.

## Important APIs, Types, And Functions
Defines `ENTRYINFO_FEATURE_INLINED`, `ENTRYINFO_FEATURE_BUDDYMIRRORED`, `EntryInfo_PARENT_ID_UNKNOWN`, list typedefs, constructors, `set()` overloads, feature-flag setters/getters, field getters, equality, and serialization.

## Control Flow
Serialization writes entry type as `uint32_t`, feature flags, three 4-byte-aligned strings, owner node ID, and padding. Feature setters set or clear individual bits.

## State, Persistence, And Dependencies
This is a serialized value object and must remain synchronized with client-side `EntryInfo.h`. Depends on `NumNodeID` and `StorageDefinitions`.

## Integration Points
Used in metadata messages, inode lookup, path traversal, and client/server protocol contracts.

## Risks
Wire layout changes require client-module updates. `ENTRYINFO_FEATURE_INLINED` may be outdated by design, so callers should not assume it is authoritative without validation.

## Test Signals
Serialization compatibility, flag toggling, owner/parent/entry identity, aligned string handling, and client-module golden vectors are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/EntryInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/EntryInfoWithDepth.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/EntryInfoWithDepth.h

## Purpose
Extends `EntryInfo` with a 0-based path depth value.

## Important APIs, Types, And Functions
Constructors, `set()`, `getEntryDepth()`, `setEntryDepth()`, and serialization via `serdes::base<EntryInfo>` plus `entryDepth`.

## Control Flow
No complex control flow; it delegates base-field handling to `EntryInfo`.

## State, Persistence, And Dependencies
Adds `uint32_t entryDepth` to the base serialized entry information.

## Integration Points
Used when callers need both entry identity and its depth in a path traversal or listing workflow.

## Risks
Base equality does not include depth unless callers explicitly compare the derived field.

## Test Signals
Serialize/deserialize base plus depth, constructor from base defaults depth to zero, and depth mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/EntryInfoWithDepth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/FileEvent.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/FileEvent.h

## Purpose
Defines file event types and a serializable event record for filesystem activity notifications.

## Important APIs, Types, And Functions
`FileEventType` enumerates flush, truncate, setattr, close/create/remove/link/rename/open events, blocked/stripe/inode-lock events, and more. `FileEvent` stores type, path, optional target validity, and target.

## Control Flow
Serialization writes type and path, then writes target only when `targetValid` is true.

## State, Persistence, And Dependencies
Value-object state only. `FileEventType` serializes as `uint32_t`.

## Integration Points
Used by event logging/notification paths that report file operations and optional target paths.

## Risks
Enum values are persisted/on-wire once events are consumed externally. Optional target must be gated consistently by `targetValid`.

## Test Signals
Round-trip events with and without target, every enum value, and compatibility with event consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/FileEvent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/Metadata.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/Metadata.h

## Purpose
Defines metadata directory names, root/disposal IDs, hash fanout constants, and special subdirectory names for BeeGFS metadata storage.

## Important APIs, Types, And Functions
Exports constants for root/disposal IDs, inode and dentry fanout/subdir names, ID-based access subdir marker, lost+found, and buddy mirror subdir.

## Control Flow
No runtime logic.

## State, Persistence, And Dependencies
No state. These constants shape on-disk metadata layout.

## Integration Points
Used by metadata server path construction, recovery, disposal handling, and buddy-mirror metadata storage.

## Risks
Changing constants breaks existing on-disk layouts. The ID-based access subdir marker is noted as potentially conflicting with user names.

## Test Signals
Layout tests should verify generated inode/dentry paths and migration/backward compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/Metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/Path.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/Path.h

## Purpose
Implements a small normalized path value type with cached separator offsets, component access, concatenation, comparison, and serialization.

## Important APIs, Types, And Functions
Constructors/assignment, `str()`, `absolute()`, `front()`, `back()`, `empty()`, `dirname()`, `size()`, `operator[]`, `/=` overloads, `/` friends, equality, stream output, and serializer/deserializer functions are provided.

## Control Flow
Construction and deserialization call `updateDirSeparators()`, which compresses consecutive slashes and removes a trailing slash. Component access uses cached separator positions and throws `std::out_of_range` for invalid indexes. Concatenation rejects absolute right-hand paths and updates separator offsets incrementally.

## State, Persistence, And Dependencies
State is `pathStr` plus `dirSeparators`. Serialization stores only the string and rebuilds separators. Depends on serialization, strings, vectors, exceptions, and debug logging.

## Integration Points
Used wherever common code needs normalized path manipulation without repeatedly parsing slashes.

## Risks
`updateDirSeparators()` does not clear `dirSeparators` before repopulating, so assignment/deserialization after prior content can leave stale offsets unless object lifecycle avoids that; this deserves tests. Absolute root path `/` normalizes to an empty string after trailing slash removal, which may be significant. Concatenation throws on absolute RHS.

## Test Signals
Test repeated assignment/deserialization, duplicate slashes, trailing slash, root path, absolute/relative indexing, dirname of single component, concatenation with empty paths, absolute RHS exceptions, and serialization round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/Path.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/PathInfo.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/PathInfo.h

## Purpose
Represents chunk-location metadata for a file, including original parent UID/entry ID and flags for layout generation and stub files.

## Important APIs, Types, And Functions
Defines `PATHINFO_FEATURE_ORIG`, `PATHINFO_FEATURE_ORIG_UNKNOWN`, `PATHINFO_FEATURE_IS_STUB`, list typedefs, constructors, setters/getters, `hasOrigFeature()`, `isStub()`, equality, and serialization.

## Control Flow
Serialization always writes flags and conditionally writes `origParentUID` and aligned `origParentEntryID` only if `PATHINFO_FEATURE_ORIG` is set.

## State, Persistence, And Dependencies
State is `flags`, `origParentUID`, and `origParentEntryID`. It is a protocol/disk value object.

## Integration Points
Used by metadata and storage code to locate chunk files across old/new layout schemes and to mark stub files.

## Risks
If the ORIG flag is absent, original parent fields are not serialized, so consumers must respect the flag. `PATHINFO_FEATURE_ORIG_UNKNOWN` requires later resolution.

## Test Signals
Round-trip with and without ORIG, stub flag detection, equality on static fields, and migration from old 2012.10 to 2014.01-style layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/PathInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/RdmaInfo.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/RdmaInfo.h

## Purpose
When `BEEGFS_NVFS` is enabled, defines RDMA buffer descriptor metadata supplied by clients and an iterator-style API to consume it.

## Important APIs, Types, And Functions
`RDMA_MAX_DMA_COUNT`, `RdmaInfo` public serialized fields (`count`, `tag`, `key`, address/length/offset arrays, `status`), `more()`, `next()`, `isValid()`, and serialization.

## Control Flow
Serialization writes count/tag/key, validates count, logs and returns early if count is too large, then serializes each buffer triple. `next()` returns the current triple and advances `cur`.

## State, Persistence, And Dependencies
State is request-supplied RDMA descriptors plus private iterator cursor. Only compiled under `BEEGFS_NVFS`. Dependencies on logging/string helpers are implied by the serialization body.

## Integration Points
Used by NVFS/RDMA read/write message paths to describe remote DMA buffers.

## Risks
`isValid()` uses `count < RDMA_MAX_DMA_COUNT`, so exactly 64 buffers are invalid despite arrays sized 64; this may be intentional or off-by-one. Serialization returns after logging invalid count, leaving deserializer state considerations to callers.

## Test Signals
Compile with and without `BEEGFS_NVFS`, validate zero/one/max/excess counts, iterator exhaustion, serialized triples, and error handling for invalid count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/RdmaInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/RemoteStorageTarget.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/RemoteStorageTarget.h

## Purpose
Represents remote storage target policy metadata: version, cooldown period, file policies, and a vector of remote target IDs.

## Important APIs, Types, And Functions
Constructors, `set()`, `reset()`, `hasInvalidIds()`, `hasDuplicateIds()`, `hasInvalidVersion()`, `validateWithDetails()`, serialization, getters, `setRstIds()`, and `toStr()` are provided.

## Control Flow
Default constructor leaves version zero/invalid. Constructors with IDs set default version 1.0, cooldown 120, and default file policy. Validation accumulates human-readable reasons.

## State, Persistence, And Dependencies
State is version bytes, cooldown, reserved field, policy bits, and `rstIdVec`. It serializes all fields. Depends on storage definitions, vectors/sets, and string streams.

## Integration Points
Used by metadata/policy code for files that can refer to remote storage targets.

## Risks
A default-constructed object is invalid until initialized. Validation checks duplicate/zero IDs but not policy semantics or cooldown ranges.

## Test Signals
Validate default invalid object, constructor defaults, reset, duplicate IDs, ID zero, serialization, and `toStr()` formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/RemoteStorageTarget.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StatData.cpp -->
# sources/distributed-fs/beegfs/common/source/common/storage/StatData.cpp

## Purpose
Implements dynamic file attribute aggregation from storage chunk metadata and equality for `StatData`.

## Important APIs, Types, And Functions
`updateDynamicFileAttribs()` updates file size, timestamps, block accounting, sparse flag, and ctime. `operator==()` compares all persisted/stat fields including chunk block vector and metadata version.

## Control Flow
The update method first checks whether any chunk info has a nonzero storage version; if none do, static metadata remains. It scans chunk info to find the last target with the maximum chunk count, max mtime/atime, per-target block counts, and then computes file length using stripe order and chunk size. It compares estimated blocks to actual used blocks with a grace threshold to set/unset the sparse flag, updates atime, ctime when mtime or size changed, mtime, and size.

## State, Persistence, And Dependencies
Mutates `StatData` fields and `ChunksBlocksVec`. Depends on `ChunkFileInfoVec`, `StripePattern`, `TimeAbs`, serialization/logging includes, and constants from `StatData.h`.

## Integration Points
Called when metadata servers merge dynamic attributes from storage targets, especially after close/stat workflows.

## Risks
Correctness depends on `fileInfoVec` order matching stripe target order and `stripePattern->getNumStripeTargetIDs()`. Partial dynamic info uses max(MDS, chunk) timestamps, while full info trusts chunk info. Sparse detection is heuristic with grace blocks.

## Test Signals
Cover no valid dynamic attributes, partial versus full dynamic info, multi-stripe file-size calculation, sparse and non-sparse thresholds, ctime update rules, zero chunks, stale chunk info, and equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StatData.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StatData.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/StatData.h

## Purpose
Defines BeeGFS stat metadata, timestamp mirroring, sparse-file block accounting, and multiple serialization formats for network and disk inode/dentry contexts.

## Important APIs, Types, And Functions
`StatDataFormat`, `MirroredTimestamps`, and `StatData` are the main exports. Constructors initialize fake data, full stat data, or new file data. APIs cover dynamic update, equality, fake/init/set operations, sparse flags, mirrored timestamps, file size/times/mode/uid/gid/nlink/meta-version getters/setters, block accounting, and `serializeFmt()`/`serializeAs()`.

## Control Flow
`serializeFmt()` conditionally writes flags/mode, network `numBlocks` versus disk sparse `chunkBlocksVec`, timestamps, file-size/nlink/meta-version depending on dir-inode format, uid/gid, and trailing mode if flags were not included.

## State, Persistence, And Dependencies
State includes flags, file size, creation/ctime, nlink, settable attributes, metadata version, and `ChunksBlocksVec`. The header explicitly must stay in sync with client-module `StatData.h`, with server-specific disk serialization differences.

## Integration Points
Used by metadata inodes, dentries, network stat responses, mirroring timestamp sync, and storage dynamic attribute aggregation.

## Risks
Format flags are compact and easy to misuse. Network serialization sends estimated/actual block count but not full chunk block vector. Sparse flag correctness depends on prior dynamic updates. Some getters return `int` for `creationTimeSecs` despite the field being `int64_t`.

## Test Signals
Golden serialization for all formats, sparse/non-sparse block count, mirrored timestamp round trip, constructors, hard-link mutations, metadata version, and client compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StatData.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StorageDefinitions.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/StorageDefinitions.h

## Purpose
Defines shared storage flags, file entry types, file inode modes, settable attributes, lock request types, and target path/fd maps.

## Important APIs, Types, And Functions
Exports open flags/masks, setattr flags, entry lock flags/masks, `DirEntryType`, `FileInodeMode`, `EntryLockRequestType`, `SettableFileAttribs`, `TargetPathMap`, and `TargetFDMap`. `DirEntryType` serializes as `uint8_t` and has stream/macro helpers.

## Control Flow
No complex logic; macros classify entry types and stream output maps enum values to readable names.

## State, Persistence, And Dependencies
No global state. The header must stay in sync with the client module because flags and enum values cross user/kernel/server boundaries.

## Integration Points
Used by `EntryInfo`, `StatData`, open/setattr/locking messages, and storage target path management.

## Risks
Changing numeric flag/enum values breaks protocol and on-disk expectations. Macros do not provide type safety.

## Test Signals
Client/server header compatibility, stream output, macro classification, and serialization width should be checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StorageDefinitions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StorageErrors.cpp -->
# sources/distributed-fs/beegfs/common/source/common/storage/StorageErrors.cpp

## Purpose
Defines the `FhgfsOpsErr` string/system-error mapping and conversion helpers.

## Important APIs, Types, And Functions
`__FHGFSOPS_ERRLIST`, `operator<<`, `FhgfsOpsErrTk::toSysErr()`, and `FhgfsOpsErrTk::fromSysErr()` are implemented.

## Control Flow
Conversions index the table when the enum value is in range. Unknown values log a critical error and backtrace; stream output prints an unknown marker, while `toSysErr()` falls back to `EPERM`. `fromSysErr()` returns the first table entry with a matching system errno, otherwise internal error.

## State, Persistence, And Dependencies
The mapping table is static const process data. Depends on POSIX errno values, logging, and Boost ios state saver.

## Integration Points
Used across storage, metadata, network response handling, and syscall translation paths.

## Risks
The mapping from sys errno back to BeeGFS error is not one-to-one and first-match based. Table order must remain synchronized with the enum. A former error slot remains as "Removed" with code 999.

## Test Signals
Verify every enum maps in range, table size matches enum, unknown-value logging/fallback, `fromSysErr()` expected first matches, and stream formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StorageErrors.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StorageErrors.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/StorageErrors.h

## Purpose
Declares BeeGFS operation error codes, their mapping table type, conversion toolkit, serialization width, and vector typedefs.

## Important APIs, Types, And Functions
`FhgfsOpsErrListEntry`, `FhgfsOpsErr`, `SerializeAs<FhgfsOpsErr>`, `FhgfsOpsErrTk`, and stream operator declaration are exported.

## Control Flow
No implementation logic in the header beyond table-size macro and constructors being private for toolkit class.

## State, Persistence, And Dependencies
The enum is signed via a negative dummy to avoid bad casts from negative return values. It must stay in sync with the client module and `__FHGFSOPS_ERRLIST`.

## Integration Points
Used almost everywhere an operation can return BeeGFS-level status.

## Risks
Adding/reordering errors is protocol-visible and must update both table and client module. Serializes as `int`.

## Test Signals
Compile-time/table-size checks, client sync, and serialization of negative dummy avoidance should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StorageErrors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StoragePool.cpp -->
# sources/distributed-fs/beegfs/common/source/common/storage/StoragePool.cpp

## Purpose
Implements a single storage pool's membership and capacity-pool side effects for targets and buddy groups.

## Important APIs, Types, And Functions
Implements target add/remove/has/get/get-and-remove, buddy-group add/remove/has/get/get-and-remove, description getter/setter, and ID getter.

## Control Flow
Public mutators lock `mutex` and call unlocked helpers. Adding a new target inserts into `members.targets` and adds it to `targetsCapacityPools` as low capacity. Removing a target removes it from both members and capacity pools. Buddy group operations mirror this with `buddyCapacityPools`. Bulk get-and-remove swaps the member set out and removes each ID from the corresponding capacity pool.

## State, Persistence, And Dependencies
State is `id`, `description`, member target/buddy sets, and owned target/buddy capacity pool objects declared in the header. No disk I/O here; serialization is in the header.

## Integration Points
Owned by `StoragePoolStore`; target and buddy mapping changes use this object to keep placement pools aligned.

## Risks
New targets/buddy groups default to `CapacityPool_LOW` until dynamic capacity updates move them. Unlocked helpers require external locking, especially when moving buddy groups and associated targets between pools.

## Test Signals
Test duplicate add idempotence, capacity-pool side effects, bulk removal, description locking, and move helpers through `StoragePoolStore`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StoragePool.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StoragePool.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/StoragePool.h

## Purpose
Declares the storage-pool value/object that groups target IDs and mirror buddy group IDs and owns capacity-pool selectors for each.

## Important APIs, Types, And Functions
Constructors create `TargetCapacityPools` and `NodeCapacityPools`; public APIs query/mutate ID, description, targets, buddy groups, and expose capacity-pool pointers. Serialization writes ID, description, members, and both capacity pools. Shared-pointer serialization helpers and virtual `initFromDesBuf()` support derived pool types.

## Control Flow
Comparison operators compare only numeric pool IDs. Friend `StoragePoolStore` can lock and call unlocked helpers for compound moves.

## State, Persistence, And Dependencies
State includes pool ID, description, `Mutex`, member sets, and shared capacity-pool objects. Serialized state includes both explicit membership and capacity-pool snapshots.

## Integration Points
Used by `StoragePoolStore`, target placement, buddy group placement, and pool-management messages.

## Risks
Serializing both member sets and capacity pools can diverge if update paths miss a side effect. Copy construction is deleted, so containers use shared pointers or value vectors carefully.

## Test Signals
Serialization consistency between member sets and capacity pools, derived `initFromDesBuf()`, comparison by ID, and default constructor behavior should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StoragePool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StoragePoolId.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/StoragePoolId.h

## Purpose
Defines the strongly typed numeric storage pool ID.

## Important APIs, Types, And Functions
`StoragePoolId` is `NumericID<uint16_t, StoragePoolIdTag>` with list/vector typedefs and iterators.

## Control Flow
No runtime logic.

## State, Persistence, And Dependencies
No state. The type must remain synchronized with the client.

## Integration Points
Used by `StoragePool`, `StoragePoolStore`, `TargetMapper`, and storage-pool messages.

## Risks
The 16-bit width bounds the maximum number of pools and is protocol-visible.

## Test Signals
Zero invalid/default semantics, ordering, serialization, and client compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StoragePoolId.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StorageTargetInfo.cpp -->
# sources/distributed-fs/beegfs/common/source/common/storage/StorageTargetInfo.cpp

## Purpose
Implements remote stat retrieval for a storage path/target.

## Important APIs, Types, And Functions
`StorageTargetInfo::statStoragePath()` sends `StatStoragePathMsg`, expects `StatStoragePathRespMsg`, returns `FhgfsOpsErr`, and fills free/total size and inode counters.

## Control Flow
The method sends a request/response via `MessagingTk`; no response maps to communication error. On response, it casts to the response type, reads the result and counters, writes output pointers, and returns the result.

## State, Persistence, And Dependencies
No persistent state. Depends on storage stat messages, `MessagingTk`, `Node`, and serialization headers.

## Integration Points
Used by management/statfs/capacity update code to query storage servers for target path space and inode data.

## Risks
Output pointers are written regardless of result code once a response exists, so callers should decide whether to trust counters on error. The cast assumes message type enforcement by `requestResponse()`.

## Test Signals
Mock success, communication failure, non-success response with counters, target ID zero/nonzero, and response type mismatch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StorageTargetInfo.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StorageTargetInfo.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/StorageTargetInfo.h

## Purpose
Defines a serializable snapshot of a storage target's path, space, inode counts, and consistency state.

## Important APIs, Types, And Functions
Constructors, `statStoragePath()`, getters, comparison/equality operators, serialization, and `StorageTargetInfoList` typedefs are exported. List serialization is marked as not having embedded item lengths.

## Control Flow
Serialization writes target ID, aligned path string, disk space totals/free, inode totals/free, and consistency state as `uint8_t`.

## State, Persistence, And Dependencies
State is target ID, path, disk/inode counters, and `TargetConsistencyState`. Depends on `Node`, `TargetStateInfo`, `StorageErrors`, and serialization.

## Integration Points
Used by storage target reporting, capacity pool updates, management tools, and stat-storage-path messages.

## Risks
`getPathStr()` returns by value, not reference. Ordering compares only target ID, while equality compares all fields.

## Test Signals
Serialization golden data, equality/order differences, consistency state width, and stat RPC integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/StorageTargetInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/Storagedata.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/Storagedata.h

## Purpose
Defines chunk storage on-disk layout constants.

## Important APIs, Types, And Functions
Exports chunk level fanout counts, chunk subdir name, user-ID prefix, and buddy-mirror chunk subdir name.

## Control Flow
No runtime logic.

## State, Persistence, And Dependencies
No state. Constants define persistent path layout.

## Integration Points
Used by storage server chunk path construction and buddy-mirrored chunk storage.

## Risks
Changing these constants breaks existing storage directory layouts.

## Test Signals
Path-construction tests and migration compatibility checks should cover them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/Storagedata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/chunkbalancer/ChunkBalancerJobStatistics.h -->
# sources/distributed-fs/beegfs/common/source/common/storage/chunkbalancer/ChunkBalancerJobStatistics.h

## Purpose
Defines chunk-balancer job state and a serializable statistics snapshot.

## Important APIs, Types, And Functions
`ChunkBalancerJobState` enumerates not-started, starting, running, success, interrupted, failure, errors, and idle. `ChunkBalancerJobStatistics` stores status, start/end times, work queue, errors, locked inodes, migrated chunks, and worker count. `reset()` and serialization are provided.

## Control Flow
`reset()` sets `startTime` to `time(NULL)`, clears end time and counters, but leaves `status` unchanged. Serialization writes status as `int32_t` followed by counters.

## State, Persistence, And Dependencies
Value-object state only. Depends on common serialization and time from common includes.

## Integration Points
Used by chunk-balancer control/status messages and management reporting.

## Risks
Because `reset()` does not set status, callers must update status separately to avoid stale state. Field ordering in serialization is protocol-visible.

## Test Signals
Reset semantics, serialization order, all job states, and management display of status/counters should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/chunkbalancer/ChunkBalancerJobStatistics.h -->
