<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/continuous_test.sh -->
# sources/distributed-fs/lizardfs/tests/tools/continuous_test.sh

Purpose: provides LizardFS test harness coverage for continuous_test.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `continuous_test_begin`; uses `assert_success`.

Control flow: The script proceeds through these visible steps: `assert_success mfsdirinfo -h "${LIZARDFS_MOUNTPOINT:-}"`; `assert_success mkdir -p "$workspace"`.

State and persistence behavior: State and persistence under test include client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: LizardFS CLI/test helpers.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/continuous_test.sh -->
