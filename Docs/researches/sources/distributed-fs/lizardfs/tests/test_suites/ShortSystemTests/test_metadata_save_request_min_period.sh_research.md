<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_save_request_min_period.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_save_request_min_period.sh

Purpose: checks shadow synchronization behavior when master save requests are throttled by METADATA_SAVE_REQUEST_MIN_PERIOD and mismatch logs should be delayed or immediate.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `truncate`, `assert_failure`, `assert_eventually`, `assert_awk_finds`, `assert_awk_finds_no`; drives configuration through `MAGIC_DISABLE_METADATA_DUMPS`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`, `METADATA_SAVE_REQUEST_MIN_PERIOD`, `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `DEBUG_LOG_DISABLE_FAIL_ON`.

Control flow: The script proceeds through these visible steps: `master_cfg="MAGIC_DISABLE_METADATA_DUMPS = 1"`; `master_cfg+="|MAGIC_DEBUG_LOG = ${TEMP_DIR}/log|LOG_FLUSH_ON=DEBUG"`; `master_cfg+="|METADATA_SAVE_REQUEST_MIN_PERIOD = $(timeout_rescale_seconds 10)"`; `MASTER_EXTRA_CONFIG="$master_cfg" \`; `DEBUG_LOG_DISABLE_FAIL_ON="master.mismatch" \`; `setup_local_empty_lizardfs info`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MAGIC_DISABLE_METADATA_DUMPS`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`, `METADATA_SAVE_REQUEST_MIN_PERIOD`, `CHUNKSERVERS`, `MASTERSERVERS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_save_request_min_period.sh -->
