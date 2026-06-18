# subset-b-006100 research

Grouped research report for the requested Ceph client KUnit and lib files. Each section preserves the source path in its title and is wrapped for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/kunit-test.c -->
# sources/distributed-fs/ceph-client/lib/kunit/kunit-test.c

Purpose: self-tests the core KUnit infrastructure rather than product code. It validates try/catch behavior, fault catching when enabled, managed resources, deferred actions, logging, status transitions, `current->kunit_test`, KUnit-managed devices/drivers, and static stubs.

Important APIs/types/functions: `kunit_try_catch_test_context`, `kunit_test_resource_context`, `kunit_resource_test_*`, `kunit_log_test`, `kunit_status_*`, `kunit_current_*`, `kunit_device_*`, and `kunit_stub_test`. It registers suites through `kunit_test_suites()`.

Control flow: each suite creates focused KUnit cases. Try/catch cases initialize `struct kunit_try_catch`, run either a normal or throwing callback, and assert whether catch ran. Resource cases allocate, remove, destroy, and clean nested resources to verify reference and LIFO cleanup rules. Device tests register KUnit devices/drivers and assert devm cleanup and probe/remove paths.

State/persistence: uses in-memory fake KUnit contexts, resource lists, action counters, log streams, `current->kunit_test`, and temporary device-model registrations. It intentionally calls `kunit_cleanup()` on fake tests.

Dependencies/integration: depends on `kunit/test.h`, `kunit/resource.h` behavior indirectly, KUnit device helpers, string streams, static stubs, kernel device model, and optional `CONFIG_KUNIT_FAULT_TEST` and `CONFIG_KUNIT_DEBUGFS`.

Risks: several cases mutate `current->kunit_test` and fake resource lists; failures in cleanup can mask later assertions. Fault tests depend on architecture/config behavior. Device tests rely on bus registration/refcount correctness.

Test signals: the file is itself a test signal. Passing suites indicate KUnit core error handling, cleanup ordering, logs, device helpers, and static stub lifecycle are internally consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/kunit-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/platform-test.c -->
# sources/distributed-fs/ceph-client/lib/kunit/platform-test.c

Purpose: KUnit tests for the KUnit platform-device and platform-driver helper APIs.

Important APIs/types/functions: `kunit_platform_device_alloc_test`, `kunit_platform_device_add_test`, `kunit_platform_device_add_twice_fails_test`, `kunit_platform_device_add_cleans_up`, `kunit_platform_driver_register_test`, `kunit_platform_device_prepare_wait_for_probe_completes_when_already_probed`, and `kunit_platform_driver_test_context`.

Control flow: device tests allocate a platform device, add it to the platform bus, validate name/id/type, test duplicate add failure, and use a fake KUnit context to force cleanup. Driver tests allocate a device, prepare a completion notifier, register a matching driver, wait for probe, and test the already-bound fast path.

State/persistence: temporarily registers platform devices and drivers in the kernel device model. A fake test object is cleaned to verify device removal and refcount migration.

Dependencies/integration: depends on `kunit/platform_device.h`, `linux/platform_device.h`, completions, `platform_bus_type`, `bus_find_device()`, and KUnit cleanup actions.

Risks: duplicate device names may collide if cleanup breaks. The test cannot directly assert refcount underflow, so it relies on absence of later refcount warnings and bus lookup failure.

Test signals: successful cases demonstrate test-managed platform devices unregister on KUnit cleanup, driver registration probes devices, and probe wait completions work both before and after binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/platform-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/platform.c -->
# sources/distributed-fs/ceph-client/lib/kunit/platform.c

Purpose: implements KUnit-managed helpers for allocating/registering platform devices, waiting for probe, and registering platform drivers with automatic cleanup.

Important APIs/types/functions: `kunit_platform_device_alloc()`, `kunit_platform_device_add()`, `kunit_platform_device_prepare_wait_for_probe()`, `kunit_platform_driver_register()`, `kunit_platform_device_alloc_init/exit`, probe notifier `kunit_platform_device_probe_notify()`, and action wrappers for unregister functions.

Control flow: allocation creates a `platform_device` as a KUnit resource. Adding first calls `platform_device_add()`. If the device came from `kunit_platform_device_alloc()`, the existing resource free function is changed from `platform_device_put()` to `platform_device_unregister()` to transfer ownership safely; otherwise an unregister action is queued. Probe wait allocates a notifier, completes immediately if already bound, or registers a bus notifier and removes it via an action. Driver registration calls `platform_driver_register()` and queues unregister.

State/persistence: stores platform-device pointers in KUnit resources, temporary notifier blocks, and platform bus registrations. All persistent kernel registrations are tied to KUnit cleanup actions/resources.

Dependencies/integration: integrates `kunit/resource.h`, Linux platform bus APIs, completions, `bus_register_notifier()`, and device locking.

Risks: the refcount transfer in `kunit_platform_device_add()` is critical; failing it can double-put or leak devices. `bus_register_notifier()` return is not checked before adding cleanup. Probe wait relies on caller keeping the completion valid.

Test signals: covered by `platform-test.c`, especially duplicate add, cleanup removal, probe completion, and already-probed behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/resource.c -->
# sources/distributed-fs/ceph-client/lib/kunit/resource.c

Purpose: implements KUnit's managed resource and action APIs, the foundation for automatic cleanup in tests.

Important APIs/types/functions: `__kunit_add_resource()`, `kunit_remove_resource()`, `kunit_destroy_resource()`, `kunit_add_action()`, `kunit_add_action_or_reset()`, `kunit_remove_action()`, `kunit_release_action()`, `struct kunit_action_ctx`, and `__kunit_action_free()`.

Control flow: adding initializes a resource kref, runs an optional init callback, sets `res->data`, then appends to `test->resources` under `test->lock`. Removal deletes the list node and drops the list reference only if linked. Destroy finds by matcher, removes it, then drops the find reference. Actions are heap-allocated resources whose free function calls the user callback; remove cancels by nulling free, while release removes and drops the last reference so the action runs immediately.

