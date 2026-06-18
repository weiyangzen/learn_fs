# subset-b-004658 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_define.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_define.h

Purpose: Central private ABI for the Sunplus SP7021 dual 10/100 L2 switch Ethernet driver. It defines the two-port model, interrupt bit groups, switch table/VLAN/PHY/register field masks, descriptor ring sizing, DMA descriptor wire format, SKB bookkeeping, and the common/netdev-private state shared by all Sunplus implementation files.

Important APIs/types: `MAX_NETDEV_NUM` fixes the driver at two net devices. `MAC_INT_RX`, `MAC_INT_TX`, and `MAC_INT_MASK_DEF` define interrupt policy used by open, interrupt, and NAPI paths. `struct spl2sw_mac_desc` is the four-word hardware descriptor for TX/RX rings. `struct spl2sw_skb_info` tracks one SKB DMA mapping. `struct spl2sw_common` owns MMIO base, platform resources, coherent descriptor memory, RX/TX rings, NAPI contexts, MDIO bus, locks, netdev array, and the enabled-port bitmask. `struct spl2sw_mac` is per-netdev state with MAC address, PHY node/mode, LAN port bit, and VLAN identifiers.

Control flow and state: This header does not execute code, but its constants encode the runtime topology. TX has one 16-entry ring plus two guard descriptors, RX has two 16-entry queues, and all hardware ownership is coordinated through `TXD_OWN`/`RXD_OWN` plus memory barriers in implementation files. Persistent driver state is in memory only; hardware-visible persistence is descriptor DMA memory and switch registers programmed from these masks.

Dependencies and integration points: Consumers depend on Linux `BIT`, `GENMASK`, descriptor DMA APIs, phylib, NAPI, platform resources, clocks/resets, and register offsets from `spl2sw_register.h`. The `lan_port` bit values are reused as VLAN, forwarding, and forced-RMII bit selectors, so all files must treat them consistently.

Risks and test signals: Ring sizes and bit masks are hard-coded, so off-by-one or wrong queue priority assumptions break data path behavior. Validate two-port open/close combinations, TX ring full/wake behavior, RX high/low queue handling, VLAN isolation between ports, MDIO/PHY link transitions, and reset recovery after descriptor errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_define.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_desc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_desc.c

Purpose: Allocates, initializes, flushes, cleans, and frees Sunplus TX/RX DMA descriptor rings and their SKB mapping side tables.

Important APIs/functions: `spl2sw_descs_init()` seeds ring counts, positions, and buffer size, allocates one coherent descriptor block, clears TX descriptors, then allocates/maps all RX SKBs. `spl2sw_descs_alloc()` lays out TX descriptors first, then RX high/low queues in the same coherent allocation. `spl2sw_rx_descs_init()` creates RX SKBs, maps them for DMA, writes buffer addresses/lengths/EOR, and sets `RXD_OWN`. `spl2sw_rx_descs_flush()` re-hands existing RX buffers to hardware after reset. `spl2sw_tx_descs_clean()`, `spl2sw_rx_descs_clean()`, `spl2sw_descs_clean()`, and `spl2sw_descs_free()` unwind mappings, SKBs, side tables, and coherent memory.

Control flow and state: Descriptor state lives in `struct spl2sw_common`: `desc_base/desc_dma/desc_size`, `tx_desc`, `rx_desc[]`, `rx_skb_info[]`, and ring indices. Hardware ownership ordering uses `wmb()` before setting `RXD_OWN`, and cleanup clears `cmd1` before zeroing other fields. RX descriptors are populated for fixed `MAC_RX_LEN_MAX` buffers and recycled by NAPI.

Dependencies and integration points: Called from probe, remove, MAC reset, and interrupt recovery paths. It depends on coherent DMA allocation, `dma_map_single()`, `dma_unmap_single()`, `netdev_alloc_skb()`, and Sunplus descriptor field definitions.

Risks and test signals: A DMA mapping failure after assigning `rx_skbinfo[j].skb` leaks the just-allocated SKB because the mapping is not stored and the local SKB is not freed before `spl2sw_rx_descs_clean()`. `spl2sw_tx_descs_init()` clears `TX_DESC_NUM + MAC_GUARD_DESC_NUM`, while TX cleanup iterates only real TX descriptors. Test probe failure unwinds, RX allocation pressure, reset flushing with live RX buffers, TX timeout cleanup, and DMA API debug for map/unmap symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_desc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_desc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_desc.h

