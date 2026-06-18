# sources/distributed-fs/ceph-client/lib/kunit/hooks-impl.h

Purpose: internal header that wires KUnit runtime hook implementations into the globally exported hook table used by code that may be built when KUnit is modular.

Important APIs: declarations for `__kunit_fail_current_test_impl()` and `__kunit_get_static_stub_address_impl()`, plus inline `kunit_install_hooks()` assigning them to `kunit_hooks.fail_current_test` and `kunit_hooks.get_static_stub_address`.

Control flow: callers invoke `kunit_install_hooks()` during KUnit initialization to populate function pointers.

State and persistence: mutates global `kunit_hooks` table declared in `hooks.c`.

Dependencies and integration: includes `kunit/test-bug.h`; integrates KUnit failure reporting and static stubbing hooks with code compiled outside the KUnit module.

Risks: hook table must be installed before users rely on it; stale pointers would be dangerous across module unload if not cleared elsewhere; declarations must match implementation signatures.

Test signals: static stub example tests, current-test failure hook tests, module/built-in KUnit build matrix.
