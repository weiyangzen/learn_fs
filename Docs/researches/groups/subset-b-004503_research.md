# subset-b-004503 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/jme.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/jme.c

## Purpose
`jme.c` is the implementation of the JMicron JMC250/JMC260 PCIe Ethernet driver. It binds a PCI driver to JMicron PCI device IDs, registers a `net_device`, manages the device MMIO register block defined in `jme.h`, and implements RX/TX DMA rings, MDIO/MII access, link management, interrupt moderation, ethtool controls, EEPROM access, wake-on-LAN, and suspend/resume behavior.

## Important APIs, Types, And Functions
The public integration surface is `jme_driver`, `jme_netdev_ops`, and `jme_ethtool_ops`. `jme_init_one()` performs PCI enablement, DMA mask selection, BAR mapping, `alloc_etherdev()`, feature setup, NAPI registration, PHY discovery, EEPROM reload, MAC address loading, and `register_netdev()`. `jme_remove_one()`, `jme_shutdown()`, `jme_suspend()`, and `jme_resume()` provide lifecycle and power management.

The core datapath functions are `jme_open()`, `jme_close()`, `jme_start_xmit()`, `jme_tx_clean_tasklet()`, `jme_process_receive()`, `jme_alloc_and_feed_skb()`, and `jme_poll()`. Hardware access is wrapped by `jread32()`, `jwrite32()`, and `jwrite32f()` from `jme.h`. PHY control is handled through `jme_mdio_read()`, `jme_mdio_write()`, `jme_reset_phy_processor()`, `jme_check_link()`, `jme_restart_an()`, `jme_phy_on()`, `jme_phy_off()`, `jme_phy_calibration()`, and revision-specific `jme_phy_setEA()` logic.

## Control Flow
Probe disables PCIe low-power link states, enables the PCI function, chooses a 64/40/32-bit coherent DMA mask, maps BAR0, seeds cached register defaults, initializes spinlocks and atomic gates, installs NAPI, discovers PHY ID for FPGA variants, powers down the PHY, resets the MAC, reloads EEPROM, reads the MAC address, and registers the network device. Opening the netdev enables NAPI, initializes tasklets, requests MSI or shared INTx, enables interrupt sources and packet coalescing, powers and configures the PHY, calibrates revision-specific PHY state, and triggers link resolution through the timer/software interrupt path.

Link-change work is serialized by `link_changing`. It stops queues, disables PCC/timers/tasklets, tears down RX/TX engines and rings when needed, resets the MAC, rechecks link state, allocates fresh rings, enables engines, restarts queues, or starts pseudo hotplug shutdown timing when link is down. RX is driven either by tasklets or NAPI depending on `JME_FLAG_POLL`; interrupt mode schedules RX clean tasklets, while polling mode disables RX PCC and schedules NAPI. TX maps skb head and fragments into descriptor chains, kicks queue 0, and frees completed mappings from `jme_tx_clean_tasklet()`.

## State And Persistence
Persistent driver state lives in `struct jme_adapter`: cached register values (`reg_txcs`, `reg_rxcs`, `reg_rxmcs`, `reg_ghc`, `reg_pmcs`, `reg_gpreg1`), PHY/link settings, ring size/masks, `mii_if`, NAPI, tasklets, work item, dynamic PCC counters, and synchronization atomics. RX/TX rings persist while the interface is carrier-up/open; descriptors are coherent DMA allocations and `jme_buffer_info` tracks skb ownership and DMA mappings. User-configured link settings are cached in `old_cmd` under `JME_FLAG_SSET`; WoL selection persists in `reg_pmcs` for suspend/shutdown. Module parameters alter pseudo hotplug behavior at load time.

## Dependencies And Integration Points
This file depends on PCI, DMA mapping, `net_device`, NAPI, tasklet, workqueue, MII, ethtool, VLAN acceleration, checksum/GSO helpers, and Linux PM APIs. It integrates with the kernel through `pci_register_driver()`, `netdev_ops`, `ethtool_ops`, `mii_if_info`, module parameters, MSI/INTx IRQ handling, and optional netpoll.

