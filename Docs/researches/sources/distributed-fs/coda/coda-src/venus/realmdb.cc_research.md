# sources/distributed-fs/coda/coda-src/venus/realmdb.cc

## Purpose
This file implements the recoverable realm database, including initialization, restart-time transient reset, realm lookup/creation, periodic cleanup, and local fake-realm identification.

## Important APIs, Types, and Functions
`LocalRealm` is initialized from the special `LOCALREALM`. `RealmDB::RealmDB()` records the database object and initializes its persistent list and `max_realmid`. `ResetTransient()` scans all realms, resets each transient state, recomputes `max_realmid`, and obtains `LocalRealm`. `GetRealm(const char *)` looks up by name or creates a new persistent `Realm`; `GetRealm(RealmId)` looks up by id. `GetDown()` deletes realms with no transient or recoverable refs by briefly taking and dropping a recoverable reference. `RealmDBInit()` creates or recovers `REALMDB` and starts a periodic cleanup daemon. `FID_IsLocalFake()` checks whether a fid belongs to the local fake realm.

## Control Flow
Startup calls `RealmDBInit()`. If metadata is being initialized, it allocates a new `RealmDB` in an RVM transaction; then `ResetTransient()` repairs runtime fields after either fresh init or recovery. Normal lookup by name creates new realms in a transaction and adds them to the persistent list. Cleanup is scheduled with `FireAndForget` and runs outside transactions, opening a transaction only around possible deletion.

## State and Persistence Behavior
`REALMDB` is a persistent root under `RecovVenusGlobals`. The realm list and `max_realmid` are recoverable. `LocalRealm` is a transient global reference acquired during reset. Newly created realm ids increment `max_realmid` and persist with the new realm.

## Dependencies and Integration Points
It depends on `fso.h` for fake object interactions, `rec_dllist.h` for recoverable lists, and `venusrecov` globals through `REALMDB`. It is called by Venus startup after recovery and before volume/filesystem initialization can rely on realm ids.

## Risks and Test Signals
Risks include deleting a realm while hidden references still exist, name normalization limited to empty/null-to-`UNKNOWN`, and persistent id monotonicity after recovery. Tests should cover fresh init, dirty restart, repeated name lookup, id lookup miss, cleanup of unreferenced realms, and local fake fid detection.
