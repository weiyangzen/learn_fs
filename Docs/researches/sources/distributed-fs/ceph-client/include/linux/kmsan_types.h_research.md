# sources/distributed-fs/ceph-client/include/linux/kmsan_types.h

## Purpose

`kmsan_types.h` defines the minimal KMSAN context types embedded in existing kernel structs. It mirrors TLS sizing expected by LLVM MemorySanitizer instrumentation. The source was read as a complete 37-line file.

## Important APIs, Types, and Functions

It defines temporary constants `KMSAN_RETVAL_SIZE` and `KMSAN_PARAM_SIZE`, `struct kmsan_context_state` containing parameter, return value, vararg, origin, and overflow TLS areas, and `struct kmsan_ctx` with context state, runtime recursion flag, and depth.

## Control Flow

There is no control flow. The compiler instrumentation and KMSAN runtime read and write these fields when tracking function parameters, return values, varargs, and origins.

## State and Persistence Behavior

The state is per-context, commonly per-task, and persists only for the lifetime of the owning task/context. The constants are undefined after struct definition to avoid leaking local sizing macros.

## Dependencies and Integration Points

It depends on fixed-width kernel types and integrates with LLVM MSan instrumentation, task state, and KMSAN runtime entry/exit logic.

## Risks and Edge Cases

The TLS sizes must match compiler pass expectations. Struct layout drift can corrupt sanitizer state. `kmsan_in_runtime` and `depth` must prevent recursive instrumentation while still restoring state on exit.

## Test Signals

KMSAN build tests with instrumentation, context switch tests, vararg metadata tests, nested runtime recursion tests, and compiler/runtime layout compatibility checks are useful.
