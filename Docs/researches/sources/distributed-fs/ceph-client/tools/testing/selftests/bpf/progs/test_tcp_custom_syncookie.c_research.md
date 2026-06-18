<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_custom_syncookie.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_custom_syncookie.c

## Purpose

Implements custom TCP syncookie handling in TC, covering option parsing, cookie encoding, SYN-ACK generation, ACK validation, and reqsk assignment kfunc/helper behavior. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 591 source lines. BPF sections: `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_csum_diff`, `bpf_endian`, `bpf_get_prandom_u32`, `bpf_helpers`, `bpf_htonl`, `bpf_htons`, `bpf_kfuncs`, `bpf_loop`, `bpf_misc`, `bpf_ntohl`, `bpf_ntohs`, `bpf_redirect`, `bpf_sk_assign_tcp_reqsk`, `bpf_sk_release`, `bpf_skb_change_tail`, `bpf_skc_lookup_tcp`, `bpf_skc_to_tcp_sock`, `bpf_sock`, `bpf_sock_tuple`, `bpf_tcp_req_attrs`, `bpf_tracing_net`. Important C functions and entry points include `tcp_custom_syncookie`. Notable globals or configuration/result fields include `bool handled_syn, handled_ack`; `int tcp_custom_syncookie(struct __sk_buff *skb)`.

## Control Flow

The TC program loads Ethernet/IP/TCP headers, handles SYN without ACK by validating headers/options, building a siphash cookie, writing TCP options, swapping endpoints, recomputing checksums, trimming skb tail, and redirecting; non-SYN packets validate ACK cookies and call `bpf_sk_assign_tcp_reqsk` on a listening socket.

## State And Persistence Behavior

`handled_syn` and `handled_ack` are observable globals; packet headers and discovered listening sockets drive transitions. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

TCP option bounds, checksum correctness, skb tail resizing, socket reference release, and cookie bit layout are all security-sensitive. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The selftest should drive IPv4/IPv6 SYN and ACK handshakes with expected MSS/window/SACK/ECN options and verify both globals plus connection establishment. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_custom_syncookie.c -->
