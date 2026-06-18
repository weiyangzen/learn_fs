<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_synchronization.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_synchronization.sh

Purpose: checks baseline shadow synchronization over metadata changes and chunkserver availability changes.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `metadata_generate_all`, `assert_success`, `assert_equals`, `assert_eventually`; drives configuration through `MAGIC_DISABLE_METADATA_DUMPS`, `OPERATIONS_DELAY_INIT`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `BACK_META_KEEP_PREVIOUS`, `CHUNKSERVERS`, `MASTERSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_0_EXTRA_CONFIG`, ....

Control flow: The script proceeds through these visible steps: `master_cfg="MAGIC_DISABLE_METADATA_DUMPS = 1"`; `master_cfg+="|OPERATIONS_DELAY_INIT = 1"`; `master_cfg+="|CHUNKS_LOOP_MIN_TIME = 1|CHUNKS_LOOP_MAX_CPU = 90"`; `master_cfg+="|BACK_META_KEEP_PREVIOUS = 0"`; `MASTER_0_EXTRA_CONFIG="$master_cfg" \`; `DEBUG_LOG_FAIL_ON="master.matoml_changelog_apply_error" \`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, quota counters and limits, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MAGIC_DISABLE_METADATA_DUMPS`, `OPERATIONS_DELAY_INIT`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `BACK_META_KEEP_PREVIOUS`, `CHUNKSERVERS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; checksum assertions can miss bugs if corruption/recalculation timing is not exercised; quota accounting risks off-by-one and soft/hard-limit drift; lock tests risk stale owners or blocked helper processes. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_synchronization.sh -->
