# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/exc_validate.c

## Purpose
Validates copy loop behavior when the source or destination faults near a protected page boundary.

## Important APIs, Types, and Functions
Defines `UCONTEXT_NIA`, `segv_handler()`, `setup_segv_handler()`, `do_one_test()`, `MAX_LEN`, `test_copy_exception()`, and `main()`; the tested function is supplied by `COPY_LOOP` macro at build time.

## Control Flow
The test maps memory with inaccessible guard pages, installs a SIGSEGV handler that advances NIP over expected faulting instructions, calls the copy loop for short lengths around page boundaries, and checks returned uncopied bytes and signal/fault behavior.

## State and Persistence
Uses temporary mappings and process signal state only; no persistence.

## Dependencies and Integration Points
Depends on mmap/mprotect, PowerPC ucontext layout, `utils.h`, and build-time `COPY_LOOP` binding to one assembly routine.

## Risks and Test Signals
Risks include incorrect instruction-length advancement and page-size assumptions. Test signals are unexpected SIGSEGV handling, wrong remaining length, or process failure.