## Risks
The driver has complex concurrency between IRQ, NAPI/tasklets, link-change work, close/suspend, and TX timeout. Several hardware waits are busy polling with fixed timeouts, so register semantics matter for hangs. DMA error unwind is delicate: if `jme_fill_tx_desc()` fails after `jme_alloc_txdesc()` has reserved descriptors, `jme_start_xmit()` returns `NETDEV_TX_OK` without an obvious skb free or `nr_free` rollback in that path. RX replacement allocates a new skb before handing the old one up; allocation failure drops but keeps the original mapping for reuse. Ettool EEPROM writes directly program SMB-backed EEPROM and need hardware validation. MTU over 1900 disables TSO/checksum features, so jumbo behavior needs regression coverage.

## Test Signals
Useful signals include PCI probe/remove with both JMC250 and JMC260 IDs, MSI fallback to INTx, open/close cycles, RX/TX under stress with SG/TSO/VLAN/checksum combinations, MTU changes around 1900 and max jumbo, ethtool coalesce/pause/WoL/EEPROM/register dumps, suspend/resume with WoL enabled and disabled, forced media and autonegotiation changes, netpoll if configured, and fault injection for DMA mapping, RX allocation, IRQ request, EEPROM reload, and PHY timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/jme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/jme.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/jme.h

## Purpose
`jme.h` is the hardware contract and private driver state definition for the JMicron JMC2x0 Ethernet driver. It defines PCI IDs, ring descriptor formats, MMIO offsets, bit masks, timing constants, cached register defaults, private adapter state, and small inline helpers used by `jme.c`.

## Important APIs, Types, And Definitions
The central types are `struct txdesc`, `struct rxdesc`, `struct jme_buffer_info`, `struct jme_ring`, `struct dynpcc_info`, and `struct jme_adapter`. TX and RX descriptors are 16-byte hardware layouts with separate command, data, and writeback views. `jme_ring` tracks coherent descriptor memory, DMA addresses, per-descriptor buffer metadata, and producer/cleaner indexes. `jme_adapter` ties PCI, netdev, MMIO, MII, rings, locks, tasklets, workqueue, cached registers, revision data, link state, ethtool state, and NAPI together.

Register enums cover MAC, PHY, MISC, and RSS MMIO windows; TX/RX control bits; SMI/MDIO fields; GHC speed/duplex/clock control; PMCS WoL bits; PHY power and link registers; SMB EEPROM interface; timers; interrupt events; packet coalescing; chip mode; and aggressive power mode/pseudo hotplug bits. Inline helpers include `jme_napi_priv()`, `smi_reg_addr()`, `smi_phy_addr()`, `jread32()`, `jwrite32()`, `jwrite32f()`, `is_buggy250()`, and `new_phy_power_ctrl()`.

## Control Flow Support
The header does not execute a standalone control flow; it shapes the implementation in `jme.c`. Descriptor ownership bits define the RX/TX state machine. `INTR_ENABLE` selects the events enabled by `jme_start_irq()`. Default register values such as `RXCS_DEFAULT`, `RXMCS_DEFAULT`, `TXMCS_DEFAULT`, `TXCS_DEFAULT`, and `GPREG*_DEFAULT` seed MAC setup and reset paths. NAPI compatibility macros map the driver's older abstraction layer onto current `struct napi_struct` calls.

## State And Persistence
State persistence is mostly structural: `jme_adapter` caches hardware configuration between operations and across suspend/resume. `reg_pmcs` preserves WoL selection; `old_cmd` preserves ethtool link settings; `flags` records MSI, user speed setting, polling mode, and shutdown state. Descriptor and buffer metadata define ownership transfer between CPU and NIC. Register constants encode hardware persistence points such as EEPROM/SMB contents and PM wake status.

## Dependencies And Integration Points
The header depends on Linux interrupt and networking types brought in by `jme.c`. It is tightly coupled to JMicron hardware register semantics and to the Linux MII, NAPI, DMA, and netdev models. It also includes debug-only register-name tables under `REG_DEBUG`, making MMIO tracing compile-time selectable.

## Risks
Because this file encodes raw hardware layouts, any incorrect bit mask, endianness annotation, descriptor offset, or default value can corrupt DMA or misprogram the MAC. `ETH_CRC_LEN` is defined as 2 in the RX extra length calculation, which is unusual relative to the common 4-byte Ethernet FCS and should be treated as hardware-specific, not generalized. Several enum values share bit positions depending on descriptor context, so code must use the correct descriptor view. The static debug name arrays are only compiled under `REG_DEBUG` but must remain aligned with register spacing if enabled.