State/persistence: mutates `struct kunit` resource lists and per-resource krefs. Actions persist until explicit remove/release or `kunit_cleanup()`.

Dependencies/integration: used broadly by KUnit allocation, platform, string-stream, device, and custom test cleanup. Depends on `linux/kref.h`, spinlocks, and KUnit assertions.

Risks: callers using `kunit_find_resource()` must balance the extra reference. Action matching depends on both function and context pointer. Resource free callbacks can remove other resources, so cleanup must avoid normal safe iteration.

Test signals: `kunit-test.c` exercises allocation, removal, destruction, LIFO cleanup, named resources, and action ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/static_stub.c -->
# sources/distributed-fs/ceph-client/lib/kunit/static_stub.c

Purpose: implements KUnit static function redirection support, allowing tests to replace selected compiled functions through hook lookup state stored on the current test.

Important APIs/types/functions: `struct kunit_static_stub_ctx`, `__kunit_get_static_stub_address_impl()`, `__kunit_activate_static_stub()`, `kunit_deactivate_static_stub()`, `__kunit_static_stub_resource_match()`, and `__kunit_static_stub_resource_free()`.

Control flow: activation asserts the real function address is non-null. A null replacement means deactivate. Otherwise it finds an existing stub resource for the real function and updates the replacement, or allocates a new context and KUnit resource. Lookup finds the matching resource and returns the replacement address. Deactivation finds the resource, removes it, and drops the lookup reference.

State/persistence: stub mappings live as KUnit resources and are automatically cleaned with the test. Each mapping stores real and replacement function addresses.

Dependencies/integration: integrates with `kunit/static_stub.h` macros and `hooks-impl.h`; consumers rely on redirect points such as `KUNIT_STATIC_STUB_REDIRECT()`.

Risks: matching trusts `res->data` after checking the free function. Deactivating a missing stub triggers KUnit assertion failure. Redirect behavior depends on hook instrumentation being compiled at call sites.

Test signals: `kunit-test.c` validates activation adds a resource, stores addresses, and deactivation removes it; `string-stream-test.c` uses a stub to observe managed destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/static_stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/string-stream-test.c -->
# sources/distributed-fs/ceph-client/lib/kunit/string-stream-test.c

Purpose: KUnit tests for `struct string_stream`, including initialization, managed freeing, concatenation, appending, newline policy, and performance instrumentation.

Important APIs/types/functions: `string_stream_test_priv`, `get_concatenated_string()`, `string_stream_destroy_stub()`, `string_stream_managed_init_test`, `string_stream_unmanaged_init_test`, `string_stream_managed_free_test`, `string_stream_resource_free_test`, line/variable length/append/newline tests, and `string_stream_performance_test`.

Control flow: tests allocate streams through managed and unmanaged constructors, add fragments, retrieve concatenated strings, compare exact content and length, and free streams through KUnit actions. Static stubbing of `string_stream_destroy()` records whether managed cleanup calls the destructor exactly once. The performance case appends 10,000 lines and logs timing and allocator size data.

State/persistence: creates transient stream fragments, KUnit actions for cleanup, deterministic pseudo-random line offsets, and current-test static stub state.

Dependencies/integration: depends on `string-stream.c`, `kunit/static_stub.h`, `kunit/test.h`, `prandom`, timekeeping, and slab `ksize()`.

Risks: static stub tests mutate `current->kunit_test`; cleanup ordering is important so the stub remains active while the target stream is freed. Performance output is informational, not pass/fail.

Test signals: exact string equality checks catch lost fragments, wrong ordering, unwanted double newlines, empty-fragment creation, and managed destructor regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/string-stream-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/string-stream.c -->
# sources/distributed-fs/ceph-client/lib/kunit/string-stream.c

Purpose: provides a small append-only string builder used by KUnit logs and assertion formatting.

Important APIs/types/functions: `alloc_string_stream()`, `string_stream_add()`, `string_stream_vadd()`, `string_stream_get_string()`, `string_stream_append()`, `string_stream_clear()`, `string_stream_is_empty()`, `string_stream_destroy()`, `kunit_alloc_string_stream()`, and `kunit_free_string_stream()`.

Control flow: each add computes formatted length with a copied `va_list`, allocates a fragment and char buffer, formats into it, optionally appends one newline if missing, then adds the fragment to the tail under a spinlock while updating total length. `get_string()` allocates a full buffer and concatenates all fragments. Managed allocation queues a KUnit action to destroy the stream; managed free releases that action immediately.

State/persistence: maintains `length`, fragment list, spinlock, GFP mask, and `append_newlines` flag. The stream persists until explicit destroy or KUnit cleanup.

Dependencies/integration: used by KUnit logging and assertion rendering. Uses slab allocation, list APIs, spinlocks, and static stub redirection in `string_stream_destroy()`.

Risks: `string_stream_append()` passes another stream's content as the format string to `string_stream_add()`, so content containing percent sequences could be interpreted. Fragment-per-add design may be allocation-heavy. `string_stream_is_empty()` reads list state without taking the stream lock.

Test signals: `string-stream-test.c` covers initialization, exact concatenation, append behavior, automatic newlines, empty adds, managed cleanup, and basic performance metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/string-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/string-stream.h -->
# sources/distributed-fs/ceph-client/lib/kunit/string-stream.h

Purpose: internal header defining KUnit string stream data structures and function prototypes.

Important APIs/types/functions: `struct string_stream_fragment`, `struct string_stream`, `kunit_alloc_string_stream()`, `kunit_free_string_stream()`, `alloc_string_stream()`, `string_stream_add()`, `string_stream_vadd()`, `string_stream_clear()`, `string_stream_get_string()`, `string_stream_append()`, `string_stream_is_empty()`, `string_stream_destroy()`, and inline `string_stream_set_append_newlines()`.

