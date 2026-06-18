<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate_retry.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate_retry.sh

Purpose: checks client truncate retry behavior when the only chunkserver is temporarily unavailable and when retry time is exceeded.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `file-generate`, `file-validate`, `truncate`, `assert_failure`, `assert_equals`, `assert_awk_finds`, `assert_awk_finds_no`, `lizardfs {fileinfo}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `FILE_SIZE=1234 file-generate file`; `lizardfs_chunkserver_daemon 0 stop`; `assert_awk_finds '/no valid copies/' "$(lizardfs fileinfo file)"`; `(sleep 3.1 && lizardfs_chunkserver_daemon 0 start) & truncate -s 123 file`; `assert_awk_finds '/[0-9A-F]+_00000002/' "$(lizardfs fileinfo file)"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; checksum assertions can miss bugs if corruption/recalculation timing is not exercised. Test signals: hard assertions, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate_retry.sh -->
