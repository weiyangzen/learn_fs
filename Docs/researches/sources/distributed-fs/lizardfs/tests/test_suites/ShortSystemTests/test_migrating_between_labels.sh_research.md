<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_migrating_between_labels.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_migrating_between_labels.sh

Purpose: checks chunk migration between labeled hdd/flop/ssd chunkserver groups after changing goals and restarting previously stopped servers.

Important APIs, functions, and commands: defines `count_chunks_on_chunkservers`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `find_all_chunks`, `find_chunkserver_chunks`, `file-generate`, `assert_eventually_prints`, `expect_eventually_prints`, `lizardfs {setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `CHUNKS_SOFT_DEL_LIMIT`, `CHUNKS_WRITE_REP_LIMIT`, `OPERATIONS_DELAY_INIT`, ....

Control flow: The script proceeds through these visible steps: `count_chunks_on_chunkservers() {`; `find_chunkserver_chunks $i`; `setup_local_empty_lizardfs info`; `lizardfs_chunkserver_daemon $i stop &`; `lizardfs_wait_for_ready_chunkservers 3`; `mkdir dir`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions, soft expectation accumulation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_migrating_between_labels.sh -->
