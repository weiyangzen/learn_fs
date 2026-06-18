# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_lookup_kern.c

Research item: `subset-b-006814` ordinal `118`. Source size: 4038 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_lookup_kern.c_research.md`.

## Purpose
The code assigns or selects sockets from maps based on tuple fields, exercising `sk_lookup`, `sk_reuseport`, and libbpf attach paths. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `?tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_sock_tuple`, `bpf_htons`, `bpf_sock`, `bpf_sk_lookup_tcp`, `bpf_printk`, `bpf_sk_release`
- Declared maps: None visible in this compact source.
- Key local types: `struct bpf_sock_tuple`, `struct iphdr`, `struct ipv6hdr`, `struct __sk_buff`, `struct ethhdr`, `struct bpf_sock`
- Main functions/subprograms: `sk_lookup_success`, `sk_lookup_success_simple`, `err_use_after_free`, `err_modify_sk_pointer`, `err_modify_sk_or_null_pointer`, `err_no_release`, `err_release_twice`, `err_release_unchecked`, `lookup_no_release`, `err_no_release_subcall`

## Control Flow
Entry programs are attached through `?tc`. Control is organized around `sk_lookup_success`, `sk_lookup_success_simple`, `err_use_after_free`, `err_modify_sk_pointer`, `err_modify_sk_or_null_pointer`, `err_no_release`, `err_release_twice`, `err_release_unchecked`, `lookup_no_release`, `err_no_release_subcall`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness. Socket references acquired from maps or helpers are explicitly released to satisfy verifier lifetime rules.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `stdbool.h`, `string.h`, `linux/bpf.h`, `linux/if_ether.h`, `linux/in.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/pkt_cls.h`, `linux/tcp.h`, `sys/socket.h`, `bpf/bpf_helpers.h`, and 1 more..
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Risks include socket reference handling, host/network byte order, `bpf_sk_assign` flag semantics, and expected errno behavior.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sk_lookup_kern.c` is a test fixture for socket lookup and reuseport BPF selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior, trace output helps diagnose unexpected helper return values.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `char _license[] SEC("license") = "GPL";` | `static struct bpf_sock_tuple *get_tuple(void *data, __u64 nh_off,` | `struct bpf_sock_tuple *result;` | `if (eth_proto == bpf_htons(ETH_P_IP)) {` | `result = (struct bpf_sock_tuple *)&iph->saddr;` | `} else if (eth_proto == bpf_htons(ETH_P_IPV6)) {` | `result = (struct bpf_sock_tuple *)&ip6h->saddr;` | `SEC("?tc")` | and 10 more marker lines
