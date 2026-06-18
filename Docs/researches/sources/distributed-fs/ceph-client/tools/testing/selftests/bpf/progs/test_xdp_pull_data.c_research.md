<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_pull_data.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_pull_data.c

## Purpose

Tests `bpf_xdp_pull_data` in fragmented XDP programs. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 48 source lines. BPF sections: `xdp.frags`, `xdp.frags`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_xdp_pull_data`. Important C functions and entry points include `xdp_find_sizes`, `xdp_pull_data_prog`. Notable globals or configuration/result fields include `int xdpf_sz`; `int sinfo_sz`; `int data_len`; `int pull_len`; `int xdp_find_sizes(struct xdp_md *ctx)`; `int xdp_pull_data_prog(struct xdp_md *ctx)`.

## Control Flow

`xdp_find_sizes` records frame/sinfo/data sizes; `xdp_pull_data_prog` pulls a requested length into the linear area.

## State And Persistence Behavior

`xdpf_sz`, `sinfo_sz`, `data_len`, and `pull_len` are globals for harness control and observation. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Fragmented XDP support and pull length bounds differ from linear XDP frames. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run on fragmented frames and validate size globals before and after pull. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_pull_data.c -->
