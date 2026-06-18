# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sockmap_mutate.c

## Purpose
`verifier_sockmap_mutate.c` tests which program types may delete from, update, look up, and mutate `sockmap` and `sockhash` maps. It focuses on helper availability and context restrictions for socket-map mutation.

## Important APIs, Types, and Functions
The file declares `sockhash` as `BPF_MAP_TYPE_SOCKHASH` and `sockmap` as `BPF_MAP_TYPE_SOCKMAP`, both keyed by `__u32` and holding `__u64` values. Helpers include `bpf_map_delete_elem`, `bpf_map_update_elem`, `bpf_map_lookup_elem`, `bpf_sk_release`, `bpf_sock_map_update`, and `bpf_sock_hash_update`. Inline helper wrappers such as `test_sockmap_delete`, `test_sockmap_update`, `test_sockmap_lookup_and_update`, `test_sockmap_mutate`, and `test_sockmap_lookup_and_mutate` are reused across program types.

## Control Flow
The action/classifier/socket/XDP/sk_lookup/sk_reuseport paths call delete or update helper wrappers and return success values. Flow dissector and raw tracepoint cases deliberately use mutation or release patterns that should be rejected in some contexts. Sockops includes separate delete, generic update, and dedicated `bpf_sock_map_update`/`bpf_sock_hash_update` paths to distinguish generic map update restrictions from sockops-specific update helpers.

## State and Persistence
State is held in the two socket maps. Some helper paths look up a socket pointer from the map and release it, so reference lifetime is part of the verifier state. There is no external persistence beyond map contents at runtime.

## Dependencies and Integration Points
The file integrates with many program sections: `action`, `classifier`, `flow_dissector`, `iter/sockmap`, `raw_tp/kfree`, `sk_lookup`, `sk_reuseport`, `socket`, `sockops`, and `xdp`. It depends on helper allowlists per program type and verifier reference tracking for `struct bpf_sock *`.

## Risks and Test Signals
Risks include allowing sockmap mutation from unsafe contexts, disallowing supported contexts, or failing to enforce `bpf_sk_release` availability. Expected failure messages include `program of this type cannot use helper bpf_sk_release` and `cannot update sockmap in this context`. Success cases prove that deletes and updates remain permitted in intended hooks.
