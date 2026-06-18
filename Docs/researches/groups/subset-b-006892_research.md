# subset-b-006892 grouped research

Complete grouped research for the requested source files. Each section preserves the source path in the title and is delimited for reconciliation splitting.

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_01.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_01.sh

## Purpose
Validates ublk loop target normal copy operation with fio verify raw block I/O.

## Important APIs, Types, and Functions
_prep_test, _create_backfile, _add_ublk_dev, _check_add_dev, _run_fio_verify_io or _mkfs_mount_test, _cleanup_test.

## Control Flow
Creates a 256M backing file, adds /dev/ublkb* as a loop target with the file and mode-specific flags, runs fio verify raw block I/O, stores the command status in ERR_CODE, and performs common cleanup.

## State and Persistence
State is limited to a temporary backing file, transient ublk block device, and optional mounted filesystem created by test_common.sh.

## Dependencies and Integration Points
Depends on test_common.sh, kublk loop target, and fio for the raw-I/O variants; filesystem variants depend on mkfs/mount helpers.

## Risks and Edge Cases
Failures can leave mounts/devices if cleanup helpers cannot run; fio variants skip when fio is unavailable.

## Test Signals
Pass is the helper return status being zero and _show_result reporting ERR_CODE=0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_01.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_02.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_02.sh

## Purpose
Validates ublk loop target normal copy operation with mkfs/mount/umount.

## Important APIs, Types, and Functions
_prep_test, _create_backfile, _add_ublk_dev, _check_add_dev, _run_fio_verify_io or _mkfs_mount_test, _cleanup_test.

## Control Flow
Creates a 256M backing file, adds /dev/ublkb* as a loop target with the file and mode-specific flags, runs mkfs/mount/umount, stores the command status in ERR_CODE, and performs common cleanup.

## State and Persistence
State is limited to a temporary backing file, transient ublk block device, and optional mounted filesystem created by test_common.sh.

## Dependencies and Integration Points
Depends on test_common.sh, kublk loop target, and fio for the raw-I/O variants; filesystem variants depend on mkfs/mount helpers.

## Risks and Edge Cases
Failures can leave mounts/devices if cleanup helpers cannot run; fio variants skip when fio is unavailable.

## Test Signals
Pass is the helper return status being zero and _show_result reporting ERR_CODE=0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_03.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_03.sh

## Purpose
Validates ublk loop target zero copy operation with fio verify raw block I/O.

## Important APIs, Types, and Functions
_prep_test, _create_backfile, _add_ublk_dev, _check_add_dev, _run_fio_verify_io or _mkfs_mount_test, _cleanup_test.

## Control Flow
Creates a 256M backing file, adds /dev/ublkb* as a loop target with the file and mode-specific flags, runs fio verify raw block I/O, stores the command status in ERR_CODE, and performs common cleanup.

## State and Persistence
State is limited to a temporary backing file, transient ublk block device, and optional mounted filesystem created by test_common.sh.

## Dependencies and Integration Points
Depends on test_common.sh, kublk loop target, and fio for the raw-I/O variants; filesystem variants depend on mkfs/mount helpers.

## Risks and Edge Cases
Failures can leave mounts/devices if cleanup helpers cannot run; fio variants skip when fio is unavailable.

## Test Signals
Pass is the helper return status being zero and _show_result reporting ERR_CODE=0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_03.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_04.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_04.sh

## Purpose
Validates ublk loop target zero copy operation with mkfs/mount/umount.

## Important APIs, Types, and Functions
_prep_test, _create_backfile, _add_ublk_dev, _check_add_dev, _run_fio_verify_io or _mkfs_mount_test, _cleanup_test.

## Control Flow
Creates a 256M backing file, adds /dev/ublkb* as a loop target with the file and mode-specific flags, runs mkfs/mount/umount, stores the command status in ERR_CODE, and performs common cleanup.

## State and Persistence
State is limited to a temporary backing file, transient ublk block device, and optional mounted filesystem created by test_common.sh.

## Dependencies and Integration Points
Depends on test_common.sh, kublk loop target, and fio for the raw-I/O variants; filesystem variants depend on mkfs/mount helpers.

## Risks and Edge Cases
Failures can leave mounts/devices if cleanup helpers cannot run; fio variants skip when fio is unavailable.

## Test Signals
Pass is the helper return status being zero and _show_result reporting ERR_CODE=0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_04.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_05.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_05.sh

## Purpose
Validates ublk loop target two queues operation with fio verify raw block I/O.

## Important APIs, Types, and Functions
_prep_test, _create_backfile, _add_ublk_dev, _check_add_dev, _run_fio_verify_io or _mkfs_mount_test, _cleanup_test.

## Control Flow
Creates a 256M backing file, adds /dev/ublkb* as a loop target with the file and mode-specific flags, runs fio verify raw block I/O, stores the command status in ERR_CODE, and performs common cleanup.

## State and Persistence
State is limited to a temporary backing file, transient ublk block device, and optional mounted filesystem created by test_common.sh.

## Dependencies and Integration Points
Depends on test_common.sh, kublk loop target, and fio for the raw-I/O variants; filesystem variants depend on mkfs/mount helpers.

## Risks and Edge Cases
Failures can leave mounts/devices if cleanup helpers cannot run; fio variants skip when fio is unavailable.

## Test Signals
Pass is the helper return status being zero and _show_result reporting ERR_CODE=0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_05.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_06.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_06.sh

## Purpose
Validates ublk loop target user copy operation with fio verify raw block I/O.

## Important APIs, Types, and Functions
_prep_test, _create_backfile, _add_ublk_dev, _check_add_dev, _run_fio_verify_io or _mkfs_mount_test, _cleanup_test.

## Control Flow
Creates a 256M backing file, adds /dev/ublkb* as a loop target with the file and mode-specific flags, runs fio verify raw block I/O, stores the command status in ERR_CODE, and performs common cleanup.

## State and Persistence
State is limited to a temporary backing file, transient ublk block device, and optional mounted filesystem created by test_common.sh.

## Dependencies and Integration Points
Depends on test_common.sh, kublk loop target, and fio for the raw-I/O variants; filesystem variants depend on mkfs/mount helpers.

## Risks and Edge Cases
Failures can leave mounts/devices if cleanup helpers cannot run; fio variants skip when fio is unavailable.

## Test Signals
Pass is the helper return status being zero and _show_result reporting ERR_CODE=0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_06.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_07.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_07.sh

## Purpose
Validates ublk loop target user copy operation with mkfs/mount/umount.

## Important APIs, Types, and Functions
_prep_test, _create_backfile, _add_ublk_dev, _check_add_dev, _run_fio_verify_io or _mkfs_mount_test, _cleanup_test.

## Control Flow
Creates a 256M backing file, adds /dev/ublkb* as a loop target with the file and mode-specific flags, runs mkfs/mount/umount, stores the command status in ERR_CODE, and performs common cleanup.

## State and Persistence
State is limited to a temporary backing file, transient ublk block device, and optional mounted filesystem created by test_common.sh.

## Dependencies and Integration Points
Depends on test_common.sh, kublk loop target, and fio for the raw-I/O variants; filesystem variants depend on mkfs/mount helpers.

## Risks and Edge Cases
Failures can leave mounts/devices if cleanup helpers cannot run; fio variants skip when fio is unavailable.

## Test Signals
Pass is the helper return status being zero and _show_result reporting ERR_CODE=0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_loop_07.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_null_01.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_null_01.sh

## Purpose
Runs a basic fio read/write smoke test against the ublk null target in default copy mode.

## Important APIs, Types, and Functions
_add_ublk_dev, _check_add_dev, fio libaio readwrite, _cleanup_test.

## Control Flow
Prepares a null test, creates a ublk null device with optional -z or -u, runs a 256M libaio readwrite fio job, records fio status, then cleans up.

## State and Persistence
No backing store is persisted; the null target discards/serves I/O through the transient ublk device.

## Dependencies and Integration Points
Depends on fio and test_common.sh null target support.

## Risks and Edge Cases
The comment says two disks but the test uses one device; the test is mostly transport/lifecycle coverage rather than data persistence validation.

## Test Signals
Pass is fio exit status 0; missing fio returns the ublk skip code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_null_01.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_null_02.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_null_02.sh

## Purpose
Runs a basic fio read/write smoke test against the ublk null target in zero copy mode.

## Important APIs, Types, and Functions
_add_ublk_dev, _check_add_dev, fio libaio readwrite, _cleanup_test.

## Control Flow
Prepares a null test, creates a ublk null device with optional -z or -u, runs a 256M libaio readwrite fio job, records fio status, then cleans up.

## State and Persistence
No backing store is persisted; the null target discards/serves I/O through the transient ublk device.

## Dependencies and Integration Points
Depends on fio and test_common.sh null target support.

## Risks and Edge Cases
The comment says two disks but the test uses one device; the test is mostly transport/lifecycle coverage rather than data persistence validation.

## Test Signals
Pass is fio exit status 0; missing fio returns the ublk skip code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_null_02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_null_03.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_null_03.sh

## Purpose
Runs a basic fio read/write smoke test against the ublk null target in user copy mode.

## Important APIs, Types, and Functions
_add_ublk_dev, _check_add_dev, fio libaio readwrite, _cleanup_test.

## Control Flow
Prepares a null test, creates a ublk null device with optional -z or -u, runs a 256M libaio readwrite fio job, records fio status, then cleans up.

## State and Persistence
No backing store is persisted; the null target discards/serves I/O through the transient ublk device.

## Dependencies and Integration Points
Depends on fio and test_common.sh null target support.

## Risks and Edge Cases
The comment says two disks but the test uses one device; the test is mostly transport/lifecycle coverage rather than data persistence validation.

## Test Signals
Pass is fio exit status 0; missing fio returns the ublk skip code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_null_03.sh -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_part_02.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_part_02.sh

## Purpose
Verifies asynchronous partition scan does not hang ublk daemon teardown when fault-injected I/O blocks partition reads.

## Important APIs, Types, and Functions
_test_partition_scan_no_hang, _add_ublk_dev_no_settle, _get_ublk_daemon_pid, __ublk_kill_daemon, _ublk_del_dev.

## Control Flow
Adds a fault_inject ublk device with 60s I/O delay without waiting for udev settle, waits briefly for async scan to hit delay, kills the daemon, checks expected state DEAD or QUIESCED depending on recovery flag, then deletes the device.

## State and Persistence
State is transient but intentionally includes a blocked partition-scan I/O path and daemon state transition.

## Dependencies and Integration Points
Depends on fault_inject target, recovery option -r, partition scan behavior, and test_common.sh state helpers.

