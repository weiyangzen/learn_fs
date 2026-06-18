<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_spin_lock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_spin_lock.c

## Purpose

Runtime and verifier coverage for `bpf_spin_lock` in hash-map values, cgroup local storage, array queue state, and global `.data` locks across subprograms. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 169 source lines. BPF sections: `.maps`, `.maps`, `.maps`, `cgroup_skb/ingress`, `.data.A`, `tc`, `tc`, `tc`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_CGROUP_STORAGE`, `BPF_MAP_TYPE_HASH`. Important helper/kfunc surface: `bpf_cgroup_storage_key`, `bpf_get_local_storage`, `bpf_helpers`, `bpf_ktime_get_ns`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_misc`, `bpf_spin_lock`, `bpf_spin_lock_test`, `bpf_spin_unlock`, `bpf_vqueue`. Important C functions and entry points include `bpf_spin_lock_test`, `lock_static_subprog_call`, `lock_static_subprog_lock`, `lock_static_subprog_unlock`. Notable globals or configuration/result fields include `int bpf_spin_lock_test(struct __sk_buff *skb)`; `int lock_static_subprog_call(struct __sk_buff *ctx)`; `int lock_static_subprog_lock(struct __sk_buff *ctx)`; `int lock_static_subprog_unlock(struct __sk_buff *ctx)`.

## Control Flow

The cgroup ingress program initializes a hash entry, toggles a counter under lock, updates a token-bucket-like queue under lock, and increments cgroup storage under lock. Three TC programs test lock ownership across static subprogram calls.

## State And Persistence Behavior

Map values hold counters and spin locks; `lockA` is a hidden global lock in `.data.A` used to validate global-lock tracking. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Verifier lock state must not be lost across branches or subprogram calls; unlocking a lock acquired elsewhere and nested helper access around locks are sensitive cases. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Expected signals are successful verifier load, no runtime `err`, and correct acceptance/rejection of the lock/subprogram patterns. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_spin_lock.c -->
