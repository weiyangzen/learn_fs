# sources/distributed-fs/openafs/src/afsmonitor/afsmon-output.c

## Purpose

`afsmon-output.c` appends `afsmonitor` probe results to output files in compact raw-longword form and optional detailed human-readable form.

## Important APIs and Functions

Public entry points are `afsmon_fsOutput()` and `afsmon_cmOutput()`. FS helpers print overall performance, RPC timing, transfer timing, detailed full performance, and callback stats. CM helpers print up/down records, overall performance, RPC timings/errors/transfers, authentication state, and replicated-access stats. Static operation-name tables label repeated arrays.

## Control Flow

`afsmon_fsOutput()` opens the output file, writes `ctime hostname FS`, emits `-1` for failed probes, otherwise writes all FS collection longwords and optional detailed output based on collection number. `afsmon_cmOutput()` does the same for `CM` records and calls full CM detailed decoding when requested. Detailed paths validate expected struct sizes where available and cast/decode xstat buffers into typed structures.

## State and Persistence Behavior

The persistent contract is the appended monitor log format consumed by `afsmon-parselog.c`. Static file pointers hold the active output stream while helper functions print.

## Dependencies and Integration Points

The file depends on `xstat_fs.h`, `xstat_cm.h`, `afsmonitor.h`, global monitor debug/error state, `afsmon_Exit()`, and parser/label tables that duplicate the same statistic ordering.

## Risks and Test Signals

Concurrent writers can interleave because output is append-only without locking. `ctime()` formatting is part of the parser contract. CM detailed output assumes full-performance layout. Width-sensitive `%d` formats and duplicated operation tables can drift. Test failed probes, compact row counts, detailed decodes, size mismatches, callback truncation, append behavior, and parser round-trip.
