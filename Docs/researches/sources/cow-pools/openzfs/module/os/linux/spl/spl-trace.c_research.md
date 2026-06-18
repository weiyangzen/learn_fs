# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-trace.c

## Purpose

Defines SPL tracepoints exactly once for Linux builds.

## Contents

The file includes `sys/taskq.h`, defines `CREATE_TRACE_POINTS`, then includes:

- `sys/trace.h`
- `sys/trace_taskq.h`

## Notes

There is no runtime logic. Its role is build/link ownership for DTrace-style tracepoint definitions used by SPL taskq instrumentation.
