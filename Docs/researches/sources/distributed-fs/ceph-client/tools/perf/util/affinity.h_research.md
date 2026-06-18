# sources/distributed-fs/ceph-client/tools/perf/util/affinity.h

## Purpose

`affinity.h` declares perf's CPU affinity helper state and APIs.

## Important APIs, Types, and Functions

`struct affinity` stores allocated CPU-set size, original and active masks, current CPU, and a `changed` flag. It declares setup, set, cleanup, and CPU-map affinity functions.

## Control Flow and State

There is no runtime flow. The struct encodes restoration state that callers must clean up.

## Dependencies and Integration Points

It forward-declares `struct perf_cpu_map` and is used by perf utilities that temporarily pin execution.

## Risks and Test Signals

Risks are callers skipping cleanup or copying the struct by value. Compile coverage and affinity lifecycle tests validate usage.
