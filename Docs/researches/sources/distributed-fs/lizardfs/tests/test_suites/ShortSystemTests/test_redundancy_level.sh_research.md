<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_redundancy_level.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_redundancy_level.sh

Purpose: checks minimum ready chunkserver requirements for standard, XOR, and EC goals as servers are stopped and restarted.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_master_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `file-generate`, `dd`, `assert_success`, `assert_failure`, `lizardfs {setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `REDUNDANCY_LEVEL`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs_chunkserver_daemon 0 stop`; `mkdir ec_dir xor4_dir std5_dir xor3_dir`; `lizardfs setgoal ec32 ec_dir`; `lizardfs setgoal xor3 xor3_dir`; `lizardfs setgoal xor4 xor4_dir`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `REDUNDANCY_LEVEL`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_redundancy_level.sh -->
