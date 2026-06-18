# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/selftest.c

## Purpose
`selftest.c` provides kernel-side infrastructure for iommufd selftests. It creates a mock IOMMU bus/device/domain implementation, test-only ioctls, fault injection hooks, access-object tests, dirty tracking tests, vIOMMU and hardware queue mocks, PASID attach/replace/detach tests, and dma-buf mapping/revocation tests.

## Important APIs, Types, And Functions
The main ioctl entry is `iommufd_test()`. Mock objects include `struct mock_iommu_domain`, `struct mock_iommu_domain_nested`, `struct mock_viommu`, `struct mock_hw_queue`, `struct mock_dev`, `struct selftest_obj`, `struct selftest_access`, and `struct iommufd_test_dma_buf`. Setup/teardown are `iommufd_test_init()` and `iommufd_test_exit()`. Public hooks for production code include `iommufd_should_fail()`, `iommufd_test_syz_conv_iova_id()`, `iommufd_selftest_is_mock_dev()`, and `iommufd_test_dma_buf_iommufd_map()`.

## Control Flow
Initialization registers debugfs fault injection, a platform IOMMU device, a mock bus, IOMMU ops, and an IOPF queue. `IOMMU_TEST_CMD` switches to handlers for adding reserved IOVAs, creating mock domains/devices, replacing HWPTs, checking mappings/refcounts/IOTLB/cache entries, creating and using access FDs, setting temporary allocation limits, marking dirty pages, triggering IOPF and vIOMMU events, PASID operations, and dma-buf get/revoke. Mock attach ops update vIOMMU/vdevice state and IOPF registration.

## State And Persistence
Persistent test state includes mock devices, bound iommufd devices, selftest objects, mock IOTLB arrays, mock device cache arrays, vIOMMU queue arrays, access item lists, exported dma-buf backing memory, and global fault-injection/memory-limit settings. Object lifetime is tied into normal iommufd object destruction.

## Dependencies And Integration Points
The file depends on iommufd core APIs, IOMMU core mock hooks, generic page-table helpers, dma-buf APIs, debugfs fault injection, platform devices, and userspace selftests consuming `iommufd_test.h`.

## Risks And Test Signals
Risks include selftest code masking production lifetime bugs, PASID rollback simulation accuracy, vIOMMU mmap cleanup, queue dependency cleanup, dma-buf revocation races, and access unmap locking. Strong test signals include successful fault-injection cleanup, page-ref checks after map/unmap, dirty bitmap round trips, nested invalidation processed counts, vevent delivery, PASID attach/replace rollback at reserved PASID 1024, and module unload waiting for mock IOMMU users.
