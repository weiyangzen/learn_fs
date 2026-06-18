<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reconnect.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reconnect.sh

Purpose: restarts or disconnects a shadow and verifies it resynchronizes after reconnect.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `assert_equals`, `assert_eventually`; drives configuration through `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MASTER_TIMEOUT`, `MAGIC_DISABLE_METADATA_DUMPS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs_master_n 1 start`; `assert_eventually "lizardfs_shadow_synchronized 1"`; `files_before=$(ls "${info[master1_data_path]}" | grep -v "stats.mfs" | sort)`; `shadow_pid=$(lizardfs_master_n 1 test 2>&1 | sed 's/.*: //')`; `assert_matches "^[0-9]+$" "$shadow_pid"`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MASTER_TIMEOUT`, `MAGIC_DISABLE_METADATA_DUMPS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reconnect.sh -->