## Test Signals
Compilation across relevant kernel configs is the first signal because the header drives many inline and macro call sites. Runtime signals include correct register dumps from ethtool, clean RX/TX descriptor ownership transitions under DMA stress, NAPI scheduling behavior, WoL bit programming, PHY link/speed reporting, and successful operation on chip revisions that trigger `is_buggy250()` and `new_phy_power_ctrl()` branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/jme.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/korina.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/korina.c

## Purpose
`korina.c` implements the IDT RC32434/Korina on-chip Ethernet controller as a platform driver. It manages MAC registers, separate RX and TX DMA register blocks, fixed-size descriptor rings, MII management, periodic media polling, NAPI RX processing, TX completion interrupts, and Device Tree platform binding.

## Important APIs, Types, And Functions
Hardware layout is described by `struct eth_regs`, `struct dma_reg`, and `struct dma_desc`. Runtime state is `struct korina_private`, containing mapped MAC/DMA registers, coherent RX/TX rings, skb and DMA-address arrays, ring indexes, chain status, IRQs, NAPI, MII state, media timer, restart work, and clock-derived MDIO frequency.

Key functions are `korina_probe()`, `korina_open()`, `korina_close()`, `korina_init()`, `korina_alloc_ring()`, `korina_free_ring()`, `korina_send_packet()`, `korina_tx()`, `korina_rx()`, `korina_poll()`, RX/TX DMA IRQ handlers, `korina_mdio_read()`, `korina_mdio_write()`, `korina_check_media()`, and `korina_restart_task()`. Integration surfaces are `korina_netdev_ops`, `netdev_ethtool_ops`, `korina_driver`, and `korina_match`.

## Control Flow
Probe allocates an Ethernet device with devres, loads or randomizes the MAC address, enables an optional `mdioclk`, maps named resources `emac`, `dma_rx`, and `dma_tx`, allocates coherent descriptor rings with `dmam_alloc_coherent()`, initializes locks/NAPI/MII, registers the netdev, and sets up the media timer and restart work.

Open calls `korina_init()` before IRQ registration. Initialization aborts any running DMA, resets the Ethernet logic, allocates and initializes rings, starts RX DMA at descriptor zero, unmasks DMA interrupts, programs address filters and MAC timing, configures MII clocking, enables RX, checks media, enables NAPI, and starts the queue. RX IRQ masks DONE/HALT/ERR and schedules NAPI; `korina_poll()` processes complete descriptors, replaces buffers, sends good packets with GRO, refreshes descriptors, restarts halted RX DMA, and unmasks IRQs after NAPI completes. TX maps a packet into the next descriptor, updates the chain or next-descriptor pointer depending on DMA activity, and TX IRQ cleanup frees completed skbs, updates stats, wakes the queue, and starts deferred chains.

## State And Persistence
Ring indexes and chain state (`rx_next_done`, `tx_next_done`, `tx_chain_head`, `tx_chain_tail`, `tx_chain_status`, `tx_count`, `tx_full`) persist for each open instance. The media timer polls link once per second through MII helpers and updates full-duplex MAC state. Restart work is scheduled on TX timeout and reconstructs rings and hardware state. The driver does not use persistent nonvolatile state beyond the configured MAC address and PHY settings exposed through MII/ethtool.

## Dependencies And Integration Points
The driver depends on platform resources, optional clocks, Device Tree compatible `idt,3243x-emac`, named MMIO resources, Linux DMA mapping, NAPI, MII library, ethtool link settings, timers, workqueues, and optional netpoll. It assumes fixed RX buffer size `KORINA_RBSIZE` and fixed 64-entry RX/TX rings.

## Risks
`korina_alloc_ring()` can leak already allocated RX skbs or DMA mappings if allocation or mapping fails mid-loop before `korina_free_ring()` sees fully initialized state. The RX DMA abort loop busy-waits for HALT while only updating the watchdog timestamp. `korina_restart_task()` disables IRQs and returns immediately on failed `korina_init()`, which can leave the interface in a partially disabled state. The driver supports only default-size receive buffers, so MTU above 1500 is not supported. The MDIO wait helper appears to poll for the busy bit being set rather than cleared, so hardware behavior should be verified carefully before modifying it.

