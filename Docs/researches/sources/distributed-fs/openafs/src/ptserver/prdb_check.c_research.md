# sources/distributed-fs/openafs/src/ptserver/prdb_check.c

## Purpose
Implements `prdb_check`, an offline consistency checker and optional rebuild-script generator for the protection database (`ptdb.DB0`).

## Important APIs, Types, And Functions
Major routines are `printheader`, `pr_Read`, `ReadHeader`, `IDHash`, `NameHash`, `readUbikHeader`, `ConvertDiskAddress`, `PrintEntryError`, `PrintContError`, `WalkHashTable`, `WalkNextChain`, `WalkOwnedChain`, `WalkChains`, `GC`, `QuoteName`, `DumpRecreate`, `CheckPrDatabase`, `WorkerBee`, and `main`. Under `SUPERGROUPS`, `zeromap`, `inccount`, and `idcount` track large sparse ID reference counts. `misc_data` accumulates counts, max/min ids, chain lengths, verbosity flags, and the rebuild output stream.

## Control Flow
`main` registers command options for database path, header display, entry display, verbose mode, and hidden rebuild output. `WorkerBee` opens the database read-only, reads Ubik and protection headers, optionally prints them, opens rebuild output, and calls `CheckPrDatabase`. The checker validates EOF alignment, walks name and ID hash tables, computes ID ranges, walks entry membership chains, continuation chains, free list, owner/orphan chains, checks unreferenced entries and membership counts, generates recreate commands, and compares observed counts/max IDs against header values.

## State And Persistence
Reads the database file directly using `lseek`/`read`; it does not use Ubik transactions. Optional `-rebuild` writes a command script capable of recreating entries and memberships. In-memory maps mark whether each entry was seen in hashes, continuation/free/owned chains, or recreate output.

## Dependencies And Integration Points
Depends on exact on-disk `prheader`, `prentry`, `contentry`, Ubik header size/magic, protection error tables, command parser, and `display.c`. It complements `pt_util` and `ptclient` as an offline diagnostic/recovery tool.

## Risks And Test Signals
Risks include stale reads if the database changes during checking, index math tied to struct size, large non-supergroup ID ranges causing big allocations, rebuild ordering edge cases for owner cycles, and diagnostics that continue after some corruption. Test signals include clean output for a known-good database, intentional hash/continuation/owner/free-list corruption detection, header count mismatch reporting, and valid rebuild script generation.
