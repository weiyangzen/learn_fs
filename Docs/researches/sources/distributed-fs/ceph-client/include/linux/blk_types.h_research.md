# sources/distributed-fs/ceph-client/include/linux/blk_types.h

## Purpose
`blk_types.h` defines foundational block-layer data structures and constants while deliberately avoiding heavier include cycles. It provides sector units, `struct block_device`, block status codes, `struct bio`, bio flags, request operation encodings, request flags, and helper classifiers.

## Important APIs, Types, And Functions
Sector constants are `SECTOR_SHIFT`, `SECTOR_SIZE`, `PAGE_SECTORS_SHIFT`, `PAGE_SECTORS`, and `SECTOR_MASK`. `struct block_device` stores partition start/size, disk and queue pointers, per-cpu stats, flags (`BD_PARTNO`, `BD_READ_ONLY`, `BD_WRITE_HOLDER`, `BD_HAS_SUBMIT_BIO`, `BD_RO_WARNED`, optional fail flag), device number, mapping, opener/holder/freeze state, metadata, writers, security, and embedded device.

`blk_status_t` values include OK, unsupported, timeout, no space, transport/target/reservation/medium/protection/resource errors, dm requeue, again, device resource, zone open/active resource, offline, duration limit, and invalid alignment/size. `blk_path_error()` classifies errors for failover retry.

`struct bio` stores queue linkage, target bdev, op/flags, ioprio, write hint/stream, status, bvec gap bit, remaining count, vec array/iterator, poll cookie or zone segments, end_io, private data, optional cgroup, crypto and integrity pointers, vector counts, refcount, and bio pool. Bio flags include cloned, chained, quiet, throttled/accounted/remapped, zone write plugging, and zone append emulation. Request operations include read, write, flush, discard, secure erase, zone append/management, write zeroes, and driver private in/out. Request flags cover failfast, sync/meta/prio/nomerge/idle, integrity, FUA, preflush, readahead, background, nowait, polled, allocation cache, swap, driver/filesystem private, atomic writes, and write-zeroes nounmap.

## Control Flow And State
The header supplies inline classifiers: `bio_op()`, `op_is_write()`, `op_is_flush()`, `op_is_sync()`, `op_is_discard()`, `op_is_zone_mgmt()`, and `op_stat_group()`. It does not implement I/O submission; it defines the state that submission, splitting, scheduling, tracing, and drivers mutate. Bio and bdev lifetimes are reference-counted elsewhere, but the fields here are the common persisted in-memory state for block I/O.

## Dependencies And Integration Points
It includes types, bvecs, device, time, and write-hint headers. `blkdev.h`, `blk-mq.h`, crypto, integrity, tracing, cgroup, and filesystem block helpers all depend on these definitions. It forward-declares several structures to keep include dependencies minimal.

## Risks And Test Signals
Risks include op/flag bit overlap, incorrect assumptions about low operation bit meaning direction, bio lifetime/refcount bugs, cgroup/crypto/integrity fields compiled out, and error classification changes affecting multipath retry. Test signals include compile-time flag layout checks, read/write/flush/zone classifier tests, bio clone/reset preservation around `BIO_RESET_BYTES`, status-to-errno mappings, and bdev flag operations.