Purpose: Declares the descriptor lifecycle API used by the Sunplus platform driver, MAC reset path, and NAPI cleanup logic.

Important APIs: Exports RX flush, TX/RX clean, combined clean/free, TX/RX init, descriptor allocation, and full descriptor initialization helpers. The separation lets probe allocate and initialize once, reset reflush RX descriptors without reallocating, and remove free all DMA resources.

State and dependencies: The header assumes `struct spl2sw_common` and descriptor constants from `spl2sw_define.h`. Callers own locking and device quiescing before invoking cleanup or reinitialization.

Risks and test signals: The API is low-level and not self-serializing. Tests should exercise all call sites: probe failure after allocation, normal remove, TX timeout reset, and cleanup with partially initialized RX queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_driver.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_driver.c

Purpose: Implements the Sunplus SP7021 platform/netdev driver: resource acquisition, netdev registration, open/stop/xmit/ioctl operations, MAC address retrieval, PHY/MDIO setup, NAPI registration, and teardown.

Important APIs/functions: `spl2sw_probe()` maps registers, gets IRQ/clock/reset, initializes descriptors/MAC/MDIO, parses `ethernet-ports/port` child nodes, registers up to two netdevs, programs static MAC table entries, connects PHYs, and enables RX/TX NAPI. `spl2sw_ethernet_open()` marks the port enabled, starts hardware, unmasks TX/RX interrupts, starts PHY, and starts the queue. `spl2sw_ethernet_stop()` stops queue/PHY, clears the enabled-port bit, and may stop hardware. `spl2sw_ethernet_start_xmit()` pads short frames, maps one linear SKB, fills one TX descriptor with VLAN/length/SOP/EOP, advances the ring, optionally stops the queue, and triggers CPU TX. `spl2sw_ethernet_tx_timeout()` stops all queues, soft-resets hardware, and wakes queues. MAC address helpers read nvmem cells, repair reversed Sunplus OUI byte order, or generate random addresses.

Control flow and state: One `struct spl2sw_common` is shared by both netdevs, and each `struct spl2sw_mac` binds one netdev to a switch port/VLAN. TX ring state is global, protected by `tx_lock`, so both netdev queues feed the same descriptor ring. `comm->enable` is a bitmask controlling whether CPU and LAN ports are disabled or active. NAPI contexts are attached to the first valid netdev but process shared rings for both ports.

Dependencies and integration points: Integrates platform bus, device tree child-port parsing, nvmem, phylib, MDIO, clocks, reset controls, DMA descriptor helpers, Sunplus MAC helpers, and netdev operations. Compatible string is `sunplus,sp7021-emac`.

Risks and test signals: Error paths after `spl2sw_descs_init()` and `spl2sw_mdio_init()` do not always free descriptors, and child `phy_node` references from `of_parse_phandle()` are not put in this file. Shared TX queue stop/wake must be valid for two netdevs. Test no valid ports, one-port and two-port DTs, nvmem defer/invalid MAC/random fallback, concurrent traffic on both ports, TX timeout recovery, open/stop one port while the other remains active, and remove after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_int.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_int.c

Purpose: Handles Sunplus interrupt dispatch plus RX/TX NAPI polling for the shared descriptor rings.

Important APIs/functions: `spl2sw_ethernet_interrupt()` reads/acks `L2SW_SW_INT_STATUS_0`, masks RX and/or TX interrupt bits, accounts descriptor errors, and schedules RX/TX NAPI. `spl2sw_rx_poll()` drains high-priority then low-priority RX queues, validates source port and length/error bits, unmaps DMA, submits packets with `netif_receive_skb()`, allocates replacement SKBs, reinitializes descriptors, and unmasks RX interrupts. `spl2sw_tx_poll()` reclaims completed TX descriptors, updates the stats for the VLAN-selected netdev, unmaps/free SKBs, clears full state, wakes stopped queues, and unmasks TX interrupts.

Control flow and state: RX source selection comes from `RXD_PKT_SP`; TX completion stats recover the netdev by `ffs(FIELD_GET(TXD_VLAN, cmd)) - 1`. RX and TX NAPI both complete and re-enable interrupt bits after their loops. TX ring mutation is protected by `tx_lock`; interrupt mask register access is serialized by `int_mask_lock`.