## Risks and Edge Cases
The test assumes 1s is enough to start partition scan and that expected state names remain stable.

## Test Signals
Pass is transition to DEAD without recovery and QUIESCED with recovery, both without blocking teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_part_02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_01.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_01.sh

## Purpose
Exercises kill-daemon recovery across null, loop, and stripe in buffered/default, no-buffer, and reissue modes.

## Important APIs, Types, and Functions
ublk_run_recover_test or ublk_run_quiesce_recover, run_io_and_recover, _have_feature, _create_backfile.

## Control Flow
Creates data files, launches target/mode combinations in background, waits for each wave, and reports any nonzero helper status through ERR_CODE.

## State and Persistence
Backfiles are temporary; the core state under test is ublk daemon death/quiesce, recovery, and I/O reissue while fio is active.

## Dependencies and Integration Points
fio, test_common.sh run_io_and_recover, ublk recovery support; zero-copy or quiesce feature gates where present.

## Risks and Edge Cases
Parallel background jobs all write ERR_CODE in the shell process context only through function bodies; diagnostics can interleave; skipped feature gates limit coverage on older kernels.

## Test Signals
Pass requires every run_io_and_recover scenario to finish with zero status; fio absence or missing feature returns skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_01.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_02.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_02.sh

## Purpose
Exercises zero-copy kill-daemon recovery across null, loop, and stripe with optional no-buffer and reissue modes.

## Important APIs, Types, and Functions
ublk_run_recover_test or ublk_run_quiesce_recover, run_io_and_recover, _have_feature, _create_backfile.

## Control Flow
Creates data files, launches target/mode combinations in background, waits for each wave, and reports any nonzero helper status through ERR_CODE.

## State and Persistence
Backfiles are temporary; the core state under test is ublk daemon death/quiesce, recovery, and I/O reissue while fio is active.

## Dependencies and Integration Points
fio, test_common.sh run_io_and_recover, ublk recovery support; zero-copy or quiesce feature gates where present.

## Risks and Edge Cases
Parallel background jobs all write ERR_CODE in the shell process context only through function bodies; diagnostics can interleave; skipped feature gates limit coverage on older kernels.

## Test Signals
Pass requires every run_io_and_recover scenario to finish with zero status; fio absence or missing feature returns skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_03.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_03.sh

## Purpose
Exercises quiesce and recover across null, loop, and stripe for normal and reissue modes.

## Important APIs, Types, and Functions
ublk_run_recover_test or ublk_run_quiesce_recover, run_io_and_recover, _have_feature, _create_backfile.

## Control Flow
Creates data files, launches target/mode combinations in background, waits for each wave, and reports any nonzero helper status through ERR_CODE.

## State and Persistence
Backfiles are temporary; the core state under test is ublk daemon death/quiesce, recovery, and I/O reissue while fio is active.

## Dependencies and Integration Points
fio, test_common.sh run_io_and_recover, ublk recovery support; zero-copy or quiesce feature gates where present.

## Risks and Edge Cases
Parallel background jobs all write ERR_CODE in the shell process context only through function bodies; diagnostics can interleave; skipped feature gates limit coverage on older kernels.

## Test Signals
Pass requires every run_io_and_recover scenario to finish with zero status; fio absence or missing feature returns skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_03.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_04.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_04.sh

## Purpose
Exercises user-copy kill-daemon recovery across null, loop, and stripe for normal and reissue modes.

## Important APIs, Types, and Functions
ublk_run_recover_test or ublk_run_quiesce_recover, run_io_and_recover, _have_feature, _create_backfile.

## Control Flow
Creates data files, launches target/mode combinations in background, waits for each wave, and reports any nonzero helper status through ERR_CODE.

## State and Persistence
Backfiles are temporary; the core state under test is ublk daemon death/quiesce, recovery, and I/O reissue while fio is active.

## Dependencies and Integration Points
fio, test_common.sh run_io_and_recover, ublk recovery support; zero-copy or quiesce feature gates where present.

## Risks and Edge Cases
Parallel background jobs all write ERR_CODE in the shell process context only through function bodies; diagnostics can interleave; skipped feature gates limit coverage on older kernels.

## Test Signals
Pass requires every run_io_and_recover scenario to finish with zero status; fio absence or missing feature returns skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_recover_04.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_01.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_01.sh

## Purpose
Tests ublk --shmem_zc using null target shared hugetlbfs zero-copy writes.

## Important APIs, Types, and Functions
_prep_test, hugetlbfs mount, /proc/sys/vm/nr_hugepages, fallocate, _add_ublk_dev, fio or _run_fio_verify_io/_mkfs_mount_test.

## Control Flow
Checks fio and hugetlbfs support, temporarily raises nr_hugepages, mounts hugetlbfs under UBLK_TEST_DIR, allocates a shared buffer file, creates the ublk device with --shmem_zc and mode-specific flags, runs I/O, deletes the device before unmount, and restores hugepage count.

## State and Persistence
Mutates global nr_hugepages during the run and creates a temporary hugetlbfs mount/file; cleanup restores the old count on the normal path.

## Dependencies and Integration Points
Depends on root privileges, hugetlbfs, fio io_uring/mmaphuge, kublk shmem_zc/htlb support, and test_common.sh.

## Risks and Edge Cases
Global hugepage count changes are risky if interrupted; mount cleanup must run after device deletion so daemon releases mmap.

## Test Signals
Pass is successful device add and fio/verify workload completion; unavailable hugepages or mount support produce skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_01.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_02.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_02.sh

## Purpose
Tests ublk --shmem_zc using loop target shared hugetlbfs fio verify.

## Important APIs, Types, and Functions
_prep_test, hugetlbfs mount, /proc/sys/vm/nr_hugepages, fallocate, _add_ublk_dev, fio or _run_fio_verify_io/_mkfs_mount_test.

## Control Flow
Checks fio and hugetlbfs support, temporarily raises nr_hugepages, mounts hugetlbfs under UBLK_TEST_DIR, allocates a shared buffer file, creates the ublk device with --shmem_zc and mode-specific flags, runs I/O, deletes the device before unmount, and restores hugepage count.

## State and Persistence
Mutates global nr_hugepages during the run and creates a temporary hugetlbfs mount/file; cleanup restores the old count on the normal path.

## Dependencies and Integration Points
Depends on root privileges, hugetlbfs, fio io_uring/mmaphuge, kublk shmem_zc/htlb support, and test_common.sh.

## Risks and Edge Cases
Global hugepage count changes are risky if interrupted; mount cleanup must run after device deletion so daemon releases mmap.

## Test Signals
Pass is successful device add and fio/verify workload completion; unavailable hugepages or mount support produce skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_03.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_03.sh

## Purpose
Tests ublk --shmem_zc using loop target filesystem fio verify through shmem zero-copy.

## Important APIs, Types, and Functions
_prep_test, hugetlbfs mount, /proc/sys/vm/nr_hugepages, fallocate, _add_ublk_dev, fio or _run_fio_verify_io/_mkfs_mount_test.

## Control Flow
Checks fio and hugetlbfs support, temporarily raises nr_hugepages, mounts hugetlbfs under UBLK_TEST_DIR, allocates a shared buffer file, creates the ublk device with --shmem_zc and mode-specific flags, runs I/O, deletes the device before unmount, and restores hugepage count.

## State and Persistence
Mutates global nr_hugepages during the run and creates a temporary hugetlbfs mount/file; cleanup restores the old count on the normal path.

## Dependencies and Integration Points
Depends on root privileges, hugetlbfs, fio io_uring/mmaphuge, kublk shmem_zc/htlb support, and test_common.sh.

## Risks and Edge Cases
Global hugepage count changes are risky if interrupted; mount cleanup must run after device deletion so daemon releases mmap.

## Test Signals
Pass is successful device add and fio/verify workload completion; unavailable hugepages or mount support produce skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_03.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_04.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_04.sh

## Purpose
Tests ublk --shmem_zc using null target shared hugetlbfs zero-copy with read-only buffer registration.

## Important APIs, Types, and Functions
_prep_test, hugetlbfs mount, /proc/sys/vm/nr_hugepages, fallocate, _add_ublk_dev, fio or _run_fio_verify_io/_mkfs_mount_test.

## Control Flow
Checks fio and hugetlbfs support, temporarily raises nr_hugepages, mounts hugetlbfs under UBLK_TEST_DIR, allocates a shared buffer file, creates the ublk device with --shmem_zc and mode-specific flags, runs I/O, deletes the device before unmount, and restores hugepage count.

## State and Persistence
Mutates global nr_hugepages during the run and creates a temporary hugetlbfs mount/file; cleanup restores the old count on the normal path.

## Dependencies and Integration Points
Depends on root privileges, hugetlbfs, fio io_uring/mmaphuge, kublk shmem_zc/htlb support, and test_common.sh.

## Risks and Edge Cases
Global hugepage count changes are risky if interrupted; mount cleanup must run after device deletion so daemon releases mmap.

## Test Signals
Pass is successful device add and fio/verify workload completion; unavailable hugepages or mount support produce skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_04.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_01.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_01.sh

## Purpose
Stress test that runs fio while removing null, loop, and stripe devices.

## Important APIs, Types, and Functions
run_io_and_remove or run_io_and_kill_daemon wrappers, fio, _have_feature, background jobs and wait.

## Control Flow
Prepares backing files, starts several target/mode workloads in parallel, injects device removal or daemon death while I/O is in flight, waits for each wave, and preserves the first observed failure in ERR_CODE.

## State and Persistence
Uses temporary backing files and transient ublk devices; test_stress_05 additionally has a local run_io_and_remove that sends SIGKILL to the daemon before deletion.

## Dependencies and Integration Points
Depends on fio, test_common.sh stress helpers, null/loop/stripe targets, and optional ZERO_COPY, AUTO_BUF_REG, PER_IO_DAEMON, and BATCH_IO feature gates.

## Risks and Edge Cases
Highly timing-sensitive and intentionally destructive to active devices; diagnostics can interleave and some feature-gated branches are skipped silently when unsupported.

## Test Signals
Pass means all lifecycle-under-I/O scenarios complete with zero helper status; missing fio/features return skip where gated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_01.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_02.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_02.sh

## Purpose
Stress test that runs fio while killing the ublk daemon with 1 and 4 queues.

## Important APIs, Types, and Functions
run_io_and_remove or run_io_and_kill_daemon wrappers, fio, _have_feature, background jobs and wait.

