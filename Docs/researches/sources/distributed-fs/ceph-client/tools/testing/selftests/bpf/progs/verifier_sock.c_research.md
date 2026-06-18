# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sock.c

## Purpose
`verifier_sock.c` is a broad verifier fixture for socket-related pointer types, helper return types, reference ownership, context field access, packet pointer invalidation, and tail-call side effects. It tests `bpf_sock`, `bpf_tcp_sock`, socket maps, reuseport maps, XSK maps, socket local storage, and packet/XDP contexts.

## Important APIs, Types, and Functions
The file uses `vmlinux.h` types, map declarations for `BPF_MAP_TYPE_REUSEPORT_SOCKARRAY`, `BPF_MAP_TYPE_SOCKHASH`, `BPF_MAP_TYPE_SOCKMAP`, `BPF_MAP_TYPE_XSKMAP`, `BPF_MAP_TYPE_SK_STORAGE`, and `BPF_MAP_TYPE_PROG_ARRAY`. It exercises helpers such as `bpf_sk_fullsock`, `bpf_tcp_sock`, `bpf_sk_release`, `bpf_sk_storage_get`, `bpf_map_lookup_elem`, `bpf_sk_select_reuseport`, `bpf_skc_to_tcp_sock`, `bpf_skc_to_tcp_request_sock`, `bpf_skb_pull_data`, `bpf_xdp_pull_data`, and `bpf_tail_call_static`.

## Control Flow
Early cgroup/skb tests inspect `skb->sk` and verify required null checks before dereferencing or converting to fullsock/tcp_sock types. Middle sections validate allowed and forbidden field offsets, narrow loads, and access past field boundaries. TC, XDP, sk_skb, reuseport, cgroup post-bind, and sock-create sections test helper availability and context-field restrictions. Later global functions call pull-data helpers or static tail calls, then the caller dereferences stale packet pointers to confirm invalidation reaches across global calls and tail-call paths.

## State and Persistence
Persistent state is map-based and verifier-visible: socket maps can return referenced socket pointers; sk-storage values include a spin lock in `struct val`; the prog array supports static tail-call tests. Reference state is critical because sockmap lookups must be released with `bpf_sk_release`.

## Dependencies and Integration Points
The file integrates many BPF program types: `cgroup/skb`, `tc`, `xdp`, `sk_skb`, `sk_reuseport`, `cgroup/post_bind4`, `cgroup/post_bind6`, and `cgroup/sock_create`. It depends on BTF/vmlinux field offsets, helper prototypes, and verifier-specific pointer classes like `sock_common_or_null`, `sock_or_null`, `tcp_sock_or_null`, packet pointers, and map-value pointers.

## Risks and Test Signals
Risks include allowing null socket dereferences, exposing fields not valid for a program type, leaking socket references, failing to reject invalid map/helper combinations, or missing packet pointer invalidation after helpers and tail calls. Test signals include verifier errors such as `invalid mem access`, `invalid sock access`, `invalid tcp_sock access`, `R1 must be referenced when passed to release function`, `Unreleased reference`, and success cases that return zero after properly checked dereferences.