## Test Signals
Probe tests should cover DT resources and optional clock absence/presence. Runtime tests should exercise open/close, RX flood, TX ring-full behavior, TX timeout restart, multicast/promiscuous/all-multicast filters, MII ioctl and ethtool link setting changes, DMA error IRQs, allocation failure during ring setup and RX replacement, and removal while the timer/work paths are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/korina.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/lantiq_etop.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/lantiq_etop.c

## Purpose
`lantiq_etop.c` implements the older Lantiq XWAY ETOP Ethernet MAC as a platform driver. It uses fixed Lantiq DMA channels for one TX and one RX path, provides an MDIO bus, connects to a PHY through phylib, and exposes a multi-queue netdev that effectively selects queue zero.

## Important APIs, Types, And Functions
Runtime state is split between `struct ltq_etop_priv` and `struct ltq_etop_chan`. `ltq_etop_priv` stores the netdev, platform device, board/platform Ethernet data, MII bus, channel array, DMA burst lengths, and a spinlock. Each channel wraps a `struct ltq_dma_channel`, a NAPI object, channel index, TX free pointer, and skb array.

Core functions include `ltq_etop_probe()`, `ltq_etop_init()`, `ltq_etop_hw_init()`, `ltq_etop_hw_exit()`, `ltq_etop_open()`, `ltq_etop_stop()`, `ltq_etop_tx()`, `ltq_etop_poll_rx()`, `ltq_etop_poll_tx()`, `ltq_etop_dma_irq()`, `ltq_etop_mdio_init()`, `ltq_etop_mdio_probe()`, `ltq_etop_mdio_rd()`, `ltq_etop_mdio_wr()`, `ltq_etop_change_mtu()`, and `ltq_etop_tx_timeout()`.

## Control Flow
The module registers a platform driver through `platform_driver_probe()`. Probe maps the ETOP register range, allocates an Ethernet device with four queues, reads required `lantiq,tx-burst-length` and `lantiq,rx-burst-length` properties, attaches weighted NAPI instances to the fixed TX channel 1 and RX channel 6, then registers the netdev. Netdev `.ndo_init` runs `ltq_etop_init()`, which enables PPE, configures MII/RMII mode, enables CRC generation, initializes the DMA port, allocates TX/RX channels and IRQs, sets MTU and MAC address, configures multicast filtering, creates an MDIO bus, finds the first PHY, connects it, limits it to 100 Mbps, and exposes PHY ethtool operations.

Open enables DMA and NAPI per fixed channel, starts the PHY, and starts all TX queues. RX NAPI consumes completed descriptors, allocates a replacement skb under lock, closes DMA on allocation failure, passes the received skb with `netif_receive_skb()`, and acks DMA IRQs on completion. TX pads short frames, checks descriptor availability, maps the skb, writes a burst-aligned DMA address and ownership bits, advances the ring, and stops the queue if the next descriptor is owned. TX NAPI frees completed skbs and wakes queues.

## State And Persistence
The global `ltq_etop_membase` holds the single mapped register base used by access macros. Per-device state includes platform data MAC/MII mode, DMA ring descriptors inside `ltq_dma_channel`, per-channel skb arrays, current DMA descriptor indexes, PHY connection state, and burst length configuration. Hardware register state is reconstructed during `.ndo_init`, timeout recovery, and remove cleanup.

## Dependencies And Integration Points
This file depends on Lantiq SoC headers (`lantiq_soc.h`, `xway_dma.h`, `lantiq_platform.h`), PMU/PPE controls, platform data, Linux phylib/mdiobus, NAPI, DMA mapping, and generic netdev APIs. It exposes ethtool link settings through phylib and uses `phy_do_ioctl` for MII ioctls.

