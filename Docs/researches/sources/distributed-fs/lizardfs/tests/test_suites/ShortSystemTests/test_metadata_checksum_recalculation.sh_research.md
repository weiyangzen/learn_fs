<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_checksum_recalculation.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_checksum_recalculation.sh

Purpose: stress-tests metadata checksum recalculation while nodes, xattrs, chunks, and goals are being mutated concurrently.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `truncate`, `attr`, `assert_success`, `expect_eventually_prints`, `expect_awk_finds`, `lizardfs {setgoal}`; drives configuration through `MAGIC_DISABLE_METADATA_DUMPS`, `METADATA_CHECKSUM_RECALCULATION_SPEED`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `DEBUG_LOG_FAIL_ON`.

Control flow: The script proceeds through these visible steps: `assert_program_installed attr`; `master_cfg="MAGIC_DISABLE_METADATA_DUMPS = 1"`; `master_cfg+="|METADATA_CHECKSUM_RECALCULATION_SPEED = 1"`; `master_cfg+="|MAGIC_DEBUG_LOG = $TEMP_DIR/log|LOG_FLUSH_ON=DEBUG"`; `MASTER_EXTRA_CONFIG="$master_cfg" \`; `DEBUG_LOG_FAIL_ON="master.fs.checksum.mismatch" \`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, extended attributes, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `attr`, environment/config variables such as `MAGIC_DISABLE_METADATA_DUMPS`, `METADATA_CHECKSUM_RECALCULATION_SPEED`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`, `CHUNKSERVERS`, `USE_RAMDISK`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; background jobs require reliable cleanup and freeze signaling; checksum assertions can miss bugs if corruption/recalculation timing is not exercised; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, soft expectation accumulation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_checksum_recalculation.sh -->
