<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/string.sh -->
# sources/distributed-fs/lizardfs/tests/tools/string.sh

Purpose: provides LizardFS test harness coverage for string.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `version_compare_gte`.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the surrounding bash test runner and installed LizardFS utilities.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/string.sh -->
