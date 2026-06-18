# sources/distributed-fs/ceph-client/drivers/net/bonding/bond_alb.c

## Purpose
`bond_alb.c` implements bonding transmit load balancing (TLB) and adaptive load balancing (ALB, which adds receive load balancing through ARP manipulation). It assigns transmit flows to slaves, tracks per-slave load, periodically rebalances, manages per-slave MAC addresses, sends learning packets to update switches, rewrites ARP sender MACs for receive balancing, and maintains receive-client hash tables for ALB mode.

## Important APIs, Types, and Functions
- TLB functions include `tlb_initialize()`, `tlb_deinitialize()`, `tlb_choose_channel()`, `tlb_get_least_loaded_slave()`, and `tlb_clear_slave()`.
- RLB functions include `rlb_initialize()`, `rlb_deinitialize()`, `rlb_arp_recv()`, `rlb_arp_xmit()`, `rlb_choose_channel()`, `rlb_update_rx_clients()`, `rlb_rebalance()`, and hash-table list helpers.
- MAC/learning helpers include `alb_send_learning_packets()`, `alb_set_slave_mac_addr()`, `alb_swap_mac_addr()`, `alb_fasten_mac_swap()`, `alb_handle_addr_collision_on_attach()`, and `alb_change_hw_addr_on_detach()`.
- Exported bonding hooks include `bond_alb_initialize()`, `bond_alb_deinitialize()`, `bond_tlb_xmit()`, `bond_alb_xmit()`, `bond_alb_monitor()`, `bond_alb_init_slave()`, `bond_alb_deinit_slave()`, `bond_alb_handle_link_change()`, `bond_alb_handle_active_change()`, `bond_alb_set_mac_address()`, and `bond_alb_clear_vlan()`.

## Control Flow
Initialization allocates the TLB transmit hash table and, for ALB, the RLB receive hash table and ARP receive probe. Transmit selection first excludes broadcast/multicast and special IPv6 neighbor-discovery cases. TLB chooses a slave by `bond_xmit_hash()` and either dynamic load buckets or the prebuilt usable-slave array. ALB adds protocol-specific logic: IPv4/IPv6 unicast traffic is hashed by destination address, while ARP replies/requests may select a receive slave and rewrite ARP source MAC to that slave's address. `bond_do_alb_xmit()` falls back to the current active slave for unbalanced traffic and rewrites Ethernet source MAC when sending on non-active slaves.

RLB tracks clients by destination IP hash and maintains secondary source-IP lists to purge stale entries when another host starts using an IP. ARP replies create or update client assignments; monitor work sends ARP replies to tell clients which slave MAC to use. Periodic monitor work also sends switch learning packets for slaves and upper VLAN/macvlan devices, clears TLB bucket load histories on rebalance intervals, manages temporary promiscuity for disabled slave MAC teaching, runs requested RLB rebalance, and drains delayed client updates/retries.

MAC lifecycle is central. In ALB/RLB, slaves need distinct receive MACs while the current active slave owns the bond MAC. Active-slave changes may swap MAC addresses, clear affected TLB buckets, send learning packets, and schedule RLB client updates. Slave attach handles address collisions before insertion; detach repairs permanent-address ownership. TLB mode uses a lighter software `dev_addr` strategy because receive balancing is not active.

## State and Persistence
State lives in `bond->alb_info`, `SLAVE_TLB_INFO(slave)`, the TLB hash table, and the RLB hash table. Important fields include per-bucket assigned slave, load history, bytes, per-slave bucket list head/load, RLB client IP/MAC/vlan/slave assignments, used/source linked-list indexes, update flags, retry/delay counters, selected RLB receive slave, learning-packet counters, and temporary promiscuity state. There is no disk persistence; state is rebuilt on bond/slave initialization and continuously refreshed by monitor work.

## Dependencies and Integration Points
The file depends on bonding internals, `net/bond_alb.h` structures/constants, ARP creation/transmit helpers, VLAN tagging APIs, IPv6 neighbor discovery parsing, netdev upper-device walking, RTNL for MAC/promiscuity changes, RCU slave iteration, and the bonding workqueue. It integrates with `bond_main.c` mode transmit hooks, link-change hooks, active-slave selection, receive probe dispatch, sysfs/netlink TLB dynamic load option, and debugfs RLB hash inspection.

## Risks
ALB requires lower drivers to support MAC address changes while open; failure returns `-EOPNOTSUPP`. Receive balancing depends on ARP behavior and does not cover non-ARP neighbor discovery in the same way, so IPv6 handling mainly avoids unsafe balancing for ND/DAD. Hash collisions can move older RLB clients back to the primary. Locking is subtle because some helpers require RTNL with no mode lock, while hash-table operations use `mode_lock` with softirqs disabled. Temporary promiscuity cleanup uses `rtnl_trylock()` and can be delayed. Incorrect MAC swaps can disrupt traffic until learning packets/ARP updates converge.

## Test Signals
Tests should cover TLB dynamic and non-dynamic transmit selection, load rebalance counters, multicast/broadcast exclusion, IPv6 ND/DAD exclusion, ALB ARP reply/request rewriting, RLB client hash insertion/update/purge, VLAN-tagged client updates, switch learning packets for bond/VLAN/macvlan uppers, MAC collision handling on attach, MAC repair on detach, active-slave MAC swaps, link down/up clearing and rebalance, promiscuity timeout cleanup, and operation when slave MAC changes fail.
