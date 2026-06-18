<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/Makefile

## Purpose
This Makefile registers the ftrace shell test suite and builds the `poll` helper.

## Important APIs, Types, And Functions
It declares `TEST_PROGS_EXTENDED := ftracetest`, `TEST_PROGS := ftracetest-ktap`, `TEST_FILES := test.d settings`, `EXTRA_CLEAN := $(OUTPUT)/logs/*`, `TEST_GEN_FILES := poll`, and includes `../lib.mk`.

## Control Flow
kselftest builds `poll`, installs the test directory and settings, and runs `ftracetest-ktap`, which delegates to `ftracetest -K -v`.

## State And Persistence
Build artifacts and logs are generated in the output tree; runtime tracing state is managed by `ftracetest`.

## Dependencies And Integration Points
It integrates with tracefs/debugfs ftrace test cases and the kselftest runner.

## Risks
All real feature requirements are in `config` and per-`.tc` metadata, so Makefile success alone does not prove runtime coverage.

## Test Signals
Successful `poll` build and KTAP output from `ftracetest-ktap` are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/Makefile -->
