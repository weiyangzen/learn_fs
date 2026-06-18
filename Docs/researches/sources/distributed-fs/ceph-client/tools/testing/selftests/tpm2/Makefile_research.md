# sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/Makefile

## Purpose
This Makefile registers TPM2 shell tests and Python helper files with kselftest.

## Important APIs, Types, and Functions
It includes `../lib.mk`, sets `TEST_PROGS := test_smoke.sh test_space.sh test_async.sh`, and exports Python helpers through `TEST_PROGS_EXTENDED := tpm2.py tpm2_tests.py`.

## Control Flow
There is no runtime logic. kselftest runs the shell wrappers and copies extended Python files for execution.

## State and Persistence
Build/run state is managed by kselftest output directories only.

## Dependencies and Integration Points
The Makefile integrates shell wrappers with the Python unittest module and depends on kselftest `lib.mk`.

## Risks
Adding new Python unittest classes without a wrapper would not make them part of default test execution.

## Test Signals
The file's signal is that the three TPM2 wrappers and helper modules are available in the test output.