Dependencies and integration points: Depends on descriptor layout, shared `spl2sw_common`, netdev stats, DMA mapping APIs, NAPI, and Sunplus interrupt mask/status registers. It is wired by `spl2sw_driver.c` through `devm_request_irq()` and `netif_napi_add*()`.

Risks and test signals: `spl2sw_rx_poll()` and `spl2sw_tx_poll()` call `napi_complete()` unconditionally even if they used the whole budget, which can re-enable interrupts while work remains. In RX low-priority processing, `h_desc` is used as the saved high-priority descriptor pointer; priority break behavior should be verified carefully. Replacement SKB allocation failures leave descriptors without buffers until later cleanup/reset. Test NAPI budget exhaustion, interrupt storms, descriptor errors, RX allocation failure, mixed high/low priority traffic, invalid source port, and TX ring full wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_int.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_int.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_int.h

Purpose: Declares the Sunplus interrupt and NAPI poll entry points.

Important APIs: `spl2sw_rx_poll()` and `spl2sw_tx_poll()` are passed to NAPI registration; `spl2sw_ethernet_interrupt()` is passed to `devm_request_irq()`.

State and dependencies: The prototypes assume `struct spl2sw_common` can be recovered from the NAPI container or IRQ `dev_id`. Implementation depends on the shared descriptor rings and interrupt mask lock in `spl2sw_common`.

Risks and test signals: Because these functions are invoked by core networking/IRQ contexts, signature changes or missing headers break probe-time registration. Build-test with NAPI and IRQ paths enabled; runtime-test interrupt masking/unmasking around poll completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mac.c

Purpose: Programs Sunplus switch/MAC hardware registers for port enablement, descriptor base addresses, flow/VLAN policies, MAC address table entries, multicast/promiscuous filtering, initialization, and soft reset.

Important APIs/functions: `spl2sw_mac_hw_init()` writes descriptor base addresses, flow-control thresholds, LED polarity, CPU/port learning behavior, forced RMII mode, PVID/VLAN membership, storm/RMC policy, and default interrupt mask. `spl2sw_mac_hw_start()` enables CPU port 0, CRC padding, and currently enabled LAN ports. `spl2sw_mac_hw_stop()` masks/clears interrupts and disables CPU ports when no netdev is enabled, then disables inactive LAN ports. `spl2sw_mac_addr_add()` and `spl2sw_mac_addr_del()` write MAC table entries and poll for completion. `spl2sw_mac_rx_mode_set()` maps netdev promiscuous/allmulti/multicast state onto CPU forwarding disable bits. `spl2sw_mac_soft_reset()` stops hardware, flushes RX descriptors, resets ring indices, reinitializes registers, and restarts.

Control flow and state: Hardware state persists in MMIO registers and the switch address table. `comm->enable` drives port-disable bits. VLAN group 0 maps CPU0+port0, and group 1 maps CPU0+port1, matching per-netdev `to_vlan` and `vlan_id`. The implementation relies on `FIELD_PREP()` with port bitmasks for multi-bit fields.

Dependencies and integration points: Called by probe, open/stop, set-rx-mode, set-MAC-address, and TX timeout paths. Depends on descriptor DMA addresses already being allocated and on register/bit definitions from `spl2sw_register.h`/`spl2sw_define.h`.

Risks and test signals: Several clear operations use `reg &= FIELD_PREP(mask, ~comm->enable) | ~mask`, so bitfield behavior with inverted small port masks is delicate. MAC table add/delete timeouts are short and hardware-dependent. Test per-port VLAN isolation, MAC address changes, promisc/allmulti/multicast transitions, open/stop one port while preserving the other, soft reset under TX load, and link speed/duplex changes after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mac.h

Purpose: Declares Sunplus MAC/switch hardware control helpers.

Important APIs: Exports start/stop, address add/delete, full hardware initialization, RX mode programming, common MAC initialization, and soft reset. These functions form the boundary between netdev/interrupt code and raw switch register programming.

State and dependencies: Callers pass either `struct spl2sw_common` for global switch operations or `struct spl2sw_mac` for per-port MAC table/filter operations. Correctness depends on descriptors being initialized before `spl2sw_mac_hw_init()` programs base addresses.

Risks and test signals: The API assumes callers serialize lifecycle transitions with netdev state and TX locks where needed. Test build linkage across driver, interrupt, and PHY files plus runtime start/stop/reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mdio.c

Purpose: Implements the Sunplus MDIO bus adapter over switch PHY control registers and registers it from the `mdio` device-tree child node.

