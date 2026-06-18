# sources/distributed-fs/orangefs/src/io/buffer/state.c

## Purpose
Implements NCAC extent state transitions for read/write access, communication completion, dirty tracking, synchronous dirty flush, pending I/O completion propagation, and read-modify-write locking.

## Important APIs, Types, And Functions
Exports `NCAC_extent_read_access`, `NCAC_extent_write_access`, `NCAC_extent_first_read_access`, `NCAC_extent_first_write_access`, `NCAC_extent_done_access`, `NCAC_extent_read_comm_done`, `NCAC_extent_write_comm_done`, `list_set_clean_page`, `NCAC_extent_read_access_recheck`, `NCAC_extent_write_access_recheck`, `data_sync_inode`, and `mark_extent_rmw_lock`.

## Control Flow
Read access increments read count, promotes inactive LRU extents, waits behind writes or pending I/O, and marks read communication when data is clean/dirty. Write access increments write count, waits behind earlier read/write communication or pending I/O, and marks write communication when safe. Done access clears communication flags, decrements/increments completion counters, marks written extents dirty, adds them to inode dirty list, and aggressively calls `data_sync_inode` unless `LAZY_SYNC` is defined. Dirty sync builds Trove list I/O arrays, submits a write, links all dirty extents through `ioreq_next`, marks them write-pending, and clears inode dirty count.

## State And Persistence
Mutates extent flags, read/write counters, completion counters, dirty lists, inode dirty counts, cache dirty counts, and Trove op ids. Persistence occurs only when dirty extents are flushed to Trove via `NCAC_aio_write`.

## Dependencies And Integration Points
Depends on internal NCAC structures, cache/list helpers, flag macros, and `ncac-trove`. It is called from job workers, request completion, eviction, and RMW paths.

## Risks And Test Signals
Risks include complex counter semantics, aggressive sync on every write completion, disabled `balance_dirty_extents`, no free of `data_sync_inode` temporary arrays, possible circular `ioreq_next` assumptions, and return values where completion may still report not ready. Tests should cover read/write transition matrices, pending I/O completion, dirty flush, RMW state, cache dirty counters, and repeated completion of shared extents.
