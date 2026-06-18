# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/memcpy_stubs.S

## Purpose
Provides minimal stub symbols expected by copied memcpy assembly.

## Important APIs, Types, and Functions
Defines `memcpy` and `backwards_memcpy` as functions that immediately return via `blr`.

## Control Flow
No copy work is performed; the stubs satisfy unresolved symbol references or alternate paths during validation builds.

## State and Persistence
No state is changed except return control flow.

## Dependencies and Integration Points
Depends on local `asm/ppc_asm.h` `FUNC_START` macro.

## Risks and Test Signals
Risk is that an exercised path may incorrectly hit a no-op stub; validation data mismatches would expose that.
