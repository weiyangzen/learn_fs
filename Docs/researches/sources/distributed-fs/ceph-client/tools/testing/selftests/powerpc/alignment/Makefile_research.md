# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/alignment/Makefile

## Purpose
Builds the PowerPC alignment selftests.

## Important APIs, Types, and Functions
`TEST_GEN_PROGS := copy_first_unaligned alignment_handler`; it includes `../../lib.mk` and `../flags.mk`, and adds `-m64` to `CFLAGS` for both generated programs.

## Control Flow
No custom targets are defined; lib.mk compiles the two C files and handles install/run integration.

## State and Persistence
No persistent state beyond build outputs.

## Dependencies and Integration Points
Depends on the PowerPC common flags and kselftest lib.mk. The generated programs depend on `../harness.c` and utility headers through normal build rules.

## Risks and Test Signals
Risk is that these tests require 64-bit PowerPC instruction support; compile or run failures point at architecture/toolchain mismatch.
