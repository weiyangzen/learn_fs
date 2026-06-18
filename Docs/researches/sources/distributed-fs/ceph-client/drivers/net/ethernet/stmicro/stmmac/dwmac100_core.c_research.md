<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100_core.c

## Purpose
Implements MAC-core operations for the older 10/100 DWMAC100 controller used by ST SoCs.

## Important APIs, Types, And Functions
Exports `dwmac100_ops` and `dwmac100_setup`. Important callbacks include `dwmac100_core_init`, `dwmac100_set_filter`, `dwmac100_flow_ctrl`, `dwmac100_set_umac_addr/get_umac_addr`, `dwmac100_dump_mac_regs`, and `dwmac100_set_mac_loopback`.

## Control Flow
Setup fills MAC register base, 10/100 link capabilities, MII register layout, and link bit masks. Core init sets `MAC_CORE_INIT` and optional VLAN tag register. Runtime callbacks program MAC enable through common `stmmac_set_mac`, configure multicast/promiscuous filtering, set pause time, and read/write the single MAC address registers.

## State And Persistence
State is limited to MAC registers and `mac_device_info`. No PMT state is meaningful because this core reports no PMT support in the callback. No disk persistence exists.

## Dependencies And Integration Points
Uses STMMAC core, DWMAC100 header definitions, common MAC address helpers, netdev multicast lists, and CRC hashing.

## Risks
DWMAC100 has only one primary address slot; `reg_n` is ignored for address operations. RX checksum offload and host IRQ status are stubs returning zero. Flow control always writes enable bit and only conditions pause time on duplex, so `fc` parameter is not honored like newer cores.

## Test Signals
10/100 link setup, MII access, multicast hash programming, promiscuous/allmulti/no-multicast transitions, loopback bit, flow-control register contents, and register dump output provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac100_core.c -->
