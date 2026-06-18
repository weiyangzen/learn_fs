# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_mock.c

## Purpose

`iommu_mock.c` instantiates the Generic PT IOMMU template using the AMDv1 format in an IOMMUFD self-test variant.

## Important APIs, Types, and Functions

- `#define PT_FMT amdv1`, `#define PT_FMT_VARIANT mock`, and `#define AMDV1_IOMMUFD_SELFTEST`: select AMDv1 with altered test constants.
- `PT_SUPPORTED_FEATURES`: enables dynamic top, DMA-incoherent handling, and AMDv1 force coherence.
- Inclusion of `iommu_template.h`: generates mock-namespaced test symbols.

## Control Flow

There is no direct runtime logic. The file exists so IOMMUFD tests can exercise the generic template with nonstandard AMDv1 parameters, including a 2 KiB granule path defined in `amdv1.h`.

## State and Persistence Behavior

Generated state follows the AMDv1 template but is intended for tests, not hardware use.

## Dependencies and Integration Points

It is built when `CONFIG_IOMMUFD_TEST` is enabled and integrates with Generic PT and IOMMUFD test infrastructure.

## Risks and Edge Cases

Because this is a variant build, symbol naming and feature differences must remain isolated from real AMDv1. It intentionally stresses cases where CPU page size and IOMMU granule differ.

## Test Signals

IOMMUFD selftests and Generic PT KUnit should verify mock initialization, mapping/unmapping, dirty behavior where compiled, and no symbol collision with real AMDv1.
