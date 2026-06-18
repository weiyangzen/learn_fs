# sources/distributed-fs/openafs/src/WINNT/afsclass/c_grp.cpp

## Purpose

`c_grp.cpp` implements `PTSGROUP`, the cached AfsClass representation of a PTS group. It retrieves group metadata, access bits, member lists, groups owned by the group, and groups to which the group belongs.

## Important APIs, Types, and Functions

Important methods include constructor/destructor, `GetIdentifier`, `Invalidate`, `OpenCell`, `GetName`, `GetStatus`, `GetMembers`, `GetMemberOf`, `GetOwnerOf`, `ChangeIdentName`, and `RefreshStatus`. `PTSGROUPACCESS_TO_ACCOUNTACCESS` maps PTS group access constants to AfsClass account-access enums.

## Control Flow

Construction captures the parent cell identifier and group name, initializes stale status, and clears multisz caches. `RefreshStatus` clears old status and strings, opens the cell, calls `wtaskPtsGroupGet`, maps returned IDs/access fields/owner/creator, then enumerates members, owned groups, and group memberships through PTS begin/next/done worker tasks. Public getters refresh first, then return copied status or cloned multisz strings. `ChangeIdentName` updates the associated `IDENT`, rehashes it, changes the group name, and updates the parent cell group hash.

## State and Persistence Behavior

State is in-memory cached `PTSGROUPSTATUS` plus three allocated multisz lists. No persistence is owned; refresh reflects PTS database state. Rename support updates local identity/cache state after an external operation.

## Dependencies and Integration Points

The file depends on `CELL` for `hCell`, `IDENT`, `NOTIFYCALLBACK`, PTS worker tasks, `FormatMultiString`, `CloneMultiString`, and string conversion helpers.

## Risks and Edge Cases

`RefreshStatus` sets `rc = FALSE` on failures but returns `TRUE` unconditionally, so callers may receive zeroed/partial status without a false return. Enumeration loops ignore status on `GetNext` and treat any failure as end-of-list. `ChangeIdentName` depends on parent hash-list update discipline.

## Test Signals

Tests should cover groups with no members, nested group memberships, owned groups, failed PTS lookups, rename rehashing, cloned multisz ownership, and notification begin/end behavior.
