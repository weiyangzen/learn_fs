# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/Kconfig

## Purpose

This Kconfig file defines the Generic Radix Page Table library and the IOMMU page-table formats that instantiate it for AMDv1, Intel VT-d second stage, RISC-V, and x86-64.

## Important APIs, Types, and Functions

- `GENERIC_PT`: top-level boolean library option, visible mainly for `COMPILE_TEST`.
- `DEBUG_GENERIC_PT`: enables extra runtime checks and full KUnit coverage behavior.
- `IOMMU_PT`: tristate generic IOMMU page-table implementation selecting `IOMMU_API`.
- `IOMMU_PT_AMDV1`, `IOMMU_PT_VTDSS`, `IOMMU_PT_RISCV64`, `IOMMU_PT_X86_64`: per-format modules.
- `IOMMU_PT_KUNIT_TEST`: KUnit test module covering enabled formats.

## Control Flow

The build graph is gated by `GENERIC_PT`, then `IOMMU_PT`, then format symbols. Format options are intended to be selected by real IOMMU drivers rather than manually chosen. The KUnit option uses dependency expressions that allow tests when each format is enabled or absent.

## State and Persistence Behavior

No runtime state is stored here. Configuration choices determine which format objects and tests are compiled and whether debug-only assertions/features are included.

## Dependencies and Integration Points

The options integrate with `drivers/iommu/generic_pt/fmt/Makefile`, generic IOMMU APIs, KUnit, and drivers such as Intel IOMMU that select `GENERIC_PT`, `IOMMU_PT`, `IOMMU_PT_X86_64`, and `IOMMU_PT_VTDSS`.

## Risks and Edge Cases

- Several formats depend on `!GENERIC_ATOMIC64` because they use 64-bit compare-exchange helpers.
- Enabling `DEBUG_GENERIC_PT` changes feature compilation for tests and may incur runtime cost.
- KUnit coverage depends on formats selected into the build; disabled formats are not tested.

## Test Signals

Build matrix coverage should include built-in and module `IOMMU_PT`, each format individually, all formats with `IOMMU_PT_KUNIT_TEST`, and debug vs non-debug builds.
