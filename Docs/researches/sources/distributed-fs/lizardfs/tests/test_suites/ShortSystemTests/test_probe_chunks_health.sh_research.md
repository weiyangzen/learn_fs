<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_chunks_health.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_chunks_health.sh

Purpose: validates lizardfs-probe chunks-health output across available, undergoal, endangered, lost, replicate, and delete classes as chunkservers are stopped.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `find_first_chunkserver_with_chunks_matching`, `expect_equals`, `expect_awk_finds`, `expect_awk_finds_no`, `lizardfs {fileinfo, setgoal}`; drives configuration through `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir_$goal`; `lizardfs setgoal $goal dir_$goal`; `export MESSAGE="Veryfing health report with all the chunkservers up"`; `expect_equals 4 $(awk '/AVA/ {chunks += ($3 + $4 + $5)} END {print chunks}' <<< "$health4")`; `expect_awk_finds "/AVA $goal 1 0 0/" "$health4"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `MESSAGE`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: soft expectation accumulation, probe health output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_chunks_health.sh -->
