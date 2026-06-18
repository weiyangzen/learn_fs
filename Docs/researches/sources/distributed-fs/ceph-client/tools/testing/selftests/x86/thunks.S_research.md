<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/thunks.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/thunks.S

## Purpose

`thunks.S` provides a 64-bit object helper for calling 32-bit compatibility-mode functions from 64-bit test code. It is used by mixed-bitness x86 selftests that need to exercise compat paths from one process image.

## Important APIs, Types, and Functions

The exported `call32_from_64` takes a stack pointer in `%rdi` and a 32-bit function pointer in `%esi`. It saves callee-saved 64-bit registers and flags, switches to the supplied stack, performs an `lretq` to USER32_CS, calls the function in `.code32`, jumps back to USER64_CS, restores the original stack, flags, and registers, then returns.

## Control Flow and State

The thunk temporarily changes CS and stack state. Caller-provided memory stores the old `%rsp` at the top of the new stack. No global data is used.

## Dependencies and Integration Points

It depends on Linux user segment selectors `0x23` and `0x33`, x86 long-mode compatibility transitions, and callers that provide a valid low 32-bit callable address and stack. It integrates with x86 selftests needing compat transitions.

## Risks and Test Signals

Risks include selector mismatch on unusual environments, invalid stack layout, or failure to preserve callee-saved state. Downstream mixed-bitness tests are the primary validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/thunks.S -->
