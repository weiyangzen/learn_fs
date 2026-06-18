<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_chunks_health_custom_goals.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_chunks_health_custom_goals.sh

Purpose: validates lizardfs-probe chunks-health output across available, undergoal, endangered, lost, replicate, and delete classes as chunkservers are stopped.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `expect_equals`, `assert_eventually_prints`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `MOUNT_EXTRA_CONFIG`, `MASTER_CUSTOM_GOALS`, `USE_RAMDISK`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs setgoal $goal file_$goal`; `expect_equals "$first_output" "$(chunks-health-trimmed)"`; `lizardfs setgoal ${new_goal} file_*`; `expect_equals "${output[$new_goal]}" "$(chunks-health-trimmed)"`; `lizardfs setgoal ${old_goal} file_${old_goal}`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `MOUNT_EXTRA_CONFIG`, `MASTER_CUSTOM_GOALS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions, soft expectation accumulation, probe health output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_chunks_health_custom_goals.sh -->
