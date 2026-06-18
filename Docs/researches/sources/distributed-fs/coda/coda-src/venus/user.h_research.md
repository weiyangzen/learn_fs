# sources/distributed-fs/coda/coda-src/venus/user.h

## Purpose
This header declares Venus user entries, token operations, authorization helpers, and the user daemon interface.

## Important APIs, Types, and Functions
`userent` stores its list handle, realm id, uid, token validity/warning state, secret and clear tokens, wait-forever flag, and demand-hoard timestamp. Public methods cover token set/get/validity/expiry, invalidation/reset, server connection, fetch-partial support probing, wait-forever state, uid access, and printing. `user_iterator` iterates over the static user table. Free functions include `UserInit`, `PutUser`, `UserPrint`, `AuthorizedUser`, `ConsoleUser`, `USERD_Init`, and `UserDaemon`.

## Control Flow
The header makes `Realm` responsible for constructing users and setting tokens while other modules interact through public methods and iterators. `PutUser()` currently has no reference-counting behavior, so returned user pointers are effectively table-owned.

## State and Persistence Behavior
All fields are transient. Tokens are process memory only, while their presence can hold runtime references to persistent realms and invalidate caches when changed.

## Dependencies and Integration Points
It depends on RPC2, auth token definitions, `olist`, communication/server declarations, and Venus private constants. Friends include FSDB and Realm so they can allocate and inspect user entries.

## Risks and Test Signals
Risks include table-owned lifetime without real `PutUser()`, broad friend access, and direct token storage. Tests should verify iteration safety, connection method declarations under transaction annotations, and no accidental copying because copy/assignment abort.
