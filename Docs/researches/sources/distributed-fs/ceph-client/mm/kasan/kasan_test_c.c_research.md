## sources/distributed-fs/ceph-client/mm/kasan/kasan_test_c.c

Purpose: KUnit suite that deliberately triggers memory safety violations to verify KASAN detection across allocator families, compiler instrumentation, tag modes, vmalloc, globals, stacks, usercopy, and Rust interop.

Important APIs and functions: suite setup uses `kasan_kunit_test_suite_start()`, enables multi-shot reporting, and registers a console trace probe. `KUNIT_EXPECT_KASAN_RESULT()` wraps expressions, handles sync and async hardware-tag fault behavior, and checks whether a KASAN report appeared. Test cases are registered in `kasan_kunit_test_cases[]` under suite name `kasan`.

Control flow: each test allocates memory, hides pointers from compiler optimization where needed, performs an in-bounds sanity access when relevant, then executes a deliberately invalid access inside the expectation macro. The suite covers kmalloc OOB/UAF/double-free/invalid-free, large kmalloc, page allocation, krealloc grow/shrink, memintrinsics, atomics and bitops, `ksize()`, RCU/workqueue auxiliary stacks, custom kmem caches, mempools, globals, stack and alloca redzones, string/memory routines, vmalloc/vmap/vm_map_ram, tag match-all behavior, Rust UAF, kernel nofault copy, and usercopy helpers.

State and persistence: temporary global state records whether a KASAN report or async fault was observed. Allocations are freed or tied to KUnit cleanup. Multi-shot KASAN state is saved and restored around the suite.

Dependencies and integration: integrates with KUnit, tracepoints, slab/page/vmalloc/mempool APIs, user-memory test helpers, hardware-tag controls, compiler instrumentation, optional Rust, and many config gates.

Risks and test signals: tests intentionally corrupt or access poisoned memory, so they rely on KASAN report suppression from failing KUnit itself. Risks are compiler optimization removing accesses, config-specific false expectations, async fault timing, and destructive tests without quarantine. Passing KUnit cases are the primary signal that KASAN mode behavior matches expectations.
