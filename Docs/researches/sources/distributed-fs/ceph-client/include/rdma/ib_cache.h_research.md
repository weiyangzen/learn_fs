# sources/distributed-fs/ceph-client/include/rdma/ib_cache.h

Purpose: declares cached accessors for RDMA device GID, P_Key, LMC, and port-state information. It hides provider queries behind software caches and reference-counted GID attributes.

Important APIs and types: GID APIs include `rdma_query_gid()`, `rdma_find_gid()`, `rdma_find_gid_by_port()`, `rdma_find_gid_by_filter()`, `rdma_get_gid_attr()`, `rdma_hold_gid_attr()`, `rdma_put_gid_attr()`, `rdma_query_gid_table()`, `rdma_read_gid_hw_context()`, `rdma_read_gid_l2_fields()`, `rdma_read_gid_attr_ndev_rcu()`, and `rdma_is_zero_gid()`. P_Key and port helpers include `ib_get_cached_pkey()`, `ib_find_cached_pkey()`, `ib_get_cached_lmc()`, and `ib_get_cached_port_state()`.

Control flow: cache users query by device/port/index or search by GID/type/netdevice. Returned `ib_gid_attr` objects must be held/put according to cache lifetime rules, and RCU-only netdevice access must occur under RCU protection. Consumers use cached P_Key/LMC/port state to initialize QPs, path records, CM messages, and address handles without synchronously querying hardware.

State and persistence: state lives in RDMA core per-device caches populated from hardware and netdev events. This header declares access, reference, and lookup functions; cache contents are runtime-only and update as ports/GIDs/netdevices change.

Dependencies and integration points: depends on `ib_verbs.h`, `ib_gid_attr`, userspace GID table entries, netdevice references, and provider cache maintenance. It integrates RDMA CM, SA, verbs, RoCE address selection, and user queries with the device cache.

Risks and test signals: risks include leaking or using after put of `ib_gid_attr`, RCU misuse for netdevices, stale GID/P_Key after netdev or port changes, wrong GID type selection for RoCE v1/v2, and index bounds errors. Test GID add/remove events, VLAN netdevice changes, P_Key table updates, port down/up transitions, userspace GID table queries, and refcount/RCU debugging.