## Control Flow
Prepares backing files, starts several target/mode workloads in parallel, injects device removal or daemon death while I/O is in flight, waits for each wave, and preserves the first observed failure in ERR_CODE.

## State and Persistence
Uses temporary backing files and transient ublk devices; test_stress_05 additionally has a local run_io_and_remove that sends SIGKILL to the daemon before deletion.

## Dependencies and Integration Points
Depends on fio, test_common.sh stress helpers, null/loop/stripe targets, and optional ZERO_COPY, AUTO_BUF_REG, PER_IO_DAEMON, and BATCH_IO feature gates.

## Risks and Edge Cases
Highly timing-sensitive and intentionally destructive to active devices; diagnostics can interleave and some feature-gated branches are skipped silently when unsupported.

## Test Signals
Pass means all lifecycle-under-I/O scenarios complete with zero helper status; missing fio/features return skip where gated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_03.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_03.sh

## Purpose
Stress test that runs remove-during-I/O zero-copy/auto-zc/per-io-task combinations.

## Important APIs, Types, and Functions
run_io_and_remove or run_io_and_kill_daemon wrappers, fio, _have_feature, background jobs and wait.

## Control Flow
Prepares backing files, starts several target/mode workloads in parallel, injects device removal or daemon death while I/O is in flight, waits for each wave, and preserves the first observed failure in ERR_CODE.

## State and Persistence
Uses temporary backing files and transient ublk devices; test_stress_05 additionally has a local run_io_and_remove that sends SIGKILL to the daemon before deletion.

## Dependencies and Integration Points
Depends on fio, test_common.sh stress helpers, null/loop/stripe targets, and optional ZERO_COPY, AUTO_BUF_REG, PER_IO_DAEMON, and BATCH_IO feature gates.

## Risks and Edge Cases
Highly timing-sensitive and intentionally destructive to active devices; diagnostics can interleave and some feature-gated branches are skipped silently when unsupported.

## Test Signals
Pass means all lifecycle-under-I/O scenarios complete with zero helper status; missing fio/features return skip where gated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_03.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_04.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_04.sh

## Purpose
Stress test that runs kill-daemon-during-I/O zero-copy/auto-zc/per-io-task combinations.

## Important APIs, Types, and Functions
run_io_and_remove or run_io_and_kill_daemon wrappers, fio, _have_feature, background jobs and wait.

## Control Flow
Prepares backing files, starts several target/mode workloads in parallel, injects device removal or daemon death while I/O is in flight, waits for each wave, and preserves the first observed failure in ERR_CODE.

## State and Persistence
Uses temporary backing files and transient ublk devices; test_stress_05 additionally has a local run_io_and_remove that sends SIGKILL to the daemon before deletion.

## Dependencies and Integration Points
Depends on fio, test_common.sh stress helpers, null/loop/stripe targets, and optional ZERO_COPY, AUTO_BUF_REG, PER_IO_DAEMON, and BATCH_IO feature gates.

## Risks and Edge Cases
Highly timing-sensitive and intentionally destructive to active devices; diagnostics can interleave and some feature-gated branches are skipped silently when unsupported.

## Test Signals
Pass means all lifecycle-under-I/O scenarios complete with zero helper status; missing fio/features return skip where gated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_04.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_05.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_05.sh

## Purpose
Stress test that kills the daemon then deletes recovery-enabled null and loop devices across reissue and data paths.

## Important APIs, Types, and Functions
run_io_and_remove or run_io_and_kill_daemon wrappers, fio, _have_feature, background jobs and wait.

## Control Flow
Prepares backing files, starts several target/mode workloads in parallel, injects device removal or daemon death while I/O is in flight, waits for each wave, and preserves the first observed failure in ERR_CODE.

## State and Persistence
Uses temporary backing files and transient ublk devices; test_stress_05 additionally has a local run_io_and_remove that sends SIGKILL to the daemon before deletion.

## Dependencies and Integration Points
Depends on fio, test_common.sh stress helpers, null/loop/stripe targets, and optional ZERO_COPY, AUTO_BUF_REG, PER_IO_DAEMON, and BATCH_IO feature gates.

## Risks and Edge Cases
Highly timing-sensitive and intentionally destructive to active devices; diagnostics can interleave and some feature-gated branches are skipped silently when unsupported.

## Test Signals
Pass means all lifecycle-under-I/O scenarios complete with zero helper status; missing fio/features return skip where gated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_05.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_06.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_06.sh

## Purpose
Stress test that runs remove-during-I/O user-copy and per-io-task cases.

## Important APIs, Types, and Functions
run_io_and_remove or run_io_and_kill_daemon wrappers, fio, _have_feature, background jobs and wait.

## Control Flow
Prepares backing files, starts several target/mode workloads in parallel, injects device removal or daemon death while I/O is in flight, waits for each wave, and preserves the first observed failure in ERR_CODE.

## State and Persistence
Uses temporary backing files and transient ublk devices; test_stress_05 additionally has a local run_io_and_remove that sends SIGKILL to the daemon before deletion.

## Dependencies and Integration Points
Depends on fio, test_common.sh stress helpers, null/loop/stripe targets, and optional ZERO_COPY, AUTO_BUF_REG, PER_IO_DAEMON, and BATCH_IO feature gates.

## Risks and Edge Cases
Highly timing-sensitive and intentionally destructive to active devices; diagnostics can interleave and some feature-gated branches are skipped silently when unsupported.

## Test Signals
Pass means all lifecycle-under-I/O scenarios complete with zero helper status; missing fio/features return skip where gated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_06.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_07.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_07.sh

## Purpose
Stress test that runs kill-daemon-during-I/O user-copy and per-io-task cases.

## Important APIs, Types, and Functions
run_io_and_remove or run_io_and_kill_daemon wrappers, fio, _have_feature, background jobs and wait.

## Control Flow
Prepares backing files, starts several target/mode workloads in parallel, injects device removal or daemon death while I/O is in flight, waits for each wave, and preserves the first observed failure in ERR_CODE.

## State and Persistence
Uses temporary backing files and transient ublk devices; test_stress_05 additionally has a local run_io_and_remove that sends SIGKILL to the daemon before deletion.

## Dependencies and Integration Points
Depends on fio, test_common.sh stress helpers, null/loop/stripe targets, and optional ZERO_COPY, AUTO_BUF_REG, PER_IO_DAEMON, and BATCH_IO feature gates.

## Risks and Edge Cases
Highly timing-sensitive and intentionally destructive to active devices; diagnostics can interleave and some feature-gated branches are skipped silently when unsupported.

## Test Signals
Pass means all lifecycle-under-I/O scenarios complete with zero helper status; missing fio/features return skip where gated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_07.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_08.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_08.sh

## Purpose
Stress test that runs batch-I/O remove-during-I/O cases for zero-copy and auto-zc.

## Important APIs, Types, and Functions
run_io_and_remove or run_io_and_kill_daemon wrappers, fio, _have_feature, background jobs and wait.

## Control Flow
Prepares backing files, starts several target/mode workloads in parallel, injects device removal or daemon death while I/O is in flight, waits for each wave, and preserves the first observed failure in ERR_CODE.

## State and Persistence
Uses temporary backing files and transient ublk devices; test_stress_05 additionally has a local run_io_and_remove that sends SIGKILL to the daemon before deletion.

## Dependencies and Integration Points
Depends on fio, test_common.sh stress helpers, null/loop/stripe targets, and optional ZERO_COPY, AUTO_BUF_REG, PER_IO_DAEMON, and BATCH_IO feature gates.

## Risks and Edge Cases
Highly timing-sensitive and intentionally destructive to active devices; diagnostics can interleave and some feature-gated branches are skipped silently when unsupported.

## Test Signals
Pass means all lifecycle-under-I/O scenarios complete with zero helper status; missing fio/features return skip where gated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_08.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_09.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_09.sh

## Purpose
Stress test that runs batch-I/O kill-daemon-during-I/O cases for zero-copy and auto-zc.

## Important APIs, Types, and Functions
run_io_and_remove or run_io_and_kill_daemon wrappers, fio, _have_feature, background jobs and wait.

## Control Flow
Prepares backing files, starts several target/mode workloads in parallel, injects device removal or daemon death while I/O is in flight, waits for each wave, and preserves the first observed failure in ERR_CODE.

## State and Persistence
Uses temporary backing files and transient ublk devices; test_stress_05 additionally has a local run_io_and_remove that sends SIGKILL to the daemon before deletion.

## Dependencies and Integration Points
Depends on fio, test_common.sh stress helpers, null/loop/stripe targets, and optional ZERO_COPY, AUTO_BUF_REG, PER_IO_DAEMON, and BATCH_IO feature gates.

## Risks and Edge Cases
Highly timing-sensitive and intentionally destructive to active devices; diagnostics can interleave and some feature-gated branches are skipped silently when unsupported.

## Test Signals
Pass means all lifecycle-under-I/O scenarios complete with zero helper status; missing fio/features return skip where gated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_09.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_01.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_01.sh

## Purpose
Validates ublk stripe target using two 256M backing files with default copy fio verify.

## Important APIs, Types, and Functions
_create_backfile, _add_ublk_dev -t stripe, _run_fio_verify_io or _mkfs_mount_test.

## Control Flow
Creates two backfiles, adds a stripe device with mode-specific queue/copy flags, runs either 512M fio verify over the combined device or filesystem mount smoke coverage, then cleans up.

## State and Persistence
Temporary backfiles hold the striped data for the test duration; the ublk device maps both files.

## Dependencies and Integration Points
Depends on test_common.sh, stripe target, fio for verify cases, and filesystem helpers for mount cases.

## Risks and Edge Cases
Stripe tests assume exact combined size and that both backfiles are available; filesystem tests do not verify cross-file data distribution directly.

## Test Signals
Pass is helper status 0 and cleanup completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_01.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_02.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_02.sh

## Purpose
Validates ublk stripe target using two 256M backing files with default copy mkfs/mount/umount.

## Important APIs, Types, and Functions
_create_backfile, _add_ublk_dev -t stripe, _run_fio_verify_io or _mkfs_mount_test.

## Control Flow
Creates two backfiles, adds a stripe device with mode-specific queue/copy flags, runs either 512M fio verify over the combined device or filesystem mount smoke coverage, then cleans up.

## State and Persistence
Temporary backfiles hold the striped data for the test duration; the ublk device maps both files.

## Dependencies and Integration Points
Depends on test_common.sh, stripe target, fio for verify cases, and filesystem helpers for mount cases.

## Risks and Edge Cases
Stripe tests assume exact combined size and that both backfiles are available; filesystem tests do not verify cross-file data distribution directly.

