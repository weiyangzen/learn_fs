<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate_xor_with_not_enough_copies.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate_xor_with_not_enough_copies.sh

Purpose: checks writes and truncates fail cleanly when an EC/XOR-style file lacks enough available parts.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `truncate`, `dd`, `assert_success`, `assert_failure`, `assert_equals`, `lizardfs {fileinfo, setgoal}`; drives configuration through `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `MASTER_CUSTOM_GOALS`, `USE_RAMDISK`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir`; `lizardfs setgoal ec31 dir`; `lizardfs_chunkserver_daemon 0 stop`; `lizardfs_chunkserver_daemon 1 stop`; `lizardfs_wait_for_ready_chunkservers 2`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `MASTER_CUSTOM_GOALS`, `USE_RAMDISK`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: hard assertions, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_truncate_xor_with_not_enough_copies.sh -->
