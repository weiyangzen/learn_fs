# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/atomics.c

## Purpose

Non-arena BPF atomic operation test program. It exercises add/sub/and/or/xor/cmpxchg/xchg over global and stack values from raw tracepoint programs filtered by PID. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

Raw tracepoint sections `add`, `sub`, `and`, `or`, `xor`, `cmpxchg`, `xchg`; GCC/C11 atomic builtins; globals such as `add64_value`, `cmpxchg64_result_succeed`, `process pid`; and `skip_tests` feature gating.

## Control Flow

Each raw tracepoint program returns unless current TGID matches `pid`. Enabled paths perform one atomic family and store old/new values in globals for userspace validation. Unsupported builds set `skip_tests`.

## State and Persistence Behavior

Global BSS/data variables hold operands and results. Stack-local atomic tests copy stack values into globals to verify side effects.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It depends on raw tracepoint attach and BPF atomic instruction support.

## Risks and Edge Cases

Atomic codegen differs by compiler features; stack atomic operations and no-return atomic variants are verifier/JIT-sensitive.

## Test Signals

Expected old values, updated values, and stack copies for each atomic family, or a skip flag on unsupported builds.
