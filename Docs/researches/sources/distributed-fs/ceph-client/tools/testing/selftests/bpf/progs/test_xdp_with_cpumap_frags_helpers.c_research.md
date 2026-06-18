<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_cpumap_frags_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_cpumap_frags_helpers.c

## Purpose

Defines CPUMAP entry programs for normal and fragmented XDP frames. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 27 source lines. BPF sections: `.maps`, `xdp/cpumap`, `xdp.frags/cpumap`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_CPUMAP`. Important helper/kfunc surface: `bpf_cpumap_val`, `bpf_helpers`. Important C functions and entry points include `xdp_dummy_cm`, `xdp_dummy_cm_frags`. Notable globals or configuration/result fields include `int xdp_dummy_cm(struct xdp_md *ctx)`; `int xdp_dummy_cm_frags(struct xdp_md *ctx)`.

## Control Flow

Both cpumap programs return `XDP_PASS`; the map type and section names drive attach validation.

## State And Persistence Behavior

`cpu_map` stores CPU redirect targets. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Expected attach type differs for `xdp/cpumap` and `xdp.frags/cpumap`. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Populate cpumap entries with these programs and verify load/redirect acceptance. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_cpumap_frags_helpers.c -->
