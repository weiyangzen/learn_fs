# sources/distributed-fs/coda/coda-src/auth2/cunlog.c

## Purpose
Minimal logout utility that tells Venus to delete locally held Coda tokens for a realm, effectively unauthenticating the user from that realm.

## APIs, Types, and Functions
`main()` uses `SplitRealmFromName()`, `codaconf_init()`, `CODACONF_STR()`, and `U_DeleteLocalTokens()`. The auth-facing data is only a realm string.

## Control Flow, State, and Persistence
If one argument is present, the code extracts its realm part; otherwise it starts with an empty realm and then allows `venus.conf`/`auth2.conf` to supply the configured default. It calls `U_DeleteLocalTokens(realm)` and exits success without checking a return value. Persistent effects are in Venus/cache-manager token state, not in this process.

## Dependencies and Integration
Integrates with Coda config files and the auth2 Venus local-token API. It is the inverse of token-acquisition tools and its result is observable through `ctokens`.

## Risks and Test Signals
Risks include silent success if token deletion fails, ambiguous empty/default realm behavior, and no usage diagnostics for extra arguments. Test signals are token disappearance in `ctokens`, correct default realm selection, and Venus-side purge behavior.
