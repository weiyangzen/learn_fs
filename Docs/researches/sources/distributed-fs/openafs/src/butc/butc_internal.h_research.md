# sources/distributed-fs/openafs/src/butc/butc_internal.h

## Purpose
`butc_internal.h` is the internal Tape Coordinator prototype header. It shares non-public functions across `butc` compilation units without exporting them as a stable external API.

## Important APIs, Types, And Functions
The header declares database-entry queue functions from `dbentries.c` (`useTape()`, `addVolume()`, `finishTape()`, `flushSavedEntries()`, `waitDbWatcher()`, `finishDump()`, `threadEntryDir()`), XBSA dump initialization when compiled with `xbsa`, task ID allocation, tape/LWP helpers, recovery helpers, authorization checks, and task abort checks.

## Control Flow
It has no runtime flow. It controls cross-file call visibility and conditional compilation. The only type forward declaration is `struct butx_transactionInfo` for the XBSA-specific `InitToServer()` signature.

## State And Persistence
The header declares functions that manipulate coordinator runtime state and backup database persistence, but owns no state itself. Its prototypes document which modules can enqueue BUDB updates, manage tape labels, prompt/unmount media, parse database tapes, and check task abort state.

## Dependencies And Integration Points
It depends on OpenAFS integer and tape/database types being available before inclusion. It is an integration point among `dbentries.c`, `dump.c`, `list.c`, `lwps.c`, `recoverDb.c`, `tcprocs.c`, and `tcstatus.c`.

## Risks And Test Signals
Risks are prototype drift and conditional XBSA mismatches. Because this is a private header, compile coverage of every platform/configuration combination is the primary test signal, especially `xbsa` and non-`xbsa` builds. Runtime tests indirectly cover it through dump, restore, tape label, database recovery, and abort-permission workflows.
