<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/combinations.py -->
# sources/distributed-fs/lizardfs/tests/tools/combinations.py

Purpose: generates bash-readable combinations and random subset selections for erasure-code and lost-part brute-force tests.

Important APIs, functions, and commands: defines `binomial`, `ith_combination_of_fixed_size`, `random_subsets_of_fixed_size`, `all_combinations`, `selected_combinations`, `bashprint`, `print_random_subsets_of_fixed_size`, `print_all_combinations`, `print_selected_combinations`.

Control flow: Control flow parses command-line arguments, loads or computes the requested data, validates input consistency, then prints machine-readable output or exits nonzero on invalid input.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: Python standard library.

Risks and test signals: Risks: randomized paths need deterministic validation to avoid irreproducible failures. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/combinations.py -->
