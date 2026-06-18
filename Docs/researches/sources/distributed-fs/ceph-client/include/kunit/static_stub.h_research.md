<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/static_stub.h -->
# sources/distributed-fs/ceph-client/include/kunit/static_stub.h

## Purpose
`static_stub.h` implements KUnit's static function redirection API. It lets a function opt into test-time replacement by placing a redirect macro at the start of the real function.

## Important APIs, types, and functions
`KUNIT_STATIC_STUB_REDIRECT(real_fn_name, args...)` is the prologue macro used by code under test. `kunit_activate_static_stub()` type-checks and registers a replacement through `__kunit_activate_static_stub()`. `kunit_deactivate_static_stub()` removes a replacement. When `CONFIG_KUNIT` is disabled, the redirect macro compiles to an empty statement and the activation APIs disappear.

## Control flow
The redirect macro obtains the current KUnit test with `kunit_get_current_test()`. Outside a KUnit context, it falls through to the real implementation. Inside a test, it asks `kunit_hooks.get_static_stub_address()` for a replacement keyed by the test and real function address; if present, it returns the replacement's result immediately.

## State and persistence behavior
Redirection state is per-test and maintained by the KUnit core, not in this header. It should be activated for a specific test and deactivated or allowed to be cleaned with test resources.

## Dependencies and integration points
The header integrates with `kunit/test-bug.h` hooks, current-task KUnit context, compiler `typecheck_fn()`, and branch prediction macros. It is an opt-in testing seam for static functions without exporting symbols globally.

## Risks and test signals
Risks include missing the prologue in the real function, mismatched replacement signatures, recursive replacement calls, and unexpected behavior if production code runs under an active KUnit test context. Test signals include replacement success, fallthrough outside KUnit, type-check compile failures for wrong signatures, and deactivation restoring the real function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/static_stub.h -->
