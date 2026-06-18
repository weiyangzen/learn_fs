# sources/distributed-fs/beegfs/meta/source/components/InternodeSyncer.cpp

Purpose: `InternodeSyncer.cpp` implements the metadata daemon's periodic cluster synchronization loop and related static startup helpers.

Important APIs/functions: The constructor initializes force flags, offline-wait logic, local consistency state, and resync flag. `syncLoop()` periodically checks network interfaces, re-registers the local node, downloads nodes/mappings/storage pools/states, updates capacity pools, sweeps metadata cache, drops idle connections, resets ID counters, publishes target state changes, and publishes capacity. Static helpers perform startup registration, node/client sync, target mapping sync, storage pool sync, target state and buddy group sync, capacity-pool download/update, quota-exceeded list download, and client-session cleanup.

Control flow: `syncLoop()` runs every three seconds and gates work by elapsed timers or atomic force flags. State publishing uses management-node compare/change semantics with retries to avoid overwriting concurrent mgmtd updates. Client sync removes sessions for clients no longer registered and, when remote communication is allowed, unlocks waiters, closes storage chunk files, closes metadata state, and unlinks disposable files.

State and persistence behavior: It mutates node stores, target mappings, buddy groups, state stores, capacity pools, storage pools, quota stores, sessions, locks, connection pools, metadata cache flush state, and local consistency state. It reads capacity from the metadata path and uses override files through `StorageTk`.

Dependencies/integration: It is tightly coupled to `App`, `NodesTk`, `MessagingTk`, `BuddyCommTk`, `SessionStore`, `MetaStore`, and management-node message types. `App::downloadMgmtInfo()` calls several static helpers before constructing the running syncer.

Risks and test signals: Risks include mgmtd unavailability causing POFFLINE marking, racey state transitions around buddy resync/offline waits, expensive client cleanup, and sync functions returning true even after partial download failures in some paths. There are no direct unit tests here; operational integration tests are needed.
