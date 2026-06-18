# sources/distributed-fs/openafs/src/bucoord/ubik_db_if.c

## Purpose
Wraps BUDB and VLDB Ubik/RX client interactions for the backup coordinator. It provides typed helper functions for backup database records, text configuration locking/get/save/versioning, BUDB/VLDB client initialization, single-server Ubik iteration, local test initialization, and temporary text-file management.

## Important APIs, Types, And Functions
Global state is `struct udbHandleS udbHandle`. BUDB wrappers include `bcdb_AddVolume`, `bcdb_AddVolumes`, `bcdb_CreateDump`, `bcdb_deleteDump`, `bcdb_listDumps`, `bcdb_DeleteVDP`, `bcdb_FindClone`, `bcdb_FindDump`, `bcdb_FindDumpByID`, `bcdb_FindLatestDump`, `bcdb_FindTape`, `bcdb_FindTapeSeq`, `bcdb_FindVolumes`, `bcdb_LookupVolume`, `bcdb_FinishDump`, `bcdb_FinishTape`, `bcdb_UseTape`, `bcdb_FindLastTape`, and `bcdb_MakeDumpAppended`. Text APIs are `bcdb_GetTextFile`, `bcdb_SaveTextFile`, `bc_LockText`, `bc_UnlockText`, `bc_CheckTextVersion`, `bc_openTextFile`, and `bc_closeTextFile`. Initialization APIs are `vldbClientInit`, `udbClientInit`, and test-only `udbLocalInit`. Specialized wrappers are `ubik_Call_SingleServer_BUDB_GetVolumes` and `ubik_Call_SingleServer_BUDB_DumpDB`.

## Control Flow
Most record functions are thin delegates to `ubik_BUDB_*`, adding list setup, result count checks, and allocated-result cleanup. `bcdb_FindDumpByID`, `bcdb_FindTape`, and `bcdb_FindTapeSeq` use list-returning BUDB RPCs and require exactly one result. Text download requires an existing lock and open temp stream, then repeatedly calls `ubik_BUDB_GetText` in 1024-byte chunks until `nextOffset == -1`, writes chunks locally, and refreshes the text version. Text save rewinds the stream, computes size, sends either a zero-length complete marker or chunked `ubik_BUDB_SaveText` calls, marking the final chunk complete. Locking loops on `BUDB_LOCKED`/`BUDB_SELFLOCKED`, printing every 30 seconds, and stores the returned lock handle.

`vldbClientInit` and `udbClientInit` choose client or server config directories from auth flags, resolve cell/server information, choose RX security objects with fallback null security, build RX connections, initialize Ubik clients, and for BUDB fetch an instance id with a short-deadtime first pass. `ubik_Call_SingleServer` selects a working server for a call series, sticks to it while `UF_SINGLESERVER` remains active, and clears state on failure or `UF_END_SINGLESERVER`.

## State And Persistence
Persistent data is the BUDB database and BUDB text configuration. Runtime state includes `udbHandle` security object/index, server RX connections, Ubik client pointer, instance id, text lock handles in each `udbClientTextT`, temp streams, and static `uServer` single-server call state. Temporary text files are created under `gettmpdir()`, unlinked immediately on Unix, and explicitly removed on NT.

## Dependencies And Integration Points
Depends on OpenAFS auth/cellconfig, RX, Ubik, VLDB, volser, BUDB generated client stubs, `afsconf_PickClientSecObj`, and `bc.h` text/config types. Configuration modules call the text APIs; command, dump, and restore modules call the BUDB record APIs; `main.c` calls the initialization routines.

## Risks And Test Signals
The thin wrappers inherit BUDB RPC semantics and often collapse multi-result or end-of-list cases into local error conventions. `bcdb_FindVolumes` points XDR output directly at caller storage, so RPC stub expectations must match. Text locking can wait indefinitely with one-second sleeps. Temp file error paths must close streams and preserve lock cleanup by callers. `ubik_Call_SingleServer` stores one static selected server, so concurrent single-server series would interfere. Test signals include authenticated, localauth, noauth, and fallback-null initialization; no-cell and too-many-server warnings; text lock contention and timeout sizing; chunked get/save including empty text; version mismatch detection; exact-one dump/tape lookup; BUDB list length consistency; single-server iteration cleanup; and local test initialization.
