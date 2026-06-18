<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_chunkservers.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_chunkservers.sh

Purpose: checks list-chunkservers porcelain fields, labels, used space, connection state, and version reporting.

Important APIs, functions, and commands: defines `list_chunkservers`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `expect_equals`, `expect_eventually_prints`, `expect_awk_finds_no`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir_$goal`; `lizardfs setgoal $goal dir_$goal`; `list_chunkservers() {`; `lizardfs-probe list-chunkservers --porcelain localhost "${info[matocl]}"`; `export MESSAGE="Veryfing chunkservers list with all the chunkservers up"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: soft expectation accumulation, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_chunkservers.sh -->
