# sources/distributed-fs/ceph-client/tools/testing/selftests/size/Makefile

## Purpose
Builds the minimal `get_size` runtime memory selftest as a static freestanding program without startup files.

## Important APIs, types, and functions
Sets `CFLAGS := -static -ffreestanding -nostartfiles -s`, declares `TEST_GEN_PROGS := get_size`, and includes `../lib.mk`.

## Control flow
The kselftest build system compiles `get_size.c` with no normal C runtime startup.

## State and persistence
Only build artifacts are produced.

## Dependencies and integration points
Depends on compiler/linker support for freestanding static binaries and the `_start` symbol in `get_size.c`.

## Risks
Some libc/toolchain combinations may not support this minimal static linking mode.

## Test signals
Successful build produces a small `get_size` program suitable for low-perturbation memory reporting.
