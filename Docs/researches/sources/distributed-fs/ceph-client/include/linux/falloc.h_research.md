# sources/distributed-fs/ceph-client/include/linux/falloc.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/falloc.h` defines kernel-side fallocate and legacy XFS-compatible space reservation ioctl contracts. The source was read as a complete 63-line file for this report.

## Important APIs, Types, and Functions

Important exports are `struct space_resv`, `FS_IOC_RESVSP`, `FS_IOC_UNRESVSP`, `FS_IOC_RESVSP64`, `FS_IOC_UNRESVSP64`, `FS_IOC_ZERO_RANGE`, and `FALLOC_FL_MODE_MASK`. On `CONFIG_X86_64`, it also defines packed `struct space_resv_32` and matching 32-bit compat ioctl numbers.

## Control Flow

There is no local execution. VFS and filesystem ioctl/fallocate paths validate user mode bits against `FALLOC_FL_MODE_MASK`, translate ioctl payloads into ranges, and dispatch to filesystem allocation, punch, zero, collapse, insert, unshare, or write-zeroes implementations.

## State and Persistence Behavior

The header describes file extent state changes but stores no data. Actual persistence is in filesystem allocation metadata and file size/extent maps.

## Dependencies and Integration Points

It includes `uapi/linux/falloc.h` for user-visible flags and uses ioctl encoding macros. Integration points are VFS fallocate, filesystem-specific space management, compat ioctl handling on x86_64, and userspace tools using legacy XFS reservation ioctls.

## Risks and Edge Cases

Only one fallocate mode may be set at a time, with separate flags such as keep-size layered on top. Compat packing is ABI-sensitive, and range operations can interact badly with sparse files, reflinks, inline data, quotas, and distributed filesystem metadata consistency.

## Test Signals

Fallocate ioctl tests across native and compat ABIs, xfstests for punch/zero/collapse/insert/unshare/write-zeroes, quota and ENOSPC tests, and CephFS client tests for extent/state propagation.
