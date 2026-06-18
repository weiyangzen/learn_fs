<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_connects_during_dumping.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_connects_during_dumping.sh

Purpose: connects a shadow while the master is dumping metadata to verify synchronization does not race a partial dump.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `mfsmetarestore`, `assert_eventually`; drives configuration through `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`, `MAGIC_DISABLE_METADATA_DUMPS`, `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `master_cfg="MFSMETARESTORE_PATH = $TEMP_DIR/metarestore.sh"`; `master_cfg+="|MAGIC_PREFER_BACKGROUND_DUMP = 1"`; `master_cfg+="|MAGIC_DISABLE_METADATA_DUMPS = 1"`; `MASTER_EXTRA_CONFIG="$master_cfg" \`; `setup_local_empty_lizardfs info`; `lizardfs_admin_master save-metadata --async # Start dumping metadata`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MFSMETARESTORE_PATH`, `MAGIC_PREFER_BACKGROUND_DUMP`, `MAGIC_DISABLE_METADATA_DUMPS`, `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; background jobs require reliable cleanup and freeze signaling; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_connects_during_dumping.sh -->
