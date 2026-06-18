# sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/pid_max.c

Purpose: verifies that `/proc/sys/kernel/pid_max` limits are enforced inside PID namespaces, including nested namespace interactions and ancestor limits.

Important APIs/functions: `do_clone()` wraps `clone()`/`__clone2()` with an allocated stack. Callback functions mount private procfs, write `pid_max`, fork many children, and validate PID allocation. Test cases are `pid_max_simple`, `pid_max_nested_limit`, and `pid_max_nested`.

Control flow: each test clones into a new PID and mount namespace. Callbacks make `/` private, detach/remount `/proc`, open `pid_max`, write 400 or 500, then fork children until limits should wrap or fail. Nested cases fill the outer namespace, create inner namespaces, and verify inner allocation cannot exceed the ancestor's configured limit.

State and persistence: mutates mount namespace, remounts procfs, writes pid_max inside the namespace, forks hundreds of short-lived children, and reaps them. Effects are namespace-scoped.

Dependencies/integration: depends on PID namespaces, mount namespaces, procfs, and `wait_for_pid()` from `pidfd.h`. Root or user namespace permissions must allow namespace creation and proc remounts.

Risks: high fork counts can be slow or affected by process limits. Incorrect cleanup could leave children until namespace teardown. The code assumes pid_max writes are namespace-scoped and accepted at the selected values.

Test signals: kselftest asserts clone success and child callback exit status zero; callback stderr messages identify limit violations or mount/write failures.