Control flow: the header exposes the append/get/clear/destroy lifecycle and lets callers toggle automatic newline appending by setting a Boolean on the stream.

State/persistence: `struct string_stream` owns `length`, list of fragments, lock, allocation flags, and newline policy. The header notes that `length` and `fragments` are protected by the lock.

Dependencies/integration: included by KUnit core, KUnit tests, and string stream implementation. Depends on Linux spinlock, stdarg, types, and list declarations from included kernel headers.

Risks: it declares `free_string_stream()` but the implementation provides `string_stream_destroy()`, so callers should use the implemented destructor path. Direct access to fields is possible and tests do it, increasing coupling.

Test signals: behavior is validated through `string-stream-test.c` and KUnit logging tests in `kunit-test.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/string-stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/test.c -->
# sources/distributed-fs/ceph-client/lib/kunit/test.c

Purpose: core KUnit runtime: suite initialization, test execution, KTAP reporting, assertion failure handling, parameterized tests, resource cleanup, module integration, and KUnit-owned allocations.

Important APIs/types/functions: `kunit_run_tests()`, `__kunit_test_suites_init()`, `__kunit_test_suites_exit()`, `kunit_init_test()`, `kunit_cleanup()`, `__kunit_do_failed_assertion()`, `__kunit_abort()`, `kunit_array_gen_params()`, `kunit_kmalloc_array()`, `kunit_kfree()`, `kunit_kstrdup_const()`, module notifier `kunit_module_notify()`, and `kunit_run_lock`.

Control flow: suite init creates debugfs state, optional suite init runs, KTAP suite start is printed, each case is initialized and run. Test bodies and cleanup are each wrapped in `kunit_try_catch_run()` kthreads so aborts, faults, and timeouts become test failures. Parameterized tests generate subcases and emit nested KTAP. Module notifications filter suites and run/list tests according to KUnit action settings.

State/persistence: manages module params `enable`, `timeout`, and `stats_enabled`; global suite counter; `current->kunit_test`; suite/case logs; per-test resource lists; debugfs suites; and module suite arrays after filtering.

Dependencies/integration: integrates KUnit attributes/filtering/executor, debugfs, device bus init, hook installation, try/catch, string streams, module notifier, tainting, and kernel allocators.

Risks: cleanup callbacks can delete arbitrary resources, so cleanup loops from the tail one item at a time. Mutating module suite arrays requires valid address checks at exit. Timeout scaling depends on speed attributes. Some parameter init/exit paths are TODO for try/catch coverage.

Test signals: `kunit-test.c` directly validates major runtime pieces; all KUnit tests rely on this file's KTAP output and status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/try-catch-impl.h -->
# sources/distributed-fs/ceph-client/lib/kunit/try-catch-impl.h

Purpose: small internal header shared by KUnit try/catch implementation and tests.

Important APIs/types/functions: inline `kunit_try_catch_init()` initializes a `struct kunit_try_catch` with owning test, try callback, catch callback, and timeout.

Control flow: the function is a direct field initializer with no allocation, validation, or side effects beyond writing the try/catch structure.

State/persistence: persists callback pointers and timeout in caller-owned `struct kunit_try_catch`; context and result fields are set later by `kunit_try_catch_run()`.

Dependencies/integration: includes public `kunit/try-catch.h` and is used by `try-catch.c`, `test.c`, and `kunit-test.c`.

Risks: no null checks are performed, so callers must provide valid callback pointers and test context. Because it is internal, misuse is contained to KUnit internals/tests.

Test signals: exercised by KUnit try/catch self-tests and by every KUnit case run through `test.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/try-catch-impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/try-catch.c -->
# sources/distributed-fs/ceph-client/lib/kunit/try-catch.c

Purpose: executes a potentially aborting KUnit callback in a separate kthread and invokes a catch callback on throw, fault, timeout, or thread creation failure.

Important APIs/types/functions: `kunit_try_catch_throw()`, `kunit_generic_run_threadfn_adapter()`, and `kunit_try_catch_run()`.

Control flow: run stores context, creates a kthread, keeps a task reference, waits on the thread completion up to the configured timeout, and stops timed-out tasks. The adapter initializes `try_result` to `-EINTR`, invokes the try function, and changes untouched `-EINTR` to success. Throw sets `-EFAULT` and exits the kthread. After completion, nonzero results are logged and catch is called; `-EFAULT` is translated back to zero before catch so KUnit aborts are not treated as infrastructure errors.

State/persistence: mutates `try_catch->context` and `try_result`; temporarily owns a kthread/task reference.

Dependencies/integration: used by `test.c` to isolate test bodies and cleanup. Depends on kthread, completions via `vfork_done`, task refcounting, and KUnit logging.

Risks: timeout handling calls `kthread_stop()` after wait timeout; callback code must be stoppable enough for cleanup. Fault reporting uses `test->last_seen` when available.

Test signals: `kunit-test.c` validates normal try, thrown try, and optional null dereference fault catching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/try-catch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/user_alloc.c -->
# sources/distributed-fs/ceph-client/lib/kunit/user_alloc.c

Purpose: provides KUnit helpers for tests that need a user address space or user mappings from kernel test threads.

Important APIs/types/functions: `struct kunit_vm_mmap_resource`, `struct kunit_vm_mmap_params`, `kunit_attach_mm()`, `kunit_vm_mmap_init()`, `kunit_vm_mmap_free()`, and `kunit_vm_mmap()`.

Control flow: `kunit_attach_mm()` returns if the task already has an `mm`, rejects non-MMU configs, allocates an `mm_struct`, sets `task_size`, chooses mmap layout, and attaches it to the current kthread via `kthread_use_mm()`. `kunit_vm_mmap()` wraps `vm_mmap()` in a KUnit resource, storing address and size for cleanup bookkeeping.