## Test Signals
Pass is helper status 0 and cleanup completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_03.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_03.sh

## Purpose
Validates ublk stripe target using two 256M backing files with two-queue fio verify.

## Important APIs, Types, and Functions
_create_backfile, _add_ublk_dev -t stripe, _run_fio_verify_io or _mkfs_mount_test.

## Control Flow
Creates two backfiles, adds a stripe device with mode-specific queue/copy flags, runs either 512M fio verify over the combined device or filesystem mount smoke coverage, then cleans up.

## State and Persistence
Temporary backfiles hold the striped data for the test duration; the ublk device maps both files.

## Dependencies and Integration Points
Depends on test_common.sh, stripe target, fio for verify cases, and filesystem helpers for mount cases.

## Risks and Edge Cases
Stripe tests assume exact combined size and that both backfiles are available; filesystem tests do not verify cross-file data distribution directly.

## Test Signals
Pass is helper status 0 and cleanup completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_03.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_04.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_04.sh

## Purpose
Validates ublk stripe target using two 256M backing files with zero-copy two-queue mkfs/mount/umount.

## Important APIs, Types, and Functions
_create_backfile, _add_ublk_dev -t stripe, _run_fio_verify_io or _mkfs_mount_test.

## Control Flow
Creates two backfiles, adds a stripe device with mode-specific queue/copy flags, runs either 512M fio verify over the combined device or filesystem mount smoke coverage, then cleans up.

## State and Persistence
Temporary backfiles hold the striped data for the test duration; the ublk device maps both files.

## Dependencies and Integration Points
Depends on test_common.sh, stripe target, fio for verify cases, and filesystem helpers for mount cases.

## Risks and Edge Cases
Stripe tests assume exact combined size and that both backfiles are available; filesystem tests do not verify cross-file data distribution directly.

## Test Signals
Pass is helper status 0 and cleanup completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_04.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_05.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_05.sh

## Purpose
Validates ublk stripe target using two 256M backing files with user-copy two-queue fio verify.

## Important APIs, Types, and Functions
_create_backfile, _add_ublk_dev -t stripe, _run_fio_verify_io or _mkfs_mount_test.

## Control Flow
Creates two backfiles, adds a stripe device with mode-specific queue/copy flags, runs either 512M fio verify over the combined device or filesystem mount smoke coverage, then cleans up.

## State and Persistence
Temporary backfiles hold the striped data for the test duration; the ublk device maps both files.

## Dependencies and Integration Points
Depends on test_common.sh, stripe target, fio for verify cases, and filesystem helpers for mount cases.

## Risks and Edge Cases
Stripe tests assume exact combined size and that both backfiles are available; filesystem tests do not verify cross-file data distribution directly.

## Test Signals
Pass is helper status 0 and cleanup completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_05.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_06.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_06.sh

## Purpose
Validates ublk stripe target using two 256M backing files with user-copy two-queue mkfs/mount/umount.

## Important APIs, Types, and Functions
_create_backfile, _add_ublk_dev -t stripe, _run_fio_verify_io or _mkfs_mount_test.

## Control Flow
Creates two backfiles, adds a stripe device with mode-specific queue/copy flags, runs either 512M fio verify over the combined device or filesystem mount smoke coverage, then cleans up.

## State and Persistence
Temporary backfiles hold the striped data for the test duration; the ublk device maps both files.

## Dependencies and Integration Points
Depends on test_common.sh, stripe target, fio for verify cases, and filesystem helpers for mount cases.

## Risks and Edge Cases
Stripe tests assume exact combined size and that both backfiles are available; filesystem tests do not verify cross-file data distribution directly.

## Test Signals
Pass is helper status 0 and cleanup completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stripe_06.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/ublk_dep.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/ublk_dep.h

## Purpose
Compatibility header that defines newer ublk ioctl/feature constants when the build headers do not provide them.

## Important APIs, Types, and Functions
UBLK_U_IO_REGISTER_IO_BUF, UBLK_U_IO_UNREGISTER_IO_BUF, UBLK_F_USER_RECOVERY_FAIL_IO, UBLK_F_ZONED.

## Control Flow
Pure preprocessor fallback: include guard checks each symbol and defines missing ioctl numbers or feature bits.

## State and Persistence
No runtime state or persistence.

## Dependencies and Integration Points
Depends on struct ublksrv_io_cmd and ioctl encoding macros from surrounding ublk build headers.

## Risks and Edge Cases
Risk is numeric drift if upstream ABI changes; fallback definitions must remain synchronized with kernel UAPI.

## Test Signals
Build success on older headers is the main signal; no direct runtime test in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/ublk_dep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/utils.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/utils.h

## Purpose
Small C utility header for ublk selftest support: generic macros, CPU-set allocator, log/debug helpers, and assertion wrapper.

## Important APIs, Types, and Functions
ARRAY_SIZE, offsetof, container_of, round_up, struct allocator, allocator_init/get/put/get_val/deinit, ilog2, ublk_err/log/dbg/assert.

## Control Flow
Inline helpers allocate a CPU_ALLOC bitmap, scan for free integer slots, set/clear bits, and provide conditional stdout/stderr logging controlled by ublk_dbg_mask.

## State and Persistence
Allocator state is the CPU bitmap plus size in caller-owned struct allocator; logging reads global ublk_dbg_mask.

## Dependencies and Integration Points
Depends on glibc CPU_ALLOC APIs, errno, stdio/varargs/assert includes from users, and an external ublk_dbg_mask definition.

## Risks and Edge Cases
No locking, so allocator is not thread-safe; macros evaluate arguments directly and should be used with side-effect caution.

## Test Signals
Compile-time integration and assertion/log behavior in ublk C tools are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/Makefile

## Purpose
Builds the uevent_filtering kselftest binary and registers it with the selftest harness.

## Important APIs, Types, and Functions
BINARIES, TEST_PROGS, EXTRA_CLEAN, CFLAGS, ../lib.mk.

## Control Flow
Declares uevent_filtering from uevent_filtering.c plus harness headers, adds no-as-needed/Wall flags, and includes the common selftest make rules.

## State and Persistence
No runtime state; build artifacts are cleaned through EXTRA_CLEAN.

## Dependencies and Integration Points
Depends on kselftest lib.mk and a C compiler/linker.

## Risks and Edge Cases
Architecture-independent but root/runtime namespace support is checked only by the binary.

## Test Signals
Successful build and kselftest execution of uevent_filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/config

## Purpose
Declares kernel config prerequisites for uevent filtering tests.

## Important APIs, Types, and Functions
CONFIG_USER_NS=y, CONFIG_NET=y.

## Control Flow
Static kselftest config fragment only.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Used by kselftest config merge tooling.

## Risks and Edge Cases
Incomplete configs can still fail at runtime if root or sysfs support is missing.

## Test Signals
Config tooling should request user and network namespace support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/uevent_filtering.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/uevent_filtering.c

## Purpose
Tests kernel uevent netlink filtering across user and network namespace ownership combinations.

## Important APIs, Types, and Functions
read_nointr, write_nointr, wait_for_pid, uevent_listener, trigger_uevent, set_death_signal, do_test, TEST(uevent_filtering).

## Control Flow
Forks a listener, optionally unshares namespaces before or after opening a NETLINK_KOBJECT_UEVENT socket, synchronizes with eventfd, writes add to /sys/devices/virtual/mem/full/uevent, waits up to two seconds, and verifies whether the event is delivered.

## State and Persistence
Creates child processes, netlink sockets, signal handlers, and an eventfd; no persistent files are modified beyond triggering the sysfs uevent.

## Dependencies and Integration Points
Requires root, /sys/devices/virtual/mem/full/uevent, NETLINK_KOBJECT_UEVENT, CLONE_NEWUSER, CLONE_NEWNET, and kselftest_harness.

## Risks and Edge Cases
Timing-sensitive delivery window; child cleanup relies on death signal and explicit SIGTERM/SIGUSR1 paths.

## Test Signals
Pass means expected receive/no-receive behavior for all namespace matrix cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/uevent_filtering.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/Makefile

## Purpose
Builds user_events ABI, dynamic-events, ftrace, and perf kselftests.

## Important APIs, Types, and Functions
TEST_GEN_PROGS=ftrace_test dyn_test perf_test abi_test; TEST_FILES=settings; CFLAGS/LDLIBS; ../lib.mk.

## Control Flow
Adds trace/user_events include flags and links rt, pthread, and math libraries through common kselftest rules.

## State and Persistence
No runtime state except generated binaries.

## Dependencies and Integration Points
Depends on kernel headers exposing linux/user_events.h and kselftest build infrastructure.

## Risks and Edge Cases
Build success does not guarantee tracefs mount or root privileges at runtime.

## Test Signals
All four generated tests compile and are discoverable by kselftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/abi_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/abi_test.c

## Purpose
Validates the user_events ioctl ABI for enablement bits, persistent events, bit-size validation, multi-format events, fork COW updates, and clone shared-VM updates.

## Important APIs, Types, and Functions
DIAG_IOCSREG, DIAG_IOCSUNREG, DIAG_IOCSDEL, struct user_reg/user_unreg, reg_enable*, reg_disable, find_multi_event_dir, event_exists/change_event/delete.

## Control Flow
Fixture mounts/checks tracefs, registers events through /sys/kernel/tracing/user_events_data, toggles enable files, verifies userspace status bits, tests invalid flags/sizes, locates multi-format event directories by format content, and checks fork/clone propagation.

## State and Persistence
Creates and deletes tracefs event directories under user_events/user_events_multi; manipulates in-process enable words and may mount tracefs temporarily.

## Dependencies and Integration Points
Requires root, tracefs, CONFIG_USER_EVENTS, linux/user_events.h, glob/stat/ioctl support, and user_events_selftests.h.

## Risks and Edge Cases
Persistent-event and multi-format cleanup can lag, so wait loops are used; tests depend on exact tracefs paths and kernel ABI errno behavior.

## Test Signals
Pass is all kselftest fixture cases completing with expected ioctl results and enable-bit transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/abi_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/config

## Purpose
Declares CONFIG_USER_EVENTS as the required kernel option for user_events tests.

## Important APIs, Types, and Functions
CONFIG_USER_EVENTS=y.

## Control Flow
Static config fragment only.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Consumed by kselftest config tooling.

## Risks and Edge Cases
Runtime still requires root and tracefs even if config is enabled.

## Test Signals
Config merge should request user_events support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/dyn_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/dyn_test.c

## Purpose
Checks that user_events dynamic_events parser and direct ABI parser accept and reject the same event field syntax and enforce format matching.

