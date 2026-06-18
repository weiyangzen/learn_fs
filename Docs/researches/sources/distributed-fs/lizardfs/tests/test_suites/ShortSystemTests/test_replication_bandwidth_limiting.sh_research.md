<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_bandwidth_limiting.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_bandwidth_limiting.sh

Purpose: verifies replication bandwidth limiting by measuring replication progress for many chunks under a small limit.

Important APIs, functions, and commands: defines `chunks_health`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `find_chunkserver_chunks`, `file-generate`, `assert_success`, `assert_equals`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `CHUNKSERVER_EXTRA_CONFIG`, `REPLICATION_BANDWIDTH_LIMIT_KBPS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `CHUNKS_WRITE_REP_LIMIT`, `CHUNKS_READ_REP_LIMIT`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir`; `lizardfs setgoal 2 dir`; `FILE_SIZE=${file_size_kb}K file-generate $(seq 1 $chunks_count)`; `assert_equals $chunks_count $(find_chunkserver_chunks 0 | wc -l)`; `lizardfs_chunkserver_daemon 0 stop`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `CHUNKSERVER_EXTRA_CONFIG`, `REPLICATION_BANDWIDTH_LIMIT_KBPS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions, probe health output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_replication_bandwidth_limiting.sh -->
