# sources/distributed-fs/ceph-client/net/netfilter/nf_bpf_link.c

## Purpose
`nf_bpf_link.c` implements BPF link attachment for netfilter hooks. It lets users create `BPF_LINK_TYPE_NETFILTER` links that register a BPF program as an IPv4 or IPv6 netfilter hook, optionally enabling IP defragmentation before the program runs.

## Important APIs, Types, And Functions
`struct bpf_nf_link` embeds `struct bpf_link`, owns an `nf_hook_ops`, tracks the target net namespace, and stores an optional defrag hook module reference. `bpf_nf_link_attach()` validates attributes, allocates/primes the BPF link, optionally calls `bpf_nf_enable_defrag()`, registers `nf_register_net_hook()`, and settles the link. `nf_hook_run_bpf()` builds `struct bpf_nf_ctx` and executes the program.

Verifier integration is provided through `netfilter_verifier_ops`: `nf_is_valid_access()` exposes read-only `skb` and `state` fields as trusted BTF pointers, and `bpf_nf_func_proto()` returns base helpers. Link lifecycle is handled by release, detach, deferred dealloc, fdinfo, link-info, and unsupported update operations.

## Control Flow
Attach validates protocol family, hook number, flags, and priority. Defrag requests require priority after conntrack defrag and dynamically request `nf_defrag_ipv4` or `nf_defrag_ipv6` if the hook is not registered. Link release is idempotent via `cmpxchg(&dead, 0, 1)`, unregisters the hook, disables defrag, and drops the netns tracker.

## State And Persistence
State is in-memory per link: hook ops, net namespace reference, defrag module reference, and a `dead` flag. The link FD owns lifetime; no durable state exists.

## Dependencies And Integration Points
This code integrates BPF link core, verifier/BTF, netfilter hook registration, net namespace lifetime tracking, and optional netfilter defrag modules. `BPF_F_NETFILTER_IP_DEFRAG` is reported in link info when active.

## Risks
Priority validation is security-sensitive because defrag and conntrack confirm ordering must remain intact. Module references around RCU defrag hooks must avoid unload races. Release must be idempotent across FD close and explicit detach. Verifier rules must remain strict: writes are rejected and only trusted `sk_buff` and `nf_hook_state` pointers are exposed.

## Test Signals
Test attach/detach for IPv4/IPv6 hook points, invalid family/hook/priority/flags, defrag auto-module loading and cleanup, link info/fdinfo, namespace teardown with live links, verifier rejection of invalid context access, and packet verdict behavior.
