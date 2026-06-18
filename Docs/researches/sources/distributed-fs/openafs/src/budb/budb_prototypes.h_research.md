<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/budb_prototypes.h -->
# sources/distributed-fs/openafs/src/budb/budb_prototypes.h

## Purpose
Provides a narrower set of budb helper prototypes, mostly for structure conversion, default tape-set generation, and debug printing.

## Important APIs, Types, And Functions
The file declares `structDumpHeader_ntoh`, `DbHeader_ntoh`, `dumpEntry_ntoh`, `tapeEntry_ntoh`, `volumeEntry_ntoh`, `default_tapeset`, and print helpers for dump, tape, and volume RPC entries.

## Control Flow
There is no executable control flow. Consumers include this header when translating RPC/database dump structures from network to host order or when formatting entries for user-visible diagnostics.

## State And Persistence
No state is defined here. The declared conversion functions are persistence-relevant because saved database streams and RPC structs use fixed network-order layouts.

## Dependencies And Integration Points
It integrates with generated `budb.h` structures and `struct_ops.c`. It complements `budb_internal.h`, but only exposes a small public-ish utility surface.

## Risks And Test Signals
Risk is declaration drift against `struct_ops.c` or generated RPC types. Test signals include dump stream decode/encode tests, admin command output for dump/tape/volume entries, and cross-endian structure conversion coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/budb_prototypes.h -->
