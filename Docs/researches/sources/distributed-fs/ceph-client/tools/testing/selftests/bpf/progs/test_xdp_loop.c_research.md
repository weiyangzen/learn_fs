<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_loop.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_loop.c

## Purpose

Loop-friendly XDP IP tunnel transmitter variant. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 230 source lines. BPF sections: `.maps`, `.maps`, `xdp`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_PERCPU_ARRAY`. Important helper/kfunc surface: `bpf_compiler`, `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_map_lookup_elem`, `bpf_ntohs`, `bpf_xdp_adjust_head`. Important C functions and entry points include `_xdp_tx_iptunnel`. Notable globals or configuration/result fields include `int _xdp_tx_iptunnel(struct xdp_md *xdp)`.

## Control Flow

It parses tunnel packets with bounded loops/helpers, updates RX counters, looks up VIP-to-tunnel mappings, and adjusts headroom for encapsulation.

## State And Persistence Behavior

`rxcnt` and `vip2tnl` maps persist counters and tunnel config. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Bounded loop verification and packet pointer lifetime after helper calls are the main edges. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Configured IPv4/IPv6 tunnel packets should produce expected encapsulated output and counter increments. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_loop.c -->
