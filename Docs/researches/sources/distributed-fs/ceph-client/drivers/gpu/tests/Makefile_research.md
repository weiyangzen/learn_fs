# sources/distributed-fs/ceph-client/drivers/gpu/tests/Makefile

Purpose: Kbuild fragment for GPU KUnit tests.

Important APIs and targets: builds `gpu_buddy_tests-y` from `gpu_buddy_test.o` and `gpu_random.o`, and includes the resulting object under `obj-$(CONFIG_GPU_BUDDY_KUNIT_TEST)`.

Control flow: no runtime flow; Kbuild conditionally compiles the test module when the config is enabled.

State and persistence: no state.

Dependencies and integration: depends on the `CONFIG_GPU_BUDDY_KUNIT_TEST` symbol and the local test/random helper sources. Integrates with kernel KUnit and the GPU buddy allocator test suite.

Risks: if new helper objects are added to the tests but not listed here, KUnit builds will miss them. The Makefile assumes the config symbol is defined elsewhere.

Test signals: successful KUnit build and discovery of the `gpu_buddy` suite.
