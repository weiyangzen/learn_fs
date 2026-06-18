<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_devmap_frags_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_devmap_frags_helpers.c

## Purpose

Defines DEVMAP entry programs for linear and fragmented XDP frames. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 27 source lines. BPF sections: `.maps`, `xdp/devmap`, `xdp.frags/devmap`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_DEVMAP`. Important helper/kfunc surface: `bpf_devmap_val`, `bpf_helpers`. Important C functions and entry points include `xdp_dummy_dm`, `xdp_dummy_dm_frags`. Notable globals or configuration/result fields include `int xdp_dummy_dm(struct xdp_md *ctx)`; `int xdp_dummy_dm_frags(struct xdp_md *ctx)`.

## Control Flow

Both devmap programs return `XDP_PASS`; behavior is mainly attach-type validation.

## State And Persistence Behavior

`dm_ports` stores devmap entries. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

The loader must attach `xdp/devmap` and `xdp.frags/devmap` programs only to compatible devmap entries. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Populate devmap with these programs and validate redirects. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_devmap_frags_helpers.c -->
