<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/filter_tests.py -->
# sources/distributed-fs/lizardfs/tests/tools/filter_tests.py

Purpose: partitions GoogleTest-style LizardFS test cases across CI nodes using stored duration data and explicit exclusions so concurrent runs have roughly balanced wall time.

Important APIs, functions, and commands: defines `get_excluded_tests_two_types`, `get_gtest_testlist`, `get_data_testlist`, `get_tests_list_with_durations`, `add_to_partition_dict`, `partition_algorithm`, `print_tests_to_run`, `get_tests_data`; uses `lizardfs {test}`.

Control flow: Control flow parses command-line arguments, loads or computes the requested data, validates input consistency, then prints machine-readable output or exits nonzero on invalid input.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `python3`, Python standard library, LizardFS CLI/test helpers.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/filter_tests.py -->
