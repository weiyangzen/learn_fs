# sources/distributed-fs/ceph-client/tools/testing/selftests/signal/Makefile

## Purpose
Builds signal selftest programs `mangle_uc_sigmask` and `sas`.

## Important APIs, types, and functions
Sets `CFLAGS = -Wall`, appends two `TEST_GEN_PROGS`, and includes `../lib.mk`.

## Control flow
The kselftest build system compiles each listed C file into a generated test program.

## State and persistence
Only build artifacts under `$(OUTPUT)` are produced.

## Dependencies and integration points
Integrates with common kselftest `lib.mk` and the local C sources.

## Risks
Simple Makefile; risk is mainly missing compiler warnings due to non-`-Werror` behavior or architecture-specific stack pointer header support.

## Test signals
Successful build emits two runnable signal tests.
