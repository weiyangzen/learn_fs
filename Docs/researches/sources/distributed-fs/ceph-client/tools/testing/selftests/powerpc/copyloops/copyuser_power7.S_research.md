# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copyuser_power7.S

## Purpose
Power7-optimized copy-user loop implementation using cache/vector-aware copy strategies for validation.

## Important APIs, Types, and Functions
Important exported symbols are produced through `_GLOBAL*`/`FUNC_START` macros and are renamed to `test_*` by local `ppc_asm.h`; the code uses alignment labels, unrolled load/store loops, and fixup/feature macros depending on the routine.

## Control Flow
Callers enter with destination, source, and length. The assembly handles small copies, alignment prologues, main unrolled loops, tail bytes, and in copy-user variants fault fixup paths that return uncopied byte counts.

## State and Persistence
No durable state; routines mutate caller-provided memory and registers. Some variants use stack frames or vector state according to the copied kernel implementation.

## Dependencies and Integration Points
Depends on local shim headers, copied kernel macro conventions, and validation programs built by the copyloops Makefile.

## Risks and Test Signals
Risks are architecture-specific instruction availability, exception fixup accuracy, and divergence from kernel source. Validation failures show as data mismatches, redzone corruption, or incorrect fault accounting.
