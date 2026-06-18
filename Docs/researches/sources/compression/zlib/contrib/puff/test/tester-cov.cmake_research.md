# sources/compression/zlib/contrib/puff/test/tester-cov.cmake

Purpose: CMake script that drives coverage-oriented puff runtime tests using crafted raw DEFLATE byte streams and expected process exit codes.

Important APIs, types, and functions: Defines `puff_cov_test(test_string expected_result)`, using `execute_process` with `cmake -E echo_append` piped through a binary writer and then into the coverage executable. It also invokes gcov at the end.

Control flow: The script first runs the coverage executable with `-w` on `zeros.raw`, then checks many malformed or edge-case streams with expected returns such as `2`, `254`, `249`, and other shell-mapped negative puff codes. It switches to `-f` mode to exercise output exhaustion and finalizes by running gcov on `puff.c.gcno`.

State and persistence: Generates coverage data files in the test working directory and relies on executable exit statuses. No CMake cache mutations are made.

Dependencies and integration points: Called by `puff/test/CMakeLists.txt` coverage tests. Requires the puff coverage executable, source directory, binary writer executable, and gcov executable arguments.

Risks: Negative C return codes are observed as platform-specific process codes, so expected values can be sensitive to shell/OS conventions. The argument comments are stale relative to actual argument use, increasing maintenance risk.

Test signals: Strongly exercises rare branches in `stored()`, `dynamic()`, `codes()`, EOF handling, invalid block types, output exhaustion, and gcov report generation.