## Risks
The driver mixes `dma_map_single()` with an immediate overwrite of RX descriptor `addr` using `CPHYSADDR()`, and TX also uses `CPHYSADDR()` for offset calculation; this is architecture-specific and risky on systems where DMA addresses differ from physical addresses. MDIO read/write busy loops have no timeout. `ltq_etop_init()` error paths call `unregister_netdev()` and `free_netdev()` from `.ndo_init`, which is unusual because registration is in progress. `ltq_etop_hw_init()` does not unwind already allocated/requested channels if a later channel setup fails. Remove calls hardware and MDIO cleanup even though netdev initialization may have failed partway.

## Test Signals
Coverage should include MII and RMII platform modes, missing burst properties, invalid MAC fallback, PHY absent and PHY connect failure, repeated register/unregister, open/stop cycles, TX timeout recovery, RX allocation failure, DMA IRQ handling, queue stop/wake, MTU updates, multicast/promiscuous filtering, and DMA address correctness on the target Lantiq architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/lantiq_etop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/lantiq_xrx200.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/lantiq_xrx200.c

## Purpose
`lantiq_xrx200.c` implements the Lantiq/Intel XRX200 PMAC Ethernet interface. It presents a netdev for the CPU-facing PMAC/DMA path, configures PMAC header/CRC behavior, uses one RX and one TX Lantiq DMA channel, and handles large packets through RX fragment chaining.

## Important APIs, Types, And Functions
`struct xrx200_priv` owns the clock, RX/TX channels, buffer sizing, netdev, device pointer, and PMAC register mapping. `struct xrx200_chan` wraps one `ltq_dma_channel`, a NAPI object, skb or RX fragment arrays, TX cleanup pointer, in-progress RX skb chain, and backpointer to private state.

Important functions are `xrx200_probe()`, `xrx200_remove()`, `xrx200_dma_init()`, `xrx200_hw_cleanup()`, `xrx200_open()`, `xrx200_close()`, `xrx200_start_xmit()`, `xrx200_poll_rx()`, `xrx200_hw_receive()`, `xrx200_tx_housekeeping()`, `xrx200_change_mtu()`, `xrx200_dma_irq()`, and PMAC register helpers `xrx200_pmac_r32()`, `xrx200_pmac_w32()`, and `xrx200_pmac_mask()`.

## Control Flow
Probe allocates a managed Ethernet device, sets MTU bounds from the DMA data limit, maps PMAC registers, reads named RX/TX IRQs, enables a clock, obtains or randomizes the MAC address, initializes Lantiq DMA rings, enables the clock gate, configures PMAC inter-packet gap and header/CRC controls, adds RX and TX NAPI, stores platform data, and registers the netdev. Open enables TX NAPI/DMA/IRQ, enables RX NAPI/DMA, flushes bootloader-leftover RX packets, enables RX IRQ, and wakes the queue. Close stops the queue, disables NAPI, and closes DMA channels.

RX NAPI loops over completed descriptors, replaces the buffer first, builds an skb from the old fragment, and either starts a new chained skb on SOP, appends fragments to `frag_list`, or submits the complete packet on EOP. TX maps a padded skb, computes a burst-alignment offset from the DMA mapping, writes descriptor address/control ownership, advances the ring, stops the queue when full, and accounts with BQL. TX NAPI consumes completed descriptors, updates stats and BQL, frees skbs, clears descriptors, and wakes the queue.

## State And Persistence
Persistent runtime state consists of DMA descriptor rings and indexes, RX fragment buffers, any partially assembled RX `skb_head`/`skb_tail`, TX skb slots, clock state, PMAC register configuration, and computed `rx_buf_size`/`rx_skb_size`. `xrx200_change_mtu()` updates buffer sizing and, for MTU increases, temporarily closes RX DMA, drains pending packets, reallocates each RX buffer, then reopens RX if the interface was running.

## Dependencies And Integration Points
The driver depends on platform Device Tree compatible `lantiq,xrx200-net`, named `rx` and `tx` IRQs, one MMIO resource, a clock, `xway_dma.h`, Linux NAPI, BQL, DMA mapping, and `of_get_ethdev_address()`. It does not connect to phylib directly in this file; it handles the CPU PMAC data path and leaves switch/PHY details elsewhere in the platform.

