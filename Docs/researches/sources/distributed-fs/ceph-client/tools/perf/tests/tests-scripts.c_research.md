## sources/distributed-fs/ceph-client/tools/perf/tests/tests-scripts.c

Purpose: discovers shell test scripts and converts them into perf `struct test_suite` instances.
Important functions: `shell_tests__dir_fd`, `shell_test__description`, `is_shell_script`, `is_test_script`, `strdup_check`, `shell_test__run`, `append_script`, `append_scripts_in_dir`, and `create_script_test_suites`.
Control flow: locates tests/shell in source, executable, or installed paths; recursively scans sorted directories excluding hidden and `base_*`; extracts description from comments after shebang; marks tests with `(exclusive)` in description; stores absolute `/proc/self/fd`-resolved path in suite private data; runs scripts through `system`.
State and persistence: dynamically allocated suite/test arrays and strings are returned NULL-terminated; scripts map shell exit `2` to `TEST_SKIP`.
Dependencies and integration: directory fd APIs, perf test harness structs, shell script executable/read bits, and `verbose` flag.
Risks: recursive fd open lacks explicit error handling for failed subdir opens; generated suite memory ownership must be handled by caller.
Test signals: discovered scripts appear as perf test cases with correct descriptions/exclusive flags and status mapping.
