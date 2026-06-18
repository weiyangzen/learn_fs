# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/kunit_generic_pt.h

## Purpose

`kunit_generic_pt.h` defines format-level KUnit tests for Generic PT primitives, independent of higher-level IOMMU map/unmap behavior.

## Important APIs, Types, and Functions

- `do_map`, `KUNIT_ASSERT_PT_LOAD`, `check_all_levels`: shared test helpers.
- Bit/log tests: `test_bitops`, `test_best_pgsize`, `test_pgsz_count`.
- Format primitive tests: `test_table_ptr`, `test_table_radix`, `test_entry_possible_sizes`, `test_entry_oa`, `test_attr_from_entry`, and dirty tests.
- Uses generated format callbacks such as `pt_install_table`, `pt_table_pa`, `pt_possible_sizes`, `pt_install_leaf_entry`, `pt_attr_from_entry`, and dirty helpers.

## Control Flow

The header is included by `iommu_template.h` only for `GENERIC_PT_KUNIT` builds. Tests initialize a format-specific IOMMU table, map enough pages to populate levels, then use recursive Generic PT walkers to visit representative entries at each level and verify callback contracts.

## State and Persistence Behavior

State is per-KUnit fixture (`kunit_iommu_priv`) and temporary page-table mappings. Tests deliberately mutate entries, clear them, and rely on fixture teardown to deinitialize the generated table.

## Dependencies and Integration Points

It depends on `kunit_iommu.h`, `pt_iter.h`, generated format callbacks, Linux KUnit, and randomization helpers. It is compiled once per enabled format through the format Makefile.

## Risks and Edge Cases

- Tests are header-based template code, so failures can be format-specific and symbol-heavy.
- Some checks skip or adjust behavior on 32-bit hosts.
- The tests assume isolated KUnit execution for page-table leak accounting in the paired IOMMU test fixture.

## Test Signals

Passing suites indicate correct bit helpers, page-size selection, radix coverage, table pointer encode/decode, leaf OA encode/decode, attribute round-trip, dirty helper behavior, and format-supported page-size reporting.
