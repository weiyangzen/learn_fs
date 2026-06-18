<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/registers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/registers.h

## Purpose
Defines IOAT PCI/MMIO register offsets, bit masks, channel states, commands, transfer capability values, and error bits.

## Important APIs, Types, and Functions
IOAT_* offsets and masks, IOAT_CHANSTS_* states, IOAT_CHANCMD_*, IOAT_INTRCTRL_MSIX_VECTOR_CONTROL.

## Control Flow
Pure constant header used by ioat.c to locate registers and interpret status/error fields.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Depends on Intel IOAT register ABI.

## Risks and Edge Cases
Incorrect offsets or masks directly corrupt hardware programming in tests.

## Test Signals
Validated by IOAT init/reset/memcpy tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/registers.h -->
