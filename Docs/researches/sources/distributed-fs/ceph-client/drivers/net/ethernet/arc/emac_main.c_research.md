# sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac_main.c

## Purpose
This file implements the ARC EMAC 10/100 net_device core: probe/remove, open/stop, DMA ring setup, NAPI RX/TX completion, interrupt handling, PHY link adjustment, multicast/promiscuous filtering, statistics, transmit, MAC address programming, and a recovery restart path for RX stalls.

## Important APIs, types, and functions
The exported APIs are `arc_emac_probe` and `arc_emac_remove`. Netdev operations include `arc_emac_open`, `arc_emac_stop`, `arc_emac_tx`, `arc_emac_set_address`, `arc_emac_stats`, and `arc_emac_set_rx_mode`. Runtime helpers include `arc_emac_tx_avail`, `arc_emac_adjust_link`, `arc_emac_tx_clean`, `arc_emac_rx`, `arc_emac_rx_miss_handle`, `arc_emac_rx_stall_check`, `arc_emac_poll`, `arc_emac_intr`, `arc_free_tx_queue`, `arc_free_rx_queue`, and `arc_emac_restart`.

## Control flow
Probe reads DT PHY/register/IRQ resources, maps MMIO, enables clock or reads `clock-frequency`, validates hardware ID revision 5 or 7, sets poll rate, clears interrupt status, requests IRQ, sets MAC address, allocates coherent RX/TX descriptor rings, probes MDIO, connects PHY, adds NAPI, and registers the netdev. Open allocates/maps RX skbs, initializes descriptors and ring pointers, enables interrupts/control bits/NAPI/PHY/queue. Interrupts acknowledge status, schedule NAPI for RX/TX, and account error-counter rollovers. NAPI cleans TX, handles missed packets, receives up to budget, reenables interrupts, and checks RX stalls. TX maps one skb into one descriptor and forces EMAC polling with `TXPL_MASK`.

## State and persistence
Runtime state lives in `arc_emac_priv`, DMA descriptors, skb mapping arrays, PHY state, and `ndev->stats`. There is no filesystem persistence. Hardware state includes MAC address registers, logical address filter registers, ring base registers, enable/status/control registers, and error counters.

## Dependencies and integration points
The file depends on Linux netdevice, DMA, NAPI, PHYLIB, OF, IRQ, clock, CRC32 multicast hashing, and the local MDIO implementation. SoC glue allocates the net_device, fills private glue fields, and calls `arc_emac_probe`; `emac_rockchip.c` is one such user.

## Risks
RX open error paths can return after partially allocated/mapped RX buffers; cleanup depends on caller/device teardown. The hardware supports single-buffer packets only; fragmented/chained RX packets are counted as length errors. Stats reads add hardware counters into cumulative stats, so repeated `ndo_get_stats` calls may double-count if counters are not clear-on-read. RX stall recovery is heuristic and restarts EMAC when missed errors rise while the current RX descriptor is still owned by hardware.

## Test signals
Probe/remove with DT resources, PHY link changes, full/half duplex register changes, TX queue stop/wake at ring full, RX traffic under NAPI budget, multicast filter programming, error counter rollover interrupts, netpoll if enabled, RX stall recovery, stop/open cycles, and DMA mapping failure paths are relevant tests.
