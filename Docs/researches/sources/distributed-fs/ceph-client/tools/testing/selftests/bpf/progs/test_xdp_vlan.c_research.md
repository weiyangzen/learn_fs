<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_vlan.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_vlan.c

## Purpose

Demonstrates and tests XDP/TC VLAN parsing, VLAN ID changes, VLAN pop by head adjustment, and TC VLAN push. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 279 source lines. BPF sections: `license`, `xdp`, `xdp`, `xdp`, `xdp`, `tc`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_ntohs`, `bpf_skb_vlan_push`, `bpf_xdp_adjust_head`. Important C functions and entry points include `parse_eth_frame`, `xdp_drop_vlan_4011`, `xdp_vlan_change`, `xdp_vlan_remove_outer`, `shift_mac_4bytes_32bit`, `xdp_vlan_remove_outer2`, `tc_vlan_push`. Notable globals or configuration/result fields include `bool parse_eth_frame(struct ethhdr *eth, void *data_end, struct parse_pkt *pkt)`; `int xdp_drop_vlan_4011(struct xdp_md *ctx)`; `int xdp_vlan_change(struct xdp_md *ctx)`; `int xdp_vlan_remove_outer(struct xdp_md *ctx)`; `int xdp_vlan_remove_outer2(struct xdp_md *ctx)`; `int tc_vlan_push(struct __sk_buff *ctx)`.

## Control Flow

Shared parser detects outer/inner VLAN tags; XDP programs drop VLAN 4011, rewrite VLAN to 0, remove outer VLAN by moving MAC addresses and adjusting head, and TC pushes VLAN tags.

## State And Persistence Behavior

No maps; packet headers are rewritten. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Network byte order, double-tag parsing, overlapping memmove, and packet head adjustment must be exact. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Send tagged and untagged frames and verify drop/pass, VLAN rewrite/removal, and TC push behavior. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_vlan.c -->
