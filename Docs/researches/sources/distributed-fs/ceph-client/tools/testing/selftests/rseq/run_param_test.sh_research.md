# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_param_test.sh

Purpose: `run_param_test.sh` orchestrates the broad rseq parameter test matrix.

Important APIs, types, and functions: it computes `NR_CPUS` from `/proc/cpuinfo`, sets `NR_THREADS` to six times CPU count, defines `TEST_LIST`/`TEST_NAME`, exports `GLIBC_TUNABLES` to disable glibc rseq registration, defines `do_tests()`, and defines `inject_blocking()`.

Control flow: it runs default parameters for every test type against `param_test`, `param_test_compare_twice`, `param_test_mm_cid`, and `param_test_mm_cid_compare_twice`. It then injects fixed delay loops at injection points 1 through 9. Next it runs legacy-mode blocking injections with yield, signal, and sleep at 25%, 50%, and 100%. Finally it probes `./check_optimized`; if supported, it repeats blocking injections in optimized mode.

State and persistence: state is shell variables and child-process environment only. Extra command-line arguments are appended to every binary invocation through `EXTRA_ARGS`.

Dependencies and integration points: depends on all four built param-test variants and `check_optimized`. It is the main integration point for `param_test.c` and architecture helper coverage.

Risks and test signals: it assumes `/proc/cpuinfo` has `processor` lines and that arrays are supported by `/bin/bash`. A single failing child exits the whole script with status 1. Useful signals are the printed phase names and final zero exit.
