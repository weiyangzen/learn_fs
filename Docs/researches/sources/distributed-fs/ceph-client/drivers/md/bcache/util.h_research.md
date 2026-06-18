<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/util.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/util.h

## Purpose
`util.h` is bcache's shared utility header for debug assertions, heap/FIFO/array allocator macros, parsing helpers, time-stat sysfs helpers, ratelimiting, arithmetic, rbtree helpers, CRC64, and bio utility declarations.

## Important APIs, Types, And Functions
It defines `EBUG_ON()`, `atomic_dec_bug()`, `atomic_inc_bug()`, `DECLARE_HEAP`, heap operations, `DECLARE_FIFO`, FIFO operations, `DECLARE_ARRAY_ALLOCATOR`, `strtoi_h()`, `strtoul_safe()`, `strtoul_safe_clamp()`, `struct time_stats`, time-stat sysfs macros, `struct bch_ratelimit`, `DIV_SAFE()`, `container_of_or_null()`, `RB_INSERT`, `RB_SEARCH`, `RB_GREATER`, `bch_crc64()`, and `fract_exp_two()`.

## Control Flow
Most helpers are statement-expression macros that mutate caller-owned structures. FIFO/heap/array helpers depend on declaration macros. Rbtree helpers use caller comparison functions. Sysfs time helpers compare `attr` and emit scaled timing fields.

## State And Persistence
The header owns no state. `bch_crc64()` participates in persistent metadata validation when used by callers.

## Dependencies, Integration Points, Risks, And Test Signals
It is included across bcache allocation, btree, sysfs, superblock, request, and writeback code. Risks include side effects in macro arguments, hidden caller returns, comparison-function correctness, and debug/non-debug behavior differences. Test heap/FIFO wraparound, array allocator reuse, rbtree helpers, time-stat output, CRC64 compatibility, and `fract_exp_two()` bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/util.h -->
