
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_xdp.c

Purpose: Maintains an RCU-protected mapping from net devices to flowtables for XDP/non-hardware-offload flowtable setup.

Important APIs and functions: `nf_flowtable_by_dev()` returns the first flowtable associated with a device under caller-held RCU read lock. `nf_flowtable_by_dev_insert()` adds a flowtable element to the per-device list, creating the hashtable node if needed. `nf_flowtable_by_dev_remove()` removes a flowtable association and frees empty device nodes after `synchronize_rcu()`. `nf_flow_offload_xdp_setup()` handles bind/unbind commands.

Control flow: Setup bind inserts `(dev -> flowtable)` under `nf_xdp_hashtable_lock`; unbind removes matching list entries and tears down an empty bucket node after readers quiesce. Lookup hashes the device pointer and returns the first registered flowtable.

State and persistence: State is an in-memory hashtable keyed by `struct net_device *` address and lists of `struct flow_offload_xdp_ft`. It is not persisted.

Dependencies and integration: Called from `nf_flow_table_offload_setup()` when hardware offload is not enabled. XDP users call `nf_flowtable_by_dev()` to locate the flowtable for a device.

Risks: The mapping assumes a device should belong to a single flowtable but stores a list and returns the first element, so duplicate binds can be surprising. Other risks are pointer-key lifetime, RCU list deletion, memory allocation failure during bind, and ensuring unbind is called before device memory reuse. Test signals include bind/unbind, duplicate bind ordering, concurrent lookup/removal, and netdevice teardown.
