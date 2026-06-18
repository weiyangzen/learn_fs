# Research: subset-b-004335

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/agere/et131x.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/agere/et131x.c

## Purpose
`et131x.c` is the Linux PCI Ethernet driver implementation for Agere/ATT ET1310 and ET131x 10/100/1000 Base-T controllers. It owns PCI probe/remove, netdev registration, MDIO/PHY integration, MAC/RXMAC/TXMAC setup, RX/TX DMA ring allocation, NAPI interrupt processing, multicast filtering, MTU changes, power-management suspend/resume, and ethtool register dumping.

## Important APIs, Types, and Functions
Key private structures are defined in this file: `struct et131x_adapter`, `struct rx_ring`, `struct fbr_lookup`, `struct tx_ring`, `struct tcb`, `struct rfd`, and `struct ce_stats`. These combine netdev/PCI/PHY pointers, MMIO base, locks, packet filters, DMA coherent rings, software queues, timer state, and accumulated hardware statistics.

Important entry points are:

- PCI driver: `et131x_pci_setup()`, `et131x_pci_remove()`, `et131x_pci_table`, `et131x_driver`, `module_pci_driver()`.
- Netdev ops: `et131x_open()`, `et131x_close()`, `et131x_tx()`, `et131x_tx_timeout()`, `et131x_change_mtu()`, `et131x_multicast()`, `et131x_stats()`, and `phy_do_ioctl`.
- NAPI/IRQ: `et131x_isr()` disables device interrupts, schedules `et131x_poll()`, and handles error/PHY/MAC-stat interrupts; `et131x_poll()` drains RX and TX completions then reenables interrupts.
- MDIO/PHY: `et131x_mdio_read()`, `et131x_mdio_write()`, `et131x_phy_mii_read()`, `et131x_mii_write()`, `et131x_mii_probe()`, and `et131x_adjust_link()`.
- Hardware setup: `et131x_soft_reset()`, `et131x_adapter_setup()`, `et131x_configure_global_regs()`, `et1310_config_mac_regs1()`, `et1310_config_mac_regs2()`, `et1310_config_rxmac_regs()`, `et1310_config_txmac_regs()`, `et1310_config_macstat_regs()`.
- DMA/data path: `et131x_rx_dma_memory_alloc()`, `et131x_tx_dma_memory_alloc()`, `et131x_config_rx_dma_regs()`, `et131x_config_tx_dma_regs()`, `nic_rx_pkts()`, `et131x_handle_recv_pkts()`, `nic_send_packet()`, `send_packet()`, `et131x_handle_send_pkts()`, `free_send_packet()`.
- EEPROM and board setup: `et131x_init_eeprom()`, `eeprom_read()`, `eeprom_write()`, `et131x_pci_init()`, `et131x_hwaddr_init()`.

## Control Flow
Probe starts in `et131x_pci_setup()`: enable PCI, request BARs, set bus mastering and a 64-bit coherent DMA mask, allocate an Ethernet device, initialize adapter defaults, read/repair EEPROM state, map BAR0, reset hardware, allocate DMA memory and RFDs, register NAPI, create/register an MDIO bus, connect the PHY, configure the adapter, leave PHY coma mode, and register the netdev. Open sets up the periodic error timer, requests a shared IRQ, enables NAPI, enables TX/RX DMA, and starts the PHY. Close stops PHY and DMA, disables NAPI, frees the IRQ, and deletes the timer.

Link changes arrive through phylib via `et131x_adjust_link()`. On link-up the driver exits PHY coma if necessary, applies speed-specific PHY fixes, computes pause/flow-control mode from link partner advertisement, adjusts FIFO depth for jumbo at gigabit, sets RX coalescing, and completes MAC configuration. On link-down it frees outstanding sends, resets TX state, soft-resets and reconfigures hardware, and cycles TX/RX.

