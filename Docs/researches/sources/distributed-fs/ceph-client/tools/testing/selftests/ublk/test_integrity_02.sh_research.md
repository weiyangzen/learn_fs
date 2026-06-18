<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_integrity_02.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_integrity_02.sh

## Purpose
Runs an end-to-end loop-target data-integrity test with fio metadata buffers, corruption injection, and expected PI error diagnostics.

## Important APIs, Types, and Functions
_setup_device, _test_fill_and_verify, _test_corrupted_reftag, _test_corrupted_data, _test_bad_apptag; fio --md_per_io_size, --pi_act, --pi_chk.

## Control Flow
Checks fio >= 3.42, creates data and metadata backing files, adds an integrity-capable loop ublk device, writes/verifies random I/O, corrupts metadata reftag and data, then verifies fio fails with expected REFTAG, Guard, and APPTAG errors.

## State and Persistence
Persists temporary backfiles and fio stderr under UBLK_TEST_DIR only for the test lifetime; corruption is intentionally written to backing files and partly reset between subtests.

## Dependencies and Integration Points
Depends on fio PI support, dd, loop ublk target, block integrity, test_common.sh backfile/device helpers.

## Risks and Edge Cases
The expected stderr strings are tightly coupled to fio/kernel messages; data corruption is destructive to the temporary backfile by design.

## Test Signals
Success is fio fill/read verify success followed by expected failures for each corruption mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_integrity_02.sh -->
