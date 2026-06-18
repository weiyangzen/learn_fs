<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_lizardfs_upgrade_overwrite_file.inc -->
# sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_lizardfs_upgrade_overwrite_file.inc

Purpose: upgrade template that starts with legacy LizardFS services, overwrites files during a staged upgrade to current binaries, and validates all files after chunkserver churn.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_chunkserver_daemon`, `lizardfs_master_daemon`, `lizardfs_wait_for_ready_chunkservers`, `lizardfs_mount_unmount`, `lizardfs_mount_start`, `mfsmount`, `lizardfsXX`, `lizardfsXX_chunkserver_daemon`, `assert_success`; drives configuration through `LZFS_MOUNT_COMMAND`, `CHUNKSERVERS`, `START_WITH_LEGACY_LIZARDFS`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `CREATE_NEW_CHUNKS_IN_MOOSEFS_FORMAT`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `OPERATIONS_DELAY_INIT`, `REPLICATION_SPEED`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_lizardfsXX_services_count_equals 1 ${CHUNKSERVERS} 1`; `mkdir dir`; `assert_success lizardfsXX mfssetgoal $GOAL dir`; `assert_success generate_files_various_filesizes file_count`; `lizardfsXX_chunkserver_daemon 0 stop`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `LZFS_MOUNT_COMMAND`, `CHUNKSERVERS`, `START_WITH_LEGACY_LIZARDFS`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `CREATE_NEW_CHUNKS_IN_MOOSEFS_FORMAT`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; upgrade tests depend on external package availability and version-specific behavior. Test signals: hard assertions, probe/admin porcelain output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_lizardfs_upgrade_overwrite_file.inc -->
