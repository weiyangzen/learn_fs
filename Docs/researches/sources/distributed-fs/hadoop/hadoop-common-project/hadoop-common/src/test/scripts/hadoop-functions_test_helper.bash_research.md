# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/scripts/hadoop-functions_test_helper.bash

## Purpose
This Bash helper provides common setup, teardown, and string-check utilities for Bats tests of Hadoop shell functions.

## Important Functions
`setup()` clears `LD_LIBRARY_PATH`, creates a unique temporary directory under `target/test-dir`, exports `TMP`, resolves `TESTBINDIR`, points `HADOOP_LIBEXEC_DIR` at `src/main/bin`, enables `HADOOP_SHELL_SCRIPT_DEBUG`, unsets `HADOOP_CONF_DIR`, `HADOOP_HOME`, and `HADOOP_PREFIX`, sets `QATESTMODE=true`, sources `hadoop-functions.sh`, and pushes into the temp directory. `teardown()` pops the directory and removes `TMP`. `strstr()` prints `true` if a substring occurs in a string and `false` otherwise.

## Control Flow
Bats automatically calls `setup` and `teardown` around each test. The helper normalizes the shell environment before sourcing production shell functions, then isolates test filesystem effects in a per-process temp directory.

## State And Persistence
Temporary state is created under `../../../target/test-dir/bats.$$.${RANDOM}` and removed in teardown. Environment variables are deliberately changed for the test process.

## Dependencies And Integration Points
It depends on Bats conventions, `BATS_TEST_DIRNAME`, `hadoop-functions.sh`, and the Hadoop source tree layout. It is consumed by shell tests in the same test scripts directory.

## Risks
Unquoted `mkdir -p ${RELTMP}` is safe for generated paths but remains shell-sensitive. If teardown is skipped after a hard kill, temp directories can remain. Source tree layout changes can break `HADOOP_LIBEXEC_DIR` resolution.

## Test Signals
Bats tests that source this helper should run in isolated temp directories and load production shell functions. Failures during setup usually indicate missing `BATS_TEST_DIRNAME`, broken path assumptions, or syntax errors in `hadoop-functions.sh`.