Important APIs/functions: `spl2sw_mdio_init()` obtains the `mdio` child, allocates a devm `mii_bus`, fills read/write callbacks, registers it with `of_mdiobus_register()`, and stores `comm->mii_bus`. `spl2sw_mdio_remove()` unregisters the bus. `spl2sw_mii_read()` and `spl2sw_mii_write()` call `spl2sw_mdio_access()`. `spl2sw_mdio_access()` temporarily programs `MAC_EXT_PHY0_ADDR`, issues read/write command fields in `L2SW_PHY_CNTL_REG0`, polls `L2SW_PHY_CNTL_REG1`, then restores external PHY0 address to 31 to avoid hardware auto-MDIO side effects.

Control flow and state: MDIO access is serialized with `mdio_lock` around the critical address-select plus command write sequence. The selected external PHY address is transient register state; persistent driver state is only `comm->mii_bus`.

Dependencies and integration points: Integrates Linux MDIO/of_mdiobus with the Sunplus switch register interface. PHY connection in `spl2sw_phy.c` depends on this bus being registered before `of_phy_connect()`.

Risks and test signals: The command completion poll checks `val & cmd`, relying on read-ready/write-done bits matching command values. The address restore occurs after polling without holding `mdio_lock`, so concurrent reads/writes may need scrutiny. Test read/write across both PHY addresses, timeout behavior, concurrent phylib accesses, remove while PHYs are disconnected, and device-tree absence of `mdio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mdio.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mdio.h

Purpose: Declares MDIO lifecycle helpers for the Sunplus driver.

Important APIs: `spl2sw_mdio_init()` registers the hardware-backed MDIO bus; `spl2sw_mdio_remove()` unregisters it.

State and dependencies: Operates on `struct spl2sw_common`, filling and clearing `comm->mii_bus`. Must be called after registers/clocks/reset are ready and before PHY connection.

Risks and test signals: Return type is `u32` despite returning negative errno values; callers currently store it in `int`. Build and runtime tests should cover missing `mdio` node, probe defer from PHY children, and unregister on partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_phy.c

Purpose: Connects each Sunplus netdev to its PHY and mirrors phylib link state into forced RMII switch mode registers.

Important APIs/functions: `spl2sw_phy_connect()` iterates registered netdevs, calls `of_phy_connect()` with each port's PHY node/mode and `spl2sw_mii_link_change()` callback, enables asymmetric pause support, and logs attached PHY info. `spl2sw_phy_remove()` disconnects each netdev PHY. `spl2sw_mii_link_change()` updates link, speed, duplex, and pause bits in `L2SW_MAC_FORCE_MODE` for the port bit represented by `mac->lan_port`, then calls `phy_print_status()`.

Control flow and state: Link state is not cached in driver memory; each phylib callback rewrites the forced RMII register. The per-port bitmask controls which of the two RMII lanes is affected.

Dependencies and integration points: Depends on MDIO bus registration, valid `phy-handle` nodes parsed in probe, phylib state machine, and Sunplus force-mode bit definitions. Open/stop call `phy_start()`/`phy_stop()` in `spl2sw_driver.c`.

Risks and test signals: Register updates are not locked, so simultaneous link callbacks on two PHYs can race read-modify-write updates. Partial failure in `spl2sw_phy_connect()` does not disconnect already connected PHYs before returning. Test both PHYs flapping concurrently, 10/100 speed, half/full duplex, pause on/off, missing PHY, and remove after a one-port connect failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_phy.h

Purpose: Declares Sunplus PHY attach/detach helpers.

Important APIs: `spl2sw_phy_connect()` attaches phylib devices for all registered ports; `spl2sw_phy_remove()` disconnects them during remove.

State and dependencies: Operates on the shared `struct spl2sw_common` and each netdev's private `struct spl2sw_mac` PHY node/mode. Requires MDIO registration first and netdevs already created.

Risks and test signals: Callers must handle partial attach failure and must not call remove before netdev private PHY pointers are meaningful. Test probe failure unwind and normal unload with one or two PHYs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_register.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_register.h

Purpose: Defines Sunplus L2 switch MMIO register offsets used by the driver.

Important APIs/constants: Covers interrupt status/mask, flow-control thresholds, address table search/write registers, PVID/VLAN membership, port ability/status/control, CPU control, global control/reset/LED/watchdog, PHY control, forced MAC mode, CPU TX trigger, and descriptor base/current-pointer registers for CPU port instances.

Control flow and state: This file is declarative. Its offsets are the address contract for all `readl()`/`writel()` operations in descriptor, MAC, MDIO, PHY, interrupt, and driver code. Hardware state persists in these registers until reset or reprogramming.

Dependencies and integration points: Used with `comm->l2sw_reg_base` from `devm_platform_ioremap_resource()`. Bit positions come from `spl2sw_define.h`, so offset and bitfield headers must remain in sync with the SP7021 hardware manual.

Risks and test signals: A wrong offset corrupts unrelated switch state. Several CPU port 1 descriptor offsets are defined but current code primarily programs CPU port 0. Test register programming with hardware trace/debugfs where available, probe reset defaults, descriptor base addresses, MDIO transactions, and interrupt ack/mask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_register.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/Kconfig

Purpose: Adds Kconfig switches for Synopsys Ethernet devices and the DWC XLGMAC driver family.

Important APIs/options: `NET_VENDOR_SYNOPSYS` gates the vendor submenu and defaults to yes. `DWC_XLGMAC` is a tristate depending on `HAS_IOMEM && HAS_DMA` and selects `BITREVERSE` and `CRC32`, matching VLAN/MAC hash-table code in `dwc-xlgmac-hw.c`. `DWC_XLGMAC_PCI` is a tristate bus glue option depending on `DWC_XLGMAC && PCI`.

Control flow and state: Build-time only. These symbols decide whether the common XLGMAC object and optional PCI module are compiled and linked. No runtime state is stored here.

Dependencies and integration points: Makefile consumes `CONFIG_DWC_XLGMAC` and `CONFIG_DWC_XLGMAC_PCI`. Source code depends on selected CRC/bit-reversal helpers and on I/O memory/DMA capabilities.

Risks and test signals: Misconfigured dependencies would produce link failures or unusable drivers on non-DMA platforms. Test all three build modes: vendor disabled, XLGMAC built-in/module without PCI, and PCI glue built-in/module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/Makefile

Purpose: Defines how the Synopsys XLGMAC driver objects are linked.

Important APIs/build targets: `obj-$(CONFIG_DWC_XLGMAC) += dwc-xlgmac.o` builds the core module from `dwc-xlgmac-net.o`, `dwc-xlgmac-desc.o`, `dwc-xlgmac-hw.o`, `dwc-xlgmac-common.o`, and `dwc-xlgmac-ethtool.o`. `dwc-xlgmac-$(CONFIG_DWC_XLGMAC_PCI) += dwc-xlgmac-pci.o` conditionally adds PCI bus binding.

Control flow and state: Build-time composition only. The object list mirrors runtime layering: common probe/init, descriptor allocation, hardware ops, netdev/NAPI, ethtool, and optional PCI resource discovery.

Dependencies and integration points: Consumed by kbuild under the Synopsys Ethernet directory and driven by Kconfig symbols in the same folder.

Risks and test signals: Missing an object breaks operation table registration or module entry points. Build-test core and PCI configurations, including module builds, to catch unresolved symbols around `xlgmac_get_netdev_ops()`, `xlgmac_init_hw_ops()`, and `xlgmac_drv_probe()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-common.c

