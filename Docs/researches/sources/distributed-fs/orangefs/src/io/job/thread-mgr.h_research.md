# sources/distributed-fs/orangefs/src/io/job/thread-mgr.h

## Purpose
`thread-mgr.h` declares the progress manager used by `job.c` to bridge asynchronous lower-layer operations into job completions.

## Important APIs and types
`struct PINT_thread_mgr_bmi_callback` stores a BMI completion callback accepting caller data, actual size, and error code. `struct PINT_thread_mgr_trove_callback` stores a TROVE callback accepting caller data and error code. The BMI API covers cancel, start, stop, context retrieval, and unexpected-handler registration. The TROVE API covers start, stop, context retrieval, and cancel. The device API covers start, stop, and unexpected-handler registration. The three `PINT_thread_mgr_*_push()` functions expose progress driving for non-threaded operation.

## Control flow and integration
The header does not implement control flow, but it establishes the callback contract used by `job.c`: job descriptors embed these callback structs and pass them as lower-layer user pointers; `thread-mgr.c` receives completed lower-layer events and calls back into `job.c`.

## State and persistence behavior
State is private to the implementation. This header exposes only context retrieval and cancellation entry points, so callers do not own the underlying BMI/TROVE contexts directly.

## Dependencies
It depends on PVFS internal/types headers, BMI, and `pint-dev` because callback signatures and contexts use those types.

## Risks
The callback data is untyped `void *`, so lifetime correctness depends on job descriptors staying alive until the manager has invoked or skipped the callback. The header exposes no explicit shutdown drain contract; callers must rely on `job_finalize()` and the implementation's ref-counted stop behavior.

## Test signals
Compile-time tests should verify callback signatures against BMI/TROVE call sites. Runtime tests should ensure cancel and push functions are available and behave consistently in threaded and non-threaded configurations.