RX uses two hardware free-buffer rings and a packet-status ring. `et131x_config_rx_dma_regs()` programs coherent memory addresses and local wrap indexes. Hardware writes a status block and packet status descriptors. NAPI calls `nic_rx_pkts()` repeatedly: it compares the hardware PSR pointer against `local_psr_full`, reads the ring/buffer index and length, advances the PSR full offset, obtains an RFD from `recv_list`, copies packet bytes out of the coherent FBR buffer into a newly allocated skb, runs `eth_type_trans()`, submits via `netif_receive_skb()`, and returns the FBR slot/RFD through `nic_return_rfd()`. `et131x_handle_recv_pkts()` enforces a budget and uses a hardware watchdog timer if work remains.

TX uses 64 software TCBs and a 512-entry TX descriptor ring. `et131x_tx()` validates queue capacity and carrier, then `send_packet()` removes a TCB from the ready list and `nic_send_packet()` maps the skb head and fragments into descriptors, wraps the software write index, appends the TCB to the send list, and writes the service request register. Gigabit mode coalesces TX interrupts. `et131x_handle_send_pkts()` reads `new_service_complete`, compares wrap/index bits with each TCB's final descriptor index, frees completed packets, returns TCBs to the ready list, and wakes the queue below a low-water mark.

Interrupt handling masks device interrupts first. RX/TX-completion status schedules NAPI and defers reenabling. Watchdog status synthesizes RX/TX work if there are unfinished receives or stale TX TCBs. MAC-stat wraps update host counters. TXDMA/RXDMA/TXMAC/RXMAC/WOL/SLV timeout branches mostly log warnings and depend on reset paths or later timeouts for recovery.

## State and Persistence Behavior
Persistent or semi-persistent device state includes EEPROM contents, the permanent MAC address copied from PCI config space, and optional EEPROM LED feature bytes. Runtime state is in `struct et131x_adapter`: flags, link state, desired/resolved flow control, packet filter, multicast table, DMA rings, local wrap indexes, RFD and TCB queues, NAPI state, error timer, and statistics.

The driver does not persist state to disk. Hardware state is reconstructed on probe, link changes, MTU changes, resume, and PHY coma exit. Suspend saves PCI state only when the interface is running, calls the same down path as close, and resume restores PCI state and restarts the interface. MTU changes are invasive: they disable TX/RX, free DMA memory, resize RX buffers based on the new jumbo size, soft-reset, reallocate rings, and reinitialize the adapter.

## Dependencies and Integration Points
The file depends on kernel PCI, DMA mapping, netdevice, ethtool, NAPI, phylib/MDIO, timers, skbuff, CRC32 multicast hashing, and MMIO accessors. It includes `et131x.h` for the hardware register map and bit definitions. Integration with user space is through the netdev interface, ethtool driver/register APIs, standard PHY ioctls, MTU changes, multicast/promiscuous flags, and sysfs/module driver binding through PCI IDs.

## Risks and Edge Cases
RX allocation and recovery paths have several fragile spots. If `dev_alloc_skb()` fails in `nic_rx_pkts()`, the function returns `NULL` after removing an RFD but before `nic_return_rfd()`, which can leak a receive descriptor/free-buffer slot and reduce future RX capacity. Partial allocation failures in RX/TX DMA setup rely on later cleanup, but some early failures can leave intermediate allocations or pointers until top-level cleanup runs.

TX mapping/unmapping is delicate. `nic_send_packet()` maps skb frags with `skb_frag_dma_map()` but `free_send_packet()` unmaps all descriptors with `dma_unmap_single()`, which is suspicious because page-backed fragments are normally unmapped with `dma_unmap_page()`. Error unwind separates head and page mappings, but successful completion does not. Descriptor counting depends on the pre-linearization fragment limit and the special split of large skb heads.

Packet filter programming appears uneven: the promiscuous/filter-zero branch clears filter bits in local `pf_ctrl` but does not write the updated `pf_ctrl`/`ctrl` registers before returning, while the non-promiscuous branch does. This is a likely behavior bug for entering promiscuous mode.

The ISR logs catastrophic MAC errors but does not perform an immediate full reset in those branches. Recovery is mostly indirect via timeout or link reset. The open path starts the error timer before `request_irq()` and returns on IRQ failure without deleting the timer, which can leave a live timer for a failed open. PHY coma and error timer logic also assume `netdev->phydev` remains valid while the timer is active.

