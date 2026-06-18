# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/scripts/run-bats.sh

## Purpose
`run-bats.sh` is the wrapper that runs Hadoop Common shell tests written in Bats and writes TAP output for Maven/test reporting.

## Important Behavior
It creates `../../../target/surefire-reports` and `../../../target/tap`, locates `bats` with `which`, writes a skip-style TAP file and exits 0 if Bats is unavailable, then runs every `*.bats` file with `bats -t`, teeing output to `target/tap/<test>.tap`. It accumulates pipeline exit status via `PIPESTATUS[0]` and exits 1 if any Bats file fails.

## Control Flow
The script is linear: prepare directories, detect tool availability, iterate Bats files, aggregate exit code, and return success/failure. Missing Bats is treated as a skipped test environment rather than a build failure.

## State And Persistence
It writes TAP files under `target/tap` and ensures surefire report directories exist. It does not clean prior TAP files.

## Dependencies And Integration Points
It depends on Bash, Bats, and the shell test layout. It integrates with Maven Surefire or build scripts that inspect TAP/surefire outputs.

## Risks
If no `*.bats` files match and shell globbing remains default, the loop may attempt to run a literal `*.bats`. `exitcode` is not initialized explicitly; Bash arithmetic treats empty as zero, but this is implicit. Missing Bats exits 0, which can hide unexecuted shell tests in CI unless the skip output is monitored.

## Test Signals
Successful runs create TAP files for each Bats test and return 0. Failure of any Bats test returns 1. Missing Bats creates `shelltest.tap` with a "not ok - no bats executable found" message but exits 0.
