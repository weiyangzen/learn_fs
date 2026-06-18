# sources/distributed-fs/ceph-client/include/linux/bpf-netns.h

Purpose: Defines the network-namespace BPF attachment management interface for hooks whose scope is a `struct net`, currently flow dissector and socket lookup. It provides attach-type conversion and configuration-dependent stubs.

Important APIs/types/functions: `to_netns_bpf_attach_type()` maps `BPF_FLOW_DISSECTOR` and `BPF_SK_LOOKUP` to internal `NETNS_BPF_*` values, returning `NETNS_BPF_INVALID` for unsupported attach types. `netns_bpf_mutex` serializes updates to netns BPF state. With `CONFIG_NET`, exported functions are `netns_bpf_prog_query()`, `netns_bpf_prog_attach()`, `netns_bpf_prog_detach()`, and `netns_bpf_link_create()`.

Control flow: BPF syscall attach/link paths convert a UAPI attach type, lock `netns_bpf_mutex`, and update per-netns BPF state in `net/netns/bpf.h`. Runtime hooks then consult the per-namespace program/link state from networking paths.

State/persistence: State is per-network namespace and protected for updates by the global mutex. The header itself does not own state beyond declaring the mutex. Without `CONFIG_NET`, all operations return `-EOPNOTSUPP`.

Dependencies/integration: Depends on net namespace BPF definitions, UAPI BPF attach types, and BPF program/link syscalls. Integrates with flow dissector and `sk_lookup` networking paths.

Risks/test signals: Risks include attach-type mismatches, cross-netns leakage, failure to hold `netns_bpf_mutex` during updates, and stale links on namespace teardown. Test signals include BPF selftests for flow dissector and sk_lookup in multiple network namespaces, namespace create/delete while links exist, attach/query/detach error paths, and `CONFIG_NET=n` build coverage.
