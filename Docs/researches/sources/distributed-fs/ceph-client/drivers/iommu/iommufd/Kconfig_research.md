# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/Kconfig

## Purpose
This Kconfig fragment defines build-time controls for the IOMMUFD userspace API, its shared driver core, VFIO container compatibility, and selftest support.

## Important Symbols
`IOMMUFD_DRIVER_CORE` is a hidden bool selected by either `IOMMUFD_DRIVER` or `IOMMUFD` when IOMMUFD is not disabled. It builds shared driver-facing helpers.

`IOMMUFD` is a tristate "IOMMU Userspace API". It selects interval-tree support and `IOMMU_API`, and provides `/dev/iommu` for userspace-managed IO page tables backed by userspace memory.

`IOMMUFD_VFIO_CONTAINER` allows IOMMUFD to provide `/dev/vfio/vfio` compatibility when `VFIO_GROUP` is enabled and native `VFIO_CONTAINER` is not. Its help warns that it lacks several native VFIO container features and is mainly for testing unmodified VFIO Type1 userspace.

`IOMMUFD_TEST` enables dangerous test support for `tools/testing/selftests/iommu`, depends on debug/fault-injection/runtime-testing options, requires AMDv1 page table support compatibility, selects DMA-BUF and `IOMMUFD_DRIVER`, and defaults off.

## Control Flow
Build selection flows from user-visible `IOMMUFD` to object inclusion in the Makefile. Enabling test support adds selftest objects and dependencies. Enabling VFIO container compatibility changes device-node compatibility behavior in the broader IOMMUFD codebase.

## State And Persistence
Kconfig symbols persist only in the kernel build configuration. They control compiled objects and conditional code paths such as test hooks, DMA-BUF support, and compatibility entry points.

## Dependencies And Integration Points
The fragment integrates with top-level IOMMU configuration, VFIO group/container options, interval tree libraries, DMA-BUF, fault injection, runtime testing, and IOMMUFD Makefile object lists.

## Risks
The compatibility option intentionally lacks feature parity with native VFIO container behavior, so enabling it in production could expose missing peer-to-peer DMA or platform-specific behavior. `IOMMUFD_TEST` is explicitly dangerous and should remain confined to selftest kernels.

## Test Signals
Build matrix signals include `IOMMUFD=n/m/y`, `IOMMUFD_VFIO_CONTAINER` with VFIO group configurations, and `IOMMUFD_TEST=y` selftest kernels. The resulting `.config` should select required dependencies and produce expected object lists.
