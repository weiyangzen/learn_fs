# sources/distributed-fs/ceph-client/tools/perf/util/mem2node.h

## Purpose

`mem2node.h` declares the physical memory to NUMA node mapping helper.

## Important APIs, Types, and Functions

`struct mem2node` contains an rb-tree root, an owned array of physical entries, and a `cnt` field. Public APIs are `mem2node__init()`, `mem2node__exit()`, and `mem2node__node()`.

## Control Flow

There is no implementation flow. Callers initialize from a `perf_env`, query addresses, then exit to release storage.

## State and Persistence Behavior

The struct stores lookup state derived from environment memory-node snapshots. It is caller-owned and must be initialized before lookup.

## Dependencies and Integration Points

It depends on Linux rbtrees and integer types plus `struct perf_env`. It is used by memory analysis code that has physical addresses and wants NUMA attribution.

## Risks and Edge Cases

The `struct phys_entry` type is opaque to callers. The `cnt` field is declared but not set by the current implementation, so callers should not rely on it unless the implementation changes.

## Test Signals

Compile tests should verify callers can allocate the struct on stack or heap. Runtime tests should verify init/query/exit sequencing and unknown address behavior.
