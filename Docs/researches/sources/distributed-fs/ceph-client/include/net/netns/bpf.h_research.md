# sources/distributed-fs/ceph-client/include/net/netns/bpf.h

Purpose: Defines per-network-namespace BPF attachment storage for namespace-scoped networking programs.

Important APIs/types/functions: `enum netns_bpf_attach_type` currently covers flow dissector and socket lookup attachment types. `struct netns_bpf` stores RCU `run_array` pointers, direct `progs`, and link lists per attach type.

Control flow: BPF attach/link operations update program arrays and link lists for a net namespace. Packet or socket lookup paths read `run_array` under RCU to execute programs.

State and persistence: Per-net runtime state only; program arrays and links must be RCU-safe and cleaned during namespace teardown.

Dependencies/integration: Depends on BPF program arrays, BPF links, RCU, flow dissector, and SK_LOOKUP hooks.

Risks/test signals: Test attach/detach/query, RCU replacement, namespace destruction with links, invalid attach type rejection, flow dissector behavior, and socket lookup program ordering.
