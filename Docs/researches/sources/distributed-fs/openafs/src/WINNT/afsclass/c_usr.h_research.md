# sources/distributed-fs/openafs/src/WINNT/afsclass/c_usr.h

## Purpose

`c_usr.h` declares `USER`, the AfsClass wrapper for KAS/PTS user accounts.

## Important APIs, Types, and Functions

`USERSTATUS` contains presence flags plus nested `KASINFO` and `PTSINFO` structures for auth settings, expiration/password/key fields, PTS quotas, IDs, owner/creator, and access controls. The class exposes close/invalidate/refresh, identity and cell access, name/status getters, user-param accessors, owner/member group list getters, and static helpers `SplitUserName` and `IsMachineAccount`.

## Control Flow

The class follows lazy refresh: status and relationship lists are loaded on demand and copied/cloned to callers.

## State and Persistence Behavior

The class caches account status and multisz group lists in memory. Persistent account data is external to KAS/PTS.

## Dependencies and Integration Points

It includes `afsclass.h` and `c_svc.h` for `ENCRYPTIONKEY`. It is managed by `CELL`, represented by `IDENT`, and related to `PTSGROUP`.

## Risks and Edge Cases

The single status structure merges KAS and PTS data that can independently exist or fail. Consumers must check `fHaveKasInfo` and `fHavePtsInfo` before using nested fields. Caller ownership of cloned multisz lists must be honored.

## Test Signals

Compile checks should validate `USERSTATUS` ABI. Runtime tests should validate refresh, split-name edge cases, missing KAS/PTS halves, group-list cloning, and identity/user-param behavior.
