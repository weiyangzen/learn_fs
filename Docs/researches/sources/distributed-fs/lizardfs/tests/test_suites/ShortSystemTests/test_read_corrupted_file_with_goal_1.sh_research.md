<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_corrupted_file_with_goal_1.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_corrupted_file_with_goal_1.sh

Purpose: corrupts a single-copy file and verifies reads surface failure rather than silently returning invalid data.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `find_chunkserver_chunks`, `file-generate`, `file-validate`, `dd`; drives configuration through `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `USE_RAMDISK`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `FILE_SIZE=1234567 file-generate file`; `find_chunkserver_chunks 0 | xargs -d'\n' -IXX \`; `if timeout -s KILL 3s file-validate file; then`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `USE_RAMDISK`, `FILE_SIZE`.

Risks and test signals: Risks: daemon kill/stop paths can leave stale state if readiness checks are wrong. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_corrupted_file_with_goal_1.sh -->
