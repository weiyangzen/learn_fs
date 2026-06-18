<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_timestamp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_timestamp.c

## Purpose
Initializes the per-network-namespace default for conntrack flow timestamping from a module parameter.

## Important APIs, Types, and Functions
Defines module parameter `tstamp` backed by `nf_ct_tstamp` and function `nf_conntrack_tstamp_pernet_init(struct net *net)`, which copies that default into `net->ct.sysctl_tstamp`.

## Control Flow
During conntrack per-net initialization, core code calls `nf_conntrack_tstamp_pernet_init()`. The function performs a direct assignment; runtime changes are then controlled by the per-net sysctl when timestamp support is enabled.

## State and Persistence
Global `nf_ct_tstamp` stores the module default. Each namespace stores its mutable runtime setting in `net->ct.sysctl_tstamp`. Actual per-connection timestamp extensions are managed elsewhere.

## Dependencies and Integration Points
Depends on conntrack timestamp extension headers and module parameter infrastructure. Integrates with `nf_conntrack_core.c` per-net initialization and `nf_conntrack_standalone.c` sysctl/proc delta-time output.

## Risks
The file is intentionally small; the main risk is assuming module parameter changes automatically rewrite existing net namespaces. They do not: this function only seeds per-net defaults at init.

## Test Signals
Load conntrack with `tstamp=0` and `tstamp=1`, create new namespaces, check `nf_conntrack_timestamp` sysctl defaults, and verify `/proc/net/nf_conntrack` shows `delta-time` only when timestamping is enabled and timestamp extensions exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_timestamp.c -->
