<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio.h

## Purpose
Umbrella public header for libvfio helpers and BDF/mmap utility APIs.

## Important APIs, Types, and Functions
Includes assert/iommu/iova_allocator/vfio_pci_device/vfio_pci_driver; vfio_selftests_get_bdf(s), mmap_reserve.

## Control Flow
Documents BDF selection from argv or VFIO_SELFTESTS_BDF and aligned virtual-address reservation for later mmap.

## State and Persistence
No state in header; libvfio.c owns BDF parsing behavior.

## Dependencies and Integration Points
Included by all VFIO tests and library implementation files.

## Risks and Edge Cases
Consumers must pass argc by pointer because BDF parsing mutates it.

## Test Signals
Compile-time integration across VFIO tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio.h -->
