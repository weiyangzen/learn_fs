# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_listen.c

Research item: `subset-b-006814` ordinal `136`. Source size: 2841 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_listen.c_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sk_skb/stream_parser`, `sk_skb/stream_verdict`, `sk_skb`, `sk_msg`, `sk_reuseport`
- BPF helpers/macros used: `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_sk_redirect_map`, `bpf_sk_redirect_hash`, `bpf_msg_redirect_map`, `bpf_msg_redirect_hash`, `bpf_sk_select_reuseport`
- Declared maps: `sock_map: BPF_MAP_TYPE_SOCKMAP, max 2, key __u32, value __u64`, `nop_map: BPF_MAP_TYPE_SOCKMAP, max 2, key __u32, value __u64`, `sock_hash: BPF_MAP_TYPE_SOCKHASH, max 2, key __u32, value __u64`, `verdict_map: BPF_MAP_TYPE_ARRAY, max 2, key int, value unsigned int`, `parser_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`
- Key local types: `struct __sk_buff`, `struct sk_msg_md`, `struct sk_reuseport_md`
- Main functions/subprograms: `prog_stream_parser`, `prog_stream_verdict`, `prog_skb_verdict`, `prog_msg_verdict`, `prog_reuseport`

## Control Flow
Entry programs are attached through `sk_skb/stream_parser`, `sk_skb/stream_verdict`, `sk_skb`, `sk_msg`, `sk_reuseport`. Control is organized around `prog_stream_parser`, `prog_stream_verdict`, `prog_skb_verdict`, `prog_msg_verdict`, `prog_reuseport`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `sock_map: BPF_MAP_TYPE_SOCKMAP, max 2, key __u32, value __u64`, `nop_map: BPF_MAP_TYPE_SOCKMAP, max 2, key __u32, value __u64`, `sock_hash: BPF_MAP_TYPE_SOCKHASH, max 2, key __u32, value __u64`, `verdict_map: BPF_MAP_TYPE_ARRAY, max 2, key int, value unsigned int`, `parser_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`. Global data/control fields include `test_sockmap`, `test_ingress`, `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `errno.h`, `stdbool.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sockmap_listen.c` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} sock_map SEC(".maps");` | `} nop_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_SOCKHASH);` | `} sock_hash SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} verdict_map SEC(".maps");` | `} parser_map SEC(".maps");` | `SEC("sk_skb/stream_parser")` | and 16 more marker lines
