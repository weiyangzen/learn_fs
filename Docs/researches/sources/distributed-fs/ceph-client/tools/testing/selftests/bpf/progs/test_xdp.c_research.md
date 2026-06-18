<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp.c

## Purpose

Classic XDP IP-in-IP tunnel transmitter test using direct packet parsing and `bpf_xdp_adjust_head`. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 234 source lines. BPF sections: `.maps`, `.maps`, `xdp`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_PERCPU_ARRAY`. Important helper/kfunc surface: `bpf_compiler`, `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_map_lookup_elem`, `bpf_ntohs`, `bpf_xdp_adjust_head`. Important C functions and entry points include `_xdp_tx_iptunnel`. Notable globals or configuration/result fields include `int _xdp_tx_iptunnel(struct xdp_md *xdp)`.

## Control Flow

The XDP program parses IPv4/IPv6 and TCP/UDP headers, looks up VIP tunnel info, prepends tunnel headers, updates counters, and returns TX/redirect-style actions.

## State And Persistence Behavior

`rxcnt` per-CPU counters and `vip2tnl` tunnel configuration map persist state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Head adjustment invalidates pointers, and tunnel map keys must match parsed VIP fields and byte order. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Feed configured VIP packets and inspect counters plus resulting encapsulated frames. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp.c -->
