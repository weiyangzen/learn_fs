<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_in_chunkserver_all_disks.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_in_chunkserver_all_disks.sh

Purpose: marks all disks of a chunkserver as EIO and verifies reads avoid bad replicas, chunk health reports EIO, and replication restores clean copies elsewhere.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_probe_master`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `file-generate`, `file-validate`, `assert_success`, `assert_equals`, `assert_eventually_prints`, `assert_awk_finds_no`, `lizardfs {fileinfo, setgoal}`; drives configuration through `USE_RAMDISK`, `MOUNTS`, `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`, `CHUNKSERVER_0_DISK_0`, `CHUNKSERVER_0_DISK_1`, `CHUNKSERVER_0_DISK_2`, `MOUNT_EXTRA_CONFIG`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir goal2`; `lizardfs setgoal 2 goal2`; `FILE_SIZE=1234 file-generate goal2/small_{1..30}`; `FILE_SIZE=300K file-generate goal2/medium_{1..30}`; `FILE_SIZE=2M file-generate goal2/big_{1..30}`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MOUNTS`, `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `CHUNKSERVER_EXTRA_CONFIG`, `HDD_TEST_FREQ`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; EIO injection depends on chunk-file naming and disk health classification. Test signals: hard assertions, content validation, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_pread_eio_in_chunkserver_all_disks.sh -->
