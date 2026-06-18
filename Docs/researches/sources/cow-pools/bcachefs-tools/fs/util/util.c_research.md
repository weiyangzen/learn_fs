# File Research: sources/cow-pools/bcachefs-tools/fs/util/util.c

Purpose: General utility implementations for parsing, printing, throttling, bio handling, and misc helpers.

Key APIs and behavior:
- Human-readable numeric parsers accept decimal fractions and binary/SI suffixes.
- Flag-list parser maps comma/semicolon-separated names to a bitmask.
- Implements zero checking, binary printing, line-safe printk output, stack backtrace capture/printing, datetime/time-unit printing.
- Renders `bch2_time_stats` through printbuf and JSON-through-seqbuf.
- Implements rate-limit delay/increment and PD controller update/debug output.
- Implements bio mapping/chaining, synchronous buffer submit, bio page allocation, random bounded u64, bio memcpy helpers, debug bio corruption, and bio text dump.
- Implements percpu u64 accumulation, colon-separated device splitting, kvmalloc mempool wrappers, and iowait-aware wait-bit timeout.

Integration:
- Implements declarations in `util.h`.
- Uses printbuf, time_stats, mean_and_variance, eytzinger, bio/block APIs, mempool APIs, and scheduler helpers.

Risks and invariants:
- `bch2_bio_map_and_chain()` submits earlier chain segments and returns only the tail.
- `bch2_bio_alloc_pages()` requires power-of-two block size and aligned size.
- Human-size parsing carefully checks overflow, but signed conversion stores through `u64` before assignment.
