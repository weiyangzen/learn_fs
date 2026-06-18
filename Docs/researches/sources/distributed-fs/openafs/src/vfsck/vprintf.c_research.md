<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/vprintf.c -->
# sources/distributed-fs/openafs/src/vfsck/vprintf.c

## Purpose
Adds OpenAFS-specific mirrored logging for fsck messages. It prints messages to stdout and, when configured, duplicates them into the vfsck log file for non-root AFS server partitions.

## Important APIs, Types, And Functions
The single function is `vfscklogprintf(char *s, long a1, ... long a10)`. It uses global `logfile` declared in `fsck.h` and standard `printf`, `fprintf`, and `fflush`.

## Control Flow
Each call prints the format string and up to ten K&R-style long arguments to stdout. If `logfile` is non-null, it writes the same formatted message to that file and flushes it immediately.

## State And Persistence
The function does not open or close the log; it writes to the already-open `logfile`. Persistent state is the appended log content, and stdout output is immediate process I/O.

## Dependencies And Integration Points
Several files define `msgprintf` as `vfscklogprintf` when `VICE` is enabled. `main.c` later fsyncs and closes `logfile` after modifications. The function depends on all callers matching its fixed ten-argument varargs convention.

## Risks And Test Signals
Risks include format/argument mismatches, truncation of non-`long` varargs on some ABIs, and logging being skipped when `logfile` setup is absent. Tests should verify mirrored output for normal, preen, and error messages and build on 32-bit/64-bit targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/vprintf.c -->
