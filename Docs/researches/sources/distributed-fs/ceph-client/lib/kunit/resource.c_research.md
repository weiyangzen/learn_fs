# sources/distributed-fs/ceph-client/lib/kunit/resource.c

Purpose: implements KUnit's managed resource and action APIs, the foundation for automatic cleanup in tests.

Important APIs/types/functions: `__kunit_add_resource()`, `kunit_remove_resource()`, `kunit_destroy_resource()`, `kunit_add_action()`, `kunit_add_action_or_reset()`, `kunit_remove_action()`, `kunit_release_action()`, `struct kunit_action_ctx`, and `__kunit_action_free()`.

Control flow: adding initializes a resource kref, runs an optional init callback, sets `res->data`, then appends to `test->resources` under `test->lock`. Removal deletes the list node and drops the list reference only if linked. Destroy finds by matcher, removes it, then drops the find reference. Actions are heap-allocated resources whose free function calls the user callback; remove cancels by nulling free, while release removes and drops the last reference so the action runs immediately.

State/persistence: mutates `struct kunit` resource lists and per-resource krefs. Actions persist until explicit remove/release or `kunit_cleanup()`.

Dependencies/integration: used broadly by KUnit allocation, platform, string-stream, device, and custom test cleanup. Depends on `linux/kref.h`, spinlocks, and KUnit assertions.

Risks: callers using `kunit_find_resource()` must balance the extra reference. Action matching depends on both function and context pointer. Resource free callbacks can remove other resources, so cleanup must avoid normal safe iteration.

Test signals: `kunit-test.c` exercises allocation, removal, destruction, LIFO cleanup, named resources, and action ordering.
