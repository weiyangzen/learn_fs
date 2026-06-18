<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_metadataservers.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_metadataservers.sh

Purpose: checks list-metadataservers output for master and shadow rows and synchronization status.

Important APIs, functions, and commands: defines `list_metadata_servers`; uses `setup_local_empty_lizardfs`, `lizardfs_probe_master`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `assert_equals`, `assert_eventually`, `assert_eventually_prints`; drives configuration through `USE_RAMDISK`, `MASTERSERVERS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `list_metadata_servers() {`; `lizardfs_probe_master list-metadataservers --porcelain`; `master_expected_state="^$ip ${info[matocl]} $host master running $meta $version\$"`; `shadow_expected_state="^$ip ${info[master1_matocl]} $host shadow connected $meta $version\$"`; `assert_matches "$master_expected_state" "$(list_metadata_servers)"`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MASTERSERVERS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_metadataservers.sh -->
