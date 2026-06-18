<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_lizardfs_upgrade_undergoal_chunks.inc -->
# sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_lizardfs_upgrade_undergoal_chunks.inc

Purpose: upgrade template that creates undergoal chunks with a legacy version and validates current-version replication/recovery behavior after service upgrade.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_wait_for_all_ready_chunkservers`, `mfsmount`, `lizardfsXX`, `assert_success`; drives configuration through `CHUNKSERVERS_GOAL_COVER`, `CHUNKSERVERS_REDUNDANT`, `CHUNKSERVERS_MINIMUM`, `REPLICATION_SPEED`, `LZFS_MOUNT_COMMAND`, `CHUNKSERVERS`, `START_WITH_LEGACY_LIZARDFS`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `CREATE_NEW_CHUNKS_IN_MOOSEFS_FORMAT`, ....

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_lizardfsXX_services_count_equals 1 $CHUNKSERVERS_GOAL_COVER 1`; `stop_lizardfsXX_chunkservers_from_to $CHUNKSERVERS_MINIMUM $CHUNKSERVERS_GOAL_COVER`; `assert_lizardfsXX_services_count_equals 1 $CHUNKSERVERS_MINIMUM 1`; `mkdir dir`; `assert_success lizardfsXX mfssetgoal $GOAL dir`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS_GOAL_COVER`, `CHUNKSERVERS_REDUNDANT`, `CHUNKSERVERS_MINIMUM`, `REPLICATION_SPEED`, `LZFS_MOUNT_COMMAND`, `CHUNKSERVERS`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; upgrade tests depend on external package availability and version-specific behavior. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/TestTemplates/test_lizardfs_upgrade_undergoal_chunks.inc -->
