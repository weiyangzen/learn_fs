# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_10.sh

## Purpose
This test verifies the ublk update-size feature.

## Important APIs, Types, and Functions
It checks `_have_feature "UPDATE_SIZE"`, creates a null device, reads size with `_get_disk_size()`, invokes `kublk update_size -n <id> -s <bytes>`, and reads the size again.

## Control Flow
The script halves the current block-device size, asks `kublk` to update the device size, and fails if the command fails or the observed block size does not equal the requested value.

## State and Persistence
It mutates the kernel-reported size of a temporary null ublk device and removes the device afterward.

## Dependencies and Integration Points
It depends on kernel `UBLK_F_UPDATE_SIZE`, `kublk` `update_size` command, and `lsblk`.

## Risks
Size must be aligned to logical block size; halving the default null size preserves alignment. Udev/lsblk timing can affect observed result.

## Test Signals
Pass means the block device reports the new requested size after update.
