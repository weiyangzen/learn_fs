<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/ioat.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/ioat.c

## Purpose
Implements the libvfio driver backend for Intel IOAT DMA engines.

## Important APIs, Types, and Functions
ioat_ops, ioat_probe/init/remove, ioat_reset, ioat_memcpy_start/wait, ioat_send_msi.

## Control Flow
Probes Intel SKX IOAT with supported version, enables PCI memory/master and MSI-X, resets channel, programs a self-linked DMA descriptor, writes chain address/control/count registers, waits for DONE or handles HALTED errors, and can request interrupt on a tiny copy.

## State and Persistence
Stores one descriptor and MSI source/destination buffers in driver.region; mutates BAR0 channel registers and MSI-X setup.

## Dependencies and Integration Points
Depends on libvfio, IOAT register/header definitions, Intel IOAT hardware, mapped BAR0, and IOMMU mappings for the descriptor region.

## Risks and Edge Cases
Busy-wait loops have no sleep in wait path; only specific IOAT versions/device IDs are supported; hardware errors reset the channel and fail the operation.

## Test Signals
VFIO driver tests call ops through the generic driver wrapper for memcpy/MSI coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/ioat.c -->
