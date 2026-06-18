# sources/distributed-fs/openafs/src/ptserver/display.h

## Purpose
Declares protection database display helpers for regular and continuation entries.

## Important APIs, Types, And Functions
Exports `pr_PrintEntry(FILE *f, int hostOrder, afs_int32 ea, struct prentry *e, int indent)` and `pr_PrintContEntry(FILE *f, int hostOrder, afs_int32 ea, struct contentry *e, int indent)`.

## Control Flow
Callers pass an output stream, byte-order flag, database address, entry pointer, and indentation. Implementations perform all formatting in `display.c`.

## State And Persistence
No state is declared. The API only writes diagnostics to a stream.

## Dependencies And Integration Points
Included by `ptclient.c`, `prdb_check.c`, and other protection database diagnostic tools. Requires surrounding includes to define `FILE`, `afs_int32`, `struct prentry`, and `struct contentry`.

## Risks And Test Signals
Risk is declaration drift with `display.c` or missing prerequisite type includes. Test signals are successful compilation and formatted database-entry output.