## Test Signals
Build signals: compile the driver with `CONFIG_ET131X` and phylib enabled, with sparse or clang warnings for MMIO and DMA mapping usage. Probe signals: PCI device binds, BAR0 maps, MDIO bus registers, PHY attaches, and `register_netdev()` succeeds. Runtime signals: link-up/down through phylib, DHCP or ping traffic, ethtool register dump, MTU changes across normal and jumbo sizes, multicast/promiscuous mode toggles, suspend/resume, TX timeout recovery, RX/TX under allocation pressure, and interrupt coalescing at gigabit versus 10/100 speeds. Risk-focused tests should inject skb allocation failure in RX, DMA mapping failure in TX, IRQ request failure in open, and multicast/promiscuous transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/agere/et131x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/agere/et131x.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/agere/et131x.h

## Purpose
`et131x.h` is the private hardware-definition header for the Agere ET1310/ET131x driver. It gives `et131x.c` a typed MMIO layout for the controller and defines bit masks, index encodings, EEPROM config offsets, MAC/RXMAC/TXMAC/RXDMA/TXDMA/MMC/MAC-stat registers, and PHY vendor register constants.

## Important APIs, Types, and Definitions
The header does not expose callable functions. Its important types are packed around register windows:

- `struct global_regs`: internal RAM split, power-management control, interrupt status/mask/alias, software reset, MSI, loopback, and watchdog registers.
- `struct txdma_regs`: TX descriptor ring base/count, service request/complete, status writeback, cache indexes, DMA error and retry/error counters.
- `struct rxdma_regs`: RX status writeback, packet status ring, free-buffer ring 0/1 descriptors, full/available offsets, thresholds, and RX interrupt coalescing controls.
- `struct txmac_regs`: TX MAC enable, shadow pointer, error counters, pause/backpressure controls.
- `struct rxmac_regs`: RX MAC enable, WOL masks, unicast filters, multicast hash registers, packet filter control, MCIF segmentation/watermark, and error state.
- `struct mac_regs`: MAC reset/configuration, interpacket gap, frame length, MII management registers, interface mode/status, and station address registers.
- `struct macstat_regs`: hardware statistic counters and carry/mask registers.
- `struct mmc_regs`: internal memory controller and SRAM access registers.
- `struct address_map`: top-level BAR layout that places each register block on 4 KiB boundaries and pads to the expected device address map.

Key constants include `DRIVER_NAME`, LBCIF EEPROM control/status bits, `ET_PM_PHY_SW_COMA`, `ET_PMCSR_INIT`, interrupt bits such as `ET_INTR_RXDMA_XFR_DONE` and `ET_INTR_PHY`, `ET_RESET_ALL`, DMA index masks/wrap bits (`ET_DMA10_MASK`, `ET_DMA10_WRAP`, `ET_DMA12_MASK`, `ET_DMA12_WRAP`), RX/TX DMA control bits, MAC config bits, RX packet filter bits, MMC controls, and PHY vendor registers (`PHY_CONFIG`, `PHY_INTERRUPT_STATUS`, `PHY_LED_2`, etc.).

## Control Flow
The header shapes control flow by making MMIO register access look like field access from `adapter->regs`. Reset code writes `global.sw_reset` and `mac.cfg1`. DMA setup writes `txdma.*` and `rxdma.*` base, size, status, and index registers. RX/TX enable paths set `rxdma.csr`, `txdma.csr`, `rxmac.ctrl`, and `txmac.ctl`. MII operations sequence `mac.mii_mgmt_addr`, `mac.mii_mgmt_cmd`, `mac.mii_mgmt_ctrl/stat`, and `mac.mii_mgmt_indicator`. Interrupt handling reads and masks `global.int_status` using the interrupt constants defined here.

The DMA wrap macros are central to ring progression. Hardware indexes are not plain counters; they combine low index bits with a wrap bit. The implementation's `INDEX10()`, `INDEX12()`, and `INDEX4()` helpers isolate descriptor indexes while preserving the separate wrap state in software.

## State and Persistence Behavior
This header defines register state, not persistent storage. Some registers reflect nonvolatile EEPROM access through LBCIF, but the header only defines offsets and bits. Runtime state represented by these structures is volatile MMIO state restored by the C driver after probe, reset, link change, MTU change, resume, or PHY coma exit. The large `address_map` padding assumes the hardware BAR layout remains stable.

