# sources/distributed-fs/coda/coda-src/venus/realm.cc

## Purpose
This file implements the persistent `Realm` abstraction: a Coda administrative namespace with a realm id, name, root volume name, cached root server addresses, and refcounts that bridge RVM state and transient runtime use. It also provides administrative server connection setup and root-server replacement.

## Important APIs, Types, and Functions
The constructor allocates recoverable strings for `name` and `rootvolname`, initializes the persistent list link, and sets a temporary recoverable reference while transient state is reset. The destructor removes the realm from the persistent list, drops root-server references, removes the realm mount entry from the local fake root, frees recoverable strings, and kills the fake mountlink object. `ResetTransient()`, `Rec_PutRef()`, `PutRef()`, `ReplaceRootServers()`, `GetAdmConn()`, `SetRootVolName()`, and `print()` are the main operations.

## Control Flow
During recovery, `ResetTransient()` clears cached root servers and transient refcount; if called inside a transaction with no recoverable references, it deletes the realm. `GetAdmConn()` resolves realm servers when unknown or stale, reorders cached addresses on retries, tries each IPv4 server as `ANYUSER_UID`, and on first successful discovery creates the realm mount entry under local `/coda` in a recovery transaction. `SetRootVolName()` replaces the recoverable string inside a transaction.

## State and Persistence Behavior
Persistent state includes `realmid`, `rec_refcount`, `name`, `rootvolname`, and list linkage. Transient state includes `refcount`, `generation`, and `rootservers`. `ReplaceRootServers()` pins `srvent` objects for new IPv4 roots and drops refs for old ones, then frees old RPC2 addrinfo. Realm deletion mutates persistent directory entries and frees RVM allocations.

## Dependencies and Integration Points
It integrates with `RealmDB`, `FSDB`, local fake volumes, RPC2 address info, server entries, connection entries, `parse_realms`, recovery transactions, and user token lookup methods declared in `realm.h` but implemented in `user.cc`.

## Risks and Test Signals
Risks include refcount imbalance between `GetRealm()`, token-held realm refs, and root-server refs; stale address retries; deletion while fake mount entries are in use; and transaction boundaries around recoverable string/list updates. Tests should cover unknown realm discovery, server re-resolution after `ERETRY`/timeouts, root volume name persistence, realm removal from fake root, and restart scanning with zero/nonzero persistent refs.
