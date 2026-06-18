# sources/distributed-fs/ceph-client/lib/kunit/static_stub.c

Purpose: implements KUnit static function redirection support, allowing tests to replace selected compiled functions through hook lookup state stored on the current test.

Important APIs/types/functions: `struct kunit_static_stub_ctx`, `__kunit_get_static_stub_address_impl()`, `__kunit_activate_static_stub()`, `kunit_deactivate_static_stub()`, `__kunit_static_stub_resource_match()`, and `__kunit_static_stub_resource_free()`.

Control flow: activation asserts the real function address is non-null. A null replacement means deactivate. Otherwise it finds an existing stub resource for the real function and updates the replacement, or allocates a new context and KUnit resource. Lookup finds the matching resource and returns the replacement address. Deactivation finds the resource, removes it, and drops the lookup reference.

State/persistence: stub mappings live as KUnit resources and are automatically cleaned with the test. Each mapping stores real and replacement function addresses.

Dependencies/integration: integrates with `kunit/static_stub.h` macros and `hooks-impl.h`; consumers rely on redirect points such as `KUNIT_STATIC_STUB_REDIRECT()`.

Risks: matching trusts `res->data` after checking the free function. Deactivating a missing stub triggers KUnit assertion failure. Redirect behavior depends on hook instrumentation being compiled at call sites.

Test signals: `kunit-test.c` validates activation adds a resource, stores addresses, and deactivation removes it; `string-stream-test.c` uses a stub to observe managed destruction.
