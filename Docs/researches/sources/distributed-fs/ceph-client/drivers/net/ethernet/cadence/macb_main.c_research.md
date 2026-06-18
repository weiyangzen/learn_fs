# sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb_main.c

## Purpose
`macb_main.c` is the primary Cadence MACB/GEM Ethernet platform driver. It supports legacy MACB, GEM gigabit controllers, old AT91 EMAC compatibility mode, multiple queues, DMA descriptor rings, NAPI RX/TX completion, phylink/PCS link management, ethtool operations, Wake-on-LAN, RX flow filters, checksum/segmentation offloads, optional PTP integration, TAPRIO/ENST traffic-control offload, platform-specific initialization, runtime PM, system suspend/resume, and OF/platform driver registration.

## Important APIs, functions, and structures
- DMA/ring helpers include `macb_dma_desc_get_size()`, descriptor index/wrap helpers, `macb_tx_desc()`, `macb_rx_desc()`, `macb_set_addr()`, and `macb_get_addr()`.
- Hardware access and detection use native/raw versus relaxed MMIO callbacks selected by `hw_is_native_io()`, with GEM detection through `hw_is_gem()`.
- MDIO and link management use Clause 22/45 MDIO callbacks, `macb_mii_init()`, `macb_mii_probe()`, phylink callbacks, SGMII PCS ops, and 10G USX PCS ops.
- The data path is centered on `macb_start_xmit()`, `macb_tx_map()`, `macb_tx_complete()`, `gem_rx()`, `gem_rx_refill()`, `macb_rx()`, `macb_rx_frame()`, `macb_rx_poll()`, `macb_tx_poll()`, and `macb_interrupt()`.
- Resource lifecycle uses `macb_open()`, `macb_close()`, coherent DMA allocation/free, ring initialization, `macb_init_hw()`, and `macb_reset_hw()`.
- Ettool and netdev integration includes stats, register dumps, WoL, link settings, ring parameters, hwtstamp ops, feature toggles, EEE, RX n-tuple filters, and `macb_netdev_ops`.
- Platform integration uses capability configuration, queue probing, clock init callbacks, OF match data, `macb_probe()`, `macb_remove()`, PM callbacks, shutdown, and `module_platform_driver()`.

## Control flow
Probe maps MMIO, selects match data, initializes clocks/runtime PM, detects I/O mode and queue count, allocates an MQ netdev, fills `struct macb`, configures caps/DMA/MTU/MAC/PHY mode, initializes IP-specific logic, creates MDIO/phylink, registers the netdev, initializes deferred work, and autosuspends.

Open resumes the device, sizes RX buffers from MTU, allocates descriptor/RX resources, initializes rings and hardware, powers the PHY, connects phylink, starts TX queues, and registers PTP. Close stops TX, disables NAPI, cancels LPI work, stops phylink, powers off PHY, resets hardware, frees DMA memory, removes PTP, and releases runtime PM.

TX maps skb head/frags into descriptors, handles checksum/FCS and LSO constraints, marks timestamp requests, writes descriptors in reverse order with barriers, wakes EEE LPI, and starts hardware. TX NAPI reclaims `TX_USED` descriptors, timestamps skb completions, updates stats, unmaps DMA, and wakes queues.

GEM RX uses per-descriptor skbs and refill; legacy MACB RX copies from coherent buffers. Interrupts disable completion sources before scheduling NAPI, handle TX used-buffer restart, queue error work, count overruns, and process WoL. Suspend/resume saves selected registers, tears down or restores PTP, reinitializes RX/hardware state, and integrates with runtime PM.

## State and persistence behavior
`struct macb` in netdev private data is the long-lived software state. Hardware state is in MMIO registers, DMA descriptors, IRQ masks, clocks, phylink/PCS state, and descriptor ownership bits. No filesystem persistence exists. Across suspend, `bp->pm_data` saves USRIO and screener state, while rings/features/flow filters are reconstructed from in-memory state.

## Dependencies and integration points
The driver depends on netdev/NAPI, DMA mapping, phylink, MDIO, ethtool, PTP hooks, runtime PM, common clocks, OF, PHY/reset APIs, Xilinx firmware calls for some SGMII setups, and platform devices. It integrates with `macb.h`, optional `macb_ptp.c` through `struct macb_ptp_info`, and `macb_pci.c` through platform-data clocks.

## Risks and test signals
High-risk areas are DMA barriers, descriptor sizing, TX error recovery, missed interrupt rescheduling, runtime PM during MDIO, 64-bit DMA high-address constraints, queue mask holes, PTP descriptor layout, EEE LPI wake timing, partial store-and-forward watermarks, feature restore after resume, and TAPRIO validation. Tests should include build matrices, probe/remove, link up/down, sustained traffic, jumbo/SG/TSO/UFO/checksum cases, multi-queue interrupts, `ethtool -S/-T`, ring changes, RX n-tuple filters, PHC timestamping, WoL wake, runtime PM MDIO, TAPRIO replace/destroy, and suspend/resume.
