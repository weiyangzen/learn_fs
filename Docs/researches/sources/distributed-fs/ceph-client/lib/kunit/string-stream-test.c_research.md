# sources/distributed-fs/ceph-client/lib/kunit/string-stream-test.c

Purpose: KUnit tests for `struct string_stream`, including initialization, managed freeing, concatenation, appending, newline policy, and performance instrumentation.

Important APIs/types/functions: `string_stream_test_priv`, `get_concatenated_string()`, `string_stream_destroy_stub()`, `string_stream_managed_init_test`, `string_stream_unmanaged_init_test`, `string_stream_managed_free_test`, `string_stream_resource_free_test`, line/variable length/append/newline tests, and `string_stream_performance_test`.

Control flow: tests allocate streams through managed and unmanaged constructors, add fragments, retrieve concatenated strings, compare exact content and length, and free streams through KUnit actions. Static stubbing of `string_stream_destroy()` records whether managed cleanup calls the destructor exactly once. The performance case appends 10,000 lines and logs timing and allocator size data.

State/persistence: creates transient stream fragments, KUnit actions for cleanup, deterministic pseudo-random line offsets, and current-test static stub state.

Dependencies/integration: depends on `string-stream.c`, `kunit/static_stub.h`, `kunit/test.h`, `prandom`, timekeeping, and slab `ksize()`.

Risks: static stub tests mutate `current->kunit_test`; cleanup ordering is important so the stub remains active while the target stream is freed. Performance output is informational, not pass/fail.

Test signals: exact string equality checks catch lost fragments, wrong ordering, unwanted double newlines, empty-fragment creation, and managed destructor regressions.
