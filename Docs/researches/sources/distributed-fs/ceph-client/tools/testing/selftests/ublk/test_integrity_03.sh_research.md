<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_integrity_03.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_integrity_03.sh

## Purpose
Exercises automatic integrity handling for NVMe-style PI on a loop-backed ublk device using fio without explicit metadata parameters.

## Important APIs, Types, and Functions
_test_fill_and_verify, _test_corrupted_reftag, _test_corrupted_data; fio libaio direct I/O.

## Control Flow
Creates 256M data and 32M metadata files, adds loop target with --integrity_capable/--integrity_reftag and NVMe checksum at offset 48, runs fio write/read, corrupts metadata and data, and expects a read error string.

## State and Persistence
Temporary backing files are mutated by dd; fio stderr is captured in a temp file and removed before cleanup.

## Dependencies and Integration Points
Depends on fio, dd, ublk loop integrity options, and test_common.sh.

## Risks and Edge Cases
Expected generic EILSEQ-style message may vary by kernel/libc/fio; corruption offsets assume the metadata tuple layout.

## Test Signals
Pass requires fio verify success before corruption and fio read failures after reftag/data corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_integrity_03.sh -->
