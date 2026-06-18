# sources/distributed-fs/orangefs/src/io/buffer/ncac-trove.c

## Purpose
Connects NCAC cache extents to Trove asynchronous storage operations, including list I/O, single-extent reads, read-modify-write reads, completion polling, and in-place coalescing of offset/length arrays.

## Important APIs, Types, And Functions
Exports `NCAC_aio_read_ext`, `NCAC_aio_write`, `do_read_for_rmw`, `NCAC_check_ioreq`, and `init_io_read`. Private helper `offset_shorten` coalesces contiguous stream and memory ranges.

## Control Flow
List I/O helpers adjust partial extents to full extent-size operations, coalesce adjacent file and memory ranges, submit Trove list operations, and return an op id. `init_io_read` starts a `trove_bstream_read_at` for a single extent. `NCAC_check_ioreq` polls `trove_dspace_test` for the stored op id and invalidates it after completion. `do_read_for_rmw` reads a full extent into cache memory before write modification.

## State And Persistence
State changes include returned Trove op ids stored on extents or requests and cache memory contents filled by Trove. Persistence is external storage through Trove reads/writes; this file itself stores no durable metadata.

## Dependencies And Integration Points
Depends on Trove APIs, NCAC internal state, `aiovec`, and state helpers. Job and state code use it to start reads, flush dirty extents, and detect I/O completion.

## Risks And Test Signals
Risks include `NCAC_aio_read_ext` calling `trove_bstream_write_list` despite its read name, `offset_shorten` using `s_cnt` in the memory compaction loop, pointer arithmetic that can move memory offsets backward when aligning to extent boundaries, fixed dummy user pointer, and only single-op completion state. Tests should verify read/write direction, coalescing correctness, alignment behavior, pending-op completion, and dirty flush data reaching Trove.
