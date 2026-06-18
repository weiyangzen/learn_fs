<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_posix_file_locks.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_posix_file_locks.sh

Purpose: validates POSIX byte-range lock ordering, blocking, unlock, and close behavior with the posixlock helper.

Important APIs, functions, and commands: defines `assert_operation_performed`, `assert_operation_not_performed`, `readlock`, `writelock`, `unlock`; uses `setup_local_empty_lizardfs`, `file-generate`, `posixlockcmd`, `assert_success`, `assert_eventually_prints`; drives configuration through `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "${info[mount0]}/dir"`; `FILE_SIZE="$size" assert_success file-generate "${info[mount0]}/dir/file_$size"`; `function assert_operation_performed() {`; `assert_eventually_prints "$1" "sed -n ${opcount}p posixlock.log"`; `function assert_operation_not_performed() {`.

State and persistence behavior: State and persistence under test include active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; daemon kill/stop paths can leave stale state if readiness checks are wrong; lock tests risk stale owners or blocked helper processes. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_posix_file_locks.sh -->
