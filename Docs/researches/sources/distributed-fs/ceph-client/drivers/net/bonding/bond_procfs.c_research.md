<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_procfs.c -->
## sources/distributed-fs/ceph-client/drivers/net/bonding/bond_procfs.c

Purpose: this file implements `/proc/net/bonding/<bond-name>` reporting. It presents a human-readable snapshot of bond-level settings, link monitoring status, ARP/NS targets, active/primary slave state, and per-slave status, including 802.3ad aggregator and LACP PDU details for privileged readers.

Important APIs, types, and functions: the seq-file iterator is `bond_info_seq_ops`, with `bond_info_seq_start()`, `bond_info_seq_next()`, `bond_info_seq_stop()`, and `bond_info_seq_show()`. Report rendering is split between `bond_info_show_master()` and `bond_info_show_slave()`. Lifecycle helpers are `bond_create_proc_entry()`, `bond_remove_proc_entry()`, `bond_create_proc_dir()`, and `bond_destroy_proc_dir()`.

Control flow: opening the proc file uses `pde_data()` to recover the `struct bonding` pointer. Iteration starts with `SEQ_START_TOKEN` for the master section and then walks slaves with `bond_for_each_slave_rcu()`. The show path prints the driver version, current bonding mode, optional fail-over MAC or transmit-hash policy, primary/current active slave details, MII and ARP monitor configuration, 802.3ad bond state, and then one slave block per slave. Creation happens per network namespace under `/proc/net/bonding`, and each bond creates a named proc entry when the bond appears.

State and persistence: this file does not own state beyond `bond->proc_entry` and `bond->proc_file_name`. It reads live bond and slave fields under RCU, including `curr_active_slave`, `primary_slave`, `params`, link status, speed, duplex, permanent hardware address, queue id, and LACP port/aggregator state.

Dependencies and integration points: it integrates with procfs, seq_file, network namespaces, `bond_net_id`, RCU slave iteration, capability checks via `capable(CAP_NET_ADMIN)`, and 802.3ad helpers such as `__bond_3ad_get_active_agg_info()` and `bond_3ad_churn_desc()`. The output depends on option lookup through `bond_opt_get_val()` for stable textual names.

Risks: output is a snapshot assembled while the bond is changing, so readers should tolerate transient `None`, `N/A`, or zero aggregator data. Privileged 802.3ad details are intentionally gated by `CAP_NET_ADMIN`; changes here can expose peer/system identifiers. Proc entry removal relies on the stored original file name, so rename handling must keep `proc_file_name` consistent.

Test signals: create and delete bonds across network namespaces, read proc output while enslaving/releasing devices, verify active-backup and 802.3ad sections, confirm capability-gated LACP fields are hidden from unprivileged readers, exercise ARP/NS target display, and validate cleanup after bond removal and namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_procfs.c -->
