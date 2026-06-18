# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rtsn.c

## Purpose
`rtsn.c` is the Renesas Ethernet-TSN platform driver for `renesas,r8a779g0-ethertsn`. It presents a single Ethernet netdev backed by one TX descriptor chain and one RX descriptor chain, configures TSN AXIBMI/MHD/RMAC hardware, registers an MDIO bus, connects to a PHY, and exposes Gen4 PTP-based hardware timestamping.

## Important APIs, Types, And Functions
The local `struct rtsn_private` owns all device state: netdev/platform device, mapped register base, reset/clock, PTP state, descriptor BATs, DMA rings, SKB arrays, indices, NAPI, statistics, MDIO bus, PHY link state, IRQs, and timestamp configuration. Register helpers are `rtsn_read()`, `rtsn_write()`, `rtsn_modify()`, and `rtsn_reg_wait()`. Open/close are `rtsn_open()` and `rtsn_stop()`. Data path functions include `rtsn_start_xmit()`, `rtsn_tx_free()`, `rtsn_rx()`, `rtsn_poll()`, and `rtsn_irq()`. Hardware setup is handled by `rtsn_reset()`, `rtsn_change_mode()`, `rtsn_axibmi_init()`, `rtsn_mhd_init()`, `rtsn_rmac_init()`, and `rtsn_hw_init()`. Probe/remove are `rtsn_probe()` and `rtsn_remove()`.

## Control Flow
Probe allocates an etherdev, maps `tsnes` and `gptp` resources, gets clock and reset controls, allocates/registers PTP, validates PHY mode, enables runtime PM, adds NAPI, reads or generates the MAC address, sets a 32-bit DMA mask, registers the MDIO bus, and registers the netdev. Opening enables NAPI and then calls `rtsn_init()`, which allocates descriptor BATs, allocates/formats coherent TX/RX rings, resets and configures hardware, connects PHY, and requests separate TX/RX IRQs. TX maps a padded SKB into a single descriptor, optionally marks TX timestamp request, advances `cur_tx`, and kicks `TRCR0`. IRQ clears TX/RX status, disables data IRQs, and schedules NAPI. NAPI drains RX descriptors up to budget, refills RX buffers, reclaims completed TX descriptors, wakes the queue, and re-enables IRQs. Stop stops PHY, disables NAPI, transitions hardware to disabled mode, frees IRQs, disconnects PHY, and frees rings/BATs.

## State And Persistence
Runtime state is volatile. TX/RX progress is tracked by monotonic `cur_*` and `dirty_*` counters modulo ring size. `stats` is stored in `rtnl_link_stats64`. Timestamp mode is held in `tstamp_tx_ctrl` and `tstamp_rx_ctrl`; RX timestamps come from timestamped RX descriptors, while TX timestamp completion samples the shared PTP clock during TX reclaim if the original SKB requested hardware timestamping. Hardware mode state is explicitly driven through DISABLE, CONFIG, and OPERATION modes.

## Dependencies And Integration Points
The driver uses platform resources, reset controller, clock framework, OF MDIO, phylib, NAPI, DMA API, runtime PM, ethtool timestamping, and `rcar_gen4_ptp`. DT must provide `tsnes` and `gptp` memory resources, `rx` and `tx` IRQ names, `phy-mode`, `phy-handle`, and an `mdio` child. Supported PHY interfaces are MII and RGMII variants. Netdev operations include hardware timestamp get/set, address validation, MAC setting, stats64, and phylib ioctl.

## Risks
TX supports only packets fitting a single descriptor and drops larger SKBs, so feature flags must not advertise scatter-gather or TSO. `rtsn_get_data_irq_status()` ORs in the TX/RX chain bits rather than masking with status, so interrupt handling should be checked carefully against hardware semantics. DMA addresses are stored as 32-bit descriptor fields, making the 32-bit DMA mask important. RX refill handles allocation failure by leaving descriptors unavailable until later polling. TX timestamping is approximate because completion uses current PTP time rather than a hardware TX timestamp descriptor. Open-time allocation means repeated up/down cycles exercise all error paths.

## Test Signals
Validation should include probe/remove, open/close cycles, MDIO scan/PHY attach, link speed changes through `rtsn_adjust_link()`, TX/RX traffic at MII and RGMII speeds, ring wrap at 1024 descriptors, large-SKB drop behavior, NAPI budget exhaustion, RX checksum feature toggling, ethtool timestamp capability, `SIOCSHWTSTAMP`/netlink hwtstamp get/set while down and up, and runtime PM balance during probe failure and remove.
