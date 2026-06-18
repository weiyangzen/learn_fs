<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_cpumap_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_cpumap_helpers.c

## Purpose

Tests redirecting to CPUMAP and executing CPUMAP programs. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 47 source lines. BPF sections: `.maps`, `xdp`, `xdp`, `xdp/cpumap`, `xdp.frags/cpumap`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_CPUMAP`. Important helper/kfunc surface: `bpf_cpumap_val`, `bpf_get_smp_processor_id`, `bpf_helpers`, `bpf_redirect_map`. Important C functions and entry points include `xdp_redir_prog`, `xdp_dummy_prog`, `xdp_dummy_cm`, `xdp_dummy_cm_frags`. Notable globals or configuration/result fields include `__u32 redirect_count = 0`; `int xdp_redir_prog(struct xdp_md *ctx)`; `int xdp_dummy_prog(struct xdp_md *ctx)`; `int xdp_dummy_cm(struct xdp_md *ctx)`; `int xdp_dummy_cm_frags(struct xdp_md *ctx)`.

## Control Flow

A normal XDP program redirects to `cpu_map`; cpumap program increments `redirect_count` on CPU 0, drops loopback ingress, and otherwise passes.

## State And Persistence Behavior

`cpu_map` and `redirect_count` are observable state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

CPU affinity and ingress ifindex checks make results topology-sensitive. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Redirect packets through cpumap and verify counter/action behavior. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_cpumap_helpers.c -->
