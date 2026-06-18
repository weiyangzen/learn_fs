# sources/distributed-fs/ceph-client/fs/zonefs/trace.h

## Purpose
`zonefs/trace.h` defines tracepoints for observing zonefs zone management, direct append/write-pointer behavior, and iomap mapping decisions.

## Important APIs, types, and functions
It declares `TRACE_SYSTEM zonefs` and trace events `zonefs_zone_mgmt`, `zonefs_file_dio_append`, and `zonefs_iomap_begin`. It uses `show_dev`, `blk_op_str`, zone sector information, inode numbers, offsets, lengths, and iomap addresses.

## Control flow
`super.c` defines `CREATE_TRACE_POINTS` before including this header, while other zonefs files include it for trace event declarations. The bottom `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` settings support trace generation from the local source directory.

## State and persistence
Tracepoints keep no filesystem state. They emit runtime diagnostic events when enabled.

## Dependencies and integration points
It depends on Linux tracepoint infrastructure, block operation names, blkdev types, and `zonefs.h`. It integrates with tracefs/perf/ftrace tooling.

## Risks and test signals
Risks include format mismatch, missing local include path, or dereferencing fields not valid at trace time. Test signals include building with tracing, enabling each event during zone management, direct writes, reads, and iomap operations.
