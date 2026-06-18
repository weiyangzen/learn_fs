## sources/distributed-fs/ceph-client/tools/perf/tests/shell/perftool-testsuite_report.sh

Purpose: driver for an external/base report shell test suite under `base_report`.
Important behavior: checks for `base_report`, exports `PERFSUITE_RUN_DIR`, executes executable `setup.sh` and `test_*` files, and cleans logs unless `PERFTEST_KEEP_LOGS=y`.
Control flow: same accumulator model as the probe suite, but without a root precondition.
State and persistence: temp run directory is the only persistent state and is removed by default.
Dependencies and integration: lets perf test treat legacy report tests as one exclusive shell suite.
Risks: broad child environment coupling and aggregate status obscure precise failing case unless logs are kept.
Test signals: missing base directory skips; any nonzero child status fails the suite.