## Risks
RX buffer cleanup checks `priv->chan_rx.skb[i]` in one error path even though RX buffers are stored in the `rx_buff` union member, so that condition may not reflect allocation state. `xrx200_start_xmit()` stores the skb before DMA mapping; on mapping failure it frees the skb but does not clear the ring slot, which can make the descriptor appear busy later. RX multi-fragment assembly assumes an EOP will follow a SOP; malformed descriptor sequences can leave `skb_head` held. MTU reallocation frees old fragments after allocating replacements, but rollback after partial failure leaves a mixed ring that must be tested on hardware.

## Test Signals
Test signals include probe with missing IRQ/clock/resource, random MAC fallback, open/close cycles, RX flushing after bootloader traffic, fragmented RX packet assembly, malformed SOP/EOP descriptor sequences, TX ring full and DMA mapping failures, BQL accounting, MTU increase/decrease and rollback, removal after failed probe steps, and traffic under PMAC header/CRC configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/lantiq_xrx200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/litex/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/litex/Kconfig

## Purpose
This Kconfig file introduces the LiteX Ethernet vendor menu and the `LITEX_LITEETH` driver option. It allows kernel configuration to expose LiteX FPGA soft-SoC Ethernet support without affecting other Ethernet vendors when disabled.

## Important Symbols
`NET_VENDOR_LITEX` is a `bool` menu gate, defaults to `y`, and follows the standard Ethernet vendor pattern: disabling it hides LiteX-specific questions rather than directly disabling common networking. `LITEX_LITEETH` is a `tristate` option named "LiteX Ethernet support" and depends on `OF && HAS_IOMEM`, matching the platform driver's Device Tree and MMIO requirements.

## Control Flow
Kconfig evaluation first offers the vendor gate. If enabled, it offers `LITEX_LITEETH`; choosing built-in or module controls whether `litex_liteeth.o` is compiled by the sibling Makefile. The help text identifies LiteX as an FPGA-oriented soft SoC and LiteEth as the target Ethernet core.

## State And Persistence
The selected symbols persist in the kernel `.config`. `LITEX_LITEETH=m` leads to a loadable module, `y` links it into the kernel image, and `n` omits the driver object.

## Dependencies And Integration Points
This file integrates with the parent Ethernet Kconfig hierarchy and with `drivers/net/ethernet/litex/Makefile`. The `OF` dependency mirrors `of_device_id` matching in `litex_liteeth.c`; `HAS_IOMEM` mirrors use of MMIO resource mapping and LiteX CSR accessors.

## Risks
The vendor gate defaults to enabled, so LiteX options appear broadly in configs even when no FPGA LiteX hardware exists. The driver depends only on `OF` and `HAS_IOMEM`; if future code adds PHY, MDIO, DMA, or PTP dependencies, this Kconfig must be updated or compile/runtime failures may appear under randconfig.

## Test Signals
Useful checks are `allnoconfig`, `defconfig`, `allyesconfig`, `allmodconfig`, and randconfig builds with `OF` or `HAS_IOMEM` disabled/enabled. Confirm that `CONFIG_LITEX_LITEETH=m` emits a module and `CONFIG_NET_VENDOR_LITEX=n` hides the driver option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/litex/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/litex/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/litex/Makefile

## Purpose
This Makefile maps the LiteX Ethernet Kconfig selection to the object built by Kbuild.

## Important Entries
The only build rule is `obj-$(CONFIG_LITEX_LITEETH) += litex_liteeth.o`. When the symbol is `y`, the object is built in; when `m`, it is built as a module; when unset, it is omitted.

## Control Flow
Kbuild expands `obj-*` variables after configuration. This file has no conditional subdirectories or composite objects, so the build path is direct from `CONFIG_LITEX_LITEETH` to `litex_liteeth.c`.

## State And Persistence
Build state is entirely driven by `.config` and generated Kbuild metadata. No runtime state is introduced here.

## Dependencies And Integration Points
It integrates with `litex/Kconfig`, the parent Ethernet Makefile that descends into this directory, and the `litex_liteeth.c` module metadata.

## Risks
The file is intentionally simple. The main risk is drift: renaming the source file or adding companion objects without updating this rule would break the build. Any future split into multiple objects would require a composite `litex_liteeth-y` style rule.

## Test Signals
Build with `CONFIG_LITEX_LITEETH=y`, `m`, and unset. Check that module naming and dependency metadata match the driver source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/litex/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/litex/litex_liteeth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/litex/litex_liteeth.c

