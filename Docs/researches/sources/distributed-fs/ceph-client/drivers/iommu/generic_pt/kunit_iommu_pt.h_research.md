# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/kunit_iommu_pt.h

## Purpose

`kunit_iommu_pt.h` defines end-to-end KUnit tests for the generated Generic PT `iommu_domain` operations, focusing on map, unmap, lookup, dynamic top growth, large-page behavior, random overlap handling, and leak detection.

## Important APIs, Types, and Functions

- Counting helpers: `count_valids`, `count_valids_single`, and recursive `__count_valids`.
- Mapping helpers: `do_map`, `do_unmap`, `check_iova`.
- Tests: `test_increase_level`, `test_map_simple`, `test_map_table_to_oa`, `test_unmap_split`, `test_random_map`, `test_pgsize_boundary`, and `test_mixed`.
- Suite lifecycle: `pt_kunit_iommu_init`, `pt_kunit_iommu_exit`, and generated suite `NS(iommu_suite)`.

## Control Flow

The suite initializes a generated IOMMU table via `kunit_iommu.h`. Tests map every reported page size, verify IOVA-to-phys translations, unmap and check empty trees, convert populated lower tables into larger leaves, ensure partial unmap of a large page returns the large size, and perform randomized map/unmap with a maple tree tracking current mappings.

## State and Persistence Behavior

Each test mutates an in-memory page-table tree and cleans it before teardown. Teardown calls `pt_iommu_deinit` and compares `NR_SECONDARY_PAGETABLE` against the baseline to catch leaks.

## Dependencies and Integration Points

It uses Linux IOMMU API entry points, Generic PT walkers, KUnit, maple tree helpers, random helpers, and global VM page-state counters.

## Risks and Edge Cases

- Random tests are probabilistic and may miss rare ordering bugs without repeated runs.
- Some cases skip on 32-bit hosts or formats with insufficient page-size/range support.
- Leak checks assume isolated execution and stable `NR_SECONDARY_PAGETABLE` accounting.

## Test Signals

Passing tests validate generated domain ops for all enabled formats, including large-page selection, overmap rejection, table cleanup, top-level growth, translation correctness, and known regression cases referenced by `test_pgsize_boundary` and `test_mixed`.
