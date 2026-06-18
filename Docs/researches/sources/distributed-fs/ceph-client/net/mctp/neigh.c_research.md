# sources/distributed-fs/ceph-client/net/mctp/neigh.c

Purpose: implements the MCTP neighbour table: static EID-to-link-layer-address mappings, RTNL new/delete/get neighbour handlers, lookup for packet output, and per-net namespace initialization.

Important APIs and functions: `mctp_neigh_add()`, `mctp_neigh_remove_dev()`, `mctp_neigh_remove()`, `mctp_rtm_newneigh()/delneigh()/getneigh()`, `mctp_fill_neigh()`, and `mctp_neigh_lookup()`.

Control flow and state: neighbours are stored in `net->mctp.neighbours`, protected by `neigh_lock` for mutation and RCU for lookup/dump. Entries hold an `mctp_dev` ref and are freed by RCU callback. Netlink add validates EID, lladdr presence and length; delete matches device/EID/static source; lookup returns copied hardware address or `-EHOSTUNREACH`.

Dependencies and integration: used by `route.c` output when a route does not carry direct hardware address. Integrates with RTNL neighbour messages and `device.c` unregister cleanup.

Risks and test signals: there are TODOs for immediate RTM_DELNEIGH notifications and richer state. `mctp_neigh_net_exit()` schedules frees without list deletion but net namespace teardown owns the list lifetime. Tests should cover duplicate add, wrong lladdr length, output next-hop lookup, dump filtering, and device unregister cleanup.
