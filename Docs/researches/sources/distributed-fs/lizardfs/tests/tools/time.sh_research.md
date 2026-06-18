<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/time.sh -->
# sources/distributed-fs/lizardfs/tests/tools/time.sh

Purpose: provides LizardFS test harness coverage for time.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `timestamp`, `nanostamp`, `wait_for`, `execution_time`.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the surrounding bash test runner and installed LizardFS utilities.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/time.sh -->
