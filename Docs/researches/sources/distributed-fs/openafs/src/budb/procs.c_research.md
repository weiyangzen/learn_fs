<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/procs.c -->
# sources/distributed-fs/openafs/src/budb/procs.c

## Purpose
Implements the main budb RPC service for dump, tape, and volume metadata. It creates and finishes dumps/tapes, records volumes, deletes database objects, lists/query entries, manages appended dumps, and provides debug dump/hash inspection RPCs.

## Important APIs, Types, And Functions
Initialization and security use `InitProcs`, `AwaitInitialization`, `callPermitted`, and `InitRPC`. Fill/list helpers include `FillVolEntry`, `FillDumpEntry`, `FillTapeEntry`, `returnList`, `AddToReturnList`, and `SendReturnList`. Mutation helpers include `GetVolInfo`, `DeleteVolInfo`, `DeleteVolFragment`, `DeleteTape`, `DeleteDump`, `deleteSomeVolumesFromTape`, `deleteDump`, `getExpiration`, and `makeAppended`. RPC bodies include `AddVolume(s)`, `CreateDump`, `DoDeleteDump`, `DoDeleteTape`, `DeleteVDP`, `FindClone`, `FindDump`, `FindLatestDump`, `FinishDump`, `FinishTape`, `GetDumps`, `GetTapes`, `GetVolumes`, `UseTape`, `MakeDumpAppended`, `FindLastTape`, `T_DumpHashTable`, `T_GetVersion`, and `T_DumpDatabase`.

## Control Flow
Every meaningful RPC opens a Ubik transaction through `InitRPC`, validates permissions/arguments, uses hash tables to locate records, mutates linked on-disk records, updates `lastUpdate` for writes, and ends or aborts the transaction through `ERROR`/`ABORT` labels. Dumps are created in-progress, tapes are attached and marked being written, volumes create fragments linked to both tape and volInfo, then finish calls clear in-progress flags. Deletes are staged in small transactions, removing volume fragments before tapes and dumps.

## State And Persistence
Persistent state is the budb graph: dumps indexed by id/name, tapes indexed by name and linked to dumps, volume fragments linked to tapes and volume info, volume info same-name chains, appended dump chains, and header counters/timestamps. Some query RPCs intentionally allow unauthenticated specific lookups.

## Dependencies And Integration Points
This is the service layer above `database.c`, `db_alloc.c`, `db_hash.c`, and struct conversion helpers. It integrates RX/RXKAD identity, afsconf superuser checks, Ubik replication, audit events, backup client RPC structs, and debug file output under `gettmpdir()`.

## Risks And Test Signals
Risks include complex linked-structure invariants, partial delete progress, unchecked string copies after length validation gaps, appended-dump loop/cycle handling outside verifier, global noauth mode, and broad debug RPC file output. Signals are end-to-end dump lifecycle tests, volume batch add, appended dump chains, delete interruption/retry, list pagination via `nextIndex`, find latest/clone/last tape, verifier after each mutation, and permission/noauth tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/procs.c -->
