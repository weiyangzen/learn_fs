# sources/distributed-fs/openafs/src/bucoord/dsvs.c

## Purpose
Maintains core in-memory abstractions for volume sets and dump schedules independent of their BUDB text persistence. It parses host and partition selectors, creates/deletes volume sets and entries, creates/deletes dump schedule nodes, and rebuilds the dump schedule tree from pathname-style schedule names.

## Important APIs, Types, And Functions
Volume-set APIs include `bc_GetPartitionID`, `bc_ParseHost`, `bc_CreateVolumeSet`, `bc_AddVolumeItem`, `bc_DeleteVolumeItem`, `bc_DeleteVolumeSet`, `bc_FindVolumeSet`, and `FreeVolumeSet`. Dump-schedule APIs include `bc_CreateDumpSchedule`, `bc_DeleteDumpSchedule`, `bc_DeleteDumpScheduleAddr`, `bc_FindDumpSchedule`, `bc_ProcessDumpSchedule`, and `FindDump`. Private helpers free `struct bc_volumeEntry` lists.

## Control Flow
Partition parsing accepts `.*` as wildcard `-1`, numeric strings, single-letter partition names, and `vicep`/`/vicep` names. Host parsing first accepts dotted IPv4 strings, then wildcard `.*`, then DNS names via `gethostbyname`. Volume-set creation rejects duplicates and prepends temporary sets while appending persistent sets. Entry creation appends to the selected set after duplicating selector strings and resolving host/partition fields. Dump schedule creation uses `FindDump` to validate path parents and reject duplicates, prepends a new node, stores expiration metadata, and rebuilds the tree. Schedule deletion recursively removes children then rebuilds parent/child/sibling links.

## State And Persistence
All state is in `struct bc_config`: `vset` is a linked list of `bc_volumeSet` objects with `bc_volumeEntry` children, and `dsched` is a flat linked list with derived tree pointers (`parent`, `firstChild`, `nextSibling`). This file does not write persistence; `vol_sets.c` and `dump_sched.c` serialize these lists into BUDB text blocks.

## Dependencies And Integration Points
Depends on `bc.h`, `bucoord_internal.h`, resolver/socket APIs, `opr_Assert`, and backup error constants. It is the shared model layer used by command handlers and by text parse/save modules.

## Risks And Test Signals
IPv4 dotted parsing does not range-check octets before bit shifting. `bc_ParseHost` byte-order handling differs between dotted names and `gethostbyname`, which deserves interoperability tests. `FindDump` is strict about leading slash and can return confusing errors for trailing slashes. `bc_ProcessDumpSchedule` exits the process if an existing schedule path cannot be found. Test signals include wildcard partition/host entries, all partition name forms, invalid dump path syntax, duplicate set/schedule rejection, temporary volume set ordering and non-persistence, recursive schedule deletion, and tree rebuild correctness for multi-level paths.
