# sources/distributed-fs/orangefs/src/io/buffer/ncac-trove.h

## Purpose
Declares NCAC storage/Trove helper functions.

## Important APIs, Types, And Functions
Declares `NCAC_aio_read_ext`, `NCAC_aio_write`, `do_read_for_rmw`, and `init_io_read`.

## Control Flow
NCAC workers call these functions to start list reads/writes, read extents for read-modify-write, and initiate single-extent reads.

## State And Persistence
No state is defined directly. Functions return Trove op ids through output pointers and operate on cache memory buffers.

## Dependencies And Integration Points
Requires PVFS/Trove types, `struct aiovec`, and `struct extent` from surrounding includes. It is used by job and state modules.

## Risks And Test Signals
Risks are type drift for `ioreq` output (`int *` in some prototypes versus `PVFS_id_gen_t *` for `init_io_read`) and mismatch between read/write naming and implementation. Compile and Trove integration tests are needed.
