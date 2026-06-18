# File Research: sources/cow-pools/bcachefs-tools/include/linux/bio.h

Purpose: userspace shim for Linux bio helper APIs and bio list handling.

Key contents:
- Defines bio priority helpers, iterator accessors, segment iteration macros, sector/byte helpers, and data/no-advance checks.
- Implements `bio_advance_iter()`, `bio_segments()`, reference helpers, flag helpers, split wrappers, and bio list operations.
- Defines `struct bio_set` and bioset creation/init/exit declarations.
- Declares bio allocation, cloning, put/endio/reset/chain/copy/advance helpers.
- Provides virtual memory bvec mapping stubs.
- `bio_init()` initializes a bio over a caller-provided vec table.

Important interactions:
- Depends on `blkdev.h`, `blk_types.h`, `bvec.h`, atomics, and mempools.
- Used by bcachefs data and VFS I/O paths that are shared with kernel code.
- Dataless operations such as discard/write-zeroes are treated specially for iterator advancement and segment counts.
