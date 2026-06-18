<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs.c

## Purpose

Covers BPF-to-BPF calls, static and global subprograms, CO-RE relocations in subprograms, and `bpf_loop` callbacks. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 124 source lines. BPF sections: `license`, `.maps`, `raw_tp/sys_enter`, `raw_tp/sys_exit`, `raw_tp/sys_enter`, `raw_tp/sys_exit`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`. Important helper/kfunc surface: `bpf_core_read`, `bpf_get_current_task`, `bpf_helpers`, `bpf_loop`, `bpf_map_lookup_elem`. Important C functions and entry points include `prog1`, `prog2`, `prog3`, `prog4`. Notable globals or configuration/result fields include `int res1 = 0`; `int res2 = 0`; `int res3 = 0`; `int res4 = 0`; `int prog1(void *ctx)`; `int prog2(void *ctx)`; `int prog3(void *ctx)`; `int prog4(void *ctx)`.

## Control Flow

Raw tracepoint programs call arithmetic subprogram chains, use `BPF_CORE_READ` on current task fields, and update result globals; later programs invoke `bpf_loop` callbacks.

## State And Persistence Behavior

`res1` through `res4` are output globals; an array map exists to exercise helper calls from subprograms. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Verifier and loader must preserve CO-RE relocation records in multi-function `.text` and track helper side effects through noinline calls. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Expected result globals are deterministic after sys_enter/sys_exit triggers and loop callback execution. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs.c -->
