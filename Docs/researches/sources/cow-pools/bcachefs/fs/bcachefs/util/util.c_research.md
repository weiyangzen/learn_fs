# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/util.c

## Summary
Implements broad bcachefs utility routines for parsing, printing, time-stat formatting, rate control, bio mapping, random values, bio copying, debugging, percpu accumulation, device-list splitting, mempool allocation, and wait-bit timeout behavior.

## Main Responsibilities
- Parses human-readable integer strings with binary/decimal unit suffixes.
- Parses comma/semicolon flag lists.
- Prints binary integers, multiline strings, stack traces, datetimes, time units, and time stats.
- Implements ratelimit delay/increment and a proportional-derivative controller.
- Maps kernel/vmalloc buffers into bios and builds chained bios over large buffers.
- Allocates bio pages, submits buffer bios synchronously, and copies to/from bios.
- Emits textual bio diagnostics.
- Accumulates percpu u64 arrays and zeroes source CPU copies.
- Splits colon-separated device strings into allocated string arrays.
- Provides `mempool_kvmalloc` shims and an IO-accounted wait-bit timeout helper.

## Key APIs
- `bch2_strtoint_h()`, `bch2_strtouint_h()`, `bch2_strtoll_h()`, `bch2_strtoull_h()`, `bch2_strtou64_h()`.
- `bch2_read_flag_list()`, `bch2_is_zero()`.
- `bch2_save_backtrace()`, `bch2_prt_backtrace()`, `bch2_prt_task_backtrace()`.
- `bch2_time_stats_to_text()`, `bch2_time_stats_json_to_text()`.
- `bch2_ratelimit_delay()`, `bch2_ratelimit_increment()`.
- `bch2_pd_controller_update()`, `bch2_pd_controller_init()`, `bch2_pd_controller_debug_to_text()`.
- `bch2_bio_map()`, `bch2_bio_map_and_chain()`, `bch2_bio_submit_buf_wait()`, `bch2_bio_alloc_pages()`.
- `bch2_get_random_u64_below()`, `memcpy_to_bio()`, `memcpy_from_bio()`, `bch2_bio_to_text()`.
- `bch2_acc_percpu_u64s()`, `bch2_split_devs()`, `bch2_bit_wait_io_timeout()`.

## Important Behavior
Human-readable parsing supports decimal fractions and suffixes such as SI one-letter units, `KiB`-style binary units, and `kB`-style decimal units with overflow checking.

`bch2_bio_map_and_chain()` returns the tail bio while submitting earlier chained bios in sector order, preserving forward submission and applying `REQ_PREFLUSH` only to the first bio.

The PD controller adjusts a rate based on proportional and derivative error terms and can suppress rate increases under backpressure when work is already delayed.

## Risks
This file contains low-level helpers used across storage and VFS paths. Incorrect bio chaining, page allocation sizing, or buffer lifetime assumptions can lead to I/O completion surprises. Several helpers assume caller-side locking, especially percpu accumulation and bio/page operations.