State/persistence: attaches an mm to the current kthread until the process dies. The resource stores mapping metadata, but the free function only frees metadata because the test monitor runs after the test mm is gone.

Dependencies/integration: depends on MMU memory-management APIs, `vm_mmap()`, `kthread_use_mm()`, KUnit resources, and exported-for-KUnit symbols.

Risks: `vm_mmap()` returns encoded errors in normal kernel API style; this code only checks zero as failure and may propagate error values as addresses. It intentionally does not unmap during resource free.

Test signals: no direct tests in this subset; callers should validate successful nonzero mapping and run under MMU configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/user_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/linear_ranges.c -->
# sources/distributed-fs/ceph-client/lib/linear_ranges.c

Purpose: generic helpers for mapping selector indexes to values and values back to selectors across one or more linear ranges.

Important APIs/types/functions: `linear_range_values_in_range()`, `linear_range_values_in_range_array()`, `linear_range_get_max_value()`, `linear_range_get_value()`, `linear_range_get_value_array()`, low/high selector lookup functions, and `linear_range_get_selector_within()`.

Control flow: value lookup checks selector bounds and computes `min + (selector - min_sel) * step`. Array helpers scan ranges in order. Low selector lookup finds the greatest selector whose value is less than or equal to the input; high lookup finds the smallest selector whose value is greater than or equal to the input. Zero-step ranges are special-cased.

State/persistence: stateless calculations only; no persistent storage.

Dependencies/integration: exported GPL symbols used by regulator-like drivers and any code representing hardware tables as `struct linear_range`. Depends on `linux/linear_range.h`, errno, and `DIV_ROUND_UP`.

Risks: assumes ranges are well-formed; unsigned arithmetic can wrap if `max_sel < min_sel` or values overflow. Array helpers assume range ordering is meaningful for fallback selector behavior.

Test signals: no direct tests in this subset. Good tests should cover zero-step ranges, selector boundaries, below/above range values, and overlapping or unordered arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/linear_ranges.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/list_debug.c -->
# sources/distributed-fs/ceph-client/lib/list_debug.c

Purpose: slow-path validation and corruption reporting for Linux doubly linked list operations under list hardening/debug configurations.

Important APIs/types/functions: `__list_add_valid_or_report()` and `__list_del_entry_valid_or_report()`.

Control flow: add validation checks null `prev`/`next`, reciprocal link consistency, and double-add of `new` against adjacent nodes. Delete validation checks null links, poison values, and reciprocal `prev->next`/`next->prev` consistency. Any corruption path reports through `CHECK_DATA_CORRUPTION()` and returns false.

State/persistence: does not mutate lists; only reads list pointers and emits diagnostics/warnings.

Dependencies/integration: called from list manipulation macros when hardening/debug slow paths are enabled. Depends on `linux/list.h`, `bug.h`, `kernel.h`, and exported symbols.

Risks: diagnostic reads may fault if corruption points to invalid memory outside safe hardening assumptions. Reporting includes pointer values and may be noisy under repeated corruption.

Test signals: no local tests here; kernel list debug/hardening tests and any corruption reports from list misuse serve as signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/list_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/list_sort.c -->
# sources/distributed-fs/ceph-client/lib/list_sort.c

Purpose: stable in-place merge sort for Linux circular doubly linked lists.

Important APIs/types/functions: public `list_sort()`, internal `merge()`, and `merge_final()`.

Control flow: `list_sort()` returns for zero/one element lists, breaks the circular list into a null-terminated singly linked list, then processes elements into a pending stack of sorted power-of-two sublists. It merges eagerly based on bit transitions in `count`, keeping merges at least 2:1 balanced. Final merging rebuilds `prev` links and restores the circular list head.

State/persistence: temporarily repurposes `prev` links in pending sublists as list-of-lists pointers and null-terminates `next` chains. On success the original list head owns a sorted circular doubly linked list.

Dependencies/integration: exported for kernel users needing stable list sorting. Comparator receives caller `priv` and list nodes and must provide antisymmetric/transitive ordering; boolean comparison style is supported.

Risks: invalid comparator ordering can produce incorrect sort results. The algorithm mutates links throughout; callers must not inspect or concurrently modify the list. Stability depends on taking `a` first when compare returns `<= 0`.

Test signals: not tested in this subset; expected signals are sorted order, stable equal-key order, and intact `next`/`prev` circular links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/list_sort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/llist.c -->
# sources/distributed-fs/ceph-client/lib/llist.c

Purpose: lockless singly linked list consumer helpers.

Important APIs/types/functions: `llist_del_first()`, `llist_del_first_this()`, and `llist_reverse_order()`.

Control flow: delete-first uses acquire load of `head->first`, reads the next pointer, and retries `try_cmpxchg()` until it removes the observed head or sees empty. Delete-first-this removes only if the current head is the supplied node. Reverse walks a null-terminated chain and reverses next pointers.

State/persistence: atomically updates `struct llist_head->first`; reverse mutates the supplied chain's next pointers.

Dependencies/integration: exported GPL symbols used by lockless producer/single-consumer queue patterns such as `lwq.c`. Requires architecture cmpxchg properties described in the file comment for NMI usage.

Risks: `llist_del_first()` supports only one simultaneous consumer without external locking. Concurrent multiple consumers can corrupt assumptions around `head->first->next`. `llist_reverse_order()` is not concurrency-safe on a live list.

Test signals: no direct tests in this subset. Correctness signals are LIFO removal from llist head, conditional removal only for matching head, and reversed batch order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/llist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-hardirq.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-hardirq.h

Purpose: macro adapter for lockdep self-tests that should run in simulated hardirq context.

Important APIs/types/functions: defines `IRQ_ENABLE`, `IRQ_DISABLE`, `IRQ_ENTER`, and `IRQ_EXIT` to the hardirq versions after undefining any prior mapping.

Control flow: included repeatedly by `locking-selftest.c` before testcase generation macros. It changes the meaning of generic IRQ macros used by generated event bodies.

