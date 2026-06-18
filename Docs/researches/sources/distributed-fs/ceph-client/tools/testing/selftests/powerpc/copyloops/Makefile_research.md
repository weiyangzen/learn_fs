# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/Makefile

## Purpose
Builds validation binaries for copied kernel PowerPC memory/copy-user assembly loops under several implementations.

## Important APIs, Types, and Functions
Defines copy loop object groups, `TEST_GEN_PROGS`, per-target object dependencies, `EXTRA_SOURCES`, `CFLAGS`, `ASFLAGS`, and target-specific `-D COPY_LOOP=...` or `-D TEST_MEMMOVE=...` mappings.

## Control Flow
The Makefile compiles shared assembly implementations and links validation harnesses against selected loop symbols such as `test___copy_tofrom_user_base`, `test_memcpy`, `test_memmove`, and Power7 variants.

## State and Persistence
Build output contains test binaries and object files. No runtime state is controlled here.

## Dependencies and Integration Points
Integrates imported kernel assembly with local shim headers under `copyloops/asm` and common PowerPC flags.

## Risks and Test Signals
Risks include symbol-name mismatches, assembler feature support, and keeping copied kernel loops synchronized with required shims. Successful builds are prerequisite signals for the validation C tests.
