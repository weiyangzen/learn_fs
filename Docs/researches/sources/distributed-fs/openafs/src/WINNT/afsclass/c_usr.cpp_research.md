# sources/distributed-fs/openafs/src/WINNT/afsclass/c_usr.cpp

## Purpose

`c_usr.cpp` implements `USER`, the cached AfsClass representation of a KAS/PTS user account. It merges authentication database fields, protection database fields, group memberships, and group ownership into one status object.

## Important APIs, Types, and Functions

Implemented methods include constructor/destructor, `GetIdentifier`, `Invalidate`, `OpenCell`, `GetName`, `GetStatus`, user-param accessors, `GetOwnerOf`, `GetMemberOf`, `RefreshStatus`, `SplitUserName`, and `IsMachineAccount`. `USERACCESS_TO_ACCOUNTACCESS` maps PTS access bits to account-access enums.

## Control Flow

Construction captures parent cell identity and principal/instance strings, initializes stale status, and clears multisz caches. `RefreshStatus` clears old state, builds the full user name, opens the cell, queries KAS principal data, maps admin/ticket/encryption/password/key/timestamp fields, queries PTS user data, maps quotas/IDs/owner/creator/access, enumerates PTS memberships and owned groups, and sends refresh notifications. Public list getters clone the cached multisz strings. `SplitUserName` separates principal and instance on the first dot unless the name is a machine account composed only of digits and dots.

## State and Persistence Behavior

The object caches `USERSTATUS`, membership/owner multisz strings, parent identity, user name/instance, and stale flag. It owns no durable state; refresh reflects KAS and PTS databases.

## Dependencies and Integration Points

The file depends on `CELL`, `IDENT`, KAS and PTS worker tasks, `ENCRYPTIONKEY` from service headers, AfsClass string/time helpers, and notifications.

## Risks and Edge Cases

`RefreshStatus` intentionally treats missing PTS as nonfatal but missing KAS as fatal only internally, then returns `TRUE` unconditionally, so callers must inspect `fHaveKasInfo`/`fHavePtsInfo` and status. Machine-account detection preserves dotted IP-like names as principals without instances. `lpiLastMod` may be null if the modifier account is not cached.

## Test Signals

Tests should cover KAS-only, PTS-only, and combined users; principal instances; machine-account split behavior; memberships and owned groups; missing modifier identities; password/key fields; and error status propagation.
