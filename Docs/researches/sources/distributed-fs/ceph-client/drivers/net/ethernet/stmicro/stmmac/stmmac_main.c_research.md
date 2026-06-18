# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_main.c

## Purpose

`stmmac_main.c` is the core Linux network driver implementation for Synopsys/STMMAC Ethernet MACs used by the Ceph client source snapshot. It owns the `net_device` lifecycle, DMA descriptor rings, TX/RX datapaths, NAPI scheduling, IRQ dispatch, PTP hardware timestamping, phylink integration, VLAN filtering/offload, XDP/AF_XDP support, traffic-control offloads, suspend/resume, debugfs surfaces, and driver probe/remove entry points that platform glue calls through exported helpers.

The file is the integration center for the STMMAC driver family. Hardware-specific register operations are largely delegated through `hwif.h` callbacks and helpers in sibling files, while this file sequences those operations with Linux networking, runtime PM, phylink, page_pool, DMA mapping, devlink, debugfs, and XDP APIs.

## Important APIs, Types, and Entry Points

- Exported platform/helper APIs: `stmmac_set_clk_tx_rate()`, `stmmac_axi_blen_to_mask()`, `stmmac_get_phy_intf_sel()`, `stmmac_plat_dat_alloc()`, `stmmac_dvr_probe()`, `stmmac_dvr_remove()`, `stmmac_suspend()`, `stmmac_resume()`, queue enable/disable helpers, and XDP open/release helpers.
- Netdevice operations: `stmmac_open()`, `stmmac_release()`, `stmmac_xmit()`, `stmmac_features_check()`, `stmmac_change_mtu()`, `stmmac_set_features()`, `stmmac_ioctl()`, `stmmac_setup_tc()`, `stmmac_set_mac_address()`, VLAN add/kill, `stmmac_get_stats64()`, `stmmac_bpf()`, `stmmac_xdp_xmit()`, `stmmac_xsk_wakeup()`, and hardware timestamp get/set.
- Phylink and PCS: `stmmac_phylink_setup()` and the `stmmac_phylink_mac_ops` callbacks configure MAC capabilities, PCS selection, link up/down, EEE LPI, and WoL.
- DMA queues: `struct stmmac_dma_conf`, `struct stmmac_rx_queue`, and `struct stmmac_tx_queue` carry descriptor memory, page pools, SKB/XDP metadata, AF_XDP pools, queue cursors, TBS/MSS state, timers, and stats synchronization.
- Timestamping/PTP: `stmmac_hwtstamp_set/get()`, `stmmac_init_timestamping()`, `stmmac_setup_ptp()`, `stmmac_get_tx_hwtstamp()`, `stmmac_get_rx_hwtstamp()`, XDP timestamp metadata, and devlink `phc_coarse_adj`.
- Interrupt/NAPI: single IRQ and multi-MSI handlers schedule `stmmac_napi_poll_rx()`, `stmmac_napi_poll_tx()`, or combined `stmmac_napi_poll_rxtx()`.
- XDP/AF_XDP: `stmmac_xdp_run_prog()`, `stmmac_xdp_xmit_xdpf()`, `stmmac_rx_zc()`, `stmmac_xdp_xmit_zc()`, and XSK metadata hooks implement in-driver XDP and zero-copy sockets.

## Control Flow

Probe is `stmmac_dvr_probe()` -> `__stmmac_dvr_probe()`. It validates DMA config, allocates the netdev and private state, initializes statistics/workqueue/timers, handles resets, detects hardware capabilities, sets netdev features/ops, adds NAPI, registers MDIO/PCS/phylink/devlink, registers the netdevice, and creates debugfs entries. Error paths unwind in reverse.

Open is `stmmac_open()` -> `stmmac_setup_dma_desc()` -> `__stmmac_open()`. It allocates descriptor resources, resumes runtime PM, attaches PHY, powers SerDes if needed, copies DMA config into `priv->dma_conf`, resets queue cursors, runs `stmmac_hw_setup()`, starts PTP/phylink, restores VLAN filters, requests IRQs, enables NAPI and TX queues, and enables DMA IRQs.

`stmmac_hw_setup()` preps PCS/RX clocks, resets and initializes DMA, writes the MAC address, initializes MAC core/MTL/safety/MMC, enables checksum/offload modes, programs ring lengths, TSO/SPH/VLAN/TBS, sets real queue counts, starts DMA, and reapplies hardware VLAN mode.

TX enters `stmmac_xmit()`, or `stmmac_tso_xmit()` for supported GSO. The path checks ring room and EST max-SDU, maps SKB head/fragments, writes descriptors, handles VLAN/TBS/timestamp/coalescing metadata, grants DMA ownership after descriptors are complete, kicks DMA, updates tail pointer, and arms TX cleanup. `stmmac_tx_clean()` reclaims descriptors, timestamps, XDP/XSK frames, SKBs, DMA maps, BQL accounting, stopped queues, and error counters.