## Important APIs, Types, and Functions
parse_dyn, parse_abi, parse, check_match, TEST_PARSE/TEST_NPARSE, TEST_MATCH/TEST_NMATCH.

## Control Flow
Writes dynamic event definitions to /sys/kernel/tracing/dynamic_events and registers equivalent ABI definitions, deletes temporary events, then verifies accepted scalar, array, loc, struct-size, and name/type matching cases.

## State and Persistence
Creates __test_event under tracefs and deletes it after parse/match checks; uses one fixture enable word.

## Dependencies and Integration Points
Requires tracefs/user_events_data/dynamic_events and root via user_events_selftests.h.

## Risks and Edge Cases
Parser equivalence is sensitive to kernel grammar changes; cleanup waits for event deletion but can be affected by busy refs.

## Test Signals
Pass means ABI and dynamic parser results agree and same-name format matching rejects incompatible definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/dyn_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/ftrace_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/ftrace_test.c

## Purpose
Tests user_events ftrace integration: registration semantics, writev data emission, fault handling, dynamic string validation, and generated print_fmt strings.

## Important APIs, Types, and Functions
trace_bytes, get_print_fmt, clear, check_print_fmt, DIAG_IOCSREG/UNREG/DEL, writev, DYN_LOC.

## Control Flow
Registers __test_event formats, toggles enable files, writes event payloads through user_events_data, checks ftrace trace size growth, validates invalid slot/disabled/negative index errors, exercises dynamic string bounds and null termination, and compares print_fmt output.

## State and Persistence
Creates tracefs events, opens status/data/enable files, writes trace buffer data, and cleans/deletes events in teardown.

## Dependencies and Integration Points
Requires root, tracefs, CONFIG_USER_EVENTS, ftrace event files, kselftest harness.

## Risks and Edge Cases
Trace buffer byte-count checks can be noisy if other tracing is active; exact print_fmt strings are ABI-sensitive.

## Test Signals
Pass means write paths and generated formats match expected behavior and all invalid writes fail with expected errno.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/ftrace_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/perf_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/perf_test.c

## Purpose
Tests user_events as perf tracepoints by attaching perf_event_open and reading raw samples from the perf mmap buffer.

## Important APIs, Types, and Functions
perf_event_open syscall wrapper, get_id, get_offset, clear, PERF_TYPE_TRACEPOINT, PERF_SAMPLE_RAW.

## Control Flow
Registers an event, obtains its tracepoint id and field offset from tracefs, opens a perf event, mmaps the perf page, writes user event data, and checks sample record type plus payload values; repeats for empty events.

## State and Persistence
Creates tracefs event, perf fd/mmap buffer, and updates enable bits through perf attachment; cleans event in teardown.

## Dependencies and Integration Points
Requires root, tracefs, perf_event_open permissions, CONFIG_USER_EVENTS, and kselftest harness.

## Risks and Edge Cases
Direct perf ring parsing assumes sample layout and immediate visibility; restricted perf_event_paranoid can block runtime.

## Test Signals
Pass means perf receives expected samples and status bits clear after perf fd close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/perf_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/user_events_selftests.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/user_events_selftests.h

## Purpose
Shared setup/teardown helpers for user_events tests that ensure root, tracefs mount, and user_events_data availability.

## Important APIs, Types, and Functions
tracefs_enabled, user_events_enabled, USER_EVENT_FIXTURE_SETUP, USER_EVENT_FIXTURE_TEARDOWN.

## Control Flow
Checks /sys/kernel/tracing, mounts tracefs if README is absent, verifies /sys/kernel/tracing/user_events_data, and unmounts tracefs in teardown only if this helper mounted it.

## State and Persistence
May mount and later unmount tracefs; communicates skip/fail state through message/fail/umount outputs.

## Dependencies and Integration Points
Depends on mount/umount, stat, errno, kselftest.h, root privileges.

## Risks and Edge Cases
Mounting tracefs in a shared environment can affect concurrent tests; root absence is treated as fail for user_events_enabled.

## Test Signals
Tests using the macros skip cleanly when user_events is absent and fail when tracefs cannot be accessed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/user_events_selftests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/Makefile

## Purpose
Builds the vDSO selftest suite, including parser-linked tests, x86 nolibc standalone test, getrandom, and architecture ChaCha assembly validation.

## Important APIs, Types, and Functions
TEST_GEN_PROGS, CFLAGS_NOLIBC, per-target dependencies, vgetrandom-chacha.S target includes.

## Control Flow
Includes Makefile.arch, lists vDSO test binaries, wires parse_vdso.c into symbol-lookup tests, configures nolibc flags for x86 standalone, and adds include paths for getrandom/chacha tests.

## State and Persistence
No runtime state; generated binaries are kselftest artifacts.

## Dependencies and Integration Points
Depends on tools/include, arch headers, kernel UAPI headers, and common selftest lib.mk.

## Risks and Edge Cases
Conditional x86 standalone and arch assembly include paths must match source tree layout.

## Test Signals
Build success for each target and kselftest execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/parse_vdso.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/parse_vdso.c

## Purpose
Reference ELF parser used by vDSO tests to initialize from AT_SYSINFO_EHDR and resolve versioned symbols.

## Important APIs, Types, and Functions
vdso_init_from_sysinfo_ehdr, vdso_sym, elf_hash, gnu_hash, vdso_match_version, check_sym, static vdso_info.

## Control Flow
Parses ELF headers/program headers, computes load offset, extracts dynamic string/symbol/hash/version tables, supports GNU hash and SysV hash lookup, and returns function addresses for matching name/version symbols.

## State and Persistence
Maintains one static global vdso_info cache; init is not thread-safe while vdso_sym is read-only after initialization.

## Dependencies and Integration Points
Depends on ELF layout, auxv-provided vDSO base, parse_vdso.h, and architecture ELF_BITS selection.

## Risks and Edge Cases
Malformed or unexpected vDSO tables can make lookup fail; version matching linearly scans verdef and assumes standard table consistency.

## Test Signals
Tests using vdso_sym skip when symbols are absent and fail when resolved calls behave incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/parse_vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/parse_vdso.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/parse_vdso.h

## Purpose
Public interface and usage notes for the vDSO parser.

## Important APIs, Types, and Functions
vdso_sym, vdso_init_from_sysinfo_ehdr prototypes.

## Control Flow
Documents the call sequence: initialize from AT_SYSINFO_EHDR, then resolve symbol names and versions.

## State and Persistence
No state in the header; implementation state lives in parse_vdso.c.

## Dependencies and Integration Points
Included by all vDSO tests that need symbol lookup.

## Risks and Edge Cases
Consumers must cache vdso_sym results and avoid racing init.

## Test Signals
Compile-time integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/parse_vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_call.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_call.h

## Purpose
Architecture adapter for invoking vDSO functions, with PowerPC register-call handling and a normal direct-call fallback elsewhere.

## Important APIs, Types, and Functions
LOADARGS_1/2/3/5, VDSO_CALL macro.

## Control Flow
On powerpc, loads the function pointer and arguments into ABI registers, branches through ctr, and normalizes error return; on other architectures expands to fn(args).

## State and Persistence
No persistent state; only inline register clobbers during calls.

## Dependencies and Integration Points
Depends on compiler support for GNU statement expressions and powerpc register asm.

## Risks and Edge Cases
Incorrect clobber/register constraints would corrupt calls only on powerpc; non-powerpc has minimal risk.

## Test Signals
vDSO tests compile and execute through VDSO_CALL on target architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_call.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_config.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_config.h

## Purpose
Architecture mapping table for vDSO symbol versions and symbol names.

## Important APIs, Types, and Functions
VDSO_VERSION, VDSO_NAMES, VDSO_32BIT, versions[], names[][].

## Control Flow
Preprocessor selects the version index and name family for each supported architecture, then tests index into versions/names to resolve gettimeofday, clock_gettime, time, getcpu, getrandom, and time64 symbols.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Depends on compiler architecture macros and exported vDSO ABI names.

## Risks and Edge Cases
Adding a new architecture or renamed symbol requires table updates; wrong index causes tests to skip or fail symbol lookup.

## Test Signals
All vDSO tests use this table; successful symbol resolution validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_standalone_test_x86.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_standalone_test_x86.c

## Purpose
Nolibc-compatible x86 standalone smoke test for vDSO gettimeofday symbol lookup and call.

## Important APIs, Types, and Functions
main, getauxval(AT_SYSINFO_EHDR), vdso_init_from_sysinfo_ehdr, vdso_sym, VDSO_CALL.

## Control Flow
Gets the vDSO base, resolves gettimeofday for the architecture table, calls it, prints the result, and returns skip/fail/pass via kselftest codes.

## State and Persistence
No persistent state.

## Dependencies and Integration Points
Built specially with nolibc flags on x86 and links parse_vdso.c.

## Risks and Edge Cases
Only tests a single symbol and skips when absent; output time is informational.

## Test Signals
Pass is ret==0 from the vDSO gettimeofday call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_standalone_test_x86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_abi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_abi.c

## Purpose
Full vDSO ABI presence and call smoke test for gettimeofday, clock_gettime/time64, clock_getres/time64, time, across a clock-id plan.

## Important APIs, Types, and Functions
vdso_test_gettimeofday, vdso_test_clock_gettime*, vdso_test_clock_getres*, vdso_test_time, VDSO_TEST_PLAN.

## Control Flow
Initializes parser, sets a 38-test kselftest plan, resolves each symbol, calls supported vDSO functions for multiple clock ids, compares clock_getres against syscall, and records pass/skip/fail per symbol/clock.

## State and Persistence
No persistent state; reads time from vDSO and syscall.

## Dependencies and Integration Points
Depends on AT_SYSINFO_EHDR, vdso_config symbol table, parse_vdso, syscalls for comparison, and kselftest.

## Risks and Edge Cases
Clock support varies by architecture/kernel, so many paths can skip; plan count must stay synchronized with tested cases.

## Test Signals
Pass/skip/fail lines in KTAP are the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_abi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_chacha.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_chacha.c

## Purpose
Validates architecture vgetrandom ChaCha20 block implementation against a C reference.

## Important APIs, Types, and Functions
reference_chacha20_blocks, __arch_chacha20_blocks_nostack weak symbol, cpu_has_capabilities, kselftest main.

## Control Flow
Generates random keys, computes reference output for 128 blocks, calls the arch nostack implementation in every split position, compares output and counters, and tests counter wrap/block-limit behavior.

## State and Persistence
No persistent state; uses stack buffers and random keys.