Purpose: Provides common XLGMAC driver initialization/removal, module metadata, default configuration, operation-table hookup, hardware feature discovery/printing, and debug packet/descriptor dumps.

Important APIs/functions: `xlgmac_drv_probe()` allocates a multiqueue netdev, stores device resources, initializes RSS mutex/debug level, calls `xlgmac_init()`, and registers the netdev. `xlgmac_init()` sets defaults, assigns IRQ/base/MAC, initializes desc/hw ops, resets hardware, reads feature registers, sets DMA mask, sizes TX/RX queues/rings from CPU and hardware capabilities, seeds RSS key/table/options, attaches netdev/ethtool ops, configures feature flags, and initializes coalescing. `xlgmac_drv_remove()` unregisters/frees the netdev. `xlgmac_get_all_hw_features()` decodes `MAC_HWF*` registers into `struct xlgmac_hw_features`; `xlgmac_print_all_hw_features()` logs decoded capabilities. Dump helpers print descriptors and packet bytes under debug.

Control flow and state: Persistent runtime state is `struct xlgmac_pdata` in netdev private memory. It stores register base, feature flags, queue counts, RSS tables, coalescing values, pause settings, stats, and operation tables. The file currently uses a static test MAC address instead of firmware/platform-provided addressing.

Dependencies and integration points: Called by PCI glue and bus-specific front ends. Integrates with `dwc-xlgmac-desc.c`, `dwc-xlgmac-hw.c`, `dwc-xlgmac-net.c`, `dwc-xlgmac-ethtool.c`, DMA mask APIs, netdev queue APIs, RSS helpers, and hardware register definitions.

