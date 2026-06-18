# sources/distributed-fs/moosefs/mfsmaster/sessions.h

## Purpose
`sessions.h` declares session operation identifiers and the master session-management API.

## Important APIs, Types, And Functions
The header defines `SES_OP_*` constants for 28 operation-stat slots and `SES_OP_STRINGS` in the same order. It declares session lifecycle, lookup, reporting, creation/change, getters, permission helpers, statistics helpers, cleanup/init, metadata replay, store/load, and legacy import functions.

## Control Flow
Connection code receives opaque session pointers from `sessions_new_session()` or `sessions_find_session()` and passes them back into getters, attach/disconnect, stats, permission, and change functions. Restore code uses the `sessions_mr_*` family. Metadata code uses `sessions_store()` and `sessions_load()`.

## State, Persistence, And Dependencies
No state is exposed. `bio.h` is required for store/load. Operation constants must remain synchronized with `SESSION_STATS` and the implementation's `opname` array.

## Integration Points
The header is consumed by client serving code, filesystem permission paths, restore, metadata storage, and open-file cleanup paths.

## Risks
`sessions_open_file()`, `sessions_connect_session_with_inode()`, `sessions_get_statscnt()`, and `sessions_sync_open_files()` are declared here but not implemented in `sessions.c`; at least `sessions_sync_open_files()` is only seen as a commented caller. This stale surface can confuse new integration work.

Any insertion into the `SES_OP_*` list requires updating `SESSION_STATS`, `SES_OP_STRINGS`, packet compatibility expectations, and statistics consumers.

## Test Signals
Build/link tests should confirm only implemented declarations are referenced. Packet tests should verify stats count and operation-name ordering remain stable.
