<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_file_lock.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_file_lock.sh

Purpose: validates that metadata files are locked so live masters block unsafe metarestore and conflicting shadow startup, while stopped daemons allow recovery.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `lizardfs_master_n`, `mfsmetarestore`, `assert_success`, `assert_failure`; drives configuration through `USE_RAMDISK`, `MASTERSERVERS`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_failure mfsmetarestore -a -d "${info[master_data_path]}"`; `assert_success lizardfs_master_daemon kill`; `assert_success mfsmetarestore -a -d "${info[master_data_path]}"`; `assert_success lizardfs_master_daemon start`; `assert_success lizardfs_master_n 1 stop`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MASTERSERVERS`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`.

Risks and test signals: Risks: daemon kill/stop paths can leave stale state if readiness checks are wrong; lock tests risk stale owners or blocked helper processes; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_file_lock.sh -->
