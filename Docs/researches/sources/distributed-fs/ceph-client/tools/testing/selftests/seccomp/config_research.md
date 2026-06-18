<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/seccomp/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/seccomp/config

## Purpose

Kernel config fragment for seccomp tests.

## Important APIs, Types, and Functions

Requests CONFIG_PID_NS, CONFIG_SECCOMP, CONFIG_SECCOMP_FILTER, and CONFIG_USER_NS.

## Control Flow and Integration

Used by selftest config tooling before building/running seccomp tests.

## State and Persistence Behavior

Static metadata only.

## Dependencies and Integration Points

Namespace and seccomp filter support.

## Risks and Edge Cases

Distro policy can disable user namespaces or restrict unprivileged behavior despite config support.

## Test Signals

Config validation plus successful seccomp_benchmark/seccomp_bpf execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/seccomp/config -->
