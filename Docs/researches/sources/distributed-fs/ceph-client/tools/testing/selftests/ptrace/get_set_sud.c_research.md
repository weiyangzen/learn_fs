# sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/get_set_sud.c

Purpose: tests ptrace get/set support for syscall user dispatch configuration on a stopped tracee.

Important APIs and functions: `sys_ptrace()` raw syscall wrapper; uses `PTRACE_TRACEME`, `PTRACE_GET_SYSCALL_USER_DISPATCH_CONFIG`, `PTRACE_SET_SYSCALL_USER_DISPATCH_CONFIG`, and `struct ptrace_sud_config`.

Control flow: fork child, child requests tracing and SIGSTOPs. Parent waits, gets default SUD config and expects dispatch off/zero fields, sets dispatch on with offset and len, gets it again, and verifies persistence.

State and persistence: configuration is held in the child task until it is killed at test end.

Dependencies and integration: requires kernel ptrace SUD support and kselftest harness.

Risks and test signals: kernels without the new ptrace request will fail. Failures indicate SUD config is not initialized, set, or returned correctly.
