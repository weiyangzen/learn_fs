<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_master_stop_during_dumping.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_master_stop_during_dumping.sh

Purpose: ensures the master can stop cleanly while an asynchronous background metadata dump is blocked inside the configured metarestore wrapper.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_master_daemon`, `mfsmetarestore`, `assert_success`, `assert_eventually`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mfsmetarestore "\$@"`; `assert_success lizardfs_admin_master save-metadata --async`; `assert_eventually 'test -e $TEMP_DIR/dump_started'`; `lizardfs_master_daemon stop`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; background jobs require reliable cleanup and freeze signaling; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_master_stop_during_dumping.sh -->
