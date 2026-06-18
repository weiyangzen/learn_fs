# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sock_fields.c

Research item: `subset-b-006814` ordinal `128`. Source size: 7500 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sock_fields.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `cgroup_skb/egress`, `cgroup_skb/ingress`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_linum_array_idx`, `bpf_spinlock_cnt`, `bpf_spin_lock`, `bpf_tcp_sock`, `bpf_sock`, `bpf_htonl`, `bpf_map_update_elem`, `bpf_ntohs`, `bpf_sk_fullsock`, `bpf_skc_to_tcp_sock`, `bpf_sk_cgroup_id`, `bpf_sk_ancestor_cgroup_id`, `bpf_sk_storage_get`, `bpf_spin_unlock`, and 1 more.
- Declared maps: `linum_map: BPF_MAP_TYPE_ARRAY, max __NR_BPF_LINUM_ARRAY_IDX, key __u32, value __u32`, `sk_pkt_out_cnt: BPF_MAP_TYPE_SK_STORAGE, key int, value struct bpf_spinlock_cnt`, `sk_pkt_out_cnt10: BPF_MAP_TYPE_SK_STORAGE, key int, value struct bpf_spinlock_cnt`
- Key local types: `struct bpf_spinlock_cnt`, `struct bpf_spin_lock`, `struct tcp_sock`, `struct bpf_tcp_sock`, `struct sockaddr_in6`, `struct bpf_sock`, `struct __sk_buff`, `enum bpf_linum_array_idx`
- Main functions/subprograms: `is_loopback6`, `skcpy`, `tpcpy`, `egress_read_sock_fields`, `ingress_read_sock_fields`, `sk_dst_port__load_word`, `sk_dst_port__load_half`, `sk_dst_port__load_byte`, `read_sk_dst_port`

## Control Flow
Entry programs are attached through `cgroup_skb/egress`, `cgroup_skb/ingress`. Control is organized around `is_loopback6`, `skcpy`, `tpcpy`, `egress_read_sock_fields`, `ingress_read_sock_fields`, `sk_dst_port__load_word`, `sk_dst_port__load_half`, `sk_dst_port__load_byte`, `read_sk_dst_port`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `linum_map: BPF_MAP_TYPE_ARRAY, max __NR_BPF_LINUM_ARRAY_IDX, key __u32, value __u32`, `sk_pkt_out_cnt: BPF_MAP_TYPE_SK_STORAGE, key int, value struct bpf_spinlock_cnt`, `sk_pkt_out_cnt10: BPF_MAP_TYPE_SK_STORAGE, key int, value struct bpf_spinlock_cnt`. Global data/control fields include `listen_tp`, `srv_sa6`, `cli_tp`, `srv_tp`, `listen_sk`, `srv_sk`, `cli_sk`, `parent_cg_id`, `child_cg_id`, `lsndtime`, and 1 more.. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `netinet/in.h`, `stdbool.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sock_fields.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `enum bpf_linum_array_idx {` | `READ_SK_DST_PORT_LINUM_IDX,` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} linum_map SEC(".maps");` | `struct bpf_spinlock_cnt {` | `struct bpf_spin_lock lock;` | `__uint(type, BPF_MAP_TYPE_SK_STORAGE);` | `__type(value, struct bpf_spinlock_cnt);` | and 45 more marker lines
