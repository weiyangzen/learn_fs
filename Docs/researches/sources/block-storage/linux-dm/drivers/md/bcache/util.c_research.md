# File Research: sources/block-storage/linux-dm/drivers/md/bcache/util.c

`util.c` implements bcache utility functions declared in `util.h`. The generated `bch_strto*_h()` parsers accept decimal numbers with binary size suffixes from `k` through `y`/`z`, reject malformed trailing characters, and check overflow for signed and unsigned targets while multiplying by 1024.

`bch_hprint()` formats signed 64-bit values into compact binary-suffix strings for sysfs, always scaling at least once so byte-like values print with a suffix. `bch_is_zero()` tests a memory range for all-zero bytes. `bch_parse_uuid()` parses up to 32 UUID hex nybbles while tolerating separators from a restricted character set.

`bch_time_stats_update()` updates max duration plus EWMA duration/frequency under a spinlock using `local_clock()`. `bch_next_delay()` implements rate-limit scheduling by advancing the next desired work time based on work done and an atomic rate, bounding both backlog and future sleep to keep writeback responsive.

`bch_bio_map()` initializes a fresh bio's bvec table to cover either a linear memory buffer or unbacked pages, directly filling `bi_io_vec`/`bi_vcnt` because callers use newly initialized bios. `bch_bio_alloc_pages()` allocates a page for each bvec and frees already allocated pages on failure. These helpers are used by cache insert, moving GC, writeback, journal/UUID/prio I/O, and sysfs formatting.
