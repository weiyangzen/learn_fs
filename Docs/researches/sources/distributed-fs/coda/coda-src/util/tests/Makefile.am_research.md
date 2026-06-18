# sources/distributed-fs/coda/coda-src/util/tests/Makefile.am

## Purpose
Builds the `proctest` utility test program under `coda-src/util/tests`.

## Important APIs, Types, And Functions
`noinst_PROGRAMS = proctest`, `proctest_SOURCES = proctest.cc`, and `proctest_LDADD` links against `coda-src/util/libutil.la`.

## Control Flow
Automake converts this file into local test build rules for `proctest`.

## State And Persistence
No runtime state is defined. Build state is limited to the test binary and its link dependency.

## Dependencies And Integration Points
Depends on the parent utility library and Automake. It provides a narrow test for process-name lookup support.

## Risks
No `TESTS` variable is declared, so the program may be built but not run by `make check` unless added elsewhere. Missing `getcommandname` support would surface at link time.

## Test Signals
Run `make check` or explicitly build `proctest`, verify linkage against `libutil.la`, and execute it on supported platforms.
