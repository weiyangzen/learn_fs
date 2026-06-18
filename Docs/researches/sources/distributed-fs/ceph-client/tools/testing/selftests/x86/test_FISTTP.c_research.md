<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FISTTP.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FISTTP.c

## Purpose

`test_FISTTP.c` tests the SSE3-era x87 `FISTTP` instruction, which stores integer values with truncation independent of the x87 rounding mode. It covers 16-bit, 32-bit, and 64-bit destinations.

## Important APIs, Types, and Functions

Global result buffers `res64`, `res32`, and `res16` receive instruction output. `test()` emits inline x87 assembly for `fisttp` variants and checks truncation results. `sighandler()` handles unsupported instruction signals. `main()` runs the test and reports pass or failure.

## Control Flow and State

The test runs a fixed sequence of floating-point loads and truncating stores, then compares memory results. State is confined to global result variables and the signal handler path.

## Dependencies and Integration Points

It depends on x87/SSE3 instruction support, assembler support for `fisttp`, signal handling for `SIGILL`, and x86 kselftest build configuration.

## Risks and Test Signals

Risks include silent rounding-mode dependence, wrong operand-size stores, or unsupported instruction behavior. Passing output confirms truncation results for all tested integer widths; unsupported systems should exit through the signal path rather than corrupt results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FISTTP.c -->