## Purpose
`litex_liteeth.c` is a small platform netdev driver for the LiteX LiteEth FPGA Ethernet core. It accesses LiteX CSR registers and shared slot buffers through MMIO, handles simple interrupt-driven RX/TX events, and exposes a basic Ethernet interface with software statistics.

## Important APIs, Types, And Functions
`struct liteeth` stores CSR base, buffer bases, slot size/counts, current TX/RX slot indexes, device, and netdev. The main routines are `liteeth_probe()`, `liteeth_open()`, `liteeth_stop()`, `liteeth_interrupt()`, `liteeth_rx()`, `liteeth_start_xmit()`, `liteeth_get_stats64()`, and `liteeth_setup_slots()`. Integration is through `liteeth_netdev_ops`, `liteeth_of_match`, and `liteeth_driver`.

## Control Flow
Probe allocates a managed Ethernet device, allocates per-CPU software stats, gets the platform IRQ, maps named resources `mac` and `buffer`, reads optional slot properties (`litex,rx-slots`, `litex,tx-slots`, `litex,slot-size`) with defaults of two slots and 0x800 bytes, divides the buffer region into RX slots followed by TX slots, obtains or randomizes the MAC address, attaches netdev ops, and registers the netdev with devres.

Open clears pending reader/writer events, requests the IRQ, enables writer and reader event interrupts, marks carrier on, and starts the queue. The IRQ handler acknowledges TX reader events and wakes the queue if stopped, then handles writer events by reading one received frame from the indicated slot and acknowledging pending bits. TX checks `LITEETH_READER_READY`, stops the queue and returns busy if hardware is not ready, rejects packets larger than `slot_size`, copies skb data into the current TX slot, writes slot/length/start CSRs, updates software stats, advances the TX slot modulo count, and frees the skb.

## State And Persistence
Runtime state is minimal: current `tx_slot`, configured slot counts/size, mapped CSR/buffer bases, IRQ, netdev carrier/queue state, and per-CPU software stats. There is no PHY, MDIO, DMA mapping, NAPI, or persistent hardware configuration in this driver. Slot layout is derived at probe time from Device Tree.

## Dependencies And Integration Points
The driver depends on LiteX CSR accessors (`litex_read8/16/32`, `litex_write8/16`), platform MMIO resources named `mac` and `buffer`, Device Tree compatible `litex,liteeth`, `of_get_ethdev_address()`, `devm_register_netdev()`, and the generic Ethernet stack. Kconfig requires `OF && HAS_IOMEM`.

## Risks
The interrupt handler processes at most one RX frame per interrupt and uses `netif_rx()` rather than NAPI, so heavy traffic may suffer drops or interrupt pressure. `liteeth_rx()` validates length only against a hard-coded 2048, not `slot_size`, which can be inconsistent if DT sets a smaller slot. TX queue stopping relies on a later reader event to wake it. There is no explicit carrier/PHY negotiation, so carrier is forced on at open. Buffer resource sizing is not checked against `num_rx_slots + num_tx_slots` times `slot_size`.

## Test Signals
Test with default and explicit slot DT properties, invalid or missing MAC, oversized TX frames, hardware-not-ready TX, RX zero length, RX length above 2048, interrupt storms, queue wake events, stats64 accuracy, open/close IRQ lifetime, and buffer resource bounds on FPGA designs with nondefault slot layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/litex/litex_liteeth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/Kconfig

## Purpose
This Kconfig file defines the Marvell Ethernet vendor menu and configuration symbols for multiple Marvell wired Ethernet families: MV643XX/Orion, MVMDIO, MVNETA and its buffer manager, MVPP2 and PTP support, PXA168, SKGE, SKY2, and sourced subtrees for Octeon and Prestera drivers.

