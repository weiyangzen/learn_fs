# sources/distributed-fs/ceph-client/tools/testing/selftests/power_supply/Makefile

## Purpose
Registers the power_supply selftest shell program and its helper file with kselftest.

## Important APIs, Types, and Functions
`TEST_PROGS := test_power_supply_properties.sh` marks the executable test; `TEST_FILES := helpers.sh` installs the sourced helper; `include ../lib.mk` pulls in common kselftest build/install rules.

## Control Flow
The Makefile has no procedural logic beyond variable declaration and inclusion of the shared lib.mk.

## State and Persistence
No runtime state is stored. Build state is delegated to kselftest output directories.

## Dependencies and Integration Points
Integrates the shell test with the tools/testing/selftests harness so `make kselftest` can copy both the test and helper.

## Risks and Test Signals
Primary risk is omitting helper installation, which would make the shell test fail at source time. The test signal is successful kselftest discovery of one program and one support file.
