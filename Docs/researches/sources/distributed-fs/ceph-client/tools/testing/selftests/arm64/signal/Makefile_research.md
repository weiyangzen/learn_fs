# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/Makefile

## Purpose

This Makefile builds each arm64 signal testcase as a standalone kselftest executable linked with the common signal test framework.

## Important APIs, Types, and Functions

It discovers `testcases/*.c` except common `testcases/testcases.c`, maps them to program names, sets `TEST_GEN_PROGS`, includes `../../lib.mk`, copies generated binaries to `$(OUTPUT)`, and defines common sources/headers for every testcase.

## Control Flow and Data Flow

For each testcase source, make compiles that file with `test_signals.c`, `test_signals_utils.c`, `testcases/testcases.c`, `signals.S`, and `sve_helpers.c`. Each testcase supplies its own `struct tdescr tde`, and the common wrapper supplies `main()`.

## State and Persistence Behavior

Only build products are created. Runtime state is owned by the generated test binaries.

## Dependencies and Integration Points

It depends on arm64 kernel headers, kselftest `lib.mk`, the common framework files, and all testcase descriptors under `testcases/`.

## Risks and Edge Cases

Secondary expansion is required so `$@.c` resolves per target. Adding a testcase without a `tde` descriptor will link-fail. Copying `$(PROGS)` to `$(OUTPUT)` assumes the local build path created binaries beside sources.

## Test Signals

Successful build creates one executable per testcase listed by `TEST_GEN_PROGS`.
