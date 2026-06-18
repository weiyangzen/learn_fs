<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multi_ec_write.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multi_ec_write.sh

Purpose: writes and overwrites a file while progressively stopping erasure-code data/parity chunkservers to validate EC write availability and failure boundaries.

Important APIs, functions, and commands: defines `for_chunkservers`; uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_ready_chunkservers`, `find_first_chunkserver_with_chunks_matching`, `file-overwrite`, `file-validate`, `dd`, `lizardfs {fileinfo, setgoal}`; drives configuration through `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `REPLICATIONS_DELAY_INIT`, `ACCEPTABLE_DIFFERENCE`, `DISABLE_CHUNKS_DEL`, `MASTER_CUSTOM_GOALS`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, ....

Control flow: The script proceeds through these visible steps: `for_chunkservers() {`; `lizardfs_chunkserver_daemon $csid "${operation}" &`; `nr_of_running_chunkservers=$((nr_of_running_chunkservers - $#))`; `nr_of_running_chunkservers=$((nr_of_running_chunkservers + $#))`; `lizardfs_wait_for_ready_chunkservers $nr_of_running_chunkservers`; `setup_local_empty_lizardfs info`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `REPLICATIONS_DELAY_INIT`, `ACCEPTABLE_DIFFERENCE`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed. Test signals: soft expectation accumulation, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multi_ec_write.sh -->
