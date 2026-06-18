<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_devmap_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_devmap_helpers.c

## Purpose

Tests DEVMAP redirect and devmap-entry program execution. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 50 source lines. BPF sections: `.maps`, `xdp`, `xdp`, `xdp/devmap`, `xdp.frags/devmap`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_DEVMAP`. Important helper/kfunc surface: `bpf_devmap_val`, `bpf_helpers`, `bpf_redirect_map`, `bpf_trace_printk`. Important C functions and entry points include `xdp_redir_prog`, `xdp_dummy_prog`, `xdp_dummy_dm`, `xdp_dummy_dm_frags`. Notable globals or configuration/result fields include `int xdp_redir_prog(struct xdp_md *ctx)`; `int xdp_dummy_prog(struct xdp_md *ctx)`; `int xdp_dummy_dm(struct xdp_md *ctx)`; `int xdp_dummy_dm_frags(struct xdp_md *ctx)`.

## Control Flow

The primary XDP program redirects to `dm_ports`; a plain `xdp` dummy program is intentionally invalid for devmap entries, while `xdp/devmap` logs ingress/egress ifindexes and passes.

## State And Persistence Behavior

`dm_ports` stores device redirect targets. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Expected attach type validation must reject the plain XDP entry program for devmap use. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Attempt both valid and invalid devmap program configurations and verify redirect results. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_devmap_helpers.c -->