Risks and test signals: Static MAC address is unsuitable for multiple devices. `dma_set_mask_and_coherent()` depends on decoded `dma_width`; bad feature reads can break DMA. Queue count selection must not exceed allocated `XLGMAC_MAX_DMA_CHANNELS`. Test probe/remove, multiple devices, feature combinations with/without TSO/RSS/RXCSUM/VLAN hash, DMA mask failures, and register feature decoding against known hardware revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-desc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-desc.c

Purpose: Owns XLGMAC channel/ring allocation, descriptor memory allocation, RX page-buffer management, TX SKB DMA mapping, and descriptor data cleanup.

Important APIs/functions: `xlgmac_init_desc_ops()` fills the descriptor operation table. `xlgmac_alloc_channels_and_rings()` allocates channel array plus TX/RX ring arrays and coherent descriptor rings. `xlgmac_map_tx_skb()` maps TSO headers, skb linear data, and frags into one or more descriptors, reserving context descriptors for MSS/VLAN changes. `xlgmac_map_rx_buffer()` allocates page-backed header and payload buffers and assigns DMA ranges. `xlgmac_tx_desc_init()` and `xlgmac_rx_desc_init()` bind descriptor metadata to DMA descriptors and call hardware reset/init callbacks. `xlgmac_unmap_desc_data()` frees TX mappings/SKBs and RX page references/mappings, including incomplete receive saved state.

Control flow and state: `struct xlgmac_ring` owns coherent descriptor memory and a parallel `struct xlgmac_desc_data` array. RX uses reusable page allocations split into 512-byte header buffers and `rx_buf_size` payload buffers; selected descriptors become responsible for unmapping pages when the page allocation is exhausted. TX mapping advances from `ring->cur` but hardware descriptor fields are filled later by `hw_ops->dev_xmit()`.

Dependencies and integration points: Used by open/close, restart, and hardware init paths. Depends on DMA APIs, page allocator, SKB fragment mapping, descriptor/hardware operation tables, and ring constants from `dwc-xlgmac.h`.

Risks and test signals: `xlgmac_init_ring()` leaks coherent descriptor memory if `desc_data_head` allocation fails because it returns without freeing `dma_desc_head` until outer cleanup sees a partially initialized ring. `xlgmac_alloc_channels()` increments `tx_ring`/`rx_ring` pointers and then frees the incremented pointer on error, which is fragile. TX error unwind maps descriptor indices linearly without wrapping, relying on sufficient ring space prechecks. Test allocation failure injection, DMA mapping failures for linear and fragmented SKBs, TSO/VLAN context transitions, RX page recycling, close/restart cleanup, and DMA API debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-desc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-ethtool.c

Purpose: Implements XLGMAC ethtool operations for driver info, debug message level, channel counts, interrupt coalescing, and hardware/stat counters.

Important APIs/functions: `xlgmac_get_ethtool_ops()` returns the static ops table. Driver info reports driver/version/bus and decoded hardware version tuple. Coalesce get/set maps RX usecs to DMA RIWT using `hw_ops->usec_to_riwt()`, validates RX/TX frame limits, stores new values, and calls hardware coalesce config. Stats support uses `xlgmac_gstring_stats[]` offsets into `struct xlgmac_pdata.stats`; `get_ethtool_stats()` refreshes MMC counters then copies u64 values.

Control flow and state: Ettool setters mutate `pdata->rx_riwt`, `rx_usecs`, `rx_frames`, and `tx_frames`, which directly affect RX descriptor interrupt bits and DMA RIWT. Stats are accumulated in software from reset-on-read MMC registers plus software events such as TSO packets and NAPI scheduling.

Dependencies and integration points: Consumes `struct xlgmac_hw_ops`, MMC read implementation in `dwc-xlgmac-hw.c`, stats layout in `dwc-xlgmac.h`, and standard ethtool/netdev APIs.

