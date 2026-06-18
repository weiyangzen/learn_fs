<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_lock.h -->
# sources/distributed-fs/openafs/src/budb/db_lock.h

## Purpose
Declares the lock record layout used for budb text block locking.

## Important APIs, Types, And Functions
`db_lockS` contains `type`, `lockState`, `lockTime`, `expires`, `instanceId`, and `lockHost`. The header typedefs `db_lockT` and `db_lockP`.

## Control Flow
No executable flow is present. The structure is manipulated by `db_lock.c`, `db_text.c`, and database header code.

## State And Persistence
The fields mirror persistent lock slots in `dbHeader.textLocks`. They track whether a text block is locked, when the lock was acquired, when it expires, and which client instance owns it.

## Dependencies And Integration Points
The same structure is also defined in `database.h`, so this header is a narrow compatibility declaration for modules that need lock types without the full database schema.

## Risks And Test Signals
There is a type inconsistency: this file defines `db_lockP` as `db_lockT`, while `database.h` defines it as `db_lockT *`. Compile coverage determines which declaration is actually used. Tests should cover lock RPCs and any consumer including this header directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_lock.h -->
