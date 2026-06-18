<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_readdir_faulty_master_parallel.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_readdir_faulty_master_parallel.sh

Purpose: runs parallel readdir workloads while the master is restarted or faulted to detect client directory-read races.

Important APIs, functions, and commands: defines `master_restarting_loop`, `thread`; uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `expect_equals`; drives configuration through `MASTER_RESTART_DELAY_SECS`, `READDIR_SLEEP_SECS`, `THREAD_COUNT`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNTS`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `master_restarting_loop() {`; `expect_success lizardfs_master_daemon restart`; `mkdir -p "$dir" && cd "$dir"`; `setup_local_empty_lizardfs info`; `master_restarting_loop 1 &`; `expect_equals $files_expected $files_iterated`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `python3`, environment/config variables such as `MASTER_RESTART_DELAY_SECS`, `READDIR_SLEEP_SECS`, `THREAD_COUNT`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNTS`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed. Test signals: soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_readdir_faulty_master_parallel.sh -->
