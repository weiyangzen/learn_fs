<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_sessions.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_sessions.sh

Purpose: verifies client session state visible through master/shadow failover and synchronization paths.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `lizardfs_master_n`, `lizardfs_wait_for_all_ready_chunkservers`, `lizardfs_mount_unmount`, `lizardfs_mount_start`, `metadata_print`, `metadata_get_all_generators`, `metadata_validate_files`, `assert_success`, `assert_failure`, `assert_equals`, ...; drives configuration through `MOUNTS`, `MASTERSERVERS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MOUNT_0_EXTRA_EXPORTS`, `MOUNT_1_EXTRA_EXPORTS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "${info[mount1]}/subdir"`; `lizardfs_mount_unmount 1`; `lizardfs_mount_start 1`; `lizardfs_master_n 1 start`; `for generator in $(metadata_get_all_generators |grep -v metadata_generate_uids_gids); do`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, quota counters and limits, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MOUNTS`, `MASTERSERVERS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MOUNT_0_EXTRA_EXPORTS`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong; quota accounting risks off-by-one and soft/hard-limit drift; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, metadata diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_sessions.sh -->
