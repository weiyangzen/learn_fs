<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/hw.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/hw.h

## Purpose
Defines IOAT hardware constants and descriptor layouts used by the IOAT VFIO driver backend.

## Important APIs, Types, and Functions
PCI_DEVICE_ID_INTEL_IOAT_*, IOAT_VER_*, IOAT_DESC_SZ, struct ioat_dma_descriptor and XOR/PQ descriptor variants.

## Control Flow
Pure descriptor/register metadata; ioat.c uses device IDs, version constants, and DMA descriptor layout to program copy operations.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Depends on stdint types and Intel IOAT hardware specification.

## Risks and Edge Cases
Large legacy descriptor set exceeds what current ioat.c uses; drift from hardware docs can break DMA programming.

## Test Signals
Compile-time layout plus IOAT selftest memcpy behavior are the signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/hw.h -->
