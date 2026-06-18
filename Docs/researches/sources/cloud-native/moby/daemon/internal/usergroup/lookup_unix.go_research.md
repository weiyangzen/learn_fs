# sources/cloud-native/moby/daemon/internal/usergroup/lookup_unix.go

## Purpose
Looks up Unix users/groups through local files first and `getent` fallback, then builds subordinate ID mappings for user namespace remapping.

## Important APIs, Types, And Functions
`LookupUser`, `LookupUID`, `LookupGroup`, and `LookupGID` call `moby/sys/user` local lookup then fallback to `getentUser`/`getentGroup`. `callGetent` resolves and runs `getent`, translates exit codes, and returns output. `LoadIdentityMapping` loads a user and reads `/etc/subuid` and `/etc/subgid` via `lookupSubRangesFile`, building sequential container ID maps.

## Control Flow
Fallback only occurs after local lookup fails. `getent` output is parsed using `user.ParsePasswd` or `user.ParseGroup`. Subordinate ranges can match by username or numeric uid and are appended in file order with cumulative container IDs.

## State And Persistence
Lookup is read-only against system files/NSS. No persistent state is changed.

## Dependencies And Integration Points
Supports hosts where users/groups come from LDAP, SSSD, or other NSS sources. Uses `resolveBinary` to avoid symlink spoofing and avoids `/dev/null` stdin assumptions.

## Risks And Test Signals
Exact `getent` exit-code semantics vary by implementation. No sorting is applied to mapping ranges. Tests cover nonexistent users/groups and root integration tests cover successful paths.
