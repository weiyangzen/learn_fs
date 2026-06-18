# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/Makefile

## Purpose
`Makefile` builds the POWER PMU sampling register selftests that verify sampled interrupt register snapshots expose expected MMCR/MMCRA/SIER/BHRB fields.

## Important APIs, Types, and Functions
The important interface is the make variable contract: `TEST_GEN_PROGS`, local `CFLAGS`, object prerequisites, and `top_srcdir`/`include .../lib.mk`. These names tell the kselftest runner which binaries are generated and which shared helper objects are pulled in.

## Control Flow and State
There is no runtime control flow in the file itself. During `make`, the selected test names are expanded into output binaries, helper objects are compiled once, and the kselftest framework installs or runs the resulting programs. State is limited to make variables and generated build artifacts under the output directory.

## Dependencies and Integration Points
It uses the same kselftest lib.mk pattern, -m64, local ../event.c wrappers, misc.c sampling helpers, and the assembly branch loop object for BHRB-oriented workloads.

## Risks and Test Signals
Risks are mostly build-contract risks: stale `TEST_GEN_PROGS` lists can omit a test, incorrect relative `top_srcdir` breaks the shared selftest rules, and missing `-m64` changes ABI assumptions in PMU or ptrace register tests. The signal is that every generated sampling binary can run under the harness and either pass on POWER9/POWER10/POWER11 hardware or skip cleanly when PMU extended-register support is absent.
