<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fsx.c -->
# sources/distributed-fs/openafs/src/tests/fsx.c

## Purpose
Runs the classic randomized file-system exerciser against an AFS-hosted file, mixing reads, writes, mmap reads/writes, truncates, and close/reopen cycles while checking an in-memory oracle.

## Important APIs, Types, and Functions
functions: prt, prterr, log4, logdump, save_buffer, report_failure, check_buffers, check_size, check_trunc_hack, doread, domapread, gendata, dowrite, domapwrite, dotruncate, writefileimage; AFS calls/macros: AFS_FALLTHROUGH

## Control Flow
Parses many tuning flags, seeds pseudo-random operations, logs the last 1000 operations, mutates `good_buf` as the expected file image, executes matching system calls on the target file, compares reads/mmap reads against the oracle, and dumps the operation log plus `.fsxgood` data on failure.

## State and Persistence Behavior
Creates and mutates one target file plus optional `.fsxlog` and `.fsxgood` evidence; global state tracks file size, biggest truncate, operation count, random seed, mapping/read/write enablement, and failure offsets.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting; AFS interfaces AFS_FALLTHROUGH

## Risks and Test Signals
High-value stress test for cache coherency, mmap/writeback, holes, truncate extension, short I/O, and close/open callback behavior; randomness means seed and options are required for reproducible failures.

## Source Notes
Read as C program; 1063 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fsx.c -->