## Dependencies and Integration Points
Depends on getrandom, tools/le_byteshift.h, arch assembly linked through vgetrandom-chacha.S, and required CPU vector capabilities on some architectures.

## Risks and Edge Cases
Very CPU-intensive nested loop; weak fallback skips if no implementation is linked.

## Test Signals
Pass is one kselftest result after all output/counter comparisons succeed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_chacha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_correctness.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_correctness.c

## Purpose
Compares vDSO time/getcpu results with syscall/vsyscall behavior for ordering and correctness.

## Important APIs, Types, and Functions
fill_function_pointers, test_clock_gettime, test_clock_gettime64, test_gettimeofday, test_time, test_getcpu, sys_* wrappers.

## Control Flow
Resolves vDSO symbols, tests supported clock ids plus invalid ids against syscall ordering/error behavior, compares timezone and time return consistency, and iterates CPU affinity to validate getcpu results.

## State and Persistence
Changes process CPU affinity during getcpu checks; no persistent files.

## Dependencies and Integration Points
Depends on AT_SYSINFO_EHDR, parse_vdso, vdso_config, syscalls, /proc/self/maps for x86 vsyscall detection.

## Risks and Edge Cases
Affinity loop stops at first unavailable CPU; invalid-clock errno handling must match vDSO ABI.

## Test Signals
Returns nonzero if any comparison increments nerrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_correctness.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_getcpu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_getcpu.c

## Purpose
Simple vDSO getcpu symbol lookup and call smoke test.

## Important APIs, Types, and Functions
main, getauxval, vdso_init_from_sysinfo_ehdr, vdso_sym, VDSO_CALL.

## Control Flow
Resolves the configured getcpu symbol, calls it with cpu/node outputs, prints the location, and maps absence/failure to kselftest skip/fail.

## State and Persistence
No persistent state.

## Dependencies and Integration Points
Depends on AT_SYSINFO_EHDR and architecture vDSO getcpu export.

## Risks and Edge Cases
Only validates call success, not cross-check against syscall.

## Test Signals
Pass is vDSO getcpu returning 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_getcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_getrandom.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_getrandom.c

## Purpose
Tests and benchmarks vDSO getrandom with opaque per-thread state, including time namespace behavior under ptrace.

## Important APIs, Types, and Functions
vgetrandom_init, vgetrandom_get_state/put_state, vgetrandom wrapper, bench_single, bench_multi, fill, kselftest.

## Control Flow
Resolves __vdso_getrandom, queries opaque state parameters, allocates aligned state blocks with mmap, performs repeated random fills, then forks under a new time namespace with ptrace to assert the vDSO path does not pass the test buffer to getrandom syscall; optional modes benchmark or fill indefinitely.

## State and Persistence
Maintains global state pool guarded by a mutex and thread-local state pointer; creates mappings, threads, namespaces, child process, and ptrace state.

## Dependencies and Integration Points
Depends on vDSO getrandom ABI, linux/random.h vgetrandom_opaque_params, pthreads, ptrace, CLONE_NEWTIME, getrandom syscall for benchmark comparisons.

## Risks and Edge Cases
Default constants are very large for benchmark modes; namespace/ptrace permissions can cause skips/failures; state allocator assumes page/cache-line alignment constraints from kernel params.

## Test Signals
Default kselftest passes two results: random fill and timens syscall-avoidance validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_getrandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_gettimeofday.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_gettimeofday.c

## Purpose
Standalone vDSO gettimeofday smoke test using the shared parser and architecture symbol table.

## Important APIs, Types, and Functions
main, getauxval, vdso_init_from_sysinfo_ehdr, vdso_sym, VDSO_CALL.

## Control Flow
Gets AT_SYSINFO_EHDR, resolves gettimeofday, calls it, prints seconds/useconds, and returns kselftest skip/fail/pass.

## State and Persistence
No persistent state.

## Dependencies and Integration Points
Depends on parse_vdso, vdso_config, vdso_call, and kselftest.

## Risks and Edge Cases
Only covers one symbol and does not compare against syscall.

## Test Signals
Pass is a zero return from vDSO gettimeofday.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vdso_test_gettimeofday.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vgetrandom-chacha.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vgetrandom-chacha.S

## Purpose
Assembly dispatcher that includes the architecture-specific vgetrandom ChaCha implementation for the chacha selftest.

## Important APIs, Types, and Functions
__ASSEMBLY__ and conditional #include of arch/*/vgetrandom-chacha.S.

## Control Flow
At assembly preprocessing time, selects the arch implementation for arm64, loongarch, powerpc, riscv64, s390x, or x86_64; unsupported architectures compile without a strong implementation, leaving the weak skip path.

## State and Persistence
No runtime state in this wrapper.

## Dependencies and Integration Points
Depends on source-tree relative arch assembly paths and architecture predefines.

## Risks and Edge Cases
Path drift or unsupported architecture causes missing implementation and skipped chacha test.

## Test Signals
Build/link of vdso_test_chacha plus runtime comparison validates inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vgetrandom-chacha.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/verification/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/verification/Makefile

## Purpose
Registers the runtime-verification KTAP wrapper as a kselftest program.

## Important APIs, Types, and Functions
TEST_PROGS=verificationtest-ktap, TEST_FILES=test.d settings, EXTRA_CLEAN logs, ../lib.mk.

## Control Flow
Common kselftest Makefile wrapper with no local compilation.

## State and Persistence
No runtime state except logs under OUTPUT/logs.

## Dependencies and Integration Points
Depends on ../ftrace/ftracetest and runtime verification test data.

## Risks and Edge Cases
Wrapper assumes relative ftrace/verification directories exist.

## Test Signals
kselftest runs verificationtest-ktap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/verification/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/verification/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/verification/config

## Purpose
Declares CONFIG_RV as required for verification tests.

## Important APIs, Types, and Functions
CONFIG_RV=y.

## Control Flow
Static config fragment only.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Used by kselftest config tooling.

## Risks and Edge Cases
Runtime also needs ftrace test infrastructure.

## Test Signals
Config tooling requests runtime verification support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/verification/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/verification/verificationtest-ktap -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/verification/verificationtest-ktap

## Purpose
Shell wrapper that runs ftracetest in KTAP mode for runtime verification tests.

## Important APIs, Types, and Functions
../ftrace/ftracetest -K -v --rv ../verification.

## Control Flow
Executes ftracetest with KTAP output and the verification directory as the runtime-verification suite.

## State and Persistence
No persistent state except ftracetest logs/output.

## Dependencies and Integration Points
Depends on /bin/sh, ftracetest, and runtime verification test files.

## Risks and Edge Cases
Relative paths make it sensitive to invocation location under kselftest.

## Test Signals
Pass/fail is delegated to ftracetest KTAP output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/verification/verificationtest-ktap -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/Makefile

## Purpose
Builds VFIO selftests and the libvfio support library on supported architectures.

## Important APIs, Types, and Functions
ARCH gate, TEST_GEN_PROGS, TEST_FILES scripts, lib/libvfio.mk, object link rule.

## Control Flow
Skips program generation on unsupported architectures; otherwise declares DMA mapping, iommufd, PCI device, driver, and perf tests, installs setup/run/cleanup scripts, compiles each test object with LIBVFIO_O, and tracks dependency files.

## State and Persistence
No runtime state; build outputs and dep files are cleaned via EXTRA_CLEAN.

## Dependencies and Integration Points
Depends on kselftest lib.mk, kernel headers, pthread, and libvfio.mk.

## Risks and Edge Cases
Only aarch64/arm64/x86_64 are enabled; Makefile references tests outside this work item too.

## Test Signals
Successful build of listed TEST_GEN_PROGS and scripts copied as TEST_FILES.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/dsa/dsa.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/dsa/dsa.c

## Purpose
Implements the libvfio driver backend for Intel DSA/IDXD devices, providing DMA memcpy and MSI generation operations.

## Important APIs, Types, and Functions
dsa_ops, dsa_probe/init/remove, dsa_command, dsa_register_cache_init, dsa_wq_init, dsa_group_init, dsa_memcpy_start/wait, dsa_send_msi.

## Control Flow
Probes Intel DSA device IDs, rejects devices requiring interrupt-handle requests, enables PCI memory/master, resets/configures device/workqueue/group, enables WQ and MSI-X, submits copy or batch descriptors through BAR2, polls completion records and SWERR, and resets on remove.

## State and Persistence
Stores descriptors, completions, cached registers, max limits, and MSI buffers in device->driver.region; mutates hardware registers and MSI-X state.

## Dependencies and Integration Points
Depends on libvfio PCI/IOMMU helpers, linux/idxd.h, DSA register definitions, Intel DSA hardware, MMIO BAR0/BAR2, and mapped DMA region.

## Risks and Edge Cases
Hardware-specific and privileged; polling loops can hang until assertion timeout; SWERR is fatal; batching has special handling for count==1 and count==2 edge cases.

## Test Signals
VFIO driver tests validate init/remove, memcpy success/error, MSI, and storm behavior through this ops table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/dsa/dsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/dsa/registers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/dsa/registers.h

## Purpose
Defines Intel IDXD/DSA register offsets, capability bitfields, command/status enums, workqueue/group config structures, descriptor error records, and device IDs.

## Important APIs, Types, and Functions
PCI_DEVICE_ID_INTEL_DSA_*, union gen_cap_reg/wq_cap_reg/group_cap_reg/engine_cap_reg/sw_err_reg/wqcfg, struct grpcfg, DSA EVL structs, IDXD_CMD_* constants.

## Control Flow
Pure hardware-description header consumed by dsa.c to read capabilities, configure workqueues/groups, issue commands, decode software errors, and size descriptor resources.

## State and Persistence
No runtime state; maps MMIO/register layouts into C types.

## Dependencies and Integration Points
Depends on linux/idxd.h and kernel-style bitfield layout assumptions.

## Risks and Edge Cases
Must track hardware spec and kernel driver definitions; bitfield packing is compiler/ABI sensitive.

## Test Signals
Build correctness and successful DSA hardware tests validate the definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/dsa/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/hw.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/hw.h

## Purpose
Defines IOAT hardware constants and descriptor layouts used by the IOAT VFIO driver backend.

## Important APIs, Types, and Functions
PCI_DEVICE_ID_INTEL_IOAT_*, IOAT_VER_*, IOAT_DESC_SZ, struct ioat_dma_descriptor and XOR/PQ descriptor variants.

## Control Flow
Pure descriptor/register metadata; ioat.c uses device IDs, version constants, and DMA descriptor layout to program copy operations.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Depends on stdint types and Intel IOAT hardware specification.