State/persistence: no runtime state; preprocessor state only.

Dependencies/integration: depends on `HARDIRQ_ENABLE`, `HARDIRQ_DISABLE`, `HARDIRQ_ENTER`, and `HARDIRQ_EXIT` being defined by the including C file.

Risks: include order matters. It intentionally has no include guard because it must be re-includable with different lock adapters.

Test signals: generated hardirq variants in `locking-selftest.c` exercise the mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-mutex.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-mutex.h

Purpose: macro adapter selecting mutex operations for generic locking self-test templates.

Important APIs/types/functions: maps `LOCK` to `ML`, `UNLOCK` to `MU`, and `INIT` to `MI`; undefines read/write lock-specific macros.

Control flow: `locking-selftest.c` includes this header before `GENERATE_TESTCASE()` blocks so generic `LOCK(A)` bodies become `mutex_lock(&mutex_A)` style operations.

State/persistence: no runtime state; preprocessor mapping only.

Dependencies/integration: requires `ML`, `MU`, and `MI` macros from `locking-selftest.c`.

Risks: no include guard by design. Mutexes are not valid in all IRQ contexts, so generated expectations must account for sleepability and PREEMPT_RT differences.

Test signals: mutex columns in the locking API self-test output reflect cases generated through this adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-rlock-hardirq.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-rlock-hardirq.h

Purpose: combined macro adapter for read-lock tests in simulated hardirq context.

Important APIs/types/functions: includes `locking-selftest-rlock.h` to select `read_lock()`/`read_unlock()` and `locking-selftest-hardirq.h` to select hardirq enter/exit/disable/enable helpers.

Control flow: consumed by `locking-selftest.c` testcase-generation macros where both generic lock and generic IRQ operations are used.

State/persistence: preprocessor-only mapping.

Dependencies/integration: depends on the base rlock and hardirq adapter headers and the macros defined by `locking-selftest.c`.

Risks: include order is the behavior; because there is no include guard, accidental insertion of guards would break repeated generation.

Test signals: hardirq read-lock variants in irqsafe, inversion, and recursion self-tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-rlock-hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-rlock-softirq.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-rlock-softirq.h

Purpose: combined macro adapter for read-lock tests in simulated softirq context.

Important APIs/types/functions: includes `locking-selftest-rlock.h` and `locking-selftest-softirq.h`.

Control flow: lets generated generic test event bodies use `read_lock()`/`read_unlock()` and softirq enter/exit helpers.

State/persistence: preprocessor-only mapping with no runtime storage.

Dependencies/integration: used by `locking-selftest.c` for softirq variants, often disabled under `CONFIG_PREEMPT_RT` via surrounding `NON_RT` or `#ifndef CONFIG_PREEMPT_RT` logic.

Risks: same re-inclusion/order sensitivity as other self-test adapters. Softirq cases differ under RT, so expectations live in the including C file.

Test signals: softirq read-lock columns/rows in generated lockdep self-test output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-rlock-softirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-rlock.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-rlock.h

Purpose: macro adapter selecting rwlock read-side operations for generic lockdep self-test templates.

Important APIs/types/functions: maps `LOCK` and `RLOCK` to `RL`, `UNLOCK` to `RU`, `WLOCK` to `WL`, and `INIT` to `RWI`.

Control flow: included before generated testcases so generic lock operations become `read_lock()`/`read_unlock()` while mixed read/write templates can still call `WLOCK`.

State/persistence: preprocessor mapping only.

Dependencies/integration: requires `RL`, `RU`, `WL`, and `RWI` macros from `locking-selftest.c`.

Risks: read locks have special recursive semantics in the self-test, controlled by `force_read_lock_recursive`; expectations differ from exclusive locks.

Test signals: rlock self-test cases check both expected no-fail recursive reads and expected failures for mixed read/write dependency cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-rlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-rsem.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-rsem.h

Purpose: macro adapter selecting read-side rwsem operations for generic locking self-test templates.

Important APIs/types/functions: maps `LOCK`/`RLOCK` to `RSL`, `UNLOCK` to `RSU`, `WLOCK` to `WSL`, and `INIT` to `RWSI`.

Control flow: included before testcase-generation macros so generic templates exercise `down_read()`/`up_read()` and mixed read/write semaphore patterns.

State/persistence: preprocessor-only mapping.

Dependencies/integration: requires rwsem macros defined in `locking-selftest.c`.

Risks: rwsems are sleepable and have different recursion/deadlock expectations than rwlocks; generated expectations intentionally mark read recursion failures for rsem cases.

Test signals: rsem column in `locking_selftest()` output, especially recursive read and mixed read/write tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-rsem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-rtmutex.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-rtmutex.h

Purpose: macro adapter selecting rtmutex operations for generic locking self-test templates when `CONFIG_RT_MUTEXES` is enabled.

Important APIs/types/functions: maps `LOCK` to `RTL`, `UNLOCK` to `RTU`, and `INIT` to `RTI`; undefines read/write-specific macros.

Control flow: included inside `#ifdef CONFIG_RT_MUTEXES` blocks before testcase generation, adding rtmutex variants to the same deadlock/double-unlock/init-held matrix.

State/persistence: preprocessor-only mapping.

Dependencies/integration: requires `RTL`, `RTU`, and `RTI` macros from `locking-selftest.c` and rtmutex declarations to exist.

Risks: only valid when rtmutex support is compiled. RT behavior can differ from raw spin and mutex semantics.

Test signals: rtmutex column in locking self-test output when built.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-rtmutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-softirq.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-softirq.h

Purpose: macro adapter for lockdep self-tests that should run in simulated softirq context.

Important APIs/types/functions: maps `IRQ_ENABLE`, `IRQ_DISABLE`, `IRQ_ENTER`, and `IRQ_EXIT` to softirq helpers.