Risks and test signals: `supported_coalesce_params` advertises max-frames generally, but TX usecs are not configurable and `xlgmac_config_tx_coalesce()` is a no-op. Stats offsets depend on exact struct layout and u64 alignment. Test invalid coalesce bounds, live coalesce changes under traffic, ethtool stats after MMC overflow/interrupts, channel reporting with different hardware queue counts, and debug message level changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-hw.c

Purpose: Implements the XLGMAC hardware operation table: MAC filtering, VLAN and RSS programming, TX/RX descriptor formatting/parsing, DMA/MTL/MAC initialization, interrupts, flow control, coalescing, FIFO/queue mapping, MMC statistics, speed selection, and reset.

Important APIs/functions: `xlgmac_init_hw_ops()` wires all callbacks. Initialization flows through `xlgmac_hw_init()`: flush TX queues, configure DMA bus/PBL/OSP/coalescing/buffer sizes/TSO/SPH/RSS, initialize descriptors, enable DMA interrupts, configure MTL scheduling/queue mapping/store-forward/thresholds/FIFOs/flow control, then configure MAC address/filtering/jumbo/pause/speed/checksum/VLAN/MMC/MAC interrupts. `xlgmac_dev_xmit()` converts `ring->pkt_info` and mapped buffers into context and normal TX descriptors, including TSO MSS, VLAN tag, checksum, interrupt coalescing, ownership barriers, and tail-pointer notification. `xlgmac_dev_read()` parses RX normal/context descriptors for length, split-header, RSS hash, VLAN tag, timestamp context, checksum state, and errors. Other key helpers program MAC address/hash/perfect filters, VLAN hash tables, RSS key/table, DMA interrupt masks, flow control, speed bits, and MMC counter accumulation.

Control flow and state: Hardware state persists in MAC/MTL/DMA registers, descriptor rings, RSS/VLAN hash registers, and MMC counters. Software state includes `pdata->active_vlans`, RSS key/table/options, stats, per-ring current MSS/VLAN, saved interrupt masks, coalescing counters, and descriptor ownership. Ordering relies on `dma_wmb()`, `dma_rmb()`, `smp_wmb()`, and MMIO writes before ownership/tail updates.

Dependencies and integration points: Called by netdev open/close/xmit/poll/feature/ethtool paths via `struct xlgmac_hw_ops`. It depends on CRC32/bitrev helpers, DCB constants for priority mapping, DMA register map, descriptor bit definitions, and feature flags decoded in common init.

Risks and test signals: `xlgmac_enable_dma_interrupts()` builds `dma_ch_ier` but writes `dma_ch_isr` to `DMA_CH_IER`, likely enabling the wrong interrupt mask. `xlgmac_flush_tx_queues()` does not reread the flush bit inside its wait loop, so timeout behavior is suspect. RSS register writes can fail busy and leave partial key/table state. Queue mapping assumes up to 12 RX queues with fixed one-to-one MTL mapping constants. Test hardware init/exit reset timeout, TX/RX descriptor ownership under stress, TSO/VLAN/RSS/RXCSUM feature toggles, promisc/allmulti/unicast overflow, VLAN 1 filtering exception, fatal bus error restart, MMC stats accuracy, per-queue FIFO sizing, and interrupt mask programming on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-net.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-net.c

Purpose: Implements the XLGMAC netdev-facing data path: open/close, TX, RX, NAPI, IRQ handling, restart, MTU/features/VLAN/MAC changes, stats, and netpoll.

Important APIs/functions: `xlgmac_get_netdev_ops()` exposes the netdev ops table. `xlgmac_open()` calculates RX buffer size, allocates rings/channels, initializes restart work/timers, and starts hardware. `xlgmac_start()` initializes hardware, enables NAPI, requests IRQs, enables TX/RX, and starts queues; `xlgmac_stop()` reverses this. `xlgmac_xmit()` prepares descriptor counts/TSO/VLAN metadata, checks ring space, maps the SKB, updates BQL, and calls `hw_ops->dev_xmit()`. `xlgmac_isr()` handles shared DMA/MAC/MMC interrupts and schedules NAPI; `xlgmac_dma_isr()` handles per-channel IRQs. `xlgmac_rx_poll()` builds SKBs from split header/payload pages, handles incomplete/context descriptors, checksum/VLAN/RSS metadata, GRO delivery, and saved state. `xlgmac_tx_poll()` reclaims completed TX descriptors and wakes queues. Feature, MTU, VLAN, MAC, and RX mode ops delegate hardware changes through `hw_ops`.