## Dependencies and Integration Points
The definitions are consumed by `et131x.c` and require Linux integer types plus MMIO accessors from the including C file. The PHY register definitions integrate with generic MII constants from `include/linux/mii.h`. The top-level map must match the PCI BAR exposed by the ET131x hardware; any mismatch affects every read/write in the driver.

## Risks and Edge Cases
The register structs are not explicitly marked `__packed`, so correctness depends on natural 32-bit layout and the padding arrays. This is typical for Linux MMIO register maps but sensitive to accidental type changes. The final `address_map` contains very large unused arrays, so compile-time layout drift could be hard to spot without offset checks. DMA wrap constants are easy to misuse because the valid descriptor number and wrap bit share the same integer. Many bit definitions encode hardware errata behavior indirectly; changing masks can alter interrupt filtering, PHY coma, jumbo handling, or flow control.

## Test Signals
Useful checks are compile-time size/offset review, sparse address-space checking of `struct address_map __iomem *`, successful ethtool register dumps, MDIO reads/writes through the MAC management register block, correct interrupt masking/unmasking, and RX/TX ring wrap tests under sustained traffic. Hardware tests should verify reset, PHY coma transitions, jumbo MTU settings, multicast hash programming, and MAC-stat carry interrupts because those paths depend directly on this header's bit definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/agere/et131x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/Kconfig

## Purpose
This Kconfig file defines the kernel configuration switches for Airoha Ethernet support. It introduces the vendor menu, the NPU support module, the main SoC Gigabit Ethernet driver, and optional flow-statistics support.

## Important APIs, Types, and Symbols
The symbols are:

- `NET_VENDOR_AIROHA`: vendor gate, visible as "Airoha devices", available on `ARCH_AIROHA` or `COMPILE_TEST`.
- `NET_AIROHA_NPU`: tristate Airoha Network Processor support. It selects `WANT_DEV_COREDUMP` and `REGMAP_MMIO`.
- `NET_AIROHA`: tristate Airoha SoC Gigabit Ethernet support. It depends on `NET_DSA || !NET_DSA`, which is effectively always true but documents that DSA is optional. It selects `NET_AIROHA_NPU` and `PAGE_POOL`.
- `NET_AIROHA_FLOW_STATS`: boolean default-y flowtable statistics option gated by both `NET_AIROHA` and `NET_AIROHA_NPU`.

## Control Flow
Kconfig controls which objects the sibling Makefile builds. Enabling `NET_VENDOR_AIROHA` opens the submenu. Enabling `NET_AIROHA` builds `airoha-eth.o` and also forces the NPU support dependency. Enabling `NET_AIROHA_NPU` builds `airoha_npu.o`. `NET_AIROHA_FLOW_STATS` is used by the broader Airoha driver set for optional flow statistics.

## State and Persistence Behavior
The file has no runtime state. It persists selected build configuration into `.config`, which then affects built-in versus module linkage and availability of page-pool, NPU, debug, and stats code paths.

## Dependencies and Integration Points
This Kconfig integrates the Airoha Ethernet driver into the Linux networking driver tree. `ARCH_AIROHA` is the native platform dependency; `COMPILE_TEST` allows build coverage elsewhere. `PAGE_POOL` is needed by `airoha_eth.c` RX buffer management. `REGMAP_MMIO` and `WANT_DEV_COREDUMP` support the NPU side.

## Risks and Edge Cases
The `depends on NET_DSA || !NET_DSA` expression for `NET_AIROHA` is tautological, so it does not constrain DSA. That may be intentional because `airoha_eth.c` has conditional DSA handling, but it can be confusing to maintainers. Since `NET_AIROHA` selects `NET_AIROHA_NPU`, build failures or runtime NPU probe assumptions can affect users who only intended to enable Ethernet. `NET_AIROHA_FLOW_STATS` defaults to enabled whenever dependencies are met, so optional stats code should stay lightweight and robust.

