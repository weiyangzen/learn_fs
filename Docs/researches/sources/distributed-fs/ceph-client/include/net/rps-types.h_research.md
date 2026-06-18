# sources/distributed-fs/ceph-client/include/net/rps-types.h

Purpose: defines the compact tagged pointer format used for RPS socket flow tables.

Important APIs and types: `typedef unsigned long rps_tag_ptr` stores a table pointer with the low five bits holding `ilog2(size)`. Helpers extract the log, compute the mask, and recover the table pointer by clearing low bits.

Control flow: RPS/RFS code reads a tag from hotdata, derives index mask from flow hash, and accesses the table pointer without storing separate size and pointer fields.

State and persistence: no owned state; it interprets packed runtime pointers.

Dependencies and integration points: used by `rps.h` and net hotdata RPS table storage.

Risks and test signals: risks include pointer alignment assumptions, table sizes beyond 31-bit log encoding, and mask overflow for invalid tags. Test RPS table allocation alignment, varying table sizes, zero tag handling, and 32/64-bit builds.
