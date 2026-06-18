# sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/run.sh

## Purpose
Tiny top-level runner for sparc64 selftests.

## Important APIs, types, and functions
Executes `(cd drivers; ./drivers_test.sh)`.

## Control flow
Changes into the `drivers` subdirectory in a subshell and runs the driver wrapper.

## State and persistence
No state beyond the child script's module and test side effects.

## Dependencies and integration points
Registered as `TEST_PROGS` by the sparc64 Makefile.

## Risks
No SPDX line and no explicit error handling; exit status is the subshell/script status.

## Test signals
All visible test signals come from `drivers_test.sh` and `adi-test`.
