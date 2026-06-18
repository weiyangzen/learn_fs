# sources/distributed-fs/ceph-client/tools/perf/util/topdown.h

## Purpose

`topdown.h` declares the architecture hook for top-down sample reading.

## Important APIs, Types, and Functions

It forward-declares `struct evsel` and exports `arch_topdown_sample_read()`.

## Control Flow and State

The header has no state. Runtime behavior depends on whether an architecture overrides the weak implementation.

## Dependencies and Integration Points

It is included by common code that wants top-down analysis without depending on a specific PMU backend.

## Risks and Test Signals

The key risk is an architecture override with incompatible semantics. Build tests should verify the declaration matches overrides.
