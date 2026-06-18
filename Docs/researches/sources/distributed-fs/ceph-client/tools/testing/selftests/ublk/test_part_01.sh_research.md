<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_part_01.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_part_01.sh

## Purpose
Tests UBLK_F_NO_AUTO_PART_SCAN behavior against a loop backing file with a DOS partition table.

## Important APIs, Types, and Functions
format_backing_file, test_auto_part_scan, test_no_auto_part_scan; sfdisk, udevadm settle, blockdev --rereadpt.

## Control Flow
Formats a backing file through a temporary ublk loop device, creates another device with normal scan and checks p1/p2 appear, then creates one with --no_auto_part_scan and checks partitions do not appear until manual rereadpt.

## State and Persistence
Writes a real partition table to the temporary backing file; creates/deletes multiple transient ublk devices.

## Dependencies and Integration Points
Depends on sfdisk, blockdev, udevadm, feature UBLK_F_NO_AUTO_PART_SCAN, and test_common.sh.

## Risks and Edge Cases
Sensitive to udev timing and partition naming; manual cleanup is embedded in each branch but failures before delete may require common cleanup.

## Test Signals
Pass requires auto partitions for the default case, no initial partitions for the disabled case, and successful manual reread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_part_01.sh -->
