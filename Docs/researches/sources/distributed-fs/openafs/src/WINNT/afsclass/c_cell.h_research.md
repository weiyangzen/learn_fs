# sources/distributed-fs/openafs/src/WINNT/afsclass/c_cell.h

## Purpose

`c_cell.h` declares `CELL`, the top-level AfsClass object representing one opened AFS cell and its cached servers, services, aggregates, filesets, users, and groups.

## Important APIs, Types, and Functions

`OP_CELL_REFRESH_ACCOUNT` describes single-account refresh events. Static APIs open, close, and reopen cells. Public methods invalidate and refresh server, VLDB, user, status, and whole-cell state; retrieve names, credentials, user params, and raw cell/KAS objects; enumerate/open servers, users, and groups. Private helpers free caches, close worker handles, reconcile VLDB entries, build group lists, and implement hash keys.

## Control Flow

The class contract is lazy and cache-backed. Public `Open*` and `Find*` methods refresh the relevant list before lookup unless a direct identifier is supplied. `RefreshAll` orchestrates server and user refresh according to requested library features.

## State and Persistence Behavior

Persistent AFS state is external. The class stores in-memory handles, credentials, stale flags, request count, server address/name caches, user/group caches, and a static process-wide list of cells.

## Dependencies and Integration Points

The header includes `afsclass.h`, `c_svr.h`, `c_agg.h`, `c_usr.h`, and `c_grp.h`. It grants friendship to all major object classes so they can share identifiers and update internal lists.

## Risks and Edge Cases

Because many fields are directly manipulated by friend classes, stale flags and ghost flags must remain consistent across files. `m_hKas` is deliberately left null to mean any KAS server, which can surprise callers expecting a concrete server handle.

## Test Signals

Header-level tests are compile and include-order checks. Functional tests should validate open/close reference behavior, enumerator contracts, credential replacement, stale flag transitions, and account refresh operation variants.
