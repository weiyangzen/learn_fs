# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/Makefile

## Purpose

The format Makefile instantiates the generic IOMMU page-table template for each enabled hardware format and builds matching KUnit objects by recompiling the same format source with `GENERIC_PT_KUNIT`.

## Important APIs, Types, and Functions

- `iommu_pt_fmt-*`: format list built from Kconfig symbols.
- `create_format`: make macro adding `iommu_<fmt>.o`, `kunit_iommu_<fmt>.o`, and test CFLAGS.
- Pattern rule for `kunit_iommu_%.o`: compiles `iommu_%.c` into a separate KUnit object.
- `IOMMU_PT_KUNIT_TEST`: aggregate test object name assigned when any format is processed.

## Control Flow

Enabled built-in and module formats are enumerated through `foreach` and passed to `create_format`. Normal objects compile the tiny `iommu_<fmt>.c` wrappers. KUnit objects reuse those same wrappers but add `-DGENERIC_PT_KUNIT=1`, causing format headers and `iommu_pt.h` to expose test suites.

## State and Persistence Behavior

No runtime state exists. The file controls object generation and ensures KUnit code is derived from the same format instantiations as production code.

## Dependencies and Integration Points

It depends on Kbuild variables from `generic_pt/Kconfig`, wrapper files such as `iommu_amdv1.c`, and template headers `iommu_pt.h`, `kunit_generic_pt.h`, and `kunit_iommu_pt.h`.

## Risks and Edge Cases

- If no format is enabled, `IOMMU_PT_KUNIT_TEST` remains empty and the KUnit target contributes no objects.
- The mock format is tied to `CONFIG_IOMMUFD_TEST`, not a public Generic PT format option.
- Recompiling the same source with different flags relies on dependency tracking through `if_changed_dep`.

## Test Signals

Validate `make M=drivers/iommu/generic_pt/fmt` with each format built in and as a module, and run KUnit with multiple enabled formats to confirm all `kunit_iommu_<fmt>.o` objects are generated.
