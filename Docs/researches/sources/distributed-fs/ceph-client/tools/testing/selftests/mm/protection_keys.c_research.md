# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/protection_keys.c

Purpose: comprehensive pkey stress/regression test covering allocation, VMA assignment, register permission updates, signal recovery, kernel accesses, ptrace, execute-only memory, THP/hugetlb allocations, and unsupported-CPU behavior.

Important APIs and functions: helpers manage tracing, `hw_pkey_get/set()`, `pkey_disable_set/clear()`, SIGSEGV recovery, `alloc_pkey()`, randomized allocation churn, `mprotect_pkey()`, pkey-aware allocation backends, and expected-fault accounting. `pkey_tests[]` covers user reads/writes, kernel `read()`, `vmsplice`, futex/GUP paths, syscall errors, allocation exhaustion, pkey 0, ptrace, and architecture-specific register ptrace modification.

Control flow: `main()` checks support, runs an unsupported-path probe if absent, initializes shadow state, configures hugetlb when possible, then executes all table tests for 22 iterations with a random pkey and rotating allocation backend.

State and dependencies: important state includes `shadow_pkey_reg`, fault counters, last siginfo pkey, malloc records, test fds, optional ftrace state, hugetlb sysfs changes, child processes, and per-thread pkey registers. Depends on architecture pkey headers, `pkey_util.c`, signals, ptrace, futex, vmsplice, and optional root.

Risks and test signals: pass signals are exact pkey-fault counts, siginfo matches, shadow/register consistency, expected syscall failures, and child ptrace observations. ABI register layout and signal-frame semantics are high-risk integration points.
