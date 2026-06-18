# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_ktls.c

Research item: `subset-b-006814` ordinal `135`. Source size: 830 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_ktls.c_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sk_msg`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_msg_cork_bytes`, `bpf_msg_push_data`, `bpf_msg_pop_data`, `bpf_msg_apply_bytes`, `bpf_msg_redirect_map`
- Declared maps: `sock_map: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`
- Key local types: `struct sk_msg_md`
- Main functions/subprograms: `prog_sk_policy`, `prog_sk_policy_redir`

## Control Flow
Entry programs are attached through `sk_msg`. Control is organized around `prog_sk_policy`, `prog_sk_policy_redir`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `sock_map: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`. Global data/control fields include `cork_byte`, `push_start`, `push_end`, `apply_bytes`, `pop_start`, `pop_end`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sockmap_ktls.c` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} sock_map SEC(".maps");` | `SEC("sk_msg")` | `bpf_msg_cork_bytes(msg, cork_byte);` | `bpf_msg_push_data(msg, push_start, push_end, 0);` | `bpf_msg_pop_data(msg, pop_start, pop_end, 0);` | `return SK_PASS;` | `bpf_msg_apply_bytes(msg, apply_bytes);` | and 1 more marker lines
