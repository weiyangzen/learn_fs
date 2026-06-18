# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/ptrace_test.c

## Purpose

`ptrace_test.c` verifies Landlock's ptrace containment model between parent and child processes with no domain, inherited domains, nested domains, parent-only domains, child-only domains, and sibling domains. It also validates audit records emitted when Landlock blocks ptrace-related access.

## Important APIs, Types, and Functions

The test creates a minimal filesystem-handling Landlock domain with `landlock_create_ruleset()` and `landlock_restrict_self()`. It probes read-style ptrace checks by opening `/proc/<pid>/environ`, probes active tracing with `ptrace(PTRACE_ATTACH)`, `PTRACE_DETACH`, and `PTRACE_TRACEME`, and reads Yama policy from `/proc/sys/kernel/yama/ptrace_scope`. It reuses `scoped_base_variants.h` for the domain topology matrix and `audit.h` for log matching.

## Control Flow and State

Parent and child synchronize through close-on-exec pipes so each side enters its intended Landlock domain before testing. Expected access booleans combine Landlock ancestry with Yama: parents can read or trace children only when not isolated from them, and children can trace parents only when not isolated and Yama permits it. The audit fixture forces a blocking domain and checks denied `PTRACE_TRACEME` and `PTRACE_ATTACH` records.

## Dependencies and Integration Points

The file depends on kselftest, Landlock's domain ancestry checks, Linux ptrace permission hooks, procfs, optional Yama policy, capabilities being dropped, and audit filtering by executable.

## Risks and Test Signals

The biggest risk is confusing Landlock denial with Yama denial; the test logs incomplete coverage when Yama is restrictive. Other risks are pipe races around stopped traced tasks and audit regex drift. Success signals are exact `EACCES` for `/proc` reads, `EPERM` for denied ptrace operations, correct wait/stop/detach transitions, and expected `blockers=ptrace opid=...` audit records.
