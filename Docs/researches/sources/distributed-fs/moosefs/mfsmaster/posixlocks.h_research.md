# sources/distributed-fs/moosefs/mfsmaster/posixlocks.h

## Purpose
`posixlocks.h` declares the POSIX byte-range lock service used by MooseFS master connection, open-file, metadata, and restore code.

## Important APIs, Types, And Functions
The header includes `<inttypes.h>` and `bio.h`. It exports the client command API `posix_lock_cmd()`, cleanup hooks `posix_lock_file_closed()` and `posix_lock_disconnected()`, listing API `posix_lock_list()`, metadata replay API `posix_lock_mr_change()`, persistence APIs `posix_lock_store()` and `posix_lock_load()`, cleanup, and initialization.

## Control Flow
Callers pass lock operation, session, inode, owner, requested type/range, pid, and optionally message/request identifiers into `posix_lock_cmd()`. The command may mutate type/start/end/pid for conflict reporting. Metadata replay bypasses client waiting logic and calls `posix_lock_mr_change()` directly.

## State, Persistence, And Dependencies
The header hides lock state. Store/load functions serialize active locks through `bio` streams; waiting locks are runtime-only and have no public type.

## Integration Points
`matoclserv` uses the command API for FUSE lock requests and wakeups. `openfiles`/session cleanup use the close/disconnect hooks. `restore.c` uses the replay API for changelog records. Metadata load/store uses the `bio` persistence API.

## Risks
The pointer parameters in `posix_lock_cmd()` are in-out fields, so callers must preserve requested values separately if needed. `connptr` is opaque and lifetime-sensitive. The API also exposes no explicit destroy hook for an individual inode; cleanup is event-driven.

## Test Signals
Header-level tests should compile all major callers and verify operation constants match `MFSCommunication.h`. Runtime tests should assert the `posix_lock_cmd()` return statuses and in-out conflict fields for GET, TRY, SET, INT, and unlock.
