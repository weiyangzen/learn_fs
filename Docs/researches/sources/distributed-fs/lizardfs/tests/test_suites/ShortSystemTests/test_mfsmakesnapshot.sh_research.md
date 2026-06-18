<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_mfsmakesnapshot.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_mfsmakesnapshot.sh

Purpose: covers snapshot creation and overwrite semantics for files and directories, including goals, trailing slashes, shared chunks, and recursive goal inheritance.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `find_all_chunks`, `assert_success`, `expect_equals`, `assert_equals`, `assert_eventually_prints`, `lizardfs {fileinfo, getgoal, makesnapshot, setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `OPERATIONS_DELAY_INIT`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir1`; `lizardfs setgoal $i dir1/file$i`; `assert_equals 5 $(find_all_chunks | wc -l) # First file has 2 chunks, the second one -- 3`; `assert_success lizardfs makesnapshot dir1 dir2`; `expect_equals "$(ls dir1 | sort)" "$(ls dir2 | sort)"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions, soft expectation accumulation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_mfsmakesnapshot.sh -->
