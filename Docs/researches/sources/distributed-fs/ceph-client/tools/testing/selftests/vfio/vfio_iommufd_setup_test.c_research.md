<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_iommufd_setup_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_iommufd_setup_test.c

## Purpose
Validates the VFIO device cdev iommufd setup ioctls and expected failure cases.

## Important APIs, Types, and Functions
vfio_device_bind_iommufd_ioctl, get_info, ioas_alloc, attach_iommufd_pt, detach_iommufd_pt; TEST_F bind/get_info_without_bind/repeated/attach.

## Control Flow
Finds the vfio cdev path for a BDF, opens cdev and /dev/iommu per fixture, verifies bind then get_info succeeds, get_info before bind fails, bad/repeated bind fails, attach/detach to a real IOAS works, and invalid pt attach fails.

## State and Persistence
Uses per-test fds only; allocates IOAS in iommufd during attach test.

## Dependencies and Integration Points
Depends on vfio-pci cdev support, /dev/iommu, libvfio cdev path discovery, and kselftest harness.

## Risks and Edge Cases
Requires device already bound to vfio-pci with cdev exposed; typo in test name attach_detatch_pt is cosmetic.

## Test Signals
Pass is expected ioctl success/failure for each fixture case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_iommufd_setup_test.c -->
