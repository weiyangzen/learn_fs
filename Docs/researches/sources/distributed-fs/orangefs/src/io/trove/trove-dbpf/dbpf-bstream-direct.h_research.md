# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream-direct.h

## Purpose
`dbpf-bstream-direct.h` is intended to expose direct bytestream worker service routines to code that posts manager operations.

## Important APIs, types, and functions
It declares `dbpf_bstream_direct_read_op_svc(void *ptr, TROVE_hint *hints)` and `dbpf_bstream_direct_write_op_svc(void *ptr, TROVE_hint *hints)`.

## Control flow and state
The header owns no state. It includes `pvfs2-internal.h` and `trove-types.h`, and uses an include guard.

## Persistence and integration
The declarations correspond conceptually to the service routines that perform direct reads/writes and dspace size updates, but the paired source defines those routines as `static int ... (void *ptr, PVFS_hint hint)`. In the current file set, the header is not the source of truth for linkage.

## Dependencies
It depends on the Trove hint type and internal PVFS definitions.

## Risks and test signals
The signature and linkage mismatch is a maintenance risk: including this header in a translation unit that expects external definitions would fail to link or warn. A compile-all test with warnings enabled should catch the mismatch. If the intended design is private static callbacks only, this header may be obsolete or should be aligned with actual callback signatures.
