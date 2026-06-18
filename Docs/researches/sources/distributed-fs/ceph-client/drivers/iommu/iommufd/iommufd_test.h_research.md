# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/iommufd_test.h

## Purpose
`iommufd_test.h` defines the UAPI-only selftest command ABI used by `selftest.c` and tools under kernel selftests. It exposes mock operation IDs, mock hardware constants, synthetic data structures, and special type IDs for testing IOAS mapping, mock domains, access pinning, dirty tracking, IOPF, vIOMMU, PASID, hardware queues, and dma-buf revocation.

## Important APIs, Types, And Functions
The central ABI is `struct iommu_test_cmd`, selected by `op` and carrying per-operation payloads in a union. Operation IDs include `IOMMU_TEST_OP_MOCK_DOMAIN`, `IOMMU_TEST_OP_MD_CHECK_MAP`, `IOMMU_TEST_OP_CREATE_ACCESS`, `IOMMU_TEST_OP_DIRTY`, `IOMMU_TEST_OP_TRIGGER_IOPF`, `IOMMU_TEST_OP_TRIGGER_VEVENT`, PASID attach/replace/detach/check commands, and dma-buf get/revoke commands. Mock constants define aperture bounds, page sizes, huge-page size, access flags, PASID width, nested IOTLB slots, device cache slots, and selftest-only type discriminators.

## Control Flow
Userspace submits `IOMMU_TEST_CMD`; the main ioctl dispatcher copies the structure and `selftest.c` switches on `op`. Each union member mirrors one command handler and uses `id` as the primary object ID, with `last` providing the minimum-size marker for ioctl validation.

## State And Persistence
The header itself has no runtime state, but its fields name persistent kernel-side state: mock devices and HWPT IDs, access item IDs, nested IOTLB entries, vdevice cache entries, dma-buf file descriptors, and returned vIOMMU mmap offsets.

## Dependencies And Integration Points
It includes public `linux/iommufd.h` and is consumed by the module's `CONFIG_IOMMUFD_TEST` implementation and userspace selftests. The selftest type constants deliberately avoid normal enum values so the generic user-data parsing paths can reject or accept them explicitly.

## Risks And Test Signals
ABI risks include structure-size drift, wrong `last` marker coverage, conflicting selftest type constants, and command union fields being misinterpreted by old userspace. Test signals are broad: every enum value should map to exactly one `selftest.c` handler, invalid flags should return the documented errno, and returned IDs/fds/offsets should remain stable across object lifetime tests.
