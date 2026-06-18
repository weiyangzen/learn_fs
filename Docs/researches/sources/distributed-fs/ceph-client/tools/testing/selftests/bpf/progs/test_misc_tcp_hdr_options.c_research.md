# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_misc_tcp_hdr_options.c

Research item: `subset-b-006814` ordinal `75`. Source size: 8877 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_misc_tcp_hdr_options.c_research.md`.

## Purpose
The program reads packet data or skb context fields and validates verifier range tracking while parsing TCP/IP headers and options. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sockops`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_sock_ops`, `bpf_load_hdr_opt`, `bpf_getsockopt`, `bpf_reserve_hdr_opt`, `bpf_store_hdr_opt`, `bpf_sock_ops_kern`, `bpf_sock_ops_cb_flags_set`, `bpf_sock_ops_cb_flags`, `bpf_setsockopt`
- Declared maps: None visible in this compact source.
- Key local types: `struct bpf_sock_ops`, `struct tcphdr`, `struct ipv6hdr`, `struct tcp_exprm_opt`, `struct tcp_opt`
- Main functions/subprograms: `__check_active_hdr_in`, `check_active_syn_in`, `check_active_hdr_in`, `active_opt_len`, `write_active_opt`, `handle_hdr_opt_len`, `handle_write_hdr_opt`, `handle_parse_hdr`, `handle_passive_estab`, `misc_estab`

## Control Flow
Entry programs are attached through `sockops`. Control is organized around `__check_active_hdr_in`, `check_active_syn_in`, `check_active_hdr_in`, `active_opt_len`, `write_active_opt`, `handle_hdr_opt_len`, `handle_write_hdr_opt`, `handle_parse_hdr`, `handle_passive_estab`, `misc_estab`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `last_addr16_n`, `active_lport_n`, `active_lport_h`, `passive_lport_n`, `passive_lport_h`, `nodelay_est_ok`, `nodelay_hdr_len_reject`, `nodelay_write_hdr_reject`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `errno.h`, `stdbool.h`, `sys/types.h`, `sys/socket.h`, `linux/ipv6.h`, `linux/tcp.h`, `linux/socket.h`, `linux/bpf.h`, `linux/types.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: `test_tcp_hdr_options.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Packet boundary checks, dynptr slice validity, checksum/endian handling, and context-field writability are the main risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_misc_tcp_hdr_options.c` is a test fixture for packet/skb metadata and TCP parsing selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `__u16 last_addr16_n = __bpf_htons(1);` | `static int __check_active_hdr_in(struct bpf_sock_ops *skops, bool check_syn)` | `ret = bpf_load_hdr_opt(skops, &hdr.reg_opt, 2, load_flags);` | `ret = bpf_load_hdr_opt(skops, &hdr.reg_opt, sizeof(hdr.reg_opt),` | `ret = bpf_load_hdr_opt(skops, &hdr.exprm_opt, sizeof(hdr.exprm_opt),` | `hdr.exprm_opt.magic = __bpf_htons(0xeB9F);` | `hdr.exprm_opt.magic != __bpf_htons(0xeB9F))` | `ret = bpf_getsockopt(skops, SOL_TCP, TCP_BPF_SYN_IP, &hdr.ip6,` | and 29 more marker lines
