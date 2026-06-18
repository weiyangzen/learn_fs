<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_metadata_generate.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_metadata_generate.sh

Purpose: generates broad metadata while a shadow is present and verifies the shadow stays synchronized and consistent.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `lizardfs_master_n`, `lizardfs_wait_for_all_ready_chunkservers`, `lizardfs_shadow_synchronized`, `metadata_print`, `metadata_generate_all`, `metadata_validate_files`, `assert_eventually`; drives configuration through `MAGIC_DISABLE_METADATA_DUMPS`, `CHUNKSERVERS`, `MASTERSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_0_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `MFSEXPORTS_EXTRA_OPTIONS`, `MFSEXPORTS_META_EXTRA_OPTIONS`, `MASTER_EXTRA_CONFIG`, ....

Control flow: The script proceeds through these visible steps: `master_cfg="MAGIC_DISABLE_METADATA_DUMPS = 1"`; `MASTER_EXTRA_CONFIG="$master_cfg" \`; `setup_local_empty_lizardfs info`; `export CHANGELOG="${info[master_data_path]}"/changelog.mfs`; `lizardfs_master_n 1 start`; `metadata_generate_all`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MAGIC_DISABLE_METADATA_DUMPS`, `CHUNKSERVERS`, `MASTERSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_0_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; daemon kill/stop paths can leave stale state if readiness checks are wrong; quota accounting risks off-by-one and soft/hard-limit drift; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, metadata diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_metadata_generate.sh -->
