<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/resource.h -->
# sources/distributed-fs/ceph-client/include/kunit/resource.h

## Purpose
`resource.h` defines KUnit's test-managed resource API. It lets tests attach allocations, named handles, and deferred cleanup actions to `struct kunit` so resources are released when a test ends or aborts.

## Important APIs, types, and functions
The central type is `struct kunit_resource`, which stores `data`, an optional `name`, a user-supplied `free` callback, a `kref`, a list node, and a `should_kfree` ownership flag. Public entry points include `kunit_add_resource()`, `kunit_add_named_resource()`, `kunit_alloc_resource()`, `kunit_alloc_and_get_resource()`, `kunit_find_resource()`, `kunit_find_named_resource()`, `kunit_destroy_resource()`, `kunit_remove_resource()`, and the reference helpers `kunit_get_resource()` / `kunit_put_resource()`. Deferred action helpers are exposed through `kunit_action_t`, `KUNIT_DEFINE_ACTION_WRAPPER()`, `kunit_add_action()`, `kunit_add_action_or_reset()`, `kunit_remove_action()`, and `kunit_release_action()`.

## Control flow
Resources are initialized through `__kunit_add_resource()`, inserted into `test->resources`, then found by reverse list scan under `test->lock`. Matches gain a reference before the lock is dropped. `kunit_put_resource()` calls `kref_put()`, which runs `kunit_release_resource()` when the last reference disappears. Named addition first checks for duplicate names and returns `-EEXIST`.

## State and persistence behavior
Resource state lives in the running `struct kunit` only. The list holds one reference, callers may hold more, and teardown or explicit destruction removes the list reference. `should_kfree` distinguishes KUnit-allocated `struct kunit_resource` objects from caller-owned ones.

## Dependencies and integration points
This header depends on `kunit/test.h`, `kref`, `list_head`, `spinlock`, and slab allocation. It underpins `kunit_kmalloc*`, action-based cleanup, and helper headers such as `kunit/skbuff.h`.

## Risks and test signals
Risks include leaking resources when references are not put, double cleanup if caller-owned resources set `should_kfree`, duplicate named resources, and lock/refcount races around lookup and destruction. Test signals are KUnit selftests for allocation cleanup, named lookup, deferred action LIFO ordering, duplicate-name rejection, forced `kunit_add_action_or_reset()` failure, and concurrent lookup/removal stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/resource.h -->
