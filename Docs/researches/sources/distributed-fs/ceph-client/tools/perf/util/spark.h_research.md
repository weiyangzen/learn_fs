# sources/distributed-fs/ceph-client/tools/perf/util/spark.h

## Purpose

`spark.h` exposes the small sparkline-rendering interface used by perf text output.

## Important APIs, Types, and Functions

It defines `NUM_SPARKS` as 8 and declares `print_spark(char *bf, int size, unsigned long *val, int numval)`.

## Control Flow and Data Flow

The header has no control flow. Callers include it to size logic around the eight-level spark scale and to call the renderer implemented in `spark.c`.

## State and Persistence Behavior

No state is declared. The macro fixes the number of visual buckets at compile time.

## Dependencies and Integration Points

It is self-contained and integrates with text display code that wants compact trend output.

## Risks and Edge Cases

Changing `NUM_SPARKS` requires updating the tick table in `spark.c`. Callers should treat the rendered output as UTF-8 bytes, not one byte per visual cell.

## Test Signals

Build coverage and simple sparkline snapshots are sufficient for the header contract.
