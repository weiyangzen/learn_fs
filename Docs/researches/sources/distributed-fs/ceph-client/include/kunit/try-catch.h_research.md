<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/try-catch.h -->
# sources/distributed-fs/ceph-client/include/kunit/try-catch.h

## Purpose
`try-catch.h` declares KUnit's generic abort/recovery primitive used to implement assertions and controlled test bailouts.

## Important APIs, types, and functions
`kunit_try_catch_func_t` is a `void (*)(void *)` callback type. `struct kunit_try_catch` stores the owning `struct kunit`, a `try_result` errno-style result, `try` and `catch` callbacks, a timeout, and caller context. `kunit_try_catch_run()` executes a try/catch pair. `kunit_try_catch_throw()` is `__noreturn` and aborts the try path. `kunit_try_catch_get_result()` returns the recorded result.

## Control flow
KUnit code sets up the structure, runs the try callback, and lets assertions or skips call `kunit_try_catch_throw()` to stop execution. The catch callback then handles the abort path and records the result. The implementation is architecture-independent at the interface level.

## State and persistence behavior
State is per active try/catch invocation and embedded in `struct kunit`. `try_result` is the durable outcome after execution; callback context remains caller-owned.

## Dependencies and integration points
The header depends only on basic kernel types and a forward `struct kunit`. `kunit/test.h` embeds it in `struct kunit` and uses it for `KUNIT_ASSERT_*`, `KUNIT_FAIL_AND_ABORT`, and `kunit_skip()`.

## Risks and test signals
Risks include throwing without a valid active try/catch, catch paths that assume fully initialized fixture state, and timeout behavior differing across architectures. Test signals include assertions aborting exactly one test case, expectations not aborting, skip reporting, and correct `try_result` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/try-catch.h -->
