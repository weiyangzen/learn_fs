# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_storage_tracing.c

Research item: `subset-b-006814` ordinal `120`. Source size: 2306 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_storage_tracing.c_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tp_btf/inet_sock_set_state`, `fentry/inet_csk_listen_start`, `fentry/tcp_connect`, `fexit/inet_csk_accept`, `tp_btf/tcp_retransmit_synack`, `tp_btf/tcp_bad_csum`
- BPF helpers/macros used: `bpf_tracing`, `bpf_core_read`, `bpf_helpers`, `bpf_sk_storage_get`, `bpf_sk_storage_delete`, `bpf_get_current_pid_tgid`, `bpf_get_current_task`, `bpf_core_read_str`
- Declared maps: `sk_stg_map: BPF_MAP_TYPE_SK_STORAGE, key int, value struct sk_stg`, `del_sk_stg_map: BPF_MAP_TYPE_SK_STORAGE, key int, value int`
- Key local types: `struct sk_stg`, `struct sock`, `struct task_struct`, `struct proto_accept_arg`, `struct request_sock`, `struct sk_buff`
- Main functions/subprograms: `BPF_PROG`, `set_task_info`

## Control Flow
Entry programs are attached through `tp_btf/inet_sock_set_state`, `fentry/inet_csk_listen_start`, `fentry/tcp_connect`, `fexit/inet_csk_accept`, `tp_btf/tcp_retransmit_synack`, `tp_btf/tcp_bad_csum`. Control is organized around `BPF_PROG`, `set_task_info`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `sk_stg_map: BPF_MAP_TYPE_SK_STORAGE, key int, value struct sk_stg`, `del_sk_stg_map: BPF_MAP_TYPE_SK_STORAGE, key int, value int`. Global data/control fields include `task_comm`, `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `vmlinux.h`, `bpf/bpf_tracing.h`, `bpf/bpf_core_read.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sk_storage_tracing.c` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_tracing.h>` | `#include <bpf/bpf_core_read.h>` | `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_SK_STORAGE);` | `} sk_stg_map SEC(".maps");` | `} del_sk_stg_map SEC(".maps");` | `SEC("tp_btf/inet_sock_set_state")` | `stg = bpf_sk_storage_get(&sk_stg_map, sk, 0,` | `BPF_SK_STORAGE_GET_F_CREATE);` | `bpf_sk_storage_delete(&del_sk_stg_map, sk);` | and 13 more marker lines