Control flow: included before generated softirq variants so generic IRQ event bodies use local BH disable/enable and lockdep softirq enter/exit paths.

State/persistence: preprocessor mapping only.

Dependencies/integration: requires `SOFTIRQ_ENABLE`, `SOFTIRQ_DISABLE`, `SOFTIRQ_ENTER`, and `SOFTIRQ_EXIT` from `locking-selftest.c`.

Risks: no include guard by design. Many softirq tests are skipped under PREEMPT_RT by the including file.

Test signals: generated softirq irqsafe and inversion cases in `locking_selftest()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-softirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-spin-hardirq.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-spin-hardirq.h

Purpose: combined adapter for spinlock tests in simulated hardirq context.

Important APIs/types/functions: includes `locking-selftest-spin.h` and `locking-selftest-hardirq.h`.

Control flow: used by `locking-selftest.c` before generating hardirq spinlock variants for irqsafe and inversion scenarios.

State/persistence: preprocessor-only.

Dependencies/integration: requires spin and hardirq macro definitions in the including file.

Risks: include order is functional and there are no guards. Spinlock behavior differs under PREEMPT_RT, so surrounding code controls which cases run and expected outcomes.

Test signals: hardirq spinlock columns in generated lockdep output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-spin-hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-spin-softirq.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-spin-softirq.h

Purpose: combined adapter for spinlock tests in simulated softirq context.

Important APIs/types/functions: includes `locking-selftest-spin.h` and `locking-selftest-softirq.h`.

Control flow: used before testcase-generation macros to bind generic lock operations to `spin_lock()` and generic IRQ operations to softirq simulation.

State/persistence: preprocessor-only.

Dependencies/integration: consumed by `locking-selftest.c`, mostly in non-RT softirq testcase blocks.

Risks: no include guard by design; PREEMPT_RT changes spinlock sleepability and surrounding code limits use.

Test signals: softirq spinlock variants in irqsafe and inversion test groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-spin-softirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-spin.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-spin.h

Purpose: macro adapter selecting spinlock operations for generic locking self-test templates.

Important APIs/types/functions: maps `LOCK` to `L`, `UNLOCK` to `U`, and `INIT` to `SI`; undefines read/write lock-specific macros.

Control flow: included repeatedly before generated testcase bodies in `locking-selftest.c`.

State/persistence: preprocessor-only mapping.

Dependencies/integration: requires `L`, `U`, and `SI` macros from the including self-test implementation.

Risks: generic templates using read/write-specific macros must not include this adapter unless those paths are irrelevant. RT kernels can make `spinlock_t` behave differently than raw spinlocks, so expectations are conditional elsewhere.

Test signals: spin column in lockdep self-test output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-spin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-wlock-hardirq.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-wlock-hardirq.h

Purpose: combined adapter for rwlock write-side tests in simulated hardirq context.

Important APIs/types/functions: includes `locking-selftest-wlock.h` and `locking-selftest-hardirq.h`.

Control flow: used by generated hardirq testcase matrices where generic lock operations should be write locks and generic IRQ operations should be hardirq simulation.

State/persistence: preprocessor-only.

Dependencies/integration: requires base wlock and hardirq macros from the self-test implementation.

Risks: include-order sensitive and intentionally unguarded. Write locks participate in exclusive dependency cycles and are expected to fail in many generated scenarios.

Test signals: hardirq wlock variants in lockdep self-test output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-wlock-hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-wlock-softirq.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-wlock-softirq.h

Purpose: combined adapter for rwlock write-side tests in simulated softirq context.

Important APIs/types/functions: includes `locking-selftest-wlock.h` and `locking-selftest-softirq.h`.

Control flow: used by `locking-selftest.c` to generate softirq write-lock variants of irqsafe and inversion patterns.

State/persistence: preprocessor-only.

Dependencies/integration: relies on wlock and softirq helper macros from the including file.

Risks: unguarded repeated inclusion is required. Softirq variants are generally disabled on PREEMPT_RT by the surrounding C file.

Test signals: softirq wlock variants in the self-test tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-wlock-softirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-wlock.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-wlock.h

Purpose: macro adapter selecting rwlock write-side operations for generic lockdep self-test templates.

Important APIs/types/functions: maps `LOCK` and `WLOCK` to `WL`, `UNLOCK` to `WU`, `RLOCK` to `RL`, and `INIT` to `RWI`.

Control flow: included before generated testcases so generic locks become `write_lock()`/`write_unlock()`, while mixed templates can also call read locks.

State/persistence: preprocessor-only mapping.

Dependencies/integration: requires rwlock helper macros in `locking-selftest.c`.

Risks: write-side locking is exclusive; generated deadlock expectations differ from read-side recursive cases. No include guards are intentional.

Test signals: wlock column and mixed read/write rwlock cases in `locking_selftest()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-wlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-wsem.h -->
# sources/distributed-fs/ceph-client/lib/locking-selftest-wsem.h

Purpose: macro adapter selecting write-side rwsem operations for generic locking self-test templates.

Important APIs/types/functions: maps `LOCK`/`WLOCK` to `WSL`, `UNLOCK` to `WSU`, `RLOCK` to `RSL`, and `INIT` to `RWSI`.

Control flow: included before generated testcases so generic lock bodies exercise `down_write()`/`up_write()` and mixed semaphore templates can use read-side operations.

State/persistence: preprocessor mapping only.

Dependencies/integration: requires rwsem helper macros from `locking-selftest.c`.

Risks: rwsems sleep and cannot be used in IRQ contexts; generated self-tests and expectations are limited accordingly. Include guards would break repeated macro remapping.

Test signals: wsem column in lockdep self-test output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest-wsem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest.c -->
# sources/distributed-fs/ceph-client/lib/locking-selftest.c

Purpose: boot-time/selftest-style lockdep test suite for spinlocks, rwlocks, mutexes, rwsems, ww_mutexes, rtmutexes, local locks, wait contexts, fs reclaim, IRQ safety, and nested lock classes.

