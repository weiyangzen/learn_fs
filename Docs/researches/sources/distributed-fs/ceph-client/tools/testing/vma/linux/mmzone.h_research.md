<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/linux/mmzone.h -->
# sources/distributed-fs/ceph-client/tools/testing/vma/linux/mmzone.h

## Purpose

`vma/linux/mmzone.h` provides a minimal mmzone header for userspace VMA testing.

## Important APIs, Types, and Functions

It declares `first_online_pgdat()` and `next_online_pgdat()`, defines `for_each_online_pgdat`, `enum zone_type`, `MAX_NR_ZONES`, `MAX_PAGE_ORDER`, `MAX_ORDER_NR_PAGES`, pageblock macros, `struct zone` with `managed_pages`, and `pg_data_t` containing `node_zones`.

## Control Flow and State

Iteration over online pgdats is delegated to externally supplied harness functions. Zone state is reduced to managed page counters.

## Dependencies and Integration Points

It depends on Linux atomic types and alignment/bit macros from shared headers. It supports imported mm code that expects zone and pgdat types while running in the VMA harness.

## Risks and Test Signals

Risks include oversimplified NUMA/zone behavior and fixed pageblock order assumptions. Successful VMA tests that touch page accounting or pgdat iteration validate the minimal model for harness purposes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/linux/mmzone.h -->
