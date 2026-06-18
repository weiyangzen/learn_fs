<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub-status.h -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub-status.h

## Purpose
Defines the scrub statistics structure and update API for bit-rot scrub status.

## APIs, Types, and Functions
`struct br_scrub_stats` tracks `scrubbed_files`, `unsigned_files`, last scrub duration, formatted last scrub completion time, start/end timestamps, `scrub_running`, and a pthread mutex. Declares the increment and start/finish update functions implemented in the C file.

## Control Flow, State, and Persistence
The header has no control flow. It defines volatile process state stored inside `br_private_t` and consumed by scrub execution and status reporting.

## Dependencies and Integration
Includes standard integer/time/pthread headers and relies on GlusterFS time string sizing being available to includers.

## Risks and Test Signals
Risks are lock initialization/destruction ownership outside this header and readers that do not take the lock. Test signals are clean initialization, concurrent scrub updates, and exported status fields matching expected counters and timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub-status.h -->