Important APIs/types/functions: `locking_selftest()`, `dotest()`, `reset_locks()`, generated testcase macros, lock operation shortcuts `L/WL/RL/ML/WSL/RSL/RTL`, IRQ simulation macros, `ww_tests()`, `queued_read_lock_tests()`, `fs_reclaim_tests()`, `wait_context_tests()`, `local_lock_tests()`, and `lockdep_set_subclass_name_test()`.

Control flow: the file defines generic event bodies, repeatedly includes tiny adapter headers to bind `LOCK`/`UNLOCK`/IRQ macros, and generates many permutations. `locking_selftest()` initializes shared lock classes, marks the current task as selftest, runs expected-success and expected-failure matrices, resets lockdep state after each case, and summarizes unexpected failures. `dotest()` silences or prints lockdep output, runs a case, compares `debug_locks` to the expected result, restores preempt/RT/RCU/IRQ accounting, then calls `reset_locks()`.

State/persistence: uses many static lock objects, ww acquire contexts, counters for total/success/expected/unexpected failures, `debug_locks`, `debug_locks_silent`, `force_read_lock_recursive`, lockdep class keys, and per-cpu local lock state.

Dependencies/integration: deeply tied to lockdep, irqflags tracing, PREEMPT_RT behavior, ww_mutex internals, fs reclaim annotations, local locks, and raw lock nesting options.

Risks: tests intentionally trigger invalid locking and must repair corrupted preempt/RCU state. Config-specific behavior is complex. A real locking failure before the suite disables it. Incorrect expected matrices can either hide regressions or disable debug locks.

Test signals: kernel log table output, expected-failure counts, and absence of unexpected failures. The suite sets `debug_locks` back to 1 only when results match expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/locking-selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lockref.c -->
# sources/distributed-fs/ceph-client/lib/lockref.c

Purpose: combined spinlock/reference-count helper operations with optional lockless cmpxchg fast paths.

Important APIs/types/functions: `lockref_get()`, `lockref_get_not_zero()`, `lockref_put_return()`, `lockref_put_or_lock()`, `lockref_mark_dead()`, `lockref_get_not_dead()`, and `CMPXCHG_LOOP`.

Control flow: when `USE_CMPXCHG_LOCKREF` is enabled, operations optimistically read the combined lock/count word, verify the embedded spinlock appears unlocked, adjust count, and try `try_cmpxchg64_relaxed()`, retrying up to 100 times. Fallback paths acquire `lockref->lock` and update `count`. `put_or_lock()` returns false with the lock held when count is too low for a simple decrement.

State/persistence: mutates `struct lockref` count and sometimes leaves the spinlock held for caller-side object destruction. `mark_dead()` sets a negative count under the lock.

Dependencies/integration: exported for VFS/object lifecycle users that need atomic refcounting with lock handoff. Depends on architecture spinlock layout and 64-bit cmpxchg support for fast path.

Risks: cmpxchg path assumes `sizeof(struct lockref)` packed word is 8 bytes and that lock value can be checked directly. Callers must obey semantics around dead/zero counts and lock ownership from `put_or_lock()`.

Test signals: no direct subset tests; concurrency stress, refcount lifecycle tests, and lockdep around fallback lock paths are expected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lockref.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/logic_iomem.c -->
# sources/distributed-fs/ceph-client/lib/logic_iomem.c

Purpose: implements logical I/O memory mapping hooks for environments where synthetic IOMEM regions are backed by callback operations instead of real MMIO.

Important APIs/types/functions: `logic_iomem_add_region()`, `ioremap()`, `iounmap()`, `get_area()`, generated `__raw_read*()`/`__raw_write*()`, `memset_io()`, `memcpy_fromio()`, and `memcpy_toio()`.

Control flow: regions are registered under a mutex and resource-requested from `iomem_resource`. `ioremap()` searches registered regions, asks region ops to map an offset, stores returned area ops/private data in `mapped_areas`, and returns a biased synthetic `__iomem` address. Reads/writes decode the area index and offset from that address and dispatch to callbacks, with fallback real/warning implementations when no area matches. Unmap calls optional area unmap and clears the slot.

State/persistence: global region list, fixed `mapped_areas` table, and resources persist until the provider handles lifetime externally. The file does not provide a remove-region API in this subset.

Dependencies/integration: hooks common I/O accessors and exports them; used by UML or test/simulated I/O backends. Depends on resource tree, mutex, `asm/io.h`, and optional indirect IOMEM fallback config.

Risks: fixed area slots can exhaust. Synthetic address encoding uses high-bit biases and area masks. `ioremap()` checks `offset + size - 1`, which can overflow. Region entries are not removed here.

Test signals: backend-specific tests should verify map/unmap, raw read/write widths, memset/copy fallbacks, invalid address warnings, and slot reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/logic_iomem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/logic_pio.c -->
# sources/distributed-fs/ceph-client/lib/logic_pio.c

Purpose: manages logical PIO token ranges and translates between firmware/hardware addresses and Linux logical I/O port addresses, including indirect PIO callbacks.

Important APIs/types/functions: `logic_pio_register_range()`, `logic_pio_unregister_range()`, `find_io_range_by_fwnode()`, `logic_pio_to_hwaddr()`, `logic_pio_trans_hwaddr()`, `logic_pio_trans_cpuaddr()`, and generated `logic_in*/logic_out*/logic_ins*/logic_outs*` when indirect PIO is enabled.

Control flow: registration validates range data, rejects duplicate firmware nodes, checks CPU MMIO overlap, assigns an `io_start` either below `MMIO_UPPER_LIMIT` or in indirect space, and links the range with RCU. Translation functions find ranges by firmware node, logical token, or CPU address. I/O helpers route low tokens to direct `_in/_out` or PCI_IOBASE access and high tokens to range-provided indirect ops.

