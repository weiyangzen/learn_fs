# sources/distributed-fs/coda/coda-src/venus/user.cc

## Purpose
This file implements transient Venus user entries, token management, authorization checks, per-user connection reset, server binding, and the periodic token-expiry warning daemon.

## Important APIs, Types, and Functions
`UserInit()` creates the global `userent::usertab` and starts `USERD`. `Realm::GetUser()` and `Realm::NewUserToken()` allocate/find per-realm user entries and install tokens. `AuthorizedUser()` and `ConsoleUser()` decide whether a uid can perform privileged local operations. `userent` methods include `SetTokens`, `GetTokens`, `TokensValid`, `CheckTokenExpiry`, `Invalidate`, `Reset`, `CheckFetchPartialSupport`, `Connect`, `GetWaitForever`, `SetWaitForever`, and print helpers. `user_iterator` wraps the global olist. `UserDaemon()` periodically scans users for token expiry warnings.

## Control Flow
Token installation copies secret/clear tokens, pins the realm while tokens are valid, resets cached user state, and marks dirty owned replicated volumes for reintegration. Invalidation drops the token-held realm reference, clears token memory, notifies the user, and resets kernel/HDB/connection/mgrp state. `Connect()` either creates an RPC2 multicast group for `INADDR_ANY` or binds to a specific server; it chooses authenticated or unauthenticated security based on requested auth and token validity, calls `ViceNewConnectFS`, then probes `ViceFetchPartial` support with retries.

## State and Persistence Behavior
User entries are transient and kept in `usertab`; tokens are stored in memory and zeroed on invalidation. Token validity holds a transient realm reference, but does not directly persist. Resetting a user purges kernel data, demotes HDB bindings, suicides connections for the uid, and kills user mgrp entries, which invalidates runtime access state across Venus subsystems.

## Dependencies and Integration Points
It depends on RPC2, Vice/auth protocols, LKA, Coda service lookup, server/connection/mgrp databases, HDB, kernel purge helpers, worker retry signaling, replicated volume iteration, and mariner/RPC statistics macros. Platform-specific console-user logic depends on utmp/passwd or defaults to allowed on Cygwin/FreeBSD.

## Risks and Test Signals
Risks include token/realm refcount imbalance, platform-dependent console authorization, using expired tokens until servers reject them, partial-fetch probing side effects, fixed-size username buffer, and retry/unbind correctness on connection failure. Tests should cover token set/get/invalidate, authenticated and unauthenticated binds, `RPC2_NOTAUTHENTICATED` invalidation, fetch-partial unsupported/supported/error paths, wait-forever retry signaling, and user reset cleanup across connections and mgrps.
