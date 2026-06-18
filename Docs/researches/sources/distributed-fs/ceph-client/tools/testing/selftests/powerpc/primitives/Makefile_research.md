# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/Makefile

## Purpose
`Makefile` builds the low-level primitive test directory, centered on load_unaligned_zeropad and local copies of small kernel headers needed by that userspace harness.

## Important APIs, Types, and Functions
The important interface is the make variable contract: `TEST_GEN_PROGS`, local `CFLAGS`, object prerequisites, and `top_srcdir`/`include .../lib.mk`. These names tell the kselftest runner which binaries are generated and which shared helper objects are pulled in.

## Control Flow and State
There is no runtime control flow in the file itself. During `make`, the selected test names are expanded into output binaries, helper objects are compiled once, and the kselftest framework installs or runs the resulting programs. State is limited to make variables and generated build artifacts under the output directory.

## Dependencies and Integration Points
It depends on the powerpc selftests make infrastructure and header search paths that point at the primitives asm/linux shim directories.

## Risks and Test Signals
Risks are mostly build-contract risks: stale `TEST_GEN_PROGS` lists can omit a test, incorrect relative `top_srcdir` breaks the shared selftest rules, and missing `-m64` changes ABI assumptions in PMU or ptrace register tests. The signal is a successful load_unaligned_zeropad binary and a pass across page-boundary offsets with exception-table fixups active.
