<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metarestore_disable_metadata_checksum_verification.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metarestore_disable_metadata_checksum_verification.sh

Purpose: corrupts the metadata checksum and proves mfsmetarestore fails normally but succeeds when checksum verification is explicitly disabled.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `mfsmetarestore`, `assert_success`, `assert_failure`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `METADATA_CHECKSUM_FREQUENCY`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `changelog_file="${info[master_data_path]}/changelog.mfs"`; `lizardfs_master_daemon kill`; `assert_failure mfsmetarestore -a -d "${info[master_data_path]}"`; `assert_success mfsmetarestore -z -a -d "${info[master_data_path]}"`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `METADATA_CHECKSUM_FREQUENCY`.

Risks and test signals: Risks: daemon kill/stop paths can leave stale state if readiness checks are wrong; checksum assertions can miss bugs if corruption/recalculation timing is not exercised; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, restore exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metarestore_disable_metadata_checksum_verification.sh -->