RX enters `stmmac_rx()` for page_pool/SKB or `stmmac_rx_zc()` for AF_XDP. Both walk DMA-completed descriptors, preserve multi-descriptor packet state across budget exits, process descriptor status/errors, run XDP, build or dispatch SKBs, apply timestamp/VLAN/hash/checksum metadata, deliver via GRO, refill descriptors, finalize XDP redirects/TX, and update stats.

Interrupt flow masks DMA interrupts before NAPI scheduling and re-enables them after NAPI completion. Hard TX errors trigger DMA threshold bumping or TX channel reset. Fatal safety or timeout paths set reset bits and queue `stmmac_service_task()`, which closes and reopens the device under RTNL.

Suspend disables queues/timers, stops DMA and SerDes, programs WoL PMT or MAC/pinctrl sleep, suspends phylink, and calls platform suspend. Resume clears PMT/sleep state, resets MDIO when appropriate, powers SerDes, prepares phylink, clears/reinitializes queues, reruns hardware setup/timestamping/coalescing, restores RX mode/VLANs, enables queues/IRQs, resumes phylink, and reattaches the netdev.

## State and Persistence Behavior

`struct stmmac_priv` is the central persistent object. It stores platform data, hardware callbacks, DMA capabilities, phylink/PCS/MDIO handles, runtime PM relationship, `priv->dma_conf`, PTP settings, RSS table/key, active VLAN bitmap, XDP program and AF_XDP queue bitmap, workqueue state bits, IRQ data, devlink/debugfs handles, and software statistics.

Descriptor rings, page pools, RX buffers, TX DMA metadata, and AF_XDP pool associations are volatile and are allocated/freed across open/close, MTU changes, XDP queue reconfiguration, suspend recovery, and remove. Timestamp, VLAN, RSS, EEE, WoL, and XDP program configuration persist in private state and are reprogrammed after open/resume where needed.

State bits coordinate asynchronous recovery: `STMMAC_RESET_REQUESTED`, `STMMAC_SERVICE_SCHED`, `STMMAC_RESETING`, and `STMMAC_DOWN` prevent duplicate resets and suppress IRQ work while the adapter is down.

## Dependencies and Integration Points

The file depends on STMMAC hardware abstraction from `hwif.h`, descriptor/core helpers from sibling STMMAC files, and platform data from `stmmac.h`. It integrates with Linux networking, phylink/phylib/PCS, DMA API, page_pool, runtime PM, PTP timestamping, XDP/BPF/AF_XDP, TC offload, devlink, debugfs, reset/pinctrl/clock, and wake IRQ APIs.

`stmmac_mdio_register()`/`stmmac_pcs_setup()` from `stmmac_mdio.c` feed the PHY/PCS state consumed by `stmmac_phylink_setup()`. Hardware register work is funneled through STMMAC callback wrappers such as DMA init, descriptor operations, MAC core init, VLAN/RSS/MMC/PTP, EST/FPE, and safety feature helpers.

## Risks and Edge Cases

- TX descriptor ordering and memory barriers are critical; DMA must not see partially initialized descriptors.
- RX multi-descriptor saved state must stay correct across NAPI budget exits, errors, XDP verdicts, split-header payloads, and FCS stripping.
- AF_XDP zero-copy uses separate buffer ownership, combined NAPI, need-wakeup rules, and RCU synchronization during queue disable.
- Hardware feature combinations conflict: TSO with TBS, hardware VLAN insertion with hardware GSO, XDP with jumbo MTU, SPH with RX checksum, and EEE with platform interrupt quirks.
- Runtime PM and RX clock stop ordering is delicate around reset, MAC address, VLAN, and filter programming.
- Probe/open/MTU/IRQ failure paths have complex unwind requirements across DMA, timers, PTP, phylink, SerDes, runtime PM, and IRQ resources.
- VLAN fallback without hash filtering supports only a small number of active VIDs.
- Devlink timestamp coarse-mode updates assume timestamp registers are accessible and initialized.

## Test Signals

Probe/remove and open/close should be tested with fixed-link, MDIO PHY, xPCS, shared IRQ, multi-MSI, PTP and non-PTP hardware, runtime PM, and debugfs enabled. Datapath tests should cover normal TX/RX, SG, jumbo, checksum fallback, VLAN offload/filtering, TSO/USO, TBS, TX/RX timestamps, RSS, split-header, GRO, NAPI coalescing, TX timeout reset, and descriptor error injection. XDP tests should cover PASS/DROP/TX/REDIRECT, ndo_xdp_xmit, AF_XDP zero-copy RX/TX, pool reconfiguration, and need-wakeup. PM tests should validate suspend/resume with and without WoL and confirm timestamping, VLANs, RX mode, queues, and IRQs are restored.
