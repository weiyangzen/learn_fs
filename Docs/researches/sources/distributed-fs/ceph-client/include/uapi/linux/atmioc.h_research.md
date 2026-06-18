<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmioc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmioc.h

## Purpose
Defines the ioctl number allocation ranges for ATM PHY, SAR, interface, backend, CLIP, LANE, MPOA, and special-purpose operations.

## Important APIs, Types, And Functions
Exports range bases and ends such as `ATMIOC_PHYCOM`, `ATMIOC_PHYTYP`, `ATMIOC_PHYPRV`, `ATMIOC_SARCOM`, `ATMIOC_SARPRV`, `ATMIOC_ITF`, `ATMIOC_BACKEND`, `ATMIOC_LANE`, `ATMIOC_MPOA`, `ATMIOC_CLIP`, and `ATMIOC_SPECIAL`.

## Control Flow
Other ATM headers compose `_IO*('a', range + offset, type)` ioctl numbers from these ranges to avoid collisions between common, type-specific, and private controls.

## State And Persistence
No state. This is a numeric namespace contract.

## Dependencies And Integration Points
Includes `<asm/ioctl.h>` so consumers get `_IO`, `_IOR`, `_IOW`, and `_IOWR`. It is included by almost every ATM UAPI header.

## Risks And Edge Cases
Overlapping private offsets can break driver utilities. The documented range boundaries are part of ABI compatibility and should not be renumbered.

## Test Signals
Compile-time uniqueness checks for known ATM ioctls and regression tests that ioctl numbers remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmioc.h -->
