<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_master_noatime.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_master_noatime.sh

Purpose: checks that master ACCESS changelog entries are produced for reads by default and stop after NO_ATIME is enabled through a live reload.

Important APIs, functions, and commands: defines `count_accesses`; uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `assert_equals`; drives configuration through `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`, `MOUNT_EXTRA_CONFIG`, `NO_ATIME`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `grep -c -w ACCESS "${info[master_data_path]}"/changelog.mfs || true`; `assert_equals $((2 * i)) $(count_accesses)`; `echo "NO_ATIME = 1" >> "${info[master_cfg]}"`; `lizardfs_master_daemon reload`; `assert_eventually_matches main.reload 'cat "${TEMP_DIR}/reloads"'`.

State and persistence behavior: State and persistence under test include client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`, `MOUNT_EXTRA_CONFIG`, `NO_ATIME`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_master_noatime.sh -->
