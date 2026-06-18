<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_metadataserver_status.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_metadataserver_status.sh

Purpose: checks metadataserver-status porcelain output for the master version/state tuple.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_n`, `assert_equals`, `assert_eventually_prints`; drives configuration through `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `assert_eventually_prints $'master\trunning' \`; `changelog_version=$(tail -1 "${info[master_data_path]}"/changelog.mfs | grep -o '^[0-9]*')`; `assert_equals $version "$((changelog_version + 1))"`; `lizardfs_master_n 1 start`; `assert_eventually_prints $'shadow\tconnected\t'$version \`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_metadataserver_status.sh -->