## Risks and Edge Cases
Large legacy descriptor set exceeds what current ioat.c uses; drift from hardware docs can break DMA programming.

## Test Signals
Compile-time layout plus IOAT selftest memcpy behavior are the signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/ioat.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/ioat.c

## Purpose
Implements the libvfio driver backend for Intel IOAT DMA engines.

## Important APIs, Types, and Functions
ioat_ops, ioat_probe/init/remove, ioat_reset, ioat_memcpy_start/wait, ioat_send_msi.

## Control Flow
Probes Intel SKX IOAT with supported version, enables PCI memory/master and MSI-X, resets channel, programs a self-linked DMA descriptor, writes chain address/control/count registers, waits for DONE or handles HALTED errors, and can request interrupt on a tiny copy.

## State and Persistence
Stores one descriptor and MSI source/destination buffers in driver.region; mutates BAR0 channel registers and MSI-X setup.

## Dependencies and Integration Points
Depends on libvfio, IOAT register/header definitions, Intel IOAT hardware, mapped BAR0, and IOMMU mappings for the descriptor region.

## Risks and Edge Cases
Busy-wait loops have no sleep in wait path; only specific IOAT versions/device IDs are supported; hardware errors reset the channel and fail the operation.

## Test Signals
VFIO driver tests call ops through the generic driver wrapper for memcpy/MSI coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/ioat/ioat.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio.h

## Purpose
Umbrella public header for libvfio helpers and BDF/mmap utility APIs.

## Important APIs, Types, and Functions
Includes assert/iommu/iova_allocator/vfio_pci_device/vfio_pci_driver; vfio_selftests_get_bdf(s), mmap_reserve.

## Control Flow
Documents BDF selection from argv or VFIO_SELFTESTS_BDF and aligned virtual-address reservation for later mmap.

## State and Persistence
No state in header; libvfio.c owns BDF parsing behavior.

## Dependencies and Integration Points
Included by all VFIO tests and library implementation files.

## Risks and Edge Cases
Consumers must pass argc by pointer because BDF parsing mutates it.

## Test Signals
Compile-time integration across VFIO tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/assert.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/assert.h

## Purpose
Assertion and ioctl helper macros for VFIO selftests that log observed values and exit with KSFT_FAIL.

## Important APIs, Types, and Functions
VFIO_ASSERT_OP/EQ/NE/LT/LE/GT/GE/TRUE/FALSE/NULL/NOT_NULL, VFIO_FAIL, ioctl_assert.

## Control Flow
Macros evaluate operands once, compare, print file/line/expression/errno, and terminate on failure; ioctl_assert wraps expected-zero ioctl calls.

## State and Persistence
No persistent state; exits process on failure.

## Dependencies and Integration Points
Depends on errno, strerror, stdio, ioctl, and kselftest.h.

## Risks and Edge Cases
Fatal-exit style is unsuitable for recoverable checks; observed values are cast to u64 which may not format all pointer/types ideally.

## Test Signals
Failures produce detailed stderr and KSFT_FAIL exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/assert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/iommu.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/iommu.h

## Purpose
Public IOMMU abstraction for VFIO selftests supporting legacy VFIO type1, iommufd compatibility, and native iommufd modes.

## Important APIs, Types, and Functions
struct iommu_mode/dma_region/iommu, iommu_init/cleanup, map/unmap/unmap_all, hva2iova, iommu_iova_ranges, FIXTURE_VARIANT_ADD_ALL_IOMMU_MODES.

## Control Flow
Declares wrappers that map/unmap DMA regions and generate fixture variants over five IOMMU modes.

## State and Persistence
struct iommu owns container/iommufd fds, IOAS id, mode pointer, and list of mapped regions.

## Dependencies and Integration Points
Depends on linux/list.h/types.h and libvfio/assert.h; implemented in iommu.c.

## Risks and Edge Cases
Mapped region tracking is in-process only and must stay synchronized with kernel unmaps.

## Test Signals
VFIO DMA tests instantiate all variants through the fixture macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/iova_allocator.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/iova_allocator.h

## Purpose
Public sequential IOVA allocator interface for VFIO tests.

## Important APIs, Types, and Functions
struct iova_allocator, iova_allocator_init/cleanup/alloc.

## Control Flow
Allocates power-of-two sized IOVAs from sorted ranges returned by iommu_iova_ranges.

## State and Persistence
Allocator stores owned range array, current range index, and offset cursor.

## Dependencies and Integration Points
Depends on iommu.h and linux/iommufd.h range type.

## Risks and Edge Cases
No free/reuse support and asserts on exhaustion; size must be power of two.

## Test Signals
DMA mapping tests use returned IOVA values for map/unmap coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/iova_allocator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/vfio_pci_device.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/vfio_pci_device.h

## Purpose
Public VFIO PCI device abstraction with BAR, config, IRQ, reset, cdev, and IOVA conversion helpers.

## Important APIs, Types, and Functions
struct vfio_pci_bar/device, vfio_pci_device_init/cleanup/reset/config_access, config read/write macros, IRQ/MSI/MSI-X helpers, vfio_pci_get_cdev_path.

## Control Flow
Declares device lifecycle, config-space access via pread/pwrite, eventfd-backed MSI/MSI-X enabling/disabling, and BDF device matching helpers.

## State and Persistence
Device object owns fds, mapped BARs, IRQ eventfds, IOMMU pointer, VFIO info structs, and embedded driver state.

## Dependencies and Integration Points
Depends on linux/vfio.h, linux/pci_regs.h, libvfio iommu/driver/assert headers.

## Risks and Edge Cases
Eventfd array uses PCI_MSIX_FLAGS_QSIZE + 1 and assumes vector indexes fit; cleanup must close all owned fds/mappings.

## Test Signals
VFIO tests use the abstraction for setup, DMA, MMIO, and perf measurement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/vfio_pci_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/vfio_pci_driver.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/vfio_pci_driver.h

## Purpose
Public generic PCI-driver operation layer used by device-specific DSA and IOAT backends.

## Important APIs, Types, and Functions
struct vfio_pci_driver_ops, struct vfio_pci_driver, probe/init/remove/memcpy/send_msi wrappers.

## Control Flow
Defines backend hooks for probe, lifecycle, async memcpy, wait, and MSI generation, plus max operation limits and a DMA region for descriptors/state.

## State and Persistence
Driver state records selected ops, initialized flag, memcpy_in_progress flag, DMA region, max limits, and MSI vector.

## Dependencies and Integration Points
Depends on libvfio/iommu.h and vfio_pci_device forward declaration.

## Risks and Edge Cases
Operation wrappers assert strict state transitions; backends must set max limits and use the provided region.

## Test Signals
Driver tests exercise wrapper state checks and backend behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/vfio_pci_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/iommu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/iommu.c

## Purpose
Implements the VFIO/IOMMU abstraction across legacy VFIO containers and native/compat iommufd.

## Important APIs, Types, and Functions
lookup_iommu_mode, __iommu_map/unmap/unmap_all, __iommu_hva2iova, iommu_iova_ranges, iommu_init/cleanup, vfio_iommu_get_info, iommufd_ioas_alloc.

## Control Flow
Initializes mode-specific fds, maps/unmaps regions with VFIO_IOMMU_MAP_DMA or IOMMU_IOAS_MAP, tracks mappings in a list, queries allowed IOVA ranges from VFIO capability chains or iommufd, sorts/validates ranges, and closes fds on cleanup.

## State and Persistence
Owns container_fd or iommufd, IOAS id, and in-process dma_regions list; kernel owns actual mappings.

## Dependencies and Integration Points
Depends on /dev/vfio/vfio, /dev/iommu, linux/vfio.h, linux/iommufd.h, list helpers, and libvfio assertions.

## Risks and Edge Cases
Mode detection uses nonzero iommufd as native indicator; unmap_all clears in-process list only after ioctl success; capability-chain parsing asserts on malformed/cyclic chains.

## Test Signals
DMA mapping tests cover map/unmap, unmap_all, overflow, and IOVA range allocation across modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/iova_allocator.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/iova_allocator.c

## Purpose
Implements a simple monotonic IOVA allocator over kernel-reported allowed ranges.

## Important APIs, Types, and Functions
iova_allocator_init, cleanup, alloc, check_add_overflow.

## Control Flow
Copies sorted ranges, then for each allocation aligns within the current range, advances offset or range index, and asserts if no range has space.

## State and Persistence
Allocator owns the ranges array and cursor; no kernel state is changed until caller maps.

## Dependencies and Integration Points
Depends on iommu_iova_ranges and linux/overflow.h.

## Risks and Edge Cases
No deallocation or fragmentation handling; power-of-two assertion rejects arbitrary sizes.

## Test Signals
Used by DMA mapping and MMIO mapping tests to choose legal IOVAs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/iova_allocator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/libvfio.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/libvfio.c

## Purpose
Implements shared libvfio utilities for BDF parsing/selection and aligned virtual-address reservation.

## Important APIs, Types, and Functions
is_bdf, get_bdfs_cmdline, get_bdf_env, vfio_selftests_get_bdfs/get_bdf, mmap_reserve.

## Control Flow
Parses trailing BDF argv entries or VFIO_SELFTESTS_BDF, skips with instructions if absent, and reserves an overlarge PROT_NONE mapping trimmed so returned address satisfies vaddr % align == offset.

## State and Persistence
BDF env pointer is stored static; mmap_reserve returns a reserved mapping caller must later map/unmap.

## Dependencies and Integration Points
Depends on mmap/munmap, ALIGN macro, kselftest skip code, and libvfio assertions.

## Risks and Edge Cases
BDF parser allows fixed hex widths and mutates argc; mmap_reserve pointer arithmetic assumes GNU C void* arithmetic.

## Test Signals
All VFIO tests use BDF selection; BAR misalignment test uses mmap_reserve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/libvfio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/libvfio.mk -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/libvfio.mk

## Purpose
Build fragment for libvfio object files and include paths.

## Important APIs, Types, and Functions
LIBVFIO_C, LIBVFIO_O, LIBVFIO_OUTPUT, object pattern rule, ARCH conditional x86 drivers.

## Control Flow
Includes subarch detection, lists common library C files, adds IOAT/DSA drivers for x86, creates output directories, adds lib include path, and compiles sources to OUTPUT/libvfio objects.

## State and Persistence
No runtime state; build state is object/dependency output under OUTPUT.

## Dependencies and Integration Points
Depends on top_srcdir scripts/subarch.include and kernel selftest make variables.

