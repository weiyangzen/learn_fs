<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/asserts.h -->
# sources/distributed-fs/lizardfs/utils/asserts.h

Purpose: defines lightweight C/C++ assertion macros for utility binaries, reporting failed conditions or mismatched values with file and line context before aborting.

Important APIs, functions, and commands: is primarily declarative or command-oriented with no reusable functions.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the surrounding bash test runner and installed LizardFS utilities.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/asserts.h -->
