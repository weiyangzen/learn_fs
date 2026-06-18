<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_dynptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_dynptr.c

## Purpose

Dynptr-based version of the XDP IP tunnel transmitter. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 256 source lines. BPF sections: `.maps`, `.maps`, `xdp`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_PERCPU_ARRAY`. Important helper/kfunc surface: `bpf_dynptr`, `bpf_dynptr_from_xdp`, `bpf_dynptr_slice`, `bpf_dynptr_slice_rdwr`, `bpf_dynptr_write`, `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_kfuncs`, `bpf_map_lookup_elem`, `bpf_ntohs`, `bpf_xdp_adjust_head`. Important C functions and entry points include `_xdp_tx_iptunnel`. Notable globals or configuration/result fields include `int _xdp_tx_iptunnel(struct xdp_md *xdp)`.

## Control Flow

The program creates an XDP dynptr, uses dynptr slices to parse IPv4/IPv6 and transport headers, looks up tunnel config, adjusts headroom, and writes encapsulation headers.

## State And Persistence Behavior

`rxcnt` and `vip2tnl` mirror the classic XDP tunnel test. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Dynptr slice lifetimes, direct pointer invalidation after head adjustment, and fragment support are the key concerns. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run the same tunnel packet cases as `test_xdp.c` and compare counters/frames. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_dynptr.c -->
