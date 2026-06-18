## sources/distributed-fs/ceph-client/tools/perf/tests/symbols.c

Purpose: validates loaded DSO function symbols are non-overlapping and non-zero length.
Important types/functions: `struct test_info`, `init_test_info`, `exit_test_info`, `find_module_map`, `get_test_dso_filename`, `create_map`, `test_dso`, `process_subdivided_dso`, `test_file`, and `test__symbols`.
Control flow: initializes a host machine/thread, chooses `dso_to_test` or current perf executable, creates a map for user DSO or finds existing kernel module map, loads symbols, walks cached symbol rb-tree, and checks function/ifunc ranges.
State and persistence: perf environment, machine, thread, map, and DSO refs are created and released.
Dependencies and integration: machine/dso/map/symbol loader APIs, optional kernel module subdivision handling.
Risks: no symbols results in skip; kernel module DSOs can split into section DSOs requiring secondary validation.
Test signals: no overlapping or zero-length function symbols in tested DSO(s).
