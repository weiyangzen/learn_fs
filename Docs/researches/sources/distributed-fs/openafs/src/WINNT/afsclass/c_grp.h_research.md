# sources/distributed-fs/openafs/src/WINNT/afsclass/c_grp.h

## Purpose

`c_grp.h` declares `PTSGROUP`, the PTS group wrapper in the AfsClass object model.

## Important APIs, Types, and Functions

`PTSGROUPSTATUS` reports member count, PTS IDs, access controls, owner, and creator. The class exposes close/invalidate/refresh, identity and parent-cell access, name/status getters, user-param accessors, and multisz getters for members, memberships, and owned groups. `ChangeIdentName` is public for internal rename handling.

## Control Flow

The public API follows the standard lazy-refresh pattern: getter methods refresh status when stale, then copy cached values to the caller.

## State and Persistence Behavior

The class stores parent cell identity, group name, identifier pointer, stale flag, status snapshot, and three allocated multisz relationship lists. Persistent data lives in PTS.

## Dependencies and Integration Points

The header depends on `afsclass.h`, `LPIDENT`, `ACCOUNTACCESS`, `HENUM` conventions, and friend access from `CELL`, `IDENT`, and `USER`.

## Risks and Edge Cases

The class exposes internally intended `ChangeIdentName` publicly, making incorrect external use possible. Callers own cloned multisz results and must free them with the library's string-freeing convention.

## Test Signals

Compile coverage should ensure `PTSGROUPSTATUS` layout and include order. Runtime tests should validate refresh staleness, identity update on rename, and multisz clone lifetime.
