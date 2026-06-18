# sources/distributed-fs/ceph-client/net/core/net-procfs.c

## Purpose

`net-procfs.c` creates procfs views for core network device and softnet state. It implements `/proc/net/dev`, `/proc/net/softnet_stat`, `/proc/net/ptype`, and `/proc/net/dev_mcast`, with per-network-namespace registration through pernet operations.

## Important APIs, Types, And Functions

The file uses seq_file iterators around `struct net_device`, `struct softnet_data`, and `struct packet_type`. `dev_seq_start()`, `dev_seq_next()`, and `dev_seq_stop()` iterate devices under RCU and `dev_seq_show()` prints the `/proc/net/dev` header and statistics using `dev_get_stats()`. Softnet iteration uses `softnet_get_online()` and `softnet_seq_show()` to expose per-online-CPU counters and queue lengths. Packet type iteration uses `struct ptype_iter_state`, `ptype_get_idx()`, `ptype_seq_next()`, and `ptype_seq_show()` to list packet handlers from device-specific, namespace, and global ptype lists. Multicast address output uses `dev_mc_seq_show()`.

Registration is performed by `dev_proc_net_init()`, `dev_proc_net_exit()`, `dev_mc_net_init()`, `dev_mc_net_exit()`, and exported initialization entry `dev_proc_init()`.

## Control Flow

When a network namespace is initialized, `dev_proc_net_init()` creates `dev`, `softnet_stat`, and `ptype` entries under `net->proc_net`, then initializes wireless extensions proc support. Failure unwinds entries in reverse order. A second pernet registration creates `dev_mcast`. Reads enter seq_file callbacks, take RCU where needed, locate the current object from the logical position, format one row, then release locks in `stop`.

The packet-type iterator first walks each device `ptype_all` list, then namespace-level `ptype_all`, namespace-level `ptype_specific`, and finally the global `ptype_base` hash buckets. It stores the current device in `ptype_iter_state` so formatting can show the device column and so next iteration can continue efficiently.

## State And Persistence Behavior

The file owns no durable state. It exposes live counters and lists from `net_device`, `softnet_data`, packet type registries, and multicast address lists. Proc entries are per-netns and are removed when the namespace exits.

## Dependencies And Integration Points

It depends on procfs, seq_file, net namespace proc directories, RCU device iteration helpers, per-CPU `softnet_data`, wireless extension proc hooks, packet type lists, and multicast address locking. `/proc/net/dev` output is a compatibility ABI consumed by many user-space tools.

## Risks

Iterator correctness is the main risk. Position handling must remain stable enough for seq_file even when devices or packet handlers change concurrently. The ptype traversal spans several list families and must filter by namespace to avoid leaking handlers across namespaces. `/proc/net/dev` formatting is ABI-sensitive; column changes can break parsers. Softnet output intentionally skips offline CPUs, so the printed CPU index must remain explicit.

## Test Signals

Useful tests read these proc files in multiple network namespaces while creating/removing interfaces, registering packet sockets, changing multicast memberships, and toggling CPUs if possible. Regression checks should compare `/proc/net/dev` column compatibility and validate that ptype/dev_mcast output does not expose another namespace's devices.
