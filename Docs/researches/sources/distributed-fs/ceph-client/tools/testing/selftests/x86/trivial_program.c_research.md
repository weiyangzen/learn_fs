<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_program.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_program.c

## Purpose

`trivial_program.c` is a generic compilation and execution probe. It checks that a selected set of build flags can produce a runnable C program.

## Important APIs, Types, and Functions

`main()` calls `puts("")` and returns zero. There are no custom types or helper APIs.

## Control Flow and State

The flow is a single print and exit. There is no state beyond libc stdout handling.

## Dependencies and Integration Points

It depends on the active compiler, linker, and libc configuration. Selftest Makefiles can use it to validate flag combinations independent of x86 bitness.

## Risks and Test Signals

The only meaningful failure is build or process startup failure. A zero exit is a pass signal for the build environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/trivial_program.c -->
