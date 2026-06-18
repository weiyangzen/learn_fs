# sources/distributed-fs/lustre-release/lnet/utils/routerstat.c

## Purpose
`routerstat.c` monitors the LNet `stats` parameter file and prints either absolute router counters or per-second deltas at a requested interval.

## Important APIs, Types, and Functions
`counters_t` mirrors the expected eleven stats fields. `timenow()` provides a floating timestamp, `subul()`/`subull()` handle unsigned wraparound deltas, `rul()`/`rull()` calculate rates, `do_stat()` reads/parses/prints stats, and `main()` locates the stats parameter via `cfs_get_param_paths()`.

## Control Flow
The first sample prints absolute values. Later samples seek to the start of the same file, parse counters, compute elapsed time and deltas against static previous counters, and print rates for errors, bytes, sends, receives, routes, and drops. With no interval or interval zero the program exits after one sample; otherwise it loops forever.

## State and Persistence Behavior
Previous counters and timestamps are static in `do_stat()`. No files or kernel state are modified.

## Dependencies and Integration Points
It integrates with libcfs parameter discovery and the kernel-exposed LNet `stats` file, plus standard POSIX read/open/seek/time APIs.

## Risks and Edge Cases
`atoi()` silently treats invalid intervals as zero, parse/read errors exit the process, the parser assumes exactly eleven fields, only the first discovered stats path is used, and very small elapsed intervals can produce noisy rates.

## Test Signals
Use fake stats files to test first-sample output, delta output, wraparound, malformed input, missing stats path, interval parsing, and short reads.
