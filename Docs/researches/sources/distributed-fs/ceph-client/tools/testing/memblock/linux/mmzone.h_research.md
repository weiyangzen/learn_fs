<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/mmzone.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/linux/mmzone.h

## Purpose

`linux/mmzone.h` supplies a compact zone and node model for compiling and testing memblock code outside the kernel.

## Important APIs, Types, and Functions

It declares `first_online_pgdat()` and `next_online_pgdat()`, defines `for_each_online_pgdat`, `enum zone_type`, `MAX_NR_ZONES`, `MAX_PAGE_ORDER`, `MAX_ORDER_NR_PAGES`, pageblock alignment helpers, `struct zone` with `managed_pages`, and `pg_data_t` with a `node_zones` array.

## Control Flow

Iteration over online pgdats is delegated to the two functions implemented in `mmzone.c`; in this simulator they currently return `NULL`, so loops over online pgdats do not execute.

## State and Persistence Behavior

The structs describe process-local simulated node/zone state only. No persistent zone data exists outside test memory structures.

## Dependencies and Integration Points

It includes atomic and memory-hotplug shims and is consumed by memblock code paths that refer to zones, pageblocks, or online nodes. It links with `mmzone.c` for iterator functions.

## Risks and Edge Cases

The model is intentionally minimal. Any memblock changes requiring real zone types, multiple zones, managed page accounting, or online pgdat iteration may compile but remain under-modeled.

## Test Signals

Successful compilation and tests that do not unexpectedly require online pgdat iteration are the main signals. New assertions around pageblock alignment should use the constants defined here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/mmzone.h -->
