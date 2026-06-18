<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multiple_master_promotions.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multiple_master_promotions.sh

Purpose: promotes multiple shadow masters in sequence and verifies metadata equality after each promotion/reconfiguration cycle.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `lizardfs_master_n`, `lizardfs_wait_for_all_ready_chunkservers`, `lizardfs_shadow_synchronized`, `metadata_print`, `assert_eventually`; drives configuration through `MASTERSERVERS`, `USE_RAMDISK`, `CHUNKSERVER_EXTRA_CONFIG`, `MASTER_RECONNECTION_DELAY`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs_master_n $shadow_id start`; `assert_eventually "lizardfs_shadow_synchronized $shadow_id"`; `touch "${info[mount0]}"/"master=$loop_nr"`; `metadata=$(metadata_print "${info[mount0]}")`; `prev_master_id=$((loop_nr % metaservers_nr))`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MASTERSERVERS`, `USE_RAMDISK`, `CHUNKSERVER_EXTRA_CONFIG`, `MASTER_RECONNECTION_DELAY`, `MFSEXPORTS_EXTRA_OPTIONS`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; daemon kill/stop paths can leave stale state if readiness checks are wrong; quota accounting risks off-by-one and soft/hard-limit drift; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, metadata diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_multiple_master_promotions.sh -->
