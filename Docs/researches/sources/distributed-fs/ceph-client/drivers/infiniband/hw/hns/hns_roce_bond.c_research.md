# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_bond.c

Purpose: Implements RoCE bonding support over Linux bonding/LAG netdevices for HNS RoCE PFs. It tracks bond groups per PCI bus, reacts to netdev notifier events, switches RDMA client instances between normal and bonded modes, and programs hardware bond state.

Important APIs/types/functions: `hns_roce_alloc_bond_grp()` creates up to two bond groups per bus and registers netdevice notifiers. `hns_roce_dealloc_bond_grp()` tears them down. `hns_roce_bond_init()` recovers or sets netdev binding during client init. `hns_roce_bond_suspend()`/`hns_roce_bond_resume()` unregister and restore notifiers across reset. Internal helpers include `hns_roce_set_bond()`, `hns_roce_clear_bond()`, `hns_roce_slave_changestate()`, `hns_roce_slave_change_num()`, and `hns_roce_set_bond_netdev()`.

Control flow: A global xarray maps bus numbers to `hns_roce_die_info`. CHANGEUPPER and CHANGELOWERSTATE events are filtered to supported bond masters and known slaves. Work is deferred by one second. The worker recomputes support and slave maps, clears unsupported bonds, creates a new bond from `NOT_BONDED`, or sends change commands for active-state and slave-count changes. Active-backup mode follows the active slave; hash mode picks active RDMA ports and supports only hash types through L23.

State and persistence: `hns_roce_bond_group` persists across events and carries upper netdev, main RoCE device, slave maps, active maps, bus/bond IDs, TX/hash mode, ready flag, state machine value, mutex, notifier, and delayed work. `hns_roce_die_info` persists per bus with bond slots and suspend nesting count.

Dependencies and integration: Depends on Linux bonding/LAG APIs, RDMA netdev lookup, HNS3 `hnae3_handle`, hardware v2 bond commands, and external helpers such as `hns_roce_bond_init_client()`, `hns_roce_bond_uninit_client()`, `hns_roce_cmd_bond()`, `roce_del_all_netdev_gids()`, and `rdma_roce_rescan_port()`.

Risks: The code assumes `netdev_master_upper_dev_get_rcu()` returns a device before `dev_hold()`, so null handling depends on notifier context. State transitions mix mutex-protected and unprotected assignments; reset/suspend paths must avoid notifier races. Main-device switching can temporarily uninit clients. Test signals include bond create/delete, active-backup failover, hash mode slave changes, netdev unregister, PF reset recovery, SR-IOV/VF rejection, same-bus enforcement, and concurrent notifier storms.
