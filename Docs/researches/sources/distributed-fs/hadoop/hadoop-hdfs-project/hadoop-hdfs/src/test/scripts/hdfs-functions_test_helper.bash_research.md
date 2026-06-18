# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/scripts/hdfs-functions_test_helper.bash

Purpose: shared BATS setup/teardown helper for HDFS shell-function tests. It creates an isolated temporary directory, prepares Hadoop shell environment variables, sources `hadoop-functions.sh`, and provides a string containment helper.

Important APIs/functions: `setup()` creates and exports `TMP`, resolves `TESTBINDIR` and `HADOOP_LIBEXEC_DIR`, enables `HADOOP_SHELL_SCRIPT_DEBUG`, unsets `HADOOP_CONF_DIR`, `HADOOP_HOME`, and `HADOOP_PREFIX`, sets `QATESTMODE=true`, sources the common Hadoop shell functions, and `pushd`s into `TMP`. `teardown()` pops the directory and removes `TMP`. `strstr()` prints `true` or `false` depending on substring presence.

Control flow: BATS invokes `setup` before each test and `teardown` after each test. The source path to `hadoop-functions.sh` is relative to the test directory, so the helper anchors tests in the source tree layout.

State and persistence behavior: creates per-process/random target directories under `../../../target/test-dir/bats.$$.$RANDOM`, exports environment variables, and deletes the temp directory after each test. No persistent test state should survive a successful teardown.

Dependencies and integration points: integrates with BATS, Hadoop shell scripts, and the `hadoop-common` script library. The helper controls compatibility behavior by unsetting legacy Hadoop home variables.

Risks: cleanup depends on `TMP` being set correctly; a failed `pushd`/`popd` or sourced-script failure could leave temporary data. Relative path assumptions are sensitive to test invocation location.

Test signals: tests using this helper should start from a clean temp directory, source Hadoop functions successfully, and be able to assert shell output with `strstr`.
