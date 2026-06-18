# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/scripts/run-bats.sh

Purpose: BATS test launcher for Hadoop HDFS shell tests. It runs all `*.bats` files in the current directory, captures TAP output, and returns failure if any test file fails.

Important APIs/functions: creates `../../../target/surefire-reports` and `../../../target/tap`; locates `bats` with `which`; emits a TAP skip/failure marker when BATS is missing; loops over `*.bats`; runs `bats -t`; captures output through `tee`; reads the command status from `PIPESTATUS[0]`; accumulates `exitcode`.

Control flow: if no BATS executable exists, the script writes `shelltest.tap`, logs skip guidance, and exits `0` so Maven does not fail purely because BATS is absent. Otherwise it runs each test and exits `1` when any result is non-zero.

State and persistence behavior: persists TAP files under `target/tap` and ensures Surefire report directories exist. It does not remove prior TAP files.

Dependencies and integration points: intended to be invoked from Maven or test scripts inside the HDFS test script directory. Depends on Bash, BATS, and standard shell utilities.

Risks: if no `*.bats` files match, Bash may pass the literal pattern unless shell options differ. Missing BATS is treated as a non-failing skip, which can hide unexecuted shell tests in environments expected to run them.

Test signals: non-zero exit reflects at least one failing BATS file; TAP artifacts provide per-file diagnostics for CI consumption.
