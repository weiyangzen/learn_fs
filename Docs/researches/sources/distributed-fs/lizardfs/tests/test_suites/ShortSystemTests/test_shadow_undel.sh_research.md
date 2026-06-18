<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_undel.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_undel.sh

Purpose: checks trash undel operations through a shadow-aware setup and verifies restored file contents.

Important APIs, functions, and commands: defines `stat_basic_info`, `only_file_in_trash`; uses `setup_local_empty_lizardfs`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `file-generate`, `file-validate`, `assert_success`, `assert_equals`, `assert_eventually`; drives configuration through `MAGIC_DISABLE_METADATA_DUMPS`, `AUTO_RECOVERY`, `CHUNKSERVERS`, `MASTERSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MOUNT_0_EXTRA_CONFIG`, `MOUNT_1_EXTRA_CONFIG`, `MFSEXPORTS_EXTRA_OPTIONS`, `MFSEXPORTS_META_EXTRA_OPTIONS`, ....

Control flow: The script proceeds through these visible steps: `master_cfg="MAGIC_DISABLE_METADATA_DUMPS = 1"`; `master_cfg+="|AUTO_RECOVERY = 1"`; `MASTER_EXTRA_CONFIG="$master_cfg" \`; `setup_local_empty_lizardfs info`; `assert_equals "1" "$(ls "$trash" | grep -v undel | wc -l)"`; `changelog_file="${info[master_data_path]}"/changelog.mfs`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, quota counters and limits, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MAGIC_DISABLE_METADATA_DUMPS`, `AUTO_RECOVERY`, `CHUNKSERVERS`, `MASTERSERVERS`, `MOUNTS`, `USE_RAMDISK`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; quota accounting risks off-by-one and soft/hard-limit drift; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, content validation, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_undel.sh -->
