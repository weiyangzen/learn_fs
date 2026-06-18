<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/util.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/util.c

## Purpose
`util.c` implements shared bcache helpers for human-readable parsing/formatting, UUID parsing, timing stats, rate limiting, and bio vector setup/allocation.

## Important APIs, Types, And Functions
`STRTO_H()` generates `bch_strtoint_h()`, `bch_strtouint_h()`, `bch_strtoll_h()`, and `bch_strtoull_h()`. `bch_hprint()` emits compact values with binary units. `bch_is_zero()` validates zero buffers, `bch_parse_uuid()` parses textual UUID hex, `bch_time_stats_update()` updates EWMA timing stats, `bch_next_delay()` computes ratelimit sleeps, `bch_bio_map()` fills bio vectors for a buffer or placeholder pages, and `bch_bio_alloc_pages()` allocates one page per vector.

## Control Flow
Parsers scan decimal text, consume optional suffixes, validate overflow, and return `0` or `-EINVAL`. Time stats lock, read `local_clock()`, and update max/EWMA fields. Rate limiting advances `next`, bounds drift, and returns a jiffy delay. Bio helpers assume initialized bios with sufficient vector storage and leave submission to callers.

## State And Persistence
No global persistent state exists. The file mutates caller-owned stat, ratelimit, UUID, and bio structures; those may feed persistent metadata paths elsewhere.

## Dependencies, Integration Points, Risks, And Test Signals
It uses kernel bio/block/page/vmalloc/time helpers and is used by sysfs, superblock validation, checksum paths, and writeback. Risks include direct bio internals, parser overflow, division by zero if rate is unset, and page allocation unwind correctness. Test suffix parsing, UUID variants, zero detection, formatting, EWMA updates, ratelimit bounds, direct/vmalloc bio mapping, and allocation failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/util.c -->
