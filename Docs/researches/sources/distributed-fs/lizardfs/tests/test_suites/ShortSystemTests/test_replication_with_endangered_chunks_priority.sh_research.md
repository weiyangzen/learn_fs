<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_with_endangered_chunks_priority.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_with_endangered_chunks_priority.sh

Purpose: verifies endangered chunks are replicated before less urgent undergoal chunks when priority is enabled.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `find_all_chunks`, `find_chunkserver_chunks`, `file-generate`, `assert_equals`, `assert_eventually_prints`, `lizardfs {checkfile}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `ACCEPTABLE_DIFFERENCE`, `CHUNKS_WRITE_REP_LIMIT`, `OPERATIONS_DELAY_INIT`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs_chunkserver_daemon 1 stop`; `lizardfs_chunkserver_daemon 2 stop`; `lizardfs_wait_for_ready_chunkservers 2`; `FILE_SIZE=1K file-generate "${info[mount0]}"/file{1..20}`; `assert_equals 20 $(lizardfs checkfile "${info[mount0]}"/* | grep 'with 2 copies: *1' | wc -l)`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_with_endangered_chunks_priority.sh -->