## Test Signals
Build matrix tests should cover `NET_AIROHA=m`, `NET_AIROHA=y`, `NET_AIROHA_NPU=m/y`, `CONFIG_NET_DSA=y/n`, `CONFIG_DEBUG_FS=y/n`, and `COMPILE_TEST=y` on non-Airoha architectures. Runtime signals are the presence of the platform driver module and NPU module according to selected tristates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/Makefile

## Purpose
This Makefile maps the Airoha Kconfig symbols to kernel objects. It builds the Ethernet driver from the main data-path and PPE sources, optionally adds debugfs support, and builds the NPU support object.

## Important APIs, Types, and Targets
Important targets are:

- `obj-$(CONFIG_NET_AIROHA) += airoha-eth.o`: builds the main Ethernet composite object when `NET_AIROHA` is enabled.
- `airoha-eth-y := airoha_eth.o airoha_ppe.o`: links the core Ethernet/platform/QDMA implementation with the packet-processing engine implementation.
- `airoha-eth-$(CONFIG_DEBUG_FS) += airoha_ppe_debugfs.o`: adds PPE debugfs support only when debugfs is enabled.
- `obj-$(CONFIG_NET_AIROHA_NPU) += airoha_npu.o`: builds the NPU support module/object independently under its Kconfig symbol.

## Control Flow
Kbuild expands the `obj-*` and composite-object variables according to `.config`. The main driver code in `airoha_eth.c` is always linked together with PPE support when `NET_AIROHA` is selected. Debugfs code is omitted unless `CONFIG_DEBUG_FS` is set.

## State and Persistence Behavior
The file has no runtime state. Its persistent effect is the generated build graph and final module/object composition for the configured kernel.

## Dependencies and Integration Points
It depends on the sibling Kconfig symbols and integrates with kernel Kbuild. `airoha_eth.o` calls functions from `airoha_ppe.o`, so the composite object keeps those internal references local to `airoha-eth.o`. `airoha_ppe_debugfs.o` is a conditional extension rather than a separate module.

## Risks and Edge Cases
The directory comment says "Mediatek SoCs built-in ethernet macs", which appears stale or copied and conflicts with the Airoha driver context. Because `airoha_eth.o` and `airoha_ppe.o` are always linked together for `NET_AIROHA`, build breakage in PPE support breaks the main Ethernet driver. Debugfs-only code needs regular build coverage because it is conditionally linked.

## Test Signals
Useful signals are successful `make M=drivers/net/ethernet/airoha` builds with `NET_AIROHA=m/y`, `NET_AIROHA_NPU=m/y`, and both `CONFIG_DEBUG_FS=y` and `n`. Module inspection should show `airoha-eth` containing `airoha_eth.o` and `airoha_ppe.o`, with debugfs symbols present only in debugfs builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_eth.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_eth.c

## Purpose
`airoha_eth.c` is the main platform Ethernet driver for Airoha EN7581/AN7583-class SoCs. It initializes front-end switch/packet-engine registers, QDMA RX/TX rings, hardware forwarding buffers, interrupts, NAPI, per-GDM net_devices, DSA metadata, ethtool statistics, and traffic-control offloads for ETS, HTB, matchall police, and PPE flower rules.

## Important APIs, Types, and Functions
The file relies on private types from `airoha_eth.h`: `struct airoha_eth`, `struct airoha_qdma`, `struct airoha_queue`, `struct airoha_irq_bank`, `struct airoha_tx_irq_queue`, `struct airoha_gdm_port`, `struct airoha_hw_stats`, and SoC data/ops structures.

Important functions include:

