<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/stack_trace.sh -->
# sources/distributed-fs/lizardfs/tests/tools/stack_trace.sh

Purpose: provides LizardFS test harness coverage for stack_trace.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `get_stack`, `print_stack`; drives configuration through `STACK`, `IFS`.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `STACK`, `IFS`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/stack_trace.sh -->
