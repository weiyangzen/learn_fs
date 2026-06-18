<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_64bit_program.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_64bit_program.c

## Purpose

`trivial_64bit_program.c` is the 64-bit companion build probe for x86 kselftests. It verifies that the build environment targets x86-64 when expected.

## Important APIs, Types, and Functions

The `__x86_64__` preprocessor check enforces architecture. `main()` prints a newline and returns zero.

## Control Flow and State

The program has trivial runtime flow and no persistent state. Its value is mostly compile-time validation.

## Dependencies and Integration Points

It depends on x86-64 compiler and libc support. It is used by the selftest build to gate 64-bit-specific test binaries.

## Risks and Test Signals

The main risk is misconfigured compiler flags. Compile success and zero exit indicate a usable 64-bit test environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_64bit_program.c -->