- MMIO helpers: `airoha_rr()`, `airoha_wr()`, `airoha_rmw()`.
- Front-end setup: `airoha_fe_init()`, `airoha_fe_maccr_init()`, `airoha_fe_vip_setup()`, `airoha_fe_pse_ports_init()`, `airoha_fe_mc_vlan_clear()`, `airoha_fe_crsn_qsel_init()`.
- QDMA RX: `airoha_qdma_init_rx_queue()`, `airoha_qdma_fill_rx_queue()`, `airoha_qdma_rx_process()`, `airoha_qdma_rx_napi_poll()`, `airoha_qdma_cleanup_rx_queue()`.
- QDMA TX: `airoha_qdma_init_tx_queue()`, `airoha_qdma_tx_irq_init()`, `airoha_dev_xmit()`, `airoha_qdma_tx_napi_poll()`, `airoha_qdma_cleanup_tx_queue()`.
- IRQ and hardware init: `airoha_irq_handler()`, `airoha_qdma_init_irq_banks()`, `airoha_qdma_hw_init()`, `airoha_qdma_init()`, `airoha_hw_init()`, `airoha_hw_cleanup()`.
- Netdev ops: `airoha_dev_init()`, `airoha_dev_open()`, `airoha_dev_stop()`, `airoha_dev_change_mtu()`, `airoha_dev_select_queue()`, `airoha_dev_get_stats64()`, `airoha_dev_set_macaddr()`.
- DSA/PPE integration: `airoha_get_dsa_tag()`, `airoha_get_fe_port()`, `airoha_set_gdm2_loopback()`, `airoha_ppe_*` calls.
- TC offloads: `airoha_tc_setup_qdisc_ets()`, `airoha_tc_setup_qdisc_htb()`, `airoha_dev_setup_tc_block()`, `airoha_dev_tc_matchall()`, rate-limit/TRTCM helpers.
- Probe/remove and SoC matching: `airoha_probe()`, `airoha_remove()`, `of_airoha_match`, `en7581_soc_data`, `an7583_soc_data`, `module_platform_driver()`.

## Control Flow
Platform probe allocates `struct airoha_eth`, obtains SoC match data, sets a 32-bit DMA mask, maps the front-end MMIO region, gets reset controls, allocates a dummy threaded-NAPI net_device, and calls `airoha_hw_init()`. Hardware init asserts/deasserts resets, initializes front-end registers, initializes each QDMA block, initializes PPE, and sets `DEV_STATE_INITIALIZED`. Probe then enables NAPI for all QDMA queues, scans child OF nodes compatible with `airoha,eth-mac`, allocates one net_device per GDM port, and registers them.

Opening a GDM net_device starts TX queues, enables VIP/IFC forwarding for that port, toggles DSA STAG handling, programs frame length, enables QDMA global TX/RX DMA, increments the QDMA user count, selects the PSE forwarding destination, and returns. Stop disables TX, disables VIP, resets netdev TX subqueues, forwards the GDM port to drop, and if the last user of that QDMA stopped, disables QDMA DMA and cleans TX rings.

RX setup allocates per-ring queue entries, coherent descriptors, and a `page_pool`; programs ring base/size/thresholds; enables scatter; and pre-fills descriptors with page-pool fragments. RX IRQs are masked, acknowledged, disabled per ring, and handed to NAPI. `airoha_qdma_rx_process()` consumes done descriptors, syncs DMA for CPU, validates length and source GDM port, builds the first skb with `napi_build_skb()`, attaches later fragments with `skb_add_rx_frag()`, handles DSA metadata from descriptor source tags, sets hardware hash/PPE information, submits to GRO, clears `q->skb`, and refills the ring.

TX selects a hardware queue from skb queue mapping, extracts or removes MTK DSA tags when needed, builds descriptor metadata for QoS channel/queue, checksum offload, TSO, front-end port, and meter. It maps the skb head and frags, chains descriptors through `NEXT_ID`, moves queue entries from the free list to an in-flight list, records the skb on the final descriptor, updates BQL, optionally stops the netdev queue near the low-water threshold, and writes `REG_TX_CPU_IDX()` when needed. TX completion NAPI drains the hardware IRQ queue, validates QDMA ring and descriptor indexes, unmaps DMA, returns entries to the free list, completes BQL, frees skbs, wakes all netdev TX queues sharing the hardware queue if space is available, and clears completion entries in chunks.

TC control flow maps qdisc and classifier requests to hardware meters/schedulers. ETS validates strict/WRR band ordering, writes TWRR weights, and reads QoS counters. HTB allocates extra software queue IDs mapped to QoS channels and configures egress TRTCM rate limiting. Matchall police configures ingress meters across RX rings. Flower offload is delegated to PPE setup callbacks.

