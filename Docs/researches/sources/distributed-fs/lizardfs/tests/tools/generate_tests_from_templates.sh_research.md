<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/generate_tests_from_templates.sh -->
# sources/distributed-fs/lizardfs/tests/tools/generate_tests_from_templates.sh

Purpose: provides LizardFS test harness coverage for generate_tests_from_templates.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: drives configuration through `CMAKE_DIRECTORY`.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `CMAKE_DIRECTORY`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/generate_tests_from_templates.sh -->
