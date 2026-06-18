# sources/distributed-fs/ceph-client/tools/testing/selftests/tmpfs/Makefile

## Purpose
This Makefile builds the tmpfs selftest binary `bug-link-o-tmpfile`.

## Important APIs, Types, and Functions
It sets `CFLAGS += -Wall -O2`, declares `TEST_GEN_PROGS += bug-link-o-tmpfile`, and includes `../lib.mk` to integrate with kselftest build/run rules.

## Control Flow
There is no runtime control flow. During `make`, kselftest infrastructure compiles the listed C program and includes it in generated test binaries.

## State and Persistence
The Makefile only affects build outputs under the kselftest output directory.

## Dependencies and Integration Points
It depends on `tools/testing/selftests/lib.mk` and the adjacent `bug-link-o-tmpfile.c`.

## Risks
The narrow build configuration means any additional tmpfs tests must be added to `TEST_GEN_PROGS` or they will not run.

## Test Signals
Successful build of `bug-link-o-tmpfile` is the only signal from this file.