## State and Persistence Behavior
Runtime state lives in `struct airoha_eth` and child QDMA/GDM structures: MMIO bases, reset handles, SoC ops, global state bits, QDMA queues, IRQ masks, page pools, coherent descriptor rings, hardware-forwarding buffer descriptors, net_device pointers, DSA metadata, PPE state, per-port hardware counters, QDMA user counts, and per-port QoS queue bitmaps.

The driver does not persist state to disk. Hardware state is reconstructed on probe and partially reprogrammed on netdev open, stop, MTU change, MAC address change, TC offload updates, and remove cleanup. Hardware counters are periodically folded into software 64-bit stats under `u64_stats_sync` and then cleared in hardware. OF child nodes persist the port topology and MAC addresses; missing MAC addresses are replaced with random addresses.

## Dependencies and Integration Points
The file depends on platform devices, device tree, reset controls, reserved memory, coherent DMA, page_pool, NAPI, skbuff, DSA, dst metadata, ethtool, phylib ethtool helpers, traffic-control offload APIs, flow blocks, BQL, and private Airoha headers `airoha_regs.h` and `airoha_eth.h`. It integrates tightly with `airoha_ppe.o` through PPE init/deinit, DSA CPU-port programming, flow offload callbacks, and skb checks. Device-tree compatible strings are `airoha,en7581-eth`, `airoha,an7583-eth`, and child `airoha,eth-mac` nodes.

## Risks and Edge Cases
The RX scattered-frame path keeps a partially built `q->skb` across descriptors. Any malformed descriptor sequence, invalid port, allocation failure, or too many fragments must free the partial skb and return pages correctly; this path is sensitive to descriptor ordering and `MORE` bit correctness. `airoha_qdma_get_gdm_port()` accepts only a narrow set of source-port encodings, so new SoC encodings need explicit updates.

TX uses `dma_map_single()` for both linear data and `skb_frag_address()` fragments. On systems where skb fragments are not safely addressable for this API, `skb_frag_dma_map()` would normally be expected. The TX error unwind restores DMA mappings and list entries, but queue accounting and descriptor contents depend on the in-flight `tx_list` being consistent. Multiple netdev queues sharing one hardware queue require broad wakeups to avoid stalls, which the driver handles but remains a concurrency-sensitive area.

Traffic-control offload has hardware-specific limitations: ETS rejects unsupported strict/WRR layouts, HTB only accepts root-parent leaf allocation, and matchall accepts only a single police action with drop/accept semantics. Rate calculations depend on hardware tick fields; zero tick/unit paths return errors. The `airoha_qdma_init_qos_stats()` function appears to write both CPU and forwarded counter configurations through `REG_CNTR_CFG(i << 1)`, which is worth reviewing because the second write may target the same counter index rather than `(i << 1) + 1`.

Probe/remove lifetime is broad: NAPI is attached to a dummy threaded net_device, netdevs are devm-allocated per port, metadata dst objects are manually freed, QDMA queues use a mix of devm/dmam resources and explicit page-pool cleanup, and IRQs are requested before `DEV_STATE_INITIALIZED`. Error unwinds need to keep those ownership boundaries intact.

## Test Signals
Build signals: `CONFIG_NET_AIROHA`, `CONFIG_NET_AIROHA_NPU`, `CONFIG_NET_DSA`, `CONFIG_DEBUG_FS`, and `COMPILE_TEST` combinations. Probe signals: reset controls acquired, `fe`/`qdma*` resources mapped, NAPI dummy device allocated, QDMA rings initialized, PPE initialized, OF child ports registered, and IRQs firing only after initialization.

Runtime signals: RX/TX traffic on LAN and WAN GDM ports, jumbo MTU changes, checksum/TSO offload, DSA MTK-tag traffic, PPE offload hit/unbind paths, page-pool recycling under pressure, shared-QDMA multi-port open/stop, BQL queue stop/wake behavior, ethtool MAC/RMON stats, hardware counter clear/fold accuracy, and remove/unbind cleanup without page-pool or metadata leaks. TC tests should cover ETS replace/destroy/stats, HTB leaf allocation/modification/deletion/query, matchall police byte and packet units, and unsupported action validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_eth.c -->
