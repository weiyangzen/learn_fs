# sources/distributed-fs/ceph-client/tools/perf/util/values.h

## Purpose

`values.h` declares the per-thread/per-counter read-values table.

## Important APIs, Types, and Functions

`struct perf_read_values` stores row count/capacity, PID/TID arrays, counter count/capacity, evsel pointer array, and a 2D value array. It declares init, destroy, add-value, and display functions.

## Control Flow and State

The table is mutable caller-owned state. Rows are keyed by PID/TID and columns by evsel pointer.

## Dependencies and Integration Points

It depends on Linux integer types and `FILE`; evsel is forward-declared. It is used by code that accumulates `PERF_RECORD_READ` results.

## Risks and Test Signals

Callers must initialize before use and destroy once. Tests should verify zeroed state and repeated accumulation.
