# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tracing_failure.c

## Purpose
Negative tests for tracing program load/attach restrictions, including spin lock helpers, denied tracing targets, and fexit on noreturn functions.

## APIs, Types, and Functions
Entry point is `test_tracing_failure()`. Helpers are `test_bpf_spin_lock()`, `test_tracing_fail_prog()`, `test_tracing_deny()`, and `test_fexit_noreturns()`.

## Control Flow, State, and Persistence
Spin-lock subtests open the skeleton, enable one autoloaded program, load successfully, and assert attach fails. Verifier/log-message subtests find a program by name, enable autoload, install a log buffer, expect skeleton load to fail, and assert the log contains the expected rejection text. `tracing_deny` first verifies the target BTF id exists and skips otherwise.

## Dependencies and Integration
Depends on `tracing_failure.skel.h`, libbpf program autoload/log APIs, vmlinux BTF lookup, and tracing attach policy in the kernel.

## Risks and Test Signals
Risks include exact verifier message drift, kernel config dependency for `__rcu_read_lock`, and changed allowed/denied target policy. Signals are attach failure for spin lock/unlock programs and load failure logs containing the expected policy messages.
