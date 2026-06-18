# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/neigh.c

Purpose: tracks neighbour entries used by representor TC tunnel encapsulations and updates offloaded flows when ARP/ND state or MAC addresses change.

Important APIs/functions: `mlx5e_rep_neigh_init`, `mlx5e_rep_neigh_cleanup`, `mlx5e_rep_neigh_entry_lookup`, `mlx5e_rep_neigh_entry_create`, `mlx5e_rep_neigh_entry_release`, and `mlx5e_rep_queue_neigh_stats_work`.

Control flow: init creates an rhashtable, RCU list, encap mutex, delayed stats work, computes the minimum neighbour probe interval, and registers a netevent notifier. Neighbour update events allocate work in atomic context, hold the neighbour and hash entry, then under RTNL snapshot neighbour MAC/state and update each attached encap flow through `mlx5e_rep_update_flows`. Periodic stats work walks the RCU list with refcounted entries and updates neighbour-used values. Delay-probe updates adjust flow-counter sampling when relevant devices change.

State and persistence: `neigh_update` holds the hashtable, list, lock, notifier, and delayed work. Each `mlx5e_neigh_hash_entry` stores key, device, encap list, refcount, and RCU node. State is runtime only and tied to representor lifetime.

Dependencies and integration: uses ARP/ND neighbour tables, netevent notifier, flow counters, TC encap update hooks, RTNL, rhashtable, RCU, and tracepoints.

Risks: refcount/RCU/list interactions are delicate because neighbour events can race with encap detach and cleanup. Cleanup flushes the workqueue before destroying the table, so any new notifier event after unregister must be impossible.

Test signals: IPv4 and IPv6 neighbour updates, neighbour device changes, encap attach/detach races, delay-probe interval changes, cleanup with queued work, and flow reoffload after MAC change.
