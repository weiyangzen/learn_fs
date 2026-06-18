# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/metadata_size.c

## Purpose
This standalone utility queries logical block metadata capabilities from a block device for ublk integrity tests.

## Important APIs, Types, and Functions
`main()` opens a block device and calls `ioctl(FS_IOC_GETLBMD_CAP, struct logical_block_metadata_cap *)`, then prints `metadata_size`, `pi_offset`, and `pi_tuple_size`.

## Control Flow
It requires exactly one device path argument, opens it read-only, performs the ioctl, prints fields on success, and exits nonzero on usage, open, or ioctl failure.

## State and Persistence
It reads kernel block-device metadata capability state and does not modify anything.

## Dependencies and Integration Points
It depends on Linux `fs.h` exposing `FS_IOC_GETLBMD_CAP` and `logical_block_metadata_cap`. `test_common.sh` invokes it through `_get_metadata_size()`.

## Risks
It assumes the queried device supports the ioctl. Output parsing in shell helpers depends on exact field labels.

## Test Signals
Printed numeric metadata fields allow integrity shell tests to assert the ublk device reports expected metadata settings.
