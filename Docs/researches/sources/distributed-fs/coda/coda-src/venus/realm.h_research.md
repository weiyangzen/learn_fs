# sources/distributed-fs/coda/coda-src/venus/realm.h

## Purpose
This header defines `Realm`, the persistent Venus representation of a Coda realm. It exposes identity, root-volume naming, root-server replacement, administrative connection acquisition, and user-token entry points.

## Important APIs, Types, and Functions
`Realm` overloads `new` and `delete` to use `rvmlib_rec_malloc/free`. It declares transaction-aware constructor/destructor, `ResetTransient`, recoverable and transient refcount methods, `Name`, `Id`, `SetRootVolName`, `GetRootVolName`, `ReplaceRootServers`, `GetAdmConn`, `GetUser`, `NewUserToken`, and `print`. Private fields distinguish persistent (`realmid`, `rec_refcount`, `name`, `rootvolname`, `realms`) from transient (`refcount`, `generation`, `rootservers`) state.

## Control Flow
The API assumes creation and persistent refcount updates occur inside recovery transactions, while server lookups and administrative connections do not. User and token helpers let `Realm` own per-realm user table lookup even though the concrete `userent` implementation is transient.

## State and Persistence Behavior
The header encodes the RVM allocation contract and makes persistence visible through transaction annotations. Root server addresses are intentionally transient and refreshed from realm discovery; the root volume name and realm identity survive restart.

## Dependencies and Integration Points
It depends on `rvmlib`, authentication token types, `venusfid.h`, and forward declarations for connection/user classes. `RealmDB` and `fsobj` are friends for persistent database management and fake mount construction.

## Risks and Test Signals
Risks are incorrect transaction usage around recoverable fields and accidental external dependence on transient `rootservers`. Compile-time annotation checks and recovery tests should verify all persistent mutations happen inside transactions and that realm lookups return referenced objects that callers eventually release.
