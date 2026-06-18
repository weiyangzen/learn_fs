<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pwrite_eio_nonheader_in_chunkserver.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pwrite_eio_nonheader_in_chunkserver.sh

Purpose: injects write EIO outside chunk headers and verifies only affected large writes are classified and repaired.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_probe_master`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `file-generate`, `assert_success`, `assert_equals`, `assert_eventually_prints`, `assert_awk_finds_no`, `lizardfs {fileinfo, setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `CHUNKSERVER_0_DISK_0`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `ACCEPTABLE_DIFFERENCE`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_success lizardfs_chunkserver_daemon 0 restart`; `lizardfs_wait_for_all_ready_chunkservers`; `mkdir test`; `lizardfs setgoal 2 test`; `FILE_SIZE=1234 assert_success file-generate test/small_{1..20}`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `CHUNKSERVER_0_DISK_0`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; EIO injection depends on chunk-file naming and disk health classification. Test signals: hard assertions, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pwrite_eio_nonheader_in_chunkserver.sh -->
