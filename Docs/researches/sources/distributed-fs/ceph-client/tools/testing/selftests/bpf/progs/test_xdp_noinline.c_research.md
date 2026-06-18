<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_noinline.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_noinline.c

## Purpose

Large noinline XDP load-balancer/verifier stress program modeled after production packet processing. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 811 source lines. BPF sections: `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `xdp`, `xdp`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_LRU_HASH`, `BPF_MAP_TYPE_PERCPU_ARRAY`. Important helper/kfunc surface: `bpf_compiler`, `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_ktime_get_ns`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_ntohs`, `bpf_prog_run`, `bpf_xdp_adjust_head`. Important C functions and entry points include `jhash`, `__jhash_nwords`, `jhash_2words`, `parse_udp`, `parse_tcp`, `encap_v6`, `encap_v4`, `swap_mac_and_send`, `send_icmp_reply`, `send_icmp6_reply`, `parse_icmpv6`, `parse_icmp`, `get_packet_hash`, `balancer_ingress_v4`, `balancer_ingress_v6`. Notable globals or configuration/result fields include `bool parse_udp(void *data, void *data_end,`; `bool parse_tcp(void *data, void *data_end,`; `bool encap_v6(struct xdp_md *xdp, struct ctl_value *cval,`; `bool encap_v4(struct xdp_md *xdp, struct ctl_value *cval,`; `int swap_mac_and_send(void *data, void *data_end)`; `int send_icmp_reply(void *data, void *data_end)`; `int send_icmp6_reply(void *data, void *data_end)`; `int parse_icmpv6(void *data, void *data_end, __u64 off,`.

## Control Flow

It parses IPv4/IPv6, TCP/UDP, and ICMP, computes jhash-based real selection, checks LRU connection state, updates stats, performs IPv4/IPv6 encapsulation via head adjustment, and handles ICMP replies.

## State And Persistence Behavior

Maps include VIP metadata, LRU connection cache, consistent-hash rings, real backends, stats, and control values. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Noinline call depth, map pointer flow, checksum/header writes, and verifier complexity are the important risks. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Load-time verifier success plus packet tests for VIP lookup, real selection, stats, and encapsulation are expected. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_noinline.c -->
