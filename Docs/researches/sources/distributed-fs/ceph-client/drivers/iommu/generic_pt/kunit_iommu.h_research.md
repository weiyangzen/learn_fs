# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/kunit_iommu.h

## Purpose

`kunit_iommu.h` provides the shared KUnit fixture, generated-symbol declarations, domain ops, driver callbacks, assertions, and configuration setup used by Generic PT format and IOMMU tests.

## Important APIs, Types, and Functions

- Generated declarations for `pt_iommu_init` and `pt_iommu_table_cfg`.
- `kunit_pt_gen_params_cfg` and `KUNIT_CASE_FMT`: per-format parameterization.
- `struct kunit_iommu_priv`: union of `iommu_domain` and generated format table, dummy device, locks, config, info, page-size data, and leak baseline.
- `pt_kunit_iotlb_sync`: frees gather pages during tests.
- `kunit_pt_ops`: generated domain ops plus test sync callback.
- `pt_kunit_driver_ops`: no-op `change_top` and top-lock callback for dynamic top tests.
- `pt_kunit_priv_init`: builds a dummy device, initializes generated page table, and derives test limits.

## Control Flow

KUnit suites allocate `kunit_iommu_priv`, register a dummy device, set feature defaults or parameterized format config, initialize the generated page-table object, and then run tests through normal `iommu_map`, `iommu_unmap`, and callback APIs.

## State and Persistence Behavior

Fixture state persists for a test case and is cleaned by suite exit. `top_lock` serializes dynamic top updates. `orig_nr_secondary_pagetable` is used by `kunit_iommu_pt.h` teardown to detect page-table leaks.

## Dependencies and Integration Points

It depends on KUnit, `iommu-pages.h`, Generic PT headers, and generated format symbols. It provides a fake driver integration surface for `iommu_pt.h`.

## Risks and Edge Cases

- The no-op `change_top` is sufficient for software tests but does not model hardware root-update failures.
- 32-bit hosts require skipped or narrowed coverage because IOMMU APIs use `unsigned long`/`dma_addr_t` differently.
- Feature defaults are expanded under debug builds and may exercise combinations production wrappers do not request.

## Test Signals

Successful fixture initialization across all format parameter sets is the main signal. Failures often indicate invalid feature combinations, unsupported hardware limits, dummy-device allocation issues, or generated API signature drift.
