# sources/distributed-fs/ceph-client/net/netfilter/xt_TEE.c

Purpose: `TEE` target duplicates matching packets to a configured gateway, optionally through a named output interface.

Important APIs/types/functions: `struct tee_net`, `struct xt_tee_priv`, `tee_tg4()`, `tee_tg6()`, `tee_tg_check()`, `tee_tg_destroy()`, netdevice notifier, and exported static key `xt_tee_enabled`.

Control flow: check rejects zero gateway, optionally allocates interface-tracking private state, resolves ifindex, links into per-net list, and increments static key. Runtime calls IPv4/IPv6 duplicate helper and continues original traversal. Netdevice events maintain ifindex. Destroy unlinks private state and decrements static key.

State and persistence: per-rule private interface state, per-net lists, netdevice notifier, and global static key. Dependencies include x_tables, nf_dup, net namespaces, netdevice events, and routing. Risks: interface rename/unregister races, duplication loops, static key balance, and init unwind. Test signals: duplication with/without interface, device register/rename/unregister, zero gateway rejection, static key inc/dec, notifier failure, and destroy cleanup.
