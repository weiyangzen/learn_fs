
# sources/distributed-fs/ceph-client/lib/test_hmm_uapi.h

## Purpose

This header defines the userspace ABI for the HMM mirror test driver.

## Important APIs, Types, And Functions

`struct hmm_dmirror_cmd` carries input address, user buffer pointer, page count, copied-page count, and fault count. Ioctls cover read, write, migrate to device, migrate to system, snapshot, exclusive migration, exclusive check, release, and flags. It also defines `HMM_DMIRROR_FLAG_FAIL_ALLOC`, snapshot protection/result byte values, and memory type identifiers for device-private and device-coherent modes.

## Control Flow And State

The header has no executable flow. Its fields are both input and output depending on ioctl: `addr`, `ptr`, and `npages` are inputs, while `cpages` and `faults` are updated by the driver.

## Dependencies And Integration Points

It includes Linux fixed-width types and ioctl macros and is included by both the kernel driver and userspace selftests. The ioctl numbers are part of the external contract for `/dev/hmm_dmirror*`.

## Risks And Test Signals

Changing struct layout, ioctl numbers, or enum values breaks userspace compatibility. Snapshot tests should verify every defined protection code, including local versus remote private/coherent device pages and PMD/PUD markers.
