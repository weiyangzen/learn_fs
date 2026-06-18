# sources/distributed-fs/ceph-client/include/net/bond_alb.h

## Purpose
This header defines adaptive load balancing support for bonding modes TLB and ALB. It provides timer constants, hash table sizes and sentinel values, transmit-load-balancing and receive-load-balancing client records, per-slave load state, per-bond ALB state, and exported functions for initialization, link/active changes, transmit selection, monitoring, MAC changes, and VLAN cleanup.

## Important APIs, Types, And Constants
- `ALB_TIMER_TICKS_PER_SEC`, `BOND_TLB_REBALANCE_INTERVAL`, `BOND_ALB_DEFAULT_LP_INTERVAL`, `BOND_TLB_REBALANCE_TICKS`, and `BOND_ALB_LP_TICKS()` define monitor timing.
- `TLB_HASH_TABLE_SIZE` and `RLB_HASH_TABLE_SIZE` are fixed at 256 and tied to byte-wide hash keys.
- `struct tlb_client_info` maps transmit clients to slaves and tracks transmitted bytes, previous load history, and per-slave linked-list indices.
- `struct rlb_client_info` maps ARP/IP client relationships to receive slaves and tracks MACs, VLAN ID, update-needed state, and used/source-hash list membership.
- `struct tlb_slave_info` tracks each slave's assigned TLB client list head and aggregate load.
- `struct alb_bond_info` owns dynamic TLB/RLB tables, rebalance counters, learning-packet counter, RLB flags, active receive slave, promisc timeout state, and retry/update counters.
- Exported functions include `bond_alb_initialize()`, `bond_alb_deinitialize()`, per-slave init/deinit, link/active-change handlers, `bond_alb_xmit()`, `bond_tlb_xmit()`, slave-selection helpers, monitor work, MAC address update, and VLAN cleanup.

## Control Flow And State
Mode setup calls `bond_alb_initialize()` before ALB monitor work starts, optionally enabling RLB for ALB mode. Each slave gets TLB state through `bond_alb_init_slave()`. Transmit paths call `bond_tlb_xmit()` or `bond_alb_xmit()`, which select slaves through hash/client tables and current `bond_slave_can_tx()` status. Periodic `bond_alb_monitor()` updates load histories, rebalances client assignments, sends learning packets, manages RLB ARP updates, and handles failover/promiscuous windows. Link and active slave changes update client assignments and may trigger learning/update bursts.

## State And Persistence Behavior
ALB/TLB state is runtime and dynamically allocated per bond. TLB entries accumulate byte counters between rebalance intervals and retain client-to-slave assignment until rebalanced or invalidated. RLB entries cache IP/MAC/VLAN associations and update-needed flags so the monitor can send corrective ARP traffic. Per-slave `tlb_slave_info` is embedded in `struct slave`. The common bond `mode_lock` protects ALB/TLB hash table access according to `bonding.h`.

## Dependencies And Integration Points
The header depends on Ethernet constants, `struct bonding`, `struct slave`, sk_buff/netdevice types supplied by implementation includes, and bond parameters such as `lp_interval` and `tlb_dynamic_lb`. It integrates with `drivers/net/bonding/bond_alb.c`, `bond_main.c` mode setup/transmit paths, VLAN handling, failover MAC handling, and ARP-based receive balancing.

## Risks
- Hash collisions intentionally replace older RLB entries; stale IP/MAC associations can cause wrong ARP updates if cleanup paths fail.
- Fixed-size tables and index sentinels require careful bounds checks around `next`/`prev` list manipulation.
- Rebalance timing constants are used in divisions and retry windows; invalid values can destabilize periodic work.
- MAC/VLAN changes must clear or update RLB entries to avoid directing peers to the wrong slave.
- Concurrent transmit and monitor updates require correct `mode_lock` use.

## Test Signals
- TLB/ALB tests should cover client assignment, byte accounting, periodic rebalancing, disabled dynamic LB, link failure, active slave change, and no-transmit-slave cases.
- RLB tests should cover ARP learning/update bursts, VLAN cleanup, failover promisc timeout, hash collision replacement, and MAC address changes.
- Stress tests should run concurrent xmit and monitor work while adding/removing slaves.
