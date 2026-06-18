# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/validate.c

## Purpose
General data-integrity validator for a build-selected copy loop.

## Important APIs, Types, and Functions
Defines size/redzone constants, `COPY_LOOP()` prototype, `do_one()`, `test_copy_loop()`, and `main()`. It uses `POISON` redzones and a VMX threshold constant.

## Control Flow
`test_copy_loop()` allocates source/destination buffers, fills redzones, iterates lengths and offsets, calls the selected copy loop, checks copied bytes and untouched guard regions, and runs via `test_harness()`.

## State and Persistence
All state is heap memory local to the process. No files are written.

## Dependencies and Integration Points
Depends on the Makefile selecting `COPY_LOOP`, libc allocation/string routines, and `utils.h` harness macros.

## Risks and Test Signals
Risks are bounded coverage (`MAX_LEN`, `MAX_OFFSET`) and implementation-specific thresholds. Test signals are data mismatch, nonzero return for nonfaulting copies, or redzone corruption.
