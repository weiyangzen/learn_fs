# sources/distributed-fs/openafs/src/afsmonitor/afsmon-parselog.c

## Purpose

`afsmon-parselog.c` is a standalone reader for compact `afsmonitor -output` logs. It converts raw longword records back into readable FS or CM statistics.

## Important APIs and Functions

Hard-coded `XSTAT_CM_FULLPERF_RESULTS_LEN` and `XSTAT_FS_FULLPERF_RESULTS_LEN` define expected record sizes. FS and CM print helpers mirror `afsmon-output.c`, and `main()` parses records, converts text longwords into a buffer, casts to xstat structures, and prints decoded sections.

## Control Flow

The program opens the named log file, allocates a line buffer and longword buffer, skips short lines, parses `day month date time year hostname hosttype`, handles `-1` failed probes, selects FS or CM expected lengths, scans values, validates counts, and dispatches to FS or CM printers.

## State and Persistence Behavior

It persists no state. It depends on the persisted compact log format from `afsmon-output.c` and on local struct layout matching the producer.

## Dependencies and Integration Points

The file depends on xstat FS/CM headers, libc parsing/allocation, and the exact compact-row format emitted by the monitor.

## Risks and Test Signals

Hard-coded lengths must change with xstat structures. Unbounded `%s` scans can overflow fixed buffers. Pointer advancement assumes ctime spacing. Direct casts from parsed `long` buffers are word-size, endian, alignment, and packing sensitive. Test parser round-trip, malformed host types, failed probes, truncated records, overlong fields, and cross-architecture compatibility.
