<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_neigh.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_neigh.c

## Purpose

Tests neighbor redirection helper behavior for IPv4 and IPv6 TC programs. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 136 source lines. BPF sections: `tc`, `tc`, `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_endian`, `bpf_helpers`, `bpf_redirect_neigh`, `bpf_skb_store_bytes`. Important C functions and entry points include `tc_chk`, `tc_dst`, `tc_src`. Notable globals or configuration/result fields include `volatile const __u32 IFINDEX_SRC`; `volatile const __u32 IFINDEX_DST`; `int tc_chk(struct __sk_buff *skb)`; `int tc_dst(struct __sk_buff *skb)`; `int tc_src(struct __sk_buff *skb)`.

## Control Flow

`tc_chk` classifies remote endpoint packets, while `tc_dst` and `tc_src` rewrite MAC/IP fields and call `bpf_redirect_neigh` toward configured ifindexes.

## State And Persistence Behavior

`IFINDEX_SRC` and `IFINDEX_DST` are const volatile inputs. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Neighbor resolution and endpoint detection are sensitive to byte order and namespace topology. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Send IPv4/IPv6 traffic through the veth topology and verify redirect direction and header rewrites. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_neigh.c -->
