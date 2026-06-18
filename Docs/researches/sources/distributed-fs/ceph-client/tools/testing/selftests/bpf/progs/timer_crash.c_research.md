<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_crash.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_crash.c

## Purpose

Regression test for corrupted timer pointer handling during map update/cancel paths. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 54 source lines. BPF sections: `.maps`, `.maps`, `fentry/do_nanosleep`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_HASH`. Important helper/kfunc surface: `bpf_get_current_task_btf`, `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_spin_lock`, `bpf_timer`, `bpf_timer_cancel`, `bpf_tracing`. Important C functions and entry points include `sys_enter`. Notable globals or configuration/result fields include `int pid = 0`; `int crash_map = 0; /* 0 for amap, 1 for hmap */`; `int sys_enter(void *ctx)`.

## Control Flow

On `do_nanosleep` for a selected pid, it writes a map value whose first word is deliberately poisoned and then updates array/hash timer maps or cancels the hash timer.

## State And Persistence Behavior

`pid` selects the task and `crash_map` chooses array vs hash map path. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Kernel timer cleanup must not trust overwritten timer internals enough to crash. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run both `crash_map` modes and ensure the kernel survives with expected selftest outcome. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_crash.c -->