State/persistence: global RCU-protected `io_range_list` guarded by `io_range_mutex` for writes. Registered range objects are owned by callers.

Dependencies/integration: used by host bridge and PCI I/O setup code. Depends on firmware nodes, RCU list traversal, resource sizes, indirect PIO ops, and `PCI_IOBASE`.

Risks: duplicate fwnode returns `-EEXIST` and is documented as success-like for callers. Registration mutates oversized CPU MMIO ranges down to 64K. Range lifetime must outlive RCU readers after unregister.

Test signals: expected tests cover duplicate registration, overlap rejection, token translation, indirect callback dispatch, and unregister grace-period safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/logic_pio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lru_cache.c -->
# sources/distributed-fs/ceph-client/lib/lru_cache.c

Purpose: DRBD-origin helper that tracks a bounded active set of labeled objects with LRU eviction and explicit transaction/commit support for persistent cache-set changes.

Important APIs/types/functions: `lc_create()`, `lc_destroy()`, `lc_reset()`, `lc_try_lock()`, `lc_find()`, `lc_is_used()`, `lc_get()`, `lc_get_cumulative()`, `lc_try_get()`, `lc_put()`, `lc_del()`, `lc_committed()`, `lc_element_by_index()`, and seq dump/stat helpers.

Control flow: creation preallocates all objects from a kmem cache, embeds `struct lc_element` at caller-specified offset, and populates the free list. Lookup uses a hash table keyed by current or pending number. `lc_get()` hits increment refcount and move to in-use; misses may mark the cache dirty, select a free/LRU element, move it to `to_be_changed`, and require the caller to persist/commit the change. `lc_committed()` promotes pending new numbers to active numbers. `lc_put()` moves unused elements to LRU.

State/persistence: maintains free, in-use, lru, and to-be-changed lists; hash slots; element array; usage/stat counters; pending change count; and flags such as locked, dirty, starving, and paranoia.

Dependencies/integration: callers must provide external locking/transaction serialization and a kmem cache. Seq helpers integrate with debug/proc style reporting.

Risks: PARANOIA macros BUG on concurrent misuse. Dirty/starving/locked protocol is subtle. Returned miss elements may not yet have `lc_number == requested`, so callers must inspect numbers and commit.

Test signals: no direct subset tests. Useful tests should cover hits, misses, pending-change limits, starving behavior, commit promotion, LRU eviction, cumulative lookup, and stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lru_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lshrdi3.c -->
# sources/distributed-fs/ceph-client/lib/lshrdi3.c

Purpose: libgcc-style helper for 64-bit logical right shift on targets that need compiler runtime support.

Important APIs/types/functions: `__lshrdi3(long long u, word_type b)`.

Control flow: if shift count is zero, returns input. Otherwise it views the 64-bit value as two 32-bit words with `DWunion`. For shifts of 32 or more, high becomes zero and low is shifted from the old high word. For smaller shifts, high is shifted right and low combines its shifted value with carries from the old high word.

State/persistence: stateless pure computation.

Dependencies/integration: exported symbol used by compiler-generated code on architectures lacking native helper availability. Depends on `linux/libgcc.h` word/union definitions.

Risks: assumes 32-bit word halves as defined by `DWunion`. Shift counts outside expected compiler-generated range may have undefined or surprising behavior.

Test signals: compiler/runtime tests should compare `__lshrdi3()` against native unsigned 64-bit logical right shifts for boundary counts 0, 1, 31, 32, 33, and 63.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lshrdi3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lwq.c -->
# sources/distributed-fs/ceph-client/lib/lwq.c

Purpose: lightweight queue built from an atomic producer `llist` plus a spinlocked ready list for single-item or batch dequeue by consumers.

Important APIs/types/functions: `__lwq_dequeue()`, `lwq_dequeue_all()`, optional `lwq_exercise()` and `lwq_test()` under `CONFIG_LWQ_TEST`.

Control flow: dequeue first checks `lwq_empty()`, takes the lock, consumes `ready` if present, otherwise marks ready with a temporary non-null sentinel, drains `new` with `llist_del_all()`, reverses it to FIFO order, and advances `ready`. Batch dequeue clears `ready`, drains `new`, unlocks, appends reversed new entries after the old ready chain, and returns the whole list.

State/persistence: `struct lwq` owns an atomic `new` llist, spinlock, and `ready` chain. Optional test allocates nodes, starts kthreads, re-enqueues work, and prints queue contents.

Dependencies/integration: depends on `llist` helpers, RCU/update headers, spinlocks, wait variables, and queue macros from `linux/lwq.h`.

Risks: sentinel `(void *)1` relies on `lwq_empty()` semantics and must not leak as a real node. Multiple dequeuers are serialized by the spinlock, while producers can enqueue from any context.

Test signals: optional module test stresses threaded dequeue/requeue, batch dequeue, safe iteration deletion, and remaining order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lwq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lz4/Makefile -->
# sources/distributed-fs/ceph-client/lib/lz4/Makefile

Purpose: kernel build fragment for LZ4 compression/decompression objects.

Important APIs/types/functions: Kbuild variables `ccflags-y`, `obj-$(CONFIG_LZ4_COMPRESS)`, `obj-$(CONFIG_LZ4HC_COMPRESS)`, and `obj-$(CONFIG_LZ4_DECOMPRESS)`.

Control flow: Kbuild adds `-O3` for this directory and includes `lz4_compress.o`, `lz4hc_compress.o`, and/or `lz4_decompress.o` according to configuration symbols.

State/persistence: no runtime state; build configuration only.

Dependencies/integration: integrated by the kernel build system and Kconfig symbols controlling LZ4 support.

Risks: forcing `-O3` can expose compiler-specific behavior or increase build time/code size, but is likely chosen for compression performance. Missing config dependencies would omit required objects.

Test signals: build matrix with compress, high-compress, and decompress configs verifies object selection; runtime compression tests validate linked implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lz4/Makefile -->
