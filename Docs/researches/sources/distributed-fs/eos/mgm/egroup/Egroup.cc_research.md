<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/egroup/Egroup.cc -->
# sources/distributed-fs/eos/mgm/egroup/Egroup.cc

## Purpose

`Egroup.cc` implements the MGM e-group membership checker declared in `Egroup.hh`. It provides cached LDAP membership lookups for CERN e-groups and a background refresh thread so MGM authorization paths can keep serving from cache instead of blocking under namespace read locks.

## Important APIs, Types, and Functions

The central APIs are `query()`, `Member()`, `refresh()`, `fetchCached()`, `scheduleRefresh()`, `DumpMember()`, `DumpMembers()`, `Reset()`, and test hook `inject()`. `isMemberUncached()` is the real LDAP path. It returns `Status::kMember`, `kNotMember`, or `kError`; `CachedEntry` stores the boolean result plus a steady-clock timestamp.

## Control Flow

Construction enables blocking mode on `mPendingQueue` and starts `Refresh`. `query()` first checks `cache` under `mMutex`; fresh hits return immediately, stale hits return the old value and enqueue a refresh, and misses call `isMemberUncached()` synchronously before storing the result. The refresh thread consumes queued `(username, egroup)` pairs, calls `refresh()`, removes the deduplication key from `mPendingSet`, and pops the queue. `isMemberUncached()` either serves injected test data or initializes an LDAP connection to `ldap://xldap`, sets protocol and network timeout options, searches the CERN user DN with a recursive `memberOf` filter, and checks returned `cn` values for the username.

## State and Persistence Behavior

State is in-memory only: `cache` maps egroup to user to cached entry, `mPendingQueue` and `mPendingSet` hold refresh work, and `injections` simulates LDAP for tests. Cache lifetime is fixed at 1800 seconds. There is no disk persistence; state is reset on process restart or `Reset()`.

## Dependencies and Integration Points

The file depends on OpenLDAP C APIs, EOS logging/string helpers, `common::SteadyClock`, `common::RWMutex`, `AssistedThread`, and `qclient::WaitableQueue`. It integrates with MGM authorization code through `Egroup::Member()` and with admin/debug output through the dump methods.

## Risks and Edge Cases

LDAP base/filter strings are hard-coded for CERN and are not escaped, so unexpected usernames or egroup names are risky. `query()` caches `kError` as non-member on synchronous misses, while `refresh()` refuses to replace cache on `kError`; this can turn transient LDAP failures into temporary denials. `injections` is not protected by `mMutex`, so test or runtime concurrent use would race. The queue has a fixed capacity of 500, and `scheduleRefresh()` does not report enqueue failure. Dump lifetimes can become negative for stale entries.

## Test Signals

Useful tests include injected membership/non-membership/error cases, stale-cache refresh scheduling and deduplication, cache miss behavior on LDAP errors, destructor shutdown of a blocked refresh thread, `Reset()` cache clearing, and dump formatting with controlled `SteadyClock` time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/egroup/Egroup.cc -->
