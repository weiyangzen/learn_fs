<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_core.c

## Purpose
Implements DWMAC4/4.10/5.10 MAC operations: core init, IRQ control, queue routing/priority, MTL algorithms, CBS, filtering, flow control, WOL, EEE, PCS, debug stats, loopback, source address insertion, ARP offload, and L3/L4 filters.

## Important APIs, Types, And Functions
Exports `dwmac4_ops`, `dwmac410_ops`, `dwmac510_ops`, and `dwmac4_setup`. Key functions include `dwmac4_core_init`, `dwmac4_irq_modify`, `dwmac4_update_caps`, queue config helpers, `dwmac4_set_filter`, `dwmac4_flow_ctrl`, `dwmac4_irq_status`, `dwmac4_irq_mtl_status`, `dwmac4_config_cbs`, `dwmac4_config_l3_filter`, and `dwmac4_config_l4_filter`.

## Control Flow
Setup populates MAC register base, link capabilities including 2.5G, MII/MDIO bit masks, VLAN count, filter capacities, and multicast hash log2. Core init writes `GMAC_CORE_INIT`, programs 1-us LPI tick from `stmmac_clk`, enables default interrupts, and initializes timestamp wait queue when timestamp IRQs are enabled. STMMAC later calls ops for queues, filters, flow control, EEE, PCS, and offloads. DWMAC410/510 ops reuse DWMAC4 logic but add DWMAC5 PPS/FPE/safety/RXP callbacks.

## State And Persistence
State resides in MAC/MTL registers, `mac_device_info`, STMMAC private stats, wait queues, and platform feature/capability structures. No disk persistence exists.

## Dependencies And Integration Points
Depends on STMMAC core, FPE, PCS, VLAN helpers, DWMAC5 extension APIs, netdev lists, CRC32 multicast hashing, and platform `dwmac4_addrs` register-layout overrides.

## Risks
Multi-queue mode disables half-duplex caps. Queue priority code relies on software not mapping a priority to multiple queues. VLAN fail queueing uses DWMAC5-defined registers in DWMAC4 filter logic. LPI tick divides clock rate by 1 MHz and assumes a valid nonzero clock. L3/L4 filter programming enables global IP filtering and must avoid stale filter registers.

## Test Signals
Core init, link caps with one vs multiple queues, RX/TX priority mapping, packet routing classes, WRR/WFQ/DWRR/SP, CBS registers, unicast overflow, multicast hash table size, VLAN filtering/fail queue, WOL, EEE timer/interrupt, PCS link, MTL overflow IRQ, ARP offload, L3/L4 ethtool filters, FPE/PPS/safety op presence on 4.10/5.10 are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_core.c -->
