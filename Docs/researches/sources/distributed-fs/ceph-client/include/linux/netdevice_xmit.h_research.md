# sources/distributed-fs/ceph-client/include/linux/netdevice_xmit.h

## Purpose
This header defines per-execution-context transmit bookkeeping used by `netdevice.h` and the network transmit path. It isolates recursion and batching fields from the larger netdevice interface.

## Important APIs, Types, and Functions
The only concrete type is `struct netdev_xmit`. It contains `recursion` for nested transmit detection, `more` for batching/doorbell decisions, optional `skip_txqueue` for egress handling, optional mirred action nesting state, and optional `nf_dup_skb_recursion` for duplicate netdevice netfilter recursion control. `MIRRED_NEST_LIMIT` is four when mirred actions are enabled.

## Control Flow
The structure is embedded in per-CPU `softnet_data` on non-RT kernels and in current task state on PREEMPT_RT through helpers in `netdevice.h`. Transmit code increments/decrements recursion, sets `more` before driver transmit, and consults recursion fields to prevent unbounded re-entry from virtual devices, mirred actions, or netfilter duplication.

## State and Persistence
State is transient and scoped to a CPU or task. It is not durable and should be treated as hot-path scratch state. Conditional fields mean layout changes with kernel config.

## Dependencies and Integration Points
The header depends on `CONFIG_NET_ACT_MIRRED`, `CONFIG_NET_EGRESS`, and `CONFIG_NF_DUP_NETDEV`, and forward-declares `struct net_device`. Consumers are transmit helpers, traffic-control mirred action code, egress path, and netfilter duplication path.

## Risks
Incorrect recursion accounting can cause stack overflow, packet loops, or false-positive drops. Incorrect `more` handling can delay TX doorbells or hurt batching. Config-dependent fields make direct layout assumptions unsafe.

## Test Signals
Exercise nested virtual-device transmission, mirred redirect/mirror chains, NF_DUP_NETDEV paths, PREEMPT_RT and non-RT builds, and batching behavior where `xmit_more` changes TX completion latency or throughput.
