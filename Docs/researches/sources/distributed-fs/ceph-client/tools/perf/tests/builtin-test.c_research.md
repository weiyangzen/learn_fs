# sources/distributed-fs/ceph-client/tools/perf/tests/builtin-test.c

Purpose: `builtin-test.c` implements the `perf test` command: suite registry, filtering, forking/parallel execution, workload dispatch, result formatting, leak checking, and command-line options.

Important APIs and state: `generic_tests` and `arch_tests` define registered suites; `workloads` defines runnable test workloads. Global options include `dont_fork`, `sequential`, `runs_per_test`, `dso_to_test`, and `test_objdump_path`. Core helpers include `build_suites`, `__cmd_test`, `start_test`, `finish_test`, `run_test_child`, `perf_test__list`, and `cmd_test`.

Control flow: `cmd_test` parses options/subcommands, handles suite listing and workloads, initializes symbols and memlock limits, builds suite ordering, and delegates to `__cmd_test`. The runner can fork each test into a child, close inherited fds, install crash signal handlers with optional backtraces, run leak checks, and collect stdout/stderr. Parallel mode runs non-exclusive tests first and exclusive tests sequentially in a second pass.

State and persistence: persistent state is limited to process execution; child pipes and fds are closed. Configuration reads `annotate.objdump`. No commits or durable test artifacts are created by the harness itself.

Dependencies, integration, risks, and tests: it integrates all perf test suites, script-generated suites, workloads, symbol initialization, parse-options, run-command, colors, and rlimits. Risks include global `num_tests` accumulation, child process cleanup on signals, and environment-sensitive suite order. Test signals are correct listing/filtering, skip handling, parallel/sequential execution, child leak detection, and nonzero failures when any suite fails.
