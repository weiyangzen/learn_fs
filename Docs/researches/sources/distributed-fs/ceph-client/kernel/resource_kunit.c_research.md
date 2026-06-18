# sources/distributed-fs/ceph-client/kernel/resource_kunit.c

## Purpose
`resource_kunit.c` is a KUnit test suite for resource range helpers and `resource.c` tree behavior. It validates `resource_union()`, `resource_intersection()`, and a realistic `region_intersects()` scenario involving System RAM ranges, memory holes, and nested CXL-window-like parent resources.

## Important APIs, Types, And Functions
The file defines static test resources `r0` through `r4`, `struct result` expectation rows, `results_for_union[]`, and `results_for_intersection[]`. Helpers `resource_do_test()`, `resource_do_union_test()`, and `resource_do_intersection_test()` run symmetric checks against expected boolean return values and range outputs. `resource_test_region_intersects()` builds a temporary resource subtree using `alloc_free_mem_region()`, `__request_region()`, and `insert_resource()`. Cleanup is registered with `kunit_add_action_or_reset()` via `remove_free_resource()` and `kfree_wrapper()`.

## Control Flow
The union and intersection tests iterate through table-driven cases and test both argument orders. The region-intersection test first allocates a free parent area under `iomem_resource`, then adds several ranges: top-level System RAM, a hole, a CXL window, another System RAM range, a larger CXL window, nested System RAM, nested code, and another nested System RAM range. It then probes offsets around boundaries to verify `REGION_INTERSECTS`, `REGION_DISJOINT`, and `REGION_MIXED` behavior.

## State And Persistence
The suite temporarily mutates the global `iomem_resource` tree while the KUnit case runs. It relies on KUnit cleanup actions to remove inserted/requested resources and free allocations. There is no persistent state beyond KUnit result reporting.

## Dependencies And Integration Points
The test depends on KUnit, `linux/ioport.h`, page-size constants, `alloc_free_mem_region()` from `resource.c`, and live resource-tree insertion/request APIs. It integrates with the kernel's KUnit runner through `kunit_test_suite(resource_test_suite)`.

## Risks
Because the region test uses the global iomem tree, cleanup ordering matters. Missing cleanup could leave artificial resources behind and poison later tests. The test assumes enough free address space exists for a 7 MiB aligned test parent. It also deliberately models nested non-RAM windows, so changes in `region_intersects()` semantics may require expectation updates rather than indicating simple breakage.

## Test Signals
Passing KUnit cases named `resource_test_union`, `resource_test_intersection`, and `resource_test_region_intersects` are the primary signal. Failures identify incorrect range endpoints, wrong boolean results, cleanup/add-action failures, inability to allocate a test window, or incorrect mixed/disjoint/intersects classification.
