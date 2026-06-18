<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reloading_metadata.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reloading_metadata.sh

Purpose: checks shadow behavior while metadata is reloaded and changed on the master.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `lizardfs_master_n`, `lizardfs_wait_for_all_ready_chunkservers`, `lizardfs_shadow_synchronized`, `metadata_print`, `assert_eventually`; drives configuration through `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MASTER_EXTRA_CONFIG`, `MASTER_TIMEOUT`, `MAGIC_DISABLE_METADATA_DUMPS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs_master_n 1 start`; `assert_eventually "lizardfs_shadow_synchronized 1"`; `shadow_pid=$(lizardfs_master_n 1 test 2>&1 | sed 's/.*: //')`; `assert_matches "^[0-9]+$" "$shadow_pid"`; `lizardfs_master_daemon restart`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MASTER_EXTRA_CONFIG`, `MASTER_TIMEOUT`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong; quota accounting risks off-by-one and soft/hard-limit drift. Test signals: hard assertions, metadata diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reloading_metadata.sh -->
