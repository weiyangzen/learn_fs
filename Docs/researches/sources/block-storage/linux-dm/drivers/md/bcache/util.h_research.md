# File Research: sources/block-storage/linux-dm/drivers/md/bcache/util.h

`util.h` provides shared bcache helper macros, data structures, and inline routines. Debug builds turn `EBUG_ON()` and atomic inc/dec checks into `BUG_ON()` assertions; non-debug builds reduce them to no-op-ish or plain atomic operations.

The heap macros implement an array-backed binary heap with caller-provided comparison, allocation via `kvmalloc()`, and add/pop/peek/full helpers. Moving GC uses this heap to choose partially used buckets. The FIFO macros implement a power-of-two ring buffer used heavily by journal pin tracking and cache bucket reserve lists; variants support exact or rounded sizing, push/pop at both ends, swapping, and moving between FIFOs.

The array allocator macros provide a fixed-size stack freelist over an embedded data array, used by keybuf-style structures where bounded allocation without runtime failure is useful. Red-black tree macros provide generic insert/search/greater/first/last/next/prev wrappers using local comparison callbacks and `container_of_or_null()`.

Parsing and formatting declarations include human-readable integer parsers, safe `kstrtoul()` wrappers, clamped parsing, `bch_hprint()`, zero test, and UUID parsing. Time helpers define `struct time_stats`, `local_clock_us()`, sysfs time-stat print/attribute macros, and `ewma_add()`.

Rate limiting is represented by `struct bch_ratelimit` with nanosecond `next` time and atomic rate; `bch_ratelimit_reset()` and `bch_next_delay()` support writeback throttling. `DIV_SAFE()` avoids divide-by-zero, `bch_crc64()` wraps big-endian CRC64 with init/final xor, and `fract_exp_two()` is a stepwise pseudo-exponential used for congestion bypass thresholds.

The header also declares `bch_bio_map()` and `bch_bio_alloc_pages()`. Because many macros evaluate caller expressions and assume specific in-scope names, this file is powerful but requires careful use at call sites.