## Risks and Edge Cases
$(shell mkdir -p ...) runs at parse time; non-x86 builds omit device drivers so probing can find no backend.

## Test Signals
Successful link of VFIO tests against LIBVFIO_O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/libvfio.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/vfio_pci_device.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/vfio_pci_device.c

## Purpose
Implements VFIO PCI device setup/teardown, BAR mapping, config access, IRQ management, group/container setup, and iommufd cdev setup.

## Important APIs, Types, and Functions
vfio_pci_device_init/cleanup, vfio_pci_irq_enable/disable/trigger, vfio_pci_config_access, vfio_pci_device_reset, vfio_pci_get_cdev_path, vfio_pci_bar_map/unmap.

## Control Flow
Finds IOMMU group or vfio cdev path, opens device via legacy group/container or iommufd bind/attach, queries device/config/BAR/IRQ info, mmaps mappable BARs with alignment, sets up eventfd IRQ vectors, probes driver backends, and cleans mappings/fds on teardown.

## State and Persistence
Device object owns VFIO fd/group fd, BAR mappings, eventfds, and embedded driver; hardware state is reset/configured by callers/backends.

## Dependencies and Integration Points
Depends on sysfs /sys/bus/pci/devices, /dev/vfio, VFIO ioctls, iommufd ioctls, mmap, eventfd, PCI config ABI.

## Risks and Edge Cases
Assumes IOMMU group is viable and vfio-pci bound; cdev path discovery expects /vfio-dev entries; BAR mapping requires power-of-two sizes and MMAP flags.

## Test Signals
VFIO tests validate config access, DMA mapping of BARs, iommufd setup, and init performance through this layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/vfio_pci_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/vfio_pci_driver.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/vfio_pci_driver.c

## Purpose
Implements generic dispatch and state validation for selected VFIO PCI driver backend operations.

## Important APIs, Types, and Functions
driver_ops array, vfio_pci_driver_probe/init/remove/memcpy_start/memcpy_wait/memcpy/send_msi, vfio_check_driver_op.

## Control Flow
Probes available x86 backends, stores the matching ops, asserts correct initialized/memcpy_in_progress state before each operation, delegates to backend hooks, and updates progress flags.

## State and Persistence
State is embedded in device->driver and tracks ops selection plus lifecycle/progress booleans.

## Dependencies and Integration Points
Depends on DSA/IOAT ops on x86 and libvfio assertions.

## Risks and Edge Cases
If multiple probes match, the last match wins; no backend on non-x86 means driver operation tests must skip/fail appropriately.

## Test Signals
Driver tests exercise init/remove, memcpy paths, MSI, and mixed-device behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/vfio_pci_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/cleanup.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/cleanup.sh

## Purpose
Restores PCI devices modified by VFIO selftest setup back to their prior drivers/SR-IOV state.

## Important APIs, Types, and Functions
cleanup_devices, main, unbind, clear_driver_override, bind, set_sriov_numvfs from lib.sh.

## Control Flow
For each recorded BDF, unbinds vfio-pci if setup bound it, clears driver_override, rebinds the saved original driver, restores sriov_numvfs, and removes the device record directory; with no args, cleans every recorded device.

## State and Persistence
Reads and deletes state under TMPDIR/vfio-selftests-devices; mutates sysfs driver binding and SR-IOV settings.

## Dependencies and Integration Points
Depends on bash, lib.sh, sysfs PCI driver files, and setup.sh-created marker files.

## Risks and Edge Cases
Unquoted paths/variables assume simple BDF names; rebinding the old driver may fail if hardware state changed.

## Test Signals
Successful cleanup removes the devices directory and restores previous bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/cleanup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/lib.sh

## Purpose
Shared shell functions for VFIO setup/cleanup scripts.

## Important APIs, Types, and Functions
DEVICES_DIR, write_to, get_driver, bind, unbind, set/get_sriov_numvfs, set/clear_driver_override.

## Control Flow
Wraps sysfs writes with echoed commands and provides small helpers to inspect and mutate PCI driver/SR-IOV state.

## State and Persistence
Uses TMPDIR/vfio-selftests-devices as persistent script state root; writes directly to /sys/bus/pci.

## Dependencies and Integration Points
Depends on bash, readlink, basename, cat, and PCI sysfs.

## Risks and Edge Cases
No error handling beyond shell failures in callers; variables are mostly unquoted.

## Test Signals
Setup/cleanup scripts rely on these helpers for reversible device preparation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/run.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/run.sh

## Purpose
Runs a VFIO test binary with all BDFs recorded by setup.sh.

## Important APIs, Types, and Functions
main, DEVICES_DIR, command invocation "$@" ${device_bdfs}.

## Control Flow
Lists prepared device BDFs, skips with exit code 4 if none exist, otherwise appends BDFs to the supplied test command.

## State and Persistence
Reads state from TMPDIR/vfio-selftests-devices only.

## Dependencies and Integration Points
Depends on bash, lib.sh, and setup.sh-created directory.

## Risks and Edge Cases
Whitespace in BDF list is not expected; command status is the test status.

## Test Signals
Used to run compiled tests against prepared devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/setup.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/setup.sh

## Purpose
Prepares PCI devices for VFIO selftests by disabling VFs, unbinding current drivers, setting vfio-pci override, and binding vfio-pci.

## Important APIs, Types, and Functions
main, get_sriov_numvfs, set_sriov_numvfs, get_driver, unbind, set_driver_override, bind.

## Control Flow
For each BDF, verifies sysfs device exists, records original SR-IOV VF count and driver, disables VFs, unbinds original driver, sets driver_override to vfio-pci, binds vfio-pci, and writes marker files for cleanup.

## State and Persistence
Persists original state under TMPDIR/vfio-selftests-devices/BDF and mutates PCI sysfs binding and sriov_numvfs.

## Dependencies and Integration Points
Depends on bash, root privileges, vfio-pci driver, PCI sysfs, and lib.sh.

## Risks and Edge Cases
Interruption can leave devices bound to vfio-pci until cleanup.sh runs; already-setup BDF exits early.

## Test Signals
Successful setup creates marker files consumed by run.sh and cleanup.sh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_dma_mapping_mmio_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_dma_mapping_mmio_test.c

## Purpose
Tests whether VFIO can IOMMU-map PCI BAR MMIO mappings, including full, partial, and deliberately misaligned virtual mappings.

## Important APIs, Types, and Functions
largest_mapped_bar, do_mmio_map_test, map_full_bar, map_partial_bar, map_bar_misaligned fixtures over all IOMMU modes.

## Control Flow
Initializes IOMMU/device/allocator, selects largest readable+writable mappable BAR, maps BAR vaddr to an allocated IOVA for legacy VFIO type1 modes and expects failure for native/compat iommufd modes, then unmaps; misaligned case remaps BAR at a chosen offset.

## State and Persistence
Creates BAR mmaps and IOMMU mappings transiently; misaligned test reserves/remaps virtual address space.

## Dependencies and Integration Points
Depends on libvfio, VFIO PCI device, IOMMU modes, page size, and a device with a writable/readable mappable BAR.

## Risks and Edge Cases
Native iommufd expectation is documented as unsupported; future compat behavior may require test update.

## Test Signals
Pass is expected map/unmap success or failure per mode and no leaked mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_dma_mapping_mmio_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_dma_mapping_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_dma_mapping_test.c

## Purpose
Tests VFIO DMA map/unmap behavior for anonymous and hugepage memory, IOVA range limits, unmap_all, overflow, and optional Intel debugfs page-table validation.

## Important APIs, Types, and Functions
parse_next_value, intel_iommu_mapping_get, iommu_mapping_get, dma_map_unmap, unmap_range, unmap_all, overflow.

## Control Flow
For each IOMMU mode and memory size, mmaps memory, allocates IOVA, maps it, verifies hva2iova, optionally reads Intel debugfs domain_translation_struct to confirm page-table level, unmaps and checks removal; limit fixture maps near last IOVA and tests overflow handling.

## State and Persistence
Creates anonymous/hugetlb mappings and IOMMU mappings; reads debugfs but does not persist data.

## Dependencies and Integration Points
Depends on libvfio, VFIO device, /sys/kernel/debug/iommu/intel for page-size introspection when available, and HugeTLB availability for huge variants.

## Risks and Edge Cases
Hugepage variants skip if pages are unavailable; debugfs parser is Intel-specific and format-sensitive.

## Test Signals
Pass means map/unmap sizes match, IOVA translation is tracked/removed, overflow returns -EOVERFLOW, and page-table level matches mapping size when checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_dma_mapping_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_iommufd_setup_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_iommufd_setup_test.c

## Purpose
Validates the VFIO device cdev iommufd setup ioctls and expected failure cases.

## Important APIs, Types, and Functions
vfio_device_bind_iommufd_ioctl, get_info, ioas_alloc, attach_iommufd_pt, detach_iommufd_pt; TEST_F bind/get_info_without_bind/repeated/attach.

## Control Flow
Finds the vfio cdev path for a BDF, opens cdev and /dev/iommu per fixture, verifies bind then get_info succeeds, get_info before bind fails, bad/repeated bind fails, attach/detach to a real IOAS works, and invalid pt attach fails.

## State and Persistence
Uses per-test fds only; allocates IOAS in iommufd during attach test.

## Dependencies and Integration Points
Depends on vfio-pci cdev support, /dev/iommu, libvfio cdev path discovery, and kselftest harness.

## Risks and Edge Cases
Requires device already bound to vfio-pci with cdev exposed; typo in test name attach_detatch_pt is cosmetic.

## Test Signals
Pass is expected ioctl success/failure for each fixture case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_iommufd_setup_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_pci_device_init_perf_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_pci_device_init_perf_test.c

## Purpose
Measures parallel VFIO PCI device initialization latency across one or more BDFs and all IOMMU modes.

## Important APIs, Types, and Functions
thread_main, timespec helpers, fixture with pthread_barrier, TEST_F init.

## Control Flow
Parses multiple BDFs, initializes one shared IOMMU, starts one thread per device behind a barrier, times vfio_pci_device_init per thread, joins, cleans devices, and prints wall/min/max/avg timing.

## State and Persistence
Creates threads, a barrier, one shared IOMMU, and transient VFIO device objects.

## Dependencies and Integration Points
Depends on pthreads, libvfio, multiple prepared devices for useful measurements, and kselftest harness.

## Risks and Edge Cases
This is performance/reporting, not pass/fail threshold; shared IOMMU setup races are intentionally allowed by libvfio container setup.

## Test Signals
Signal is printed timing data with successful device init/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_pci_device_init_perf_test.c -->
