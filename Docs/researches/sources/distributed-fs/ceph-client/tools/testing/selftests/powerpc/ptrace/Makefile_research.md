# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/Makefile

## Purpose
`Makefile` selects the ptrace powerpc selftests, splitting always-built tests from 64-bit-only transactional-memory, pkey, hardware-breakpoint, TAR, syscall, and VSX programs.

## Important APIs, Types, and Functions
The important interface is the make variable contract: `TEST_GEN_PROGS`, local `CFLAGS`, object prerequisites, and `top_srcdir`/`include .../lib.mk`. These names tell the kselftest runner which binaries are generated and which shared helper objects are pulled in.

## Control Flow and State
There is no runtime control flow in the file itself. During `make`, the selected test names are expanded into output binaries, helper objects are compiled once, and the kselftest framework installs or runs the resulting programs. State is limited to make variables and generated build artifacts under the output directory.

## Dependencies and Integration Points
It pulls in kselftest lib.mk, disables PIE for register/assembly assumptions, links local assembly helpers, and uses kernel UAPI headers for ptrace, pkeys, and breakpoint structures.

## Risks and Test Signals
Risks are mostly build-contract risks: stale `TEST_GEN_PROGS` lists can omit a test, incorrect relative `top_srcdir` breaks the shared selftest rules, and missing `-m64` changes ABI assumptions in PMU or ptrace register tests. The signal is successful build of TEST_GEN_PROGS and runtime pass/skip results on hardware with the required ptrace, TM, pkey, DAWR, and perf capabilities.
