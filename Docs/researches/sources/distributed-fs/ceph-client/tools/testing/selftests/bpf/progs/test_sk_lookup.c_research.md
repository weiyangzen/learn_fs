# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_lookup.c

Research item: `subset-b-006814` ordinal `117`. Source size: 18993 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_lookup.c_research.md`.

## Purpose
The code assigns or selects sockets from maps based on tuple fields, exercising `sk_lookup`, `sk_reuseport`, and libbpf attach paths. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sk_lookup`, `sk_reuseport`
- BPF helpers/macros used: `bpf_endian`, `bpf_helpers`, `bpf_htonl`, `bpf_htons`, `bpf_sk_lookup`, `bpf_sock`, `bpf_map_lookup_elem`, `bpf_sk_assign`, `bpf_sk_release`, `bpf_sk_select_reuseport`, `bpf_printk`, `bpf_map_update_elem`
- Declared maps: `redir_map: BPF_MAP_TYPE_SOCKMAP, max MAX_SOCKS, key __u32, value __u64`, `run_map: BPF_MAP_TYPE_ARRAY, max 2, key int, value int`
- Key local types: `struct bpf_sk_lookup`, `struct sk_reuseport_md`, `struct bpf_sock`
- Main functions/subprograms: `lookup_pass`, `lookup_drop`, `check_ifindex`, `reuseport_pass`, `reuseport_drop`, `redir_port`, `redir_ip4`, `redir_ip6`, `select_sock_a`, `select_sock_a_no_reuseport`, `select_sock_b`, `sk_assign_eexist`, `sk_assign_replace_flag`, `sk_assign_null`, `access_ctx_sk`, `ctx_narrow_access`, and 8 more.

## Control Flow
Entry programs are attached through `sk_lookup`, `sk_reuseport`. Control is organized around `lookup_pass`, `lookup_drop`, `check_ifindex`, `reuseport_pass`, `reuseport_drop`, `redir_port`, `redir_ip4`, `redir_ip6`, `select_sock_a`, `select_sock_a_no_reuseport`, `select_sock_b`, `sk_assign_eexist`, and 12 more.. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Several branches converge through `goto` cleanup paths, which is typical for reference-release or error-return validation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `redir_map: BPF_MAP_TYPE_SOCKMAP, max MAX_SOCKS, key __u32, value __u64`, `run_map: BPF_MAP_TYPE_ARRAY, max 2, key int, value int`. Global data/control fields include `KEY_PROG1`, `KEY_PROG2`, `PROG_DONE`, `KEY_SERVER_A`, `KEY_SERVER_B`, `SRC_PORT`, `SRC_IP4`, `SRC_IP6`, `DST_PORT`, `DST_IP4`, and 2 more.. The program deliberately persists observations through maps or event buffers for user-space assertions. Socket references acquired from maps or helpers are explicitly released to satisfy verifier lifetime rules.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `errno.h`, `stdbool.h`, `stddef.h`, `linux/bpf.h`, `linux/in.h`, `sys/socket.h`, `bpf/bpf_endian.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Risks include socket reference handling, host/network byte order, `bpf_sk_assign` flag semantics, and expected errno behavior.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sk_lookup.c` is a test fixture for socket lookup and reuseport BPF selftest. Test signals are: trace output helps diagnose unexpected helper return values.
High-signal code markers observed: `#include <bpf/bpf_endian.h>` | `#include <bpf/bpf_helpers.h>` | `bpf_htonl((((__u32)(a) & 0xffU) << 24) |	\` | `{ bpf_htonl(aaaa), bpf_htonl(bbbb), bpf_htonl(cccc), bpf_htonl(dddd) }` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} redir_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} run_map SEC(".maps");` | `static const __u16 SRC_PORT = bpf_htons(8008);` | `SEC("sk_lookup")` | and 56 more marker lines
