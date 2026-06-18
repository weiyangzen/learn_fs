<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metarestore_autorecovery_metadata_version.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metarestore_autorecovery_metadata_version.sh

Purpose: verifies auto-recovery preserves or reconstructs the on-disk metadata version after normal save, changelog-only recovery, and deleted metadata cases.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_admin_master`, `lizardfs_probe_master`, `lizardfs_master_daemon`, `mfsmetarestore`, `file-generate`, `assert_success`, `assert_equals`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`, `BACK_META_KEEP_PREVIOUS`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `changelog_file="${info[master_data_path]}/changelog.mfs"`; `FILE_SIZE=1K assert_success file-generate "${info[mount0]}"/file_${i}_{1..10}`; `assert_success lizardfs_admin_master save-metadata`; `latest_metadata_version=$(lizardfs_probe_master metadataserver-status | cut -f3)`; `on_disk_metadata_version=$(mfsmetarestore -g -d "${info[master_data_path]}")`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`, `BACK_META_KEEP_PREVIOUS`, `FILE_SIZE`.

Risks and test signals: Risks: daemon kill/stop paths can leave stale state if readiness checks are wrong; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metarestore_autorecovery_metadata_version.sh -->
