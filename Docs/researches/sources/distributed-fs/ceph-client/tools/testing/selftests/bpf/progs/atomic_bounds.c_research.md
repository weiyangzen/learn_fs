# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/atomic_bounds.c

## Purpose

Verifier scalar-bounds regression for atomic fetch-add results. It checks whether the verifier can infer that a stack-local atomic fetch-add returns zero and therefore a `while (b)` loop is unreachable. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`SEC("fentry/bpf_fentry_test1")`, `BPF_PROG(sub, int x)`, `__sync_fetch_and_add()` on a stack local, compile-time `ENABLE_ATOMICS_TESTS`, and global `skip_tests`.

## Control Flow

When atomics tests are enabled, the fentry program initializes `a` to zero, assigns `b = __sync_fetch_and_add(&a, 1)`, and contains a loop guarded by `b`. Correct verifier reasoning treats `b` as certainly zero, so the program loads. Without atomics support the harness sees `skip_tests=true`.

## State and Persistence Behavior

Only BSS skip/result globals are used. No maps are declared.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here.

## Risks and Edge Cases

Feature gating must match compiler/kernel atomic support; otherwise expected verifier behavior can become architecture-dependent.

## Test Signals

Harness observes `skip_tests` or successful load/run with expected atomic bounds behavior.
