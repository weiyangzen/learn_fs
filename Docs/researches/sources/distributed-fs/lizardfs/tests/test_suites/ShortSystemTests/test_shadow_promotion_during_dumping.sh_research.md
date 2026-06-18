<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_promotion_during_dumping.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_promotion_during_dumping.sh

Purpose: promotes a shadow while metadata dumping is in progress to validate promotion safety under dump races.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_shadow`, `lizardfs_master_daemon`, `lizardfs_master_n`, `lizardfs_wait_for_all_ready_chunkservers`, `lizardfs_shadow_synchronized`, `mfsmetarestore`, `metadata_print`, `assert_eventually`; drives configuration through `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`, `MAGIC_DISABLE_METADATA_DUMPS`, `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `master_cfg="MFSMETARESTORE_PATH = $TEMP_DIR/metarestore.sh"`; `master_cfg+="|MAGIC_PREFER_BACKGROUND_DUMP = 1"`; `master_cfg+="|MAGIC_DISABLE_METADATA_DUMPS = 1"`; `MASTER_EXTRA_CONFIG="$master_cfg" \`; `setup_local_empty_lizardfs info`; `mfsmetarestore "\$@"`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`, `MAGIC_DISABLE_METADATA_DUMPS`, `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; background jobs require reliable cleanup and freeze signaling; daemon kill/stop paths can leave stale state if readiness checks are wrong. Test signals: hard assertions, metadata diff checks, restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_promotion_during_dumping.sh -->
