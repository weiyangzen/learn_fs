<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_bpf_link.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_bpf_link.h

## Purpose
`nf_bpf_link.h` defines the BPF netfilter link attach context and conditional attach helper for BPF programs bound to netfilter hooks.

## Important APIs, types, and functions
It defines `struct bpf_nf_ctx` with hook state and skb pointers, and `bpf_nf_link_attach` or an `-EOPNOTSUPP` stub depending on CONFIG_NETFILTER_BPF_LINK.

## Control flow
BPF syscall attach code passes attributes and a program to `bpf_nf_link_attach`, producing a persistent link to a netfilter hook. BPF program context exposes the current skb and hook state.

## State and persistence
Link lifetime and hook registration state live in the implementation. The context is transient per invocation.

## Dependencies and integration points
It depends on BPF attr/prog forward declarations, nf_hook_state, skb, and CONFIG_NETFILTER_BPF_LINK. It integrates BPF link infrastructure with netfilter.

## Risks and test signals
Risks include disabled-build fallback handling, hook state lifetime, skb mutation safety, and link detach ordering. Tests should cover attach/detach, program execution, namespace hooks, and CONFIG off builds.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_bpf_link.h` completely for this pass (15 lines, 365 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_bpf_link.h -->
