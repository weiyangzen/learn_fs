<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/test-bug.h -->
# sources/distributed-fs/ceph-client/include/kunit/test-bug.h

## Purpose
`test-bug.h` exposes low-overhead hooks that let ordinary kernel code detect and fail the currently running KUnit test, without depending on the full test framework when KUnit is disabled.

## Important APIs, types, and functions
When `CONFIG_KUNIT` is enabled, the header declares the `kunit_running` static key and `kunit_hooks`, containing `fail_current_test()` and `get_static_stub_address()` callbacks. `kunit_get_current_test()` returns `current->kunit_test` only when the static key says tests are running. `kunit_fail_current_test(fmt, ...)` reports a failure through the hooks. Without KUnit, these APIs compile to `NULL`/no-op behavior.

## Control flow
Both helper paths first check `static_branch_unlikely(&kunit_running)`. This keeps production code cheap when no KUnit test is executing. The failure macro passes `__FILE__`, `__LINE__`, and the formatted message to the KUnit hook table.

## State and persistence behavior
The only persistent state declared here is the global static key and hook table, populated by KUnit core code. Per-test identity lives on `current->kunit_test`.

## Dependencies and integration points
This header integrates scheduler task state, jump labels, static stubs, and failure reporting. It is included by static-stub support and by code that wants to convert internal bug checks into KUnit failures during tests.

## Risks and test signals
Risks include assuming `kunit_running` means every task has a current test, using the fail macro outside a task-associated test, and hook table misuse during module load/unload. Test signals include no-op behavior without KUnit, current-test detection only in the test task, and accurate file/line failure reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/test-bug.h -->
