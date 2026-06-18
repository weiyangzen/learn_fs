# sources/distributed-fs/ceph-client/tools/testing/selftests/capabilities/validate_cap.c

## Purpose

`validate_cap.c` is the execed helper for the capability selftest. It verifies that `CAP_NET_BIND_SERVICE` is present or absent in the effective, permitted, inheritable, and ambient sets exactly as specified by command-line arguments.

## Important APIs, Types, and Functions

Functions are `bool_arg` and `main`. It uses `capng_get_caps_process`, `capng_have_capability`, `prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_IS_SET, ...)`, optional `getauxval(AT_SECURE)`, and kselftest message helpers. Arguments `argv[1]` through `argv[4]` are boolean strings for effective, permitted, inheritable, and ambient.

## Control Flow

`main` requires exactly four expected-state arguments, records whether `AT_SECURE` is set when glibc supports `getauxval`, loads current process capabilities with libcap-ng, compares each capability set and ambient state with `bool_arg`, prints a mismatch and exits nonzero on the first failure, otherwise prints success.

## State and Persistence Behavior

It is read-only with respect to capability state. It observes current process credentials after exec and exits.

## Dependencies and Integration Points

It depends on libcap-ng, capability UAPI, `prctl` ambient-capability support, and glibc `getauxval` where available. It is copied and executed by `test_execve.c`, including setuid/setgid variants.

## Risks and Test Signals

Risks include helper escaping with elevated file mode, unsupported ambient capability API, wrong boolean arguments, and secureexec environment effects. Signals are exact match of E/P/I/A states and diagnostic inclusion of `AT_SECURE` state for mismatches.
