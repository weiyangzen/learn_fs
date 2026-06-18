# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/deny_namespace.c

## Purpose
Tests LSM/cgroup-like policy for denying namespace creation under selected credential/capability conditions.

## Important APIs, types, and functions
Uses `test_deny_namespace.skel.h`, `cap_helpers.h`, `fork()`, `waitpid()`, `unshare()`/user namespace creation helpers, and test subfunctions for privileged BPF-denied and unprivileged no-BPF cases. `wait_for_pid()` normalizes child exit handling.

## Control flow and state
The file loads/attaches the deny-namespace skeleton for one subtest, forks children to attempt namespace creation, and checks child status. Another subtest drops/adjusts capabilities to validate unprivileged behavior without BPF. State is child PIDs, capability state, and skeleton BSS if used.

## Dependencies and integration points
Requires user namespace support, capabilities manipulation, generated LSM skeleton, and kernel namespace policy hooks. Integrated as `test_deny_namespace()`.

## Risks and test signals
Host sysctls may disable unprivileged user namespaces. Passing signals are expected child exit statuses: BPF-denied creation fails where policy applies, and no-BPF unprivileged behavior matches kernel configuration assumptions.
