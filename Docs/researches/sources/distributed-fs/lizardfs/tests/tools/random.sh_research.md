<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/random.sh -->
# sources/distributed-fs/lizardfs/tests/tools/random.sh

Purpose: provides LizardFS test harness coverage for random.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: `parse_si_suffix`, `random`, `unique_file`, `pseudorandom_init`, `prng`, `pseudorandom`, and subset helpers provide deterministic and nondeterministic data generation.

Control flow: Control flow is linear and sourced by the surrounding LizardFS test runner; it sets up prerequisites, executes the target scenario, then relies on assertions to signal failure.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `python3`, `tee`.

Risks and test signals: Risks: randomized paths need deterministic validation to avoid irreproducible failures. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/random.sh -->
