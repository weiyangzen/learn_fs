<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_goal_with_labels.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_goal_with_labels.sh

Purpose: checks XOR goal placement with chunkserver labels and goal transitions across ssd/hdd/mixed labels.

Important APIs, functions, and commands: defines `chunks_state`, `count_chunks_on_chunkservers`; uses `setup_local_empty_lizardfs`, `find_all_chunks`, `find_chunkserver_chunks`, `file-generate`, `assert_equals`, `assert_eventually_prints`, `lizardfs {setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `CHUNKS_SOFT_DEL_LIMIT`, `CHUNKS_WRITE_REP_LIMIT`, `OPERATIONS_DELAY_INIT`, ....

Control flow: The script proceeds through these visible steps: `count_chunks_on_chunkservers() {`; `find_chunkserver_chunks $i`; `setup_local_empty_lizardfs info`; `mkdir dir`; `lizardfs setgoal xor2_ssd dir`; `FILE_SIZE=1K file-generate dir/file`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: hard assertions, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_goal_with_labels.sh -->
