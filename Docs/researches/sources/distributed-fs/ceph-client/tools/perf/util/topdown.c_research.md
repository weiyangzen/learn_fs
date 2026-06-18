# sources/distributed-fs/ceph-client/tools/perf/util/topdown.c

## Purpose

`topdown.c` provides the weak generic implementation of architecture-specific top-down sample reading.

## Important APIs, Types, and Functions

`arch_topdown_sample_read(struct evsel *leader)` is defined weakly and returns false.

## Control Flow and State

There is no state. Architectures can override the weak symbol to indicate and perform top-down sample reading for event groups.

## Dependencies and Integration Points

It depends on `topdown.h` and is linked into perf unless an architecture implementation replaces it.

## Risks and Test Signals

The default must remain conservative. Tests should verify non-supporting builds return false and architecture builds override as intended.
