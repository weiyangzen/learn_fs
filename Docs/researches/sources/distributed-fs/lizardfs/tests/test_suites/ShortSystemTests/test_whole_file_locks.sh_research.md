<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_whole_file_locks.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_whole_file_locks.sh

Purpose: validates whole-file flock and POSIX-style lock behavior plus admin manage-locks listing and forced unlock operations.

Important APIs, functions, and commands: defines `test_locks`; uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_master_daemon`, `file-generate`, `assert_success`, `assert_equals`, `assert_eventually_prints`; drives configuration through `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "${info[mount0]}/dir"`; `FILE_SIZE="$size" assert_success file-generate "${info[mount0]}/dir/file_$size"`; `function assert_operation_performed() {`; `assert_eventually_prints "$1" "sed -n ${opcount}p ${logfile}"`; `assert_operation_performed "read open: $1"`.

State and persistence behavior: State and persistence under test include active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; daemon kill/stop paths can leave stale state if readiness checks are wrong; lock tests risk stale owners or blocked helper processes. Test signals: hard assertions, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_whole_file_locks.sh -->
