<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub-status.c -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub-status.c

## Purpose
Thread-safe counters and timestamp updates for bit-rot scrub statistics.

## APIs, Types, and Functions
Implements `br_inc_unsigned_file_count()`, `br_inc_scrubbed_file()`, `br_update_scrub_start_time()`, and `br_update_scrub_finish_time()`. These update fields in `br_scrub_stats_t` under its pthread mutex.

## Control Flow, State, and Persistence
Each function returns immediately on null input. Counter increments lock, update one counter, and unlock. Start time stores `scrub_start_time`. Finish time validates the supplied formatted time fits in `last_scrub_time`, then records `scrub_end_time`, calculates `scrub_duration`, and copies the string. State is volatile in `br_private_t.scrub_stat` and later exposed by bit-rot status code.

## Dependencies and Integration
Depends on pthreads, `GF_TIMESTR_SIZE` from GlusterFS common utilities, and `bit-rot-scrub-status.h`. Called by scrub execution in `bit-rot-scrub.c` and status export in `bit-rot.c`.

## Risks and Test Signals
Risks include unsynchronized readers elsewhere seeing partial stats, finish updates silently skipped if the time string is too long, and duration underflow if finish precedes start due to bad sequencing. Test signals are concurrent scrub counter updates, status dictionary values, and start/finish duration correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub-status.c -->
