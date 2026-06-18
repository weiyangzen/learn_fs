# sources/distributed-fs/ceph-client/block/blk-lib.c

## Purpose
`blk-lib.c` provides exported helper operations for block-device range management: discard, write zeroes, zeroout fallback, and secure erase. It translates large logical ranges into bio chains that obey device limits and block-size alignment.

## Important APIs, Types, And Functions
Exported APIs include `__blkdev_issue_discard()`, `blkdev_issue_discard()`, `__blkdev_issue_zeroout()`, `blkdev_issue_zeroout()`, and `blkdev_issue_secure_erase()`. `blk_alloc_discard_bio()` allocates one discard bio at a granularity-aligned size. Internal helpers include `bio_discard_limit()`, `bio_write_zeroes_limit()`, `__blkdev_issue_write_zeroes()`, `blkdev_issue_write_zeroes()`, `__blkdev_issue_zero_pages()`, and `blkdev_issue_zero_pages()`.

## Control Flow
Discard starts by computing an aligned per-bio sector limit, allocating zero-vector discard bios, chaining them with `bio_chain_and_submit()`, and then waiting on the anchor bio in the synchronous wrapper. Zeroout first validates alignment and read-only state, tries hardware `REQ_OP_WRITE_ZEROES` if the queue advertises support, and falls back to explicit writes of the kernel zero folio unless `BLKDEV_ZERO_NOFALLBACK` is set. `BLKDEV_ZERO_KILLABLE` lets long loops stop on fatal signals. Secure erase caps each bio by the device maximum and `BIO_MAX_SECTORS`, checks logical-block alignment, and submits a chain of `REQ_OP_SECURE_ERASE` bios.

## State And Persistence
The file creates transient bio chains and plugs; it does not persist state. Device queue limits may change at runtime, especially write-zeroes capability after transport errors, so wrappers re-check limits and map post-error zeroes failure to `-EOPNOTSUPP` when support is withdrawn.

## Dependencies And Integration Points
It integrates with `struct block_device`, queue limits exposed through `bdev_*` helpers, bio allocation/submission, plugging, zero folios, and exported block APIs used by filesystems, dm/md, and utilities that need discard or zeroing.

## Risks And Test Signals
Important risks are sector-count overflow when shifting to bytes, discard granularity misalignment for partitions, fallback behavior on devices that drop write-zeroes support, killable loops leaving partial progress, and read-only/alignment error paths. Tests should cover partition-offset discard alignment, zeroout with and without `REQ_NOUNMAP`, devices that fail write-zeroes then require fallback, secure erase limit splitting, and full-device operations that exercise `cond_resched()`.
