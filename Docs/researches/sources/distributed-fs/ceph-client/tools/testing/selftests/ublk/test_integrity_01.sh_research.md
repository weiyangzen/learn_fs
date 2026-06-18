<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_integrity_01.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_integrity_01.sh

## Purpose
Validates ublk null-target integrity parameter plumbing through sysfs without doing data I/O.

## Important APIs, Types, and Functions
_check_value, _add_ublk_dev, _get_metadata_size, _ublk_del_dev; sysfs integrity attributes under /sys/block/ublkb*/integrity.

## Control Flow
Prepares a null test, creates four devices with metadata-only, integrity-capable IP checksum, T10-DIF reftag, and NVMe CRC64/tag configurations, compares metadata and kernel-exposed integrity fields, then deletes each device.

## State and Persistence
Uses only transient ublk devices and sysfs reads; ERR_CODE records any mismatch and cleanup removes devices.

## Dependencies and Integration Points
Depends on test_common.sh, kublk/ublksrv support for --metadata_size, --pi_offset, --csum_type, --integrity_capable, --integrity_reftag, and the block integrity sysfs ABI.

## Risks and Edge Cases
Brittle to exact sysfs format names and kernel feature support; failure cleanup depends on _ublk_del_dev after partial assertion chains.

## Test Signals
Pass requires all expected metadata values and sysfs integrity fields to match; any mismatch sets ERR_CODE=255.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_integrity_01.sh -->
