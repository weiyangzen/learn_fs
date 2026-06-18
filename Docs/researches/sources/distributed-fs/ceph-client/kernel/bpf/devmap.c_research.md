# sources/distributed-fs/ceph-client/kernel/bpf/devmap.c

## Purpose
`devmap.c` implements `BPF_MAP_TYPE_DEVMAP` and `BPF_MAP_TYPE_DEVMAP_HASH`, the map backends used by XDP `bpf_redirect_map()` to redirect packets to net devices. It is optimized for lockless datapath lookup under RCU while keeping updates, deletions, flushes, and netdevice unregister cleanup coherent.

## Important APIs, types, and functions
`struct bpf_dtab` is the map container; array maps use `netdev_map`, while hash maps use `dev_index_head`, `index_lock`, `items`, and `n_buckets`. `struct bpf_dtab_netdev` is the map value object containing the netdev reference, optional devmap XDP program, RCU head, key/index, and exposed `bpf_devmap_val`. `struct xdp_dev_bulk_queue` is a per-CPU transmit queue attached to a netdevice. Public integration functions include `dev_xdp_enqueue()`, `dev_map_enqueue()`, `dev_map_enqueue_multi()`, `dev_map_generic_redirect()`, `dev_map_redirect_multi()`, and `__dev_flush()`. Map ops are exported through `dev_map_ops` and `dev_map_hash_ops`.

## Control flow
Allocation validates key/value sizes and flags, forces `BPF_F_RDONLY_PROG`, allocates either an array of RCU netdev pointers or a power-of-two hash table, and links the map into `dev_map_list` for notifier scans. Updates copy `bpf_devmap_val`, resolve the ifindex with `dev_get_by_index()`, optionally acquire an XDP program fd compatible with `BPF_XDP_DEVMAP`, then publish the new object with `xchg()` for array maps or under `index_lock` for hash maps. Old entries are freed by RCU callback. Deletion removes the entry with `xchg()` or `hlist_del_init_rcu()` and schedules `__dev_map_entry_free()`.

The datapath looks up entries under RCU/local BH protection. XDP frame redirects validate target XDP transmit support, scatter-gather support, and MTU using `xdp_ok_fwd_dev()`, then enqueue frames in the target device's per-CPU bulk queue. `bq_xmit_all()` optionally runs a devmap-attached XDP program, transmits via `ndo_xdp_xmit`, frees unsent frames, resets the queue count, and emits tracepoints. Broadcast/multi redirect clones all but the final frame/SKB and can exclude ingress and upper devices.

## State and persistence behavior
The map persists netdevice references and optional BPF program references until update/delete/free. Per-CPU bulk queues live on netdevices with `ndo_xdp_xmit` and are allocated on `NETDEV_REGISTER`. Map free unlinks from the global list, waits for RCU and any earlier entry-free callbacks, then frees all entries and backing storage. Netdevice unregister scans all devmaps and removes matching entries before the device disappears.

## Dependencies and integration points
This file is tightly coupled with XDP redirect core (`__bpf_xdp_redirect_map()`), netdevice notifier infrastructure, `netdev_ops->ndo_xdp_xmit`, generic XDP SKB transmit, trace events, RCU, local locks, and BPF map ops. It depends on drivers calling `xdp_do_flush()` before leaving NAPI poll so queued frames are transmitted outside the lookup critical path.

## Risks and test signals
Important risks are RCU lifetime bugs, stale netdev references during unregister, flush-list leaks, incorrect clone/free ownership in multi redirect, unsupported XDP feature handling, and races among syscall update/delete, BPF redirect, and notifier removal. Tests should exercise array and hash map update/delete/lookup, value sizes with and without prog fd, redirect to devices lacking `ndo_xdp_xmit` or SG support, broadcast with ingress exclusion, netdevice unregister cleanup, XDP program actions on devmap egress, generic SKB redirect drops, and map free after pending RCU callbacks.
