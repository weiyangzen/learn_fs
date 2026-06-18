# sources/distributed-fs/ceph-client/drivers/hv/mshv_debugfs_counters.c

## Purpose

`mshv_debugfs_counters.c` is data-only support for `mshv_debugfs.c`. It maps Hyper-V stats-page counter indices to printable names for hypervisor, logical processor, partition, and VP counters.

## Important APIs, Types, and Functions

- `hv_hypervisor_counters[]` names hypervisor-wide counters such as logical processors, partitions, pages, and startup cost.
- `hv_lp_counters[]` names logical processor counters, with architecture-specific x86_64 and arm64 suffix ranges.
- `hv_partition_counters[]` names partition counters including GPA/device pages, TLBs, attached devices, auto suspend, and active child partitions.
- `hv_vp_counters[]` names VP counters including runtime, intercepts, hypercalls, interrupts, nested virtualization, dispatch, waiting, VTL, and architecture-specific events.

## Control Flow

There is no executable control flow beyond static array initialization. `mshv_debugfs.c` includes this file after defining `MSHV_DEBUGFS_C`, then iterates the arrays and skips NULL entries when printing stats.

## State and Persistence Behavior

The arrays are static and immutable after load. Sparse indices intentionally preserve the Hyper-V counter numbering so `stats->data[idx]` lines up with the name.

## Dependencies and Integration Points

The file must be included only from `mshv_debugfs.c`; it emits a preprocessor error otherwise. Architecture guards tailor counter names to x86_64 or arm64 Hyper-V layouts.

## Risks and Edge Cases

Counter names must stay synchronized with Hyper-V `hv_stats_page` layouts. Sparse arrays make missing indices silent in output, which is useful for reserved slots but can hide newly added counters. Architecture-specific index drift would produce misleading debugfs labels without compile errors.

## Test Signals

Build both x86_64 and arm64 configurations, verify debugfs output names match known Hyper-V counters, check sparse NULL entries are skipped, and add review checks when `hvhdk.h` counter definitions change.
