<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_spin_lock_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_spin_lock_fail.c

## Purpose

Negative verifier tests for spin-lock identity, global locks, map-value locks, inner-map locks, kptr allocations, and sleepable-helper calls while locked. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 317 source lines. BPF sections: `.maps`, `.maps`, `.data.A`, `.data.B`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?syscall`, `?syscall`, `?syscall`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_ARRAY_OF_MAPS`. Important helper/kfunc surface: `bpf_copy_from_user`, `bpf_copy_from_user_str`, `bpf_experimental`, `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_obj_drop`, `bpf_obj_new`, `bpf_printk`, `bpf_spin_lock`, `bpf_spin_unlock`, `bpf_this_cpu_ptr`, `bpf_tracing`. Important C functions and entry points include `lock_id_kptr_preserve`, `lock_id_global_zero`, `lock_id_mapval_preserve`, `lock_id_innermapval_preserve`, `lock_id_mismatch_mapval_mapval`, `lock_id_mismatch_innermapval_innermapval1`, `lock_id_mismatch_innermapval_innermapval2`, `global_subprog`, `lock_global_subprog_call1`, `lock_global_subprog_call2`, `lock_global_sleepable_helper_subprog`, `lock_global_sleepable_kfunc_subprog`, `lock_global_sleepable_subprog_indirect`. Notable globals or configuration/result fields include `int lock_id_kptr_preserve(void *ctx)`; `int lock_id_global_zero(void *ctx)`; `int lock_id_mapval_preserve(void *ctx)`; `int lock_id_innermapval_preserve(void *ctx)`; `int lock_id_mismatch_mapval_mapval(void *ctx)`; `int lock_id_mismatch_innermapval_innermapval1(void *ctx)`; `int lock_id_mismatch_innermapval_innermapval2(void *ctx)`; `int global_subprog(struct __sk_buff *ctx)`.

## Control Flow

Many optional `?tc` and `?syscall` programs deliberately lock one object and unlock another, or call helpers/kfuncs through subprograms while lock state is active.

## State And Persistence Behavior

State includes an array map value with a lock, a map-in-map reference to it, and two global locks in separate `.data` sections. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

If lock IDs are not preserved through `bpf_this_cpu_ptr`, map-in-map lookup, kptr allocation, or subprogram calls, the verifier could accept unsafe unlocks or reject valid identity preservation. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness expects specific verifier failures or successes; log messages should identify lock-id mismatch and disallowed sleepable operations. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_spin_lock_fail.c -->
