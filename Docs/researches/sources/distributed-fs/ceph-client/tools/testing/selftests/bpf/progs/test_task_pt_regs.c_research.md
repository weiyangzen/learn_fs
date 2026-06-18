<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_pt_regs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_pt_regs.c

## Purpose

Tests retrieving a task's saved pt_regs from BPF and comparing it with the active uprobe context. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 36 source lines. BPF sections: `uprobe`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_get_current_task_btf`, `bpf_helpers`, `bpf_probe_read_kernel`, `bpf_task_pt_regs`, `bpf_tracing`. Important C functions and entry points include `handle_uprobe`. Notable globals or configuration/result fields include `char current_regs[PT_REGS_SIZE] = {}`; `char ctx_regs[PT_REGS_SIZE] = {}`; `int uprobe_res = 0`; `int handle_uprobe(struct pt_regs *ctx)`.

## Control Flow

The uprobe handler reads current task BTF, calls `bpf_task_pt_regs`, and uses `bpf_probe_read_kernel` to compare register bytes.

## State And Persistence Behavior

`uprobe_res` records the comparison result for user-space assertions. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Architecture-specific `struct pt_regs` size/layout and task state must match the uprobe context. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Trigger the uprobe and check `uprobe_res` for successful register matching. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_pt_regs.c -->
