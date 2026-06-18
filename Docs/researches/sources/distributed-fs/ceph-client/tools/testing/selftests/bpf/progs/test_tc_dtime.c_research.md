<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_dtime.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_dtime.c

## Purpose

Validates delivery-time (`skb->tstamp`) propagation and clearing across end-host and forwarding namespace TC hooks. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 392 source lines. BPF sections: `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_endian`, `bpf_fwd`, `bpf_helpers`, `bpf_redirect_neigh`, `bpf_skb_set_tstamp`. Important C functions and entry points include `egress_host`, `ingress_host`, `ingress_fwdns_prio100`, `egress_fwdns_prio100`, `ingress_fwdns_prio101`, `egress_fwdns_prio101`. Notable globals or configuration/result fields include `volatile const __u32 IFINDEX_SRC`; `volatile const __u32 IFINDEX_DST`; `__u32 dtimes[__NR_TESTS][__MAX_CNT] = {}`; `__u32 errs[__NR_TESTS][__MAX_CNT] = {}`; `__u32 test = 0`; `int egress_host(struct __sk_buff *skb)`; `int ingress_host(struct __sk_buff *skb)`; `int ingress_fwdns_prio100(struct __sk_buff *skb)`.

## Control Flow

Six TC programs classify test traffic by IP family/protocol/source namespace, set magic timestamps, use `bpf_skb_set_tstamp`, and redirect with `bpf_redirect_neigh`.

## State And Persistence Behavior

`dtimes[test][stage]` and `errs[test][stage]` arrays record observed timestamp paths; `test`, `IFINDEX_SRC`, and `IFINDEX_DST` are harness-controlled. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Forwarding vs local delivery has subtle timestamp semantics; route forwarding and BPF forwarding paths intentionally differ. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run IPv4/IPv6 TCP/UDP and route-forwarding cases and compare `dtimes`/`errs` matrices. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_dtime.c -->
