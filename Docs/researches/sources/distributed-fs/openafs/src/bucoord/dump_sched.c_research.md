# sources/distributed-fs/openafs/src/bucoord/dump_sched.c

## Purpose
Implements `backup` commands and BUDB text-block synchronization for dump schedules. It adds, deletes, lists, parses, saves, updates, and modifies expiration metadata for schedule nodes represented by `struct bc_dumpSchedule`.

## Important APIs, Types, And Functions
Command handlers are `bc_AddDumpCmd`, `bc_DeleteDumpCmd`, `bc_ListDumpScheduleCmd`, and `bc_SetExpCmd`. Persistence helpers are `bc_ParseDumpSchedule`, `bc_SaveDumpSchedule`, and `bc_UpdateDumpSchedule`. `ListDumpSchedule` recursively prints a schedule tree with expiration details.

## Control Flow
Mutating commands lock `TB_DUMPSCHEDULE`, refresh the local schedule from BUDB, modify the in-memory tree through `dsvs.c` helpers, save the text block back to BUDB, and unlock. Listing refreshes the schedule and prints only root nodes, recursively visiting children. Parsing validates a magic/version header, then reads `dump-name period expDate expType` lines into the flat schedule list; after update, `bc_ProcessDumpSchedule` rebuilds the tree. Saving truncates the local temp stream, writes the header and all schedule records, calls `bcdb_SaveTextFile`, increments the local version, and updates text size.

## State And Persistence
State is `bc_globalConfig->dsched` plus `bc_globalConfig->configText[TB_DUMPSCHEDULE]`. Persistent storage is BUDB configuration text, protected by BUDB text locks. The `period` field is currently serialized as `"any"` and not used in the in-memory creation path; expiration fields are preserved.

## Dependencies And Integration Points
Depends on ktime conversion, BUDB client text locking/versioning from `ubik_db_if.c`, dump-schedule model helpers from `dsvs.c`, error macros, com_err, and global `udbHandle`. The schedule data drives `commands.c` dump parent selection and expiration propagation into `dump.c`.

## Risks And Test Signals
Several early returns after failed refresh skip the `error_exit` unlock path if the lock was already acquired. Clearing obsolete schedule entries frees only the schedule node and leaks `name`. The parser rejects any malformed line and has fixed-size field buffers. Test signals include add/delete/set expiration with lock/unlock verification, stale version refresh, empty schedule text, invalid magic/version, malformed lines, tree listing indentation, relative and absolute expiration formatting, and save failure behavior that leaves session-local changes.
