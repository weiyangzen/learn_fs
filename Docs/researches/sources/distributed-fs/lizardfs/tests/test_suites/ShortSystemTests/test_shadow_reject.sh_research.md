<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reject.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reject.sh

Purpose: checks rejection paths for invalid or incompatible shadow-master connections.

Important APIs, functions, and commands: defines `my_client`, `run_my_client`; uses `setup_local_empty_lizardfs`, `lizardfs_admin_shadow`, `lizardfs_master_daemon`, `lizardfs_master_n`, `lizardfs_shadow_synchronized`, `assert_success`, `assert_failure`, `assert_equals`, `assert_eventually`; drives configuration through `MASTERSERVERS`, `USE_RAMDISK`, `PORT`.

Control flow: The script proceeds through these visible steps: `assert_program_installed nc`; `setup_local_empty_lizardfs info`; `lizardfs_master_n 1 start`; `assert_eventually 'lizardfs_shadow_synchronized 1'`; `local PORT=${info[master${1}_${2}]}`; `assert_equals "$expected_status" `cat ${TEMP_DIR}/${ma_to_someone}_exit_status || echo 1``.

State and persistence behavior: State and persistence under test include metadata files/changelogs, shadow-master synchronization state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MASTERSERVERS`, `USE_RAMDISK`, `PORT`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_shadow_reject.sh -->
