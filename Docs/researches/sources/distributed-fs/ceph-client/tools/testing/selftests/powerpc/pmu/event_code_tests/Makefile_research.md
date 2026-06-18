# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/Makefile

## Purpose
`Makefile` builds the POWER PMU event-code validation programs that exercise raw event encodings, alternative-event handling, generic PMU fallback, blacklists, and group constraint rejection paths.

## Important APIs, Types, and Functions
The important interface is the make variable contract: `TEST_GEN_PROGS`, local `CFLAGS`, object prerequisites, and `top_srcdir`/`include .../lib.mk`. These names tell the kselftest runner which binaries are generated and which shared helper objects are pulled in.

## Control Flow and State
There is no runtime control flow in the file itself. During `make`, the selected test names are expanded into output binaries, helper objects are compiled once, and the kselftest framework installs or runs the resulting programs. State is limited to make variables and generated build artifacts under the output directory.

## Dependencies and Integration Points
It includes the selftests top-level lib.mk, forces 64-bit compilation with -m64, links the shared PMU helpers from ../event.c and sampling_tests/misc.c where needed, and compiles each C file into a standalone kselftest binary.

## Risks and Test Signals
Risks are mostly build-contract risks: stale `TEST_GEN_PROGS` lists can omit a test, incorrect relative `top_srcdir` breaks the shared selftest rules, and missing `-m64` changes ABI assumptions in PMU or ptrace register tests. The signal is successful production and execution of all listed TEST_GEN_PROGS, especially the negative tests that must fail perf_event_open for invalid or incompatible event groups.
