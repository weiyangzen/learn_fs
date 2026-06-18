<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_checksum_error_recovery.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_checksum_error_recovery.sh

Purpose: checks that a shadow can recover from metadata checksum error conditions and resynchronize with the master.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `assert_success`, `assert_eventually`; drives configuration through `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`, `MAGIC_DEBUG_LOG`, `LOG_FLUSH_ON`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `sed -i 's/file/fool/g' "${info[master_data_path]}"/changelog.mfs`; `lizardfs_master_n 1 start`; `assert_eventually "lizardfs_shadow_synchronized 1"`; `assert_success awk '`; `/master.mismatch/ && i == 0 {i++; next;}`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state, chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MASTERSERVERS`, `USE_RAMDISK`, `MASTER_EXTRA_CONFIG`, `MAGIC_DISABLE_METADATA_DUMPS`, `MAGIC_DEBUG_LOG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; checksum assertions can miss bugs if corruption/recalculation timing is not exercised; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_checksum_error_recovery.sh -->
