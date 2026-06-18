# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_change_tail.c

Research item: `subset-b-006814` ordinal `130`. Source size: 1085 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_change_tail.c_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sk_skb`
- BPF helpers/macros used: `bpf_helpers`, `bpf_skb_pull_data`, `bpf_skb_change_tail`
- Declared maps: `sock_map_rx: BPF_MAP_TYPE_SOCKMAP, max 1, key int, value int`
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `prog_skb_verdict`

## Control Flow
Entry programs are attached through `sk_skb`. Control is organized around `prog_skb_verdict`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `sock_map_rx: BPF_MAP_TYPE_SOCKMAP, max 1, key int, value int`. Global data/control fields include `change_tail_ret`, `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sockmap_change_tail.c` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} sock_map_rx SEC(".maps");` | `SEC("sk_skb")` | `bpf_skb_pull_data(skb, 1);` | `return SK_PASS;` | `change_tail_ret = bpf_skb_change_tail(skb, skb->len - 1, 0);` | `change_tail_ret = bpf_skb_change_tail(skb, skb->len + 1, 0);` | `change_tail_ret = bpf_skb_change_tail(skb, BPF_SKB_MAX_LEN, 0);` | `char _license[] SEC("license") = "GPL";`
