<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_snapshot_goal.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_snapshot_goal.sh

Purpose: checks snapshot goal behavior and chunk placement across labeled server groups and recursive snapshot scenarios.

Important APIs, functions, and commands: defines `chunks_state`; uses `setup_local_empty_lizardfs`, `find_all_chunks`, `file-generate`, `file-validate`, `assert_success`, `assert_failure`, `assert_equals`, `assert_eventually_prints`, `lizardfs {makesnapshot, setgoal, settrashtime}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `ACCEPTABLE_DIFFERENCE`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `OPERATIONS_DELAY_INIT`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs setgoal 4 file`; `FILE_SIZE=$((1000 + LIZARDFS_CHUNK_SIZE)) file-generate file`; `assert_success file-validate file`; `assert_equals "8 standard" "$(chunks_state)"`; `lizardfs makesnapshot file file_snapshot1`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `ACCEPTABLE_DIFFERENCE`, `CHUNKS_LOOP_MIN_TIME`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: hard assertions, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_snapshot_goal.sh -->