Control flow and state: Runtime state is in `xlgmac_pdata`, `xlgmac_channel`, and per-ring indices. A shared NAPI instance is used unless `per_channel_irq` is set. TX uses BQL and `netdev_xmit_more()`; a TX timer forces polling when coalescing delays interrupts. RX refreshes dirty descriptors when more than one-eighth of the ring needs reallocation. Fatal bus errors and TX timeouts schedule `restart_work` under RTNL.

Dependencies and integration points: Depends on descriptor ops for DMA mapping/freeing, hardware ops for register operations, Linux NAPI/GRO/BQL/VLAN/RSS APIs, IRQ management, timers, and netdev feature plumbing.

Risks and test signals: `xlgmac_change_mtu()` writes MTU and restarts without an explicit running check, relying on `xlgmac_restart_dev()`. Open error after `xlgmac_start()` failure frees rings but does not cancel already initialized work beyond stop failure path. RX saved-state handling is complex when budget ends before a context descriptor arrives. Test shared vs per-channel IRQ modes, NAPI budget exhaustion, fragmented jumbo RX, TSO with many frags, queue stop/wake, xmit_more batching, MTU changes while up/down, feature toggles under traffic, fatal bus error restart, and netpoll.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-pci.c

Purpose: Provides PCI bus binding for the Synopsys DWC XLGMAC core driver.

Important APIs/functions: `xlgmac_probe()` enables the PCI device with managed APIs, finds and maps the first non-empty BAR, sets bus mastering, fills `struct xlgmac_resources` with IRQ and MMIO base, and calls `xlgmac_drv_probe()`. `xlgmac_remove()` delegates to `xlgmac_drv_remove()`. The PCI ID table matches Synopsys vendor ID with device `0x7302`, and `module_pci_driver()` registers the driver.

Control flow and state: PCI-managed resources own device enablement and BAR mappings. Runtime netdev state is created by common probe and stored as device drvdata. No suspend/resume or MSI/MSI-X setup is implemented here; it uses `pcidev->irq`.

Dependencies and integration points: Built only when `CONFIG_DWC_XLGMAC_PCI` is enabled. Integrates PCI core, managed BAR mapping, and common XLGMAC resource-based probe.

Risks and test signals: If all BARs are empty, index `i` can reach `PCI_STD_NUM_BARS` before `pcim_iomap_table(pcidev)[i]` is used. The first non-empty BAR is assumed to be MAC registers. Test devices with unexpected BAR layout, shared legacy IRQ behavior, probe/remove repeat, DMA bus mastering, and absence of MSI support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-reg.h

Purpose: Defines the XLGMAC MAC/MMC/MTL/DMA register map, bit positions, enumerated field values, descriptor attribute bits, and register-address helper macros.

Important APIs/constants: MAC offsets cover TX/RX control, packet filter, hash tables, VLAN, flow control, queue mapping, interrupts, version/features, MAC addresses, and RSS. MMC offsets cover TX/RX counters and interrupt enables. MTL offsets cover operation mode, queue scheduling, FIFO, flow-control, interrupts, and traffic-class registers. DMA offsets cover reset, system bus, interrupt status, debug/status, per-channel control, ring base/tail/length, interrupt enable, watchdog, and status. Descriptor constants describe RX/TX normal/context descriptor fields, packet attributes, error bits, RSS type values, VLAN insertion, and helper macros `XLGMAC_MTL_REG()`/`XLGMAC_DMA_REG()`.

Control flow and state: Declarative only. These constants are the hardware ABI used by `dwc-xlgmac-hw.c`, `dwc-xlgmac-net.c`, `dwc-xlgmac-common.c`, and ethtool stats. Descriptor bit definitions also define the state machine for DMA ownership and packet metadata propagation.

Dependencies and integration points: Paired with bit manipulation macros from `dwc-xlgmac.h`. Kconfig selects CRC/bitrev support because hash programming in hardware code uses those helpers with this register map.

Risks and test signals: Wrong positions or lengths silently corrupt hardware programming. Some queue mapping constants are fixed for queues 0-11, while the driver advertises up to 16 DMA channels. Test feature-register decoding, TX/RX descriptor bit interpretation, RSS/VLAN/MAC hash writes, interrupt enable masks, and MTL queue mapping on hardware variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-reg.h -->
