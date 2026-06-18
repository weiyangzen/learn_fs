<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_recovery.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_recovery.sh

Purpose: kills the master after broad metadata generation, reconstructs metadata from changelogs with mfsmetarestore, and verifies printed metadata and file contents survive.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_master_daemon`, `lizardfs_metalogger_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `mfsmetarestore`, `metadata_print`, `metadata_generate_all`, `metadata_validate_files`, `assert_success`; drives configuration through `MAGIC_DISABLE_METADATA_DUMPS`, `AUTO_RECOVERY`, `EMPTY_TRASH_PERIOD`, `EMPTY_RESERVED_INODES_PERIOD`, `CHUNKSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_0_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `MFSEXPORTS_EXTRA_OPTIONS`, ....

Control flow: The script proceeds through these visible steps: `master_cfg="MAGIC_DISABLE_METADATA_DUMPS = 1"`; `master_cfg+="|AUTO_RECOVERY = 1"`; `master_cfg+="|EMPTY_TRASH_PERIOD = 1"`; `master_cfg+="|EMPTY_RESERVED_INODES_PERIOD = 1"`; `MASTER_EXTRA_CONFIG="$master_cfg" \`; `DEBUG_LOG_FAIL_ON="master.fs.checksum.mismatch" \`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, quota counters and limits, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MAGIC_DISABLE_METADATA_DUMPS`, `AUTO_RECOVERY`, `EMPTY_TRASH_PERIOD`, `EMPTY_RESERVED_INODES_PERIOD`, `CHUNKSERVERS`, `MOUNTS`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong; checksum assertions can miss bugs if corruption/recalculation timing is not exercised; quota accounting risks off-by-one and soft/hard-limit drift. Test signals: hard assertions, metadata diff checks, restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_recovery.sh -->
