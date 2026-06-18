<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_devmap_tailcall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_devmap_tailcall.c

## Purpose

Tests tail calls from XDP programs that interact with devmap-style execution. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 29 source lines. BPF sections: `xdp`, `.maps`, `xdp`. Map types declared or referenced: `BPF_MAP_TYPE_PROG_ARRAY`. Important helper/kfunc surface: `bpf_helpers`, `bpf_tail_call`, `bpf_tracing`. Important C functions and entry points include `xdp_devmap`, `xdp_entry`. Notable globals or configuration/result fields include `int xdp_devmap(struct xdp_md *ctx)`; `int xdp_entry(struct xdp_md *ctx)`.

## Control Flow

`xdp_entry` tail-calls through a prog array into `xdp_devmap`; fallback behavior is visible if the tail call misses.

## State And Persistence Behavior

`xdp_map` is a program array initialized with the callee program. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Program-array initialization and expected attach type must be compatible with tail-call target. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run entry program and verify the tail-call path's return action. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_devmap_tailcall.c -->