## Important Symbols
`NET_VENDOR_MARVELL` gates the menu and defaults to `y` when broad platform dependencies are met. `MV643XX_ETH` depends on older PPC/Orion platforms or compile testing plus `INET`, and selects `PHYLIB` and `MVMDIO`. `MVMDIO` depends on `HAS_IOMEM` and selects `PHYLIB`. `MVNETA` depends on `ARCH_MVEBU || COMPILE_TEST` and selects `MVMDIO`, `PHYLINK`, `PAGE_POOL`, and `PAGE_POOL_STATS`. `MVNETA_BM_ENABLE` and hidden `MVNETA_BM` coordinate buffer-manager support with 32-bit-only constraints and module/built-in compatibility. `MVPP2` selects `MVMDIO`, `PHYLINK`, and `PAGE_POOL`; `MVPP2_PTP` gates PTP support on compatible built-in/module combinations. `PXA168_ETH`, `SKGE`, `SKGE_DEBUG`, `SKGE_GENESIS`, `SKY2`, and `SKY2_DEBUG` configure additional Marvell PCI/SoC adapters.

## Control Flow
Kconfig first evaluates the vendor menu. If enabled, each driver symbol becomes visible according to architecture, bus, debugfs, PTP, and compile-test conditions. Several symbols select shared infrastructure instead of requiring the user to pick it manually. The file then sources Kconfig files for `octeontx2`, `octeon_ep`, `octeon_ep_vf`, and `prestera`, extending the same vendor menu with subtree-specific options.

## State And Persistence
Selections persist in `.config` and determine which Marvell objects and subdirectories the sibling Makefile builds. Hidden `MVNETA_BM` encodes policy so buffer-manager support is built in a form compatible with `MVNETA`.

## Dependencies And Integration Points
This file integrates with the parent Ethernet Kconfig, Marvell Makefile, phylib/phylink, page-pool infrastructure, debugfs, PTP clock infrastructure, architecture symbols, and sourced child Kconfig files. It is a dependency hub: incorrect selects or depends clauses can break randconfig builds in unrelated Marvell drivers.

## Risks
The mixed use of `select` and architecture dependencies can hide missing lower-level dependencies in randconfig. `MVPP2_PTP` has a nuanced built-in/module expression that must stay aligned with both `PTP_1588_CLOCK` and `MVPP2` link modes. `MVNETA_BM` must not become modular when `MVNETA=y`; the hidden symbol enforces this and is easy to regress. Sourced subtree paths must match directory structure or Kconfig parsing fails.

## Test Signals
Use `allmodconfig`, `allyesconfig`, `randconfig`, and platform-specific configs for MVEBU, Orion, PPC32, PCI-only, and COMPILE_TEST. Verify that selected symbols produce expected objects, PTP combinations link correctly, debug options require DEBUG_FS, and sourced Octeon/Prestera menus remain reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/Makefile

## Purpose
This Makefile maps Marvell Ethernet Kconfig symbols to object files and child directories built by Kbuild.

## Important Entries
The file builds `mvmdio.o`, `mv643xx_eth.o`, `mvneta_bm.o`, `mvneta.o`, `pxa168_eth.o`, `skge.o`, and `sky2.o` based on their matching `CONFIG_*` symbols. It descends into `mvpp2/` when `CONFIG_MVPP2` is enabled. It always descends into `octeon_ep/`, `octeon_ep_vf/`, `octeontx2/`, and `prestera/`; those subdirectories are expected to gate their own objects internally.

## Control Flow
During Kbuild, `obj-$(CONFIG_...)` expands to built-in, module, or omitted objects. `obj-y` subdirectories are visited unconditionally as part of the Marvell vendor tree, allowing child Makefiles to evaluate their own config-controlled objects.

## State And Persistence
There is no runtime state. Build state comes from `.config`, generated Kbuild variables, and child Makefile decisions.

## Dependencies And Integration Points
It integrates directly with `marvell/Kconfig` symbols and the source files/subdirectories in the Marvell Ethernet driver tree. It also relies on child directories having Makefiles that correctly handle disabled configs because several are entered through unconditional `obj-y`.

## Risks
The unconditional subdirectory descent can expose child Makefile errors even when a feature is disabled. Renaming a driver source or changing a Kconfig symbol without updating this file breaks build coverage. The `mvpp2/` directory is conditional while Octeon/Prestera directories are unconditional, so maintainers need to preserve the intended split when adding new Marvell families.

## Test Signals
Build with each Marvell symbol as `y`, `m`, and unset where legal. Run `make M=drivers/net/ethernet/marvell` style module builds if supported by the source tree, plus randconfig to catch stale object names or child-directory dependency problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/Makefile -->
