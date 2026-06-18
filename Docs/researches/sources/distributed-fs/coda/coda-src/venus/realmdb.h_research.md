# sources/distributed-fs/coda/coda-src/venus/realmdb.h

## Purpose
This header declares the persistent realm database and the special local realm used for fake/local volumes.

## Important APIs, Types, and Functions
`LOCALREALM` is `"localhost"`, `LocalRealm` is the transient pointer to that realm, and `REALMDB` maps to `rvg->recov_REALMDB`. `RealmDB` has RVM allocation operators, constructor/destructor, `ResetTransient`, name/id `GetRealm` overloads, `GetDown`, and print helpers. Private fields are the persistent realm list and `max_realmid`.

## Control Flow
The API is built around startup initialization via `RealmDBInit()`, followed by lookup/creation during realm discovery and periodic cleanup through `GetDown()`.

## State and Persistence Behavior
The class is recoverable and owned by the recovery globals. Its list links must be mutated with recoverable list helpers, and `max_realmid` is persistent so newly created realm ids do not collide after restart.

## Dependencies and Integration Points
It depends on `rvmlib`, `realm.h`, and recovery globals from `venusrecov.h` through the `REALMDB` macro. `fsobj` is a friend for fake realm object construction.

## Risks and Test Signals
Tests should validate that `RealmDB` is never destructed during normal shutdown, that fresh metadata init creates the persistent root, and that all callers can include the header without pulling in implementation-only dependencies.
