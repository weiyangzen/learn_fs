# subset-b-004620 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_main.c

Purpose: Implements the common Samsung SXGBE 10G/2.5G/1G Ethernet netdev driver core. It owns net_device allocation, open/stop, DMA ring allocation, TX/RX paths, NAPI polling, IRQ handling, PHY attach/link adjustment, EEE LPI timer handling, multicast/unicast filtering, MTU changes, feature toggles, stats, MDIO registration, and module/platform registration glue.

Important APIs and flow: `sxgbe_drv_probe()` allocates an `alloc_etherdev_mqs()` device, resets DMA, initializes hardware ops, allocates per-queue state, enables supported offloads, adds NAPI, obtains the CSR clock, registers MDIO, and registers the netdev. `sxgbe_open()` enables the clock, attaches the PHY, allocates descriptor rings, initializes DMA/MTL/MAC, requests common/TX/RX/LPI IRQs, starts DMA, starts PHY, configures RX watchdog and EEE, then enables NAPI and queues. `sxgbe_release()` reverses runtime state. `sxgbe_xmit()` maps skb head/frags into normal/context descriptors with TSO, VLAN/timestamp context support, interrupt coalescing, EEE exit, owner handoff, and DMA kick. `sxgbe_rx()` drains descriptors under NAPI, hands packets to GRO or `netif_receive_skb()`, and refills buffers.

State and dependencies: Persistent driver state lives in `struct sxgbe_priv_data`, with per-queue `cur_tx/dirty_tx`, `cur_rx/dirty_rx`, DMA descriptor memory, skb arrays, `hw_cap`, EEE timers, stats lock, NAPI, PHY state, platform data, clock, and operation tables from core/desc/dma/mtl modules. It depends on Linux netdev, PHYLIB, DMA mapping, timers, platform data, hardware register definitions, and MDIO helpers.

Risks and test signals: High-risk areas are open error unwinding after partial IRQ/ring allocation, descriptor DMA mapping failures that log but can still continue, TX context descriptor accounting, RX refill mapping error omissions, MTU down/up reinitialization, EEE timer deletion, and queue count assumptions. Tests should cover probe/remove, open/close loops, PHY absent/bad speed, TSO and fragmented skb TX, RX checksum toggles, multicast filter programming, TX timeout reset, RX/TX IRQ paths, EEE entry/exit interrupts, MTU changes while running, and fault injection for DMA/ring/IRQ allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_mdio.c

Purpose: Provides SXGBE MDIO bus access and registration. It bridges PHYLIB `mii_bus` operations to the controller's SMA/MDIO registers for Clause 22 and Clause 45 PHY transactions.

Important APIs and flow: `sxgbe_mdio_busy_wait()` polls the data register busy bit for up to three seconds. `sxgbe_mdio_ctrl_data()` builds the command word using the access command, skip-address-frame bit, `priv->clk_csr`, payload, and busy bit. Clause-specific helpers program address/data registers. `sxgbe_mdio_read_c22()`, `sxgbe_mdio_write_c22()`, `sxgbe_mdio_read_c45()`, and `sxgbe_mdio_write_c45()` are installed into `struct mii_bus`. `sxgbe_mdio_register()` allocates and registers the bus, scans discovered PHYs, assigns probed IRQs when requested, auto-selects `plat->phy_addr` when unset, and stores `priv->mii`. `sxgbe_mdio_unregister()` unregisters and frees it.

State and dependencies: The bus uses the netdev as `bus->priv`, platform `sxgbe_mdio_bus_data` for masks/IRQs, `priv->hw->mii` register offsets initialized by `sxgbe_get_ops()`, and `priv->clk_csr` from platform or dynamic clock-rate selection. It mutates `plat->phy_addr` when the MAC did not specify one.

Risks and test signals: Clause 22 access rejects PHY addresses 4 and above, so board data must match hardware limitations. Busy-wait timeout, missing `mdio_bus_data`, and no-PHY discovery are key failure paths. Tests should exercise C22/C45 reads and writes, phy mask behavior, probed IRQ assignment, auto phy address selection, timeout injection, unregister without register, and probe failure after successful `mdiobus_register()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_mtl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_mtl.c

Purpose: Implements SXGBE MTL operation callbacks used by the main driver to configure queue scheduling, FIFO sizes, TX/RX queue enablement, thresholds, flow control, and RX queue to DMA channel mapping.

Important APIs and flow: `sxgbe_mtl_init()` updates global MTL operation mode fields for ETS algorithm and receive arbitration. `sxgbe_mtl_dma_dm_rxqueue()` enables dynamic RX queue mapping across three mapping registers. FIFO helpers encode queue FIFO size in 256-byte units. Queue helpers enable/disable TX queues. Flow-control helpers set active/deactive thresholds and enable RX flow control. FEP/FUP helpers toggle forwarding of error/undersized packets. `sxgbe_set_tx_mtl_mode()` maps byte thresholds to TTC encodings or store-and-forward; `sxgbe_set_rx_mtl_mode()` maps RTC thresholds or RX store-and-forward. `sxgbe_get_mtl_ops()` exports the static ops table.

State and dependencies: The file has no persistent private state; it mutates MMIO registers through `readl()`/`writel()` using offsets and bit definitions from `sxgbe_reg.h` and mode constants from `sxgbe_mtl.h`. `sxgbe_main.c` calls these through `priv->hw->mtl`.

Risks and test signals: Several setters OR new mode bits without clearing old threshold fields, so repeated threshold changes may leave stale bits unless hardware encodings are compatible. FIFO-size helpers assume multiples of 256 and nonzero queue sizes. Tests should verify register bit results for each TTC/RTC threshold, store-and-forward mode, repeated threshold bumps from TX/RX interrupts, queue enable/disable, dynamic RX mapping, and flow-control threshold programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_mtl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_mtl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_mtl.h

Purpose: Declares SXGBE MTL constants, threshold encodings, flow-control encodings, and the `struct sxgbe_mtl_ops` callback interface consumed by the common driver.

Important APIs and types: Defines ETS/RAA masks and encodings, TX/RX FIFO divisors, RX forwarding flags, flow-control enable bits, dynamic RX queue mapping value, flow-control threshold bit shifts, `enum ttc_control`, `enum rtc_control`, `enum flow_control_th`, and the MTL operations table with callbacks for initialization, FIFO sizing, TX queue enable/disable, threshold mode selection, dynamic RX queue mapping, flow control, and FEP/FUP toggles. `sxgbe_get_mtl_ops()` is the exported accessor.

State and dependencies: This header is a hardware contract shared by `sxgbe_mtl.c` and `sxgbe_main.c`. It depends on kernel bit macros and `__iomem` pointer usage from included call sites.

Risks and test signals: Constants must match the SXGBE hardware register layout; incorrect shifts or threshold values silently program wrong queue behavior. Build coverage should catch signature drift between the header and implementation. Runtime validation should compare programmed MMIO values against expected queue modes for all supported TX/RX thresholds and flow-control levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_mtl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_platform.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_platform.c

Purpose: Provides the platform-driver wrapper for SXGBE. It parses device-tree platform data, maps MMIO resources, invokes the common SXGBE probe/remove entry points, maps IRQs, and exposes PM callbacks.

Important APIs and flow: `sxgbe_probe_config_dt()` reads PHY interface mode, ethernet alias bus id, allocates MDIO bus data and DMA config, and reads Samsung PBL/burst-map properties. `sxgbe_platform_probe()` maps resource 0, allocates DT platform data, calls `sxgbe_drv_probe()`, parses common, TX queue, RX queue, and LPI IRQs from the DT node, reads the MAC address, stores the netdev in platform data, and returns. `sxgbe_platform_remove()` calls `sxgbe_drv_remove()`. PM wrappers call common suspend/resume/freeze/restore stubs. `sxgbe_register_platform()` and `sxgbe_unregister_platform()` are used by `sxgbe_main.c` module init/exit.

State and dependencies: Platform state is `struct sxgbe_plat_data` allocated with devm, a mapped `ioaddr`, IRQ mappings on each queue, and the netdev stored with `platform_set_drvdata()`. It depends on OF helpers, platform resource mapping, SXGBE common probe/remove functions, and compatible string `samsung,sxgbe-v2.0a`.

Risks and test signals: Probe calls the common driver before IRQ numbers are parsed, so error paths must be checked carefully because `platform_get_drvdata()` is still old/null until late success. IRQ mapping disposal on partial TX/RX loops is delicate. Tests should cover DT property variants, missing IRQs at every position, failed common probe, MAC address absent/present, remove after successful probe, and PM callback routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_reg.h

Purpose: Central register map and bitfield definition header for the Samsung SXGBE MAC, MDIO/SMA, MMC counters, L3/L4/RSS/PTP/PPS blocks, MTL queues, DMA global state, DMA channels, speed control, feature discovery, and interrupt status/enable masks.

Important APIs and types: Defines register offsets such as core TX/RX config, packet filters, EEE LPI, VLAN, flow control, interrupt status, hardware feature registers, MDIO command/data, MAC address slots, MMC counters, RSS, timestamping, MTL global/queue registers, DMA global/channel registers, and descriptor pointer/tail registers. It also defines feature extraction macros for capability registers 0..2, queue register address macros, speed encodings, RX/TX enable bits, VLAN controls, checksum/jumbo bits, DMA interrupt masks, and channel status bits.

State and dependencies: The header carries no state; it is the shared symbolic ABI between register-access implementation files and the SXGBE hardware. `sxgbe_main.c`, `sxgbe_mdio.c`, `sxgbe_mtl.c`, and lower-level core/DMA/descriptor modules depend on these names remaining stable.

Risks and test signals: Register offsets and bitfield masks are hardware-critical and failures can appear as silent nonfunctional TX/RX, bad stats, broken MDIO, or wrong offload reporting. The typo-like macro `SXGBE_HW_FEAT_PMT_TEMOTE_WOP` is used by the driver and should not be renamed casually. Tests should include compile coverage of every consumer plus hardware or emulated register validation for feature extraction, interrupt mask composition, MMC stats offsets, MTL queue address calculations, and DMA channel address calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/Kconfig

Purpose: Defines Kconfig options for SEEQ-family Ethernet drivers.

Important APIs and flow: `NET_VENDOR_SEEQ` is the vendor menu gate, defaults to `y`, and depends on `HAS_IOMEM`. Within the vendor block, `ARM_ETHER3` builds Acorn/ANT Ether3 support for `ARM && ARCH_ACORN`, while `SGISEEQ` builds SGI Seeq controller support when `SGI_HAS_SEEQ` is available.

State and dependencies: This file controls whether `ether3.o` and `sgiseeq.o` are visible and selectable. It integrates with the parent Ethernet vendor menu and the `seeq/Makefile` object selections.

Risks and test signals: Dependency mistakes either expose drivers on unsupported architectures or hide them from valid legacy platforms. Build tests should cover vendor disabled, vendor enabled with unsupported arch, Acorn enabled, and SGI Seeq enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/Makefile

Purpose: Maps SEEQ Kconfig symbols to driver objects.

Important APIs and flow: `obj-$(CONFIG_ARM_ETHER3) += ether3.o` builds the Acorn/ANT Ether3 driver, and `obj-$(CONFIG_SGISEEQ) += sgiseeq.o` builds the SGI Seeq8003 driver.

State and dependencies: The Makefile depends entirely on Kconfig symbol selection and provides no additional state. It is consumed by the kernel build system under the Ethernet driver tree.

Risks and test signals: The main risk is symbol/object drift if driver files or Kconfig names change. Build coverage for both tristate options as built-in and module should confirm object selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/ether3.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/ether3.c

Purpose: Implements the Acorn/ANT Ether3 SEEQ NQ8005 network driver for Acorn expansion-card systems. It manages slow MMIO register access, local buffer memory, open/close, TX/RX handling, multicast mode, timeout recovery, expansion-card probe/remove, and module registration.

Important APIs and flow: `ether3_probe()` claims expansion-card resources, allocates a netdev, maps MEMC space, reads the MAC address from the card chunk directory, detects bus width, performs chip reset and RAM tests, registers netdev ops, and registers the device. `ether3_open()` requests the IRQ, initializes chip state in `ether3_init_for_open()`, and starts the queue. `ether3_sendpacket()` pads frames, writes packet data and chained TX headers into card buffer memory, starts TX if idle, and stops the queue when the ring is full. `ether3_interrupt()` acknowledges RX/TX interrupts and calls `ether3_rx()` and `ether3_tx()`. RX reads chained packet headers from local RAM, filters looped-back own-source frames, reports hardware errors, builds skb data, and advances `REG_RECVEND`. TX scans completed headers and updates stats.

State and dependencies: `struct dev_priv` stores MMIO base, SEEQ window, cached command/config registers, TX head/tail, RX head, LED timer, owning netdev, and broken-card flag. It depends on Acorn `ecard` APIs, legacy SEEQ buffer windows, manual IRQ control, netdev stats, and `ether3.h` register/header constants.

Risks and test signals: Hardware timing requires udelay after register accesses. Probe ignores the return value of `ether3_addr()` before setting the MAC, and timeout handling uses local IRQ masking plus direct buffer reads. Tests should cover bus-width detection, RAM-test failure, open/close IRQ lifecycle, TX ring full, RX wraparound, malformed next pointer, multicast/promiscuous changes, timeout reset, LED timer removal, and resource cleanup after probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/ether3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/ether3.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/ether3.h

Purpose: Defines the register offsets, command/status/config bits, TX/RX header/status flags, buffer memory layout, queue limits, and private state structures for the Ether3 driver.

Important APIs and types: Register macros derive addresses from `priv(dev)->seeq`, including command/status, config registers, buffer window, receive/transmit pointers, and DMA address. Command/status bits control RX/TX enablement, FIFO direction, interrupt enables/acks, and DMA/FIFO operations. TX/RX header flags describe chained local-memory packets. Buffer layout divides local RAM into TX and RX regions with 16 TX slots. `struct dev_priv` stores cached registers, ring pointers, timer, netdev, and broken flag. `struct ether3_data` distinguishes card variants by name and base offset.

State and dependencies: This header is tightly coupled to `ether3.c` and Acorn expansion-card mapping. It embeds state layout used by `netdev_priv()` and register macros used throughout the driver.

Risks and test signals: Since register macros evaluate `priv(dev)`, callers must pass a valid registered netdev with initialized private state. Buffer constants must remain compatible with TX slot sizing and RX wrap logic. Tests should validate register address calculations for Ether3/EtherB offsets, TX/RX flag interpretation, and build coverage after any private-structure changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/ether3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/sgiseeq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/sgiseeq.c

Purpose: Implements the SGI Seeq8003 Ethernet driver using SGI HPC3 DMA. It presents a Lance-like ring model over HPC DMA descriptors, handles RX/TX, multicast mode, timeout reset, platform probe/remove, and DMA descriptor allocation.

Important APIs and flow: `sgiseeq_probe()` allocates a netdev, allocates a noncoherent descriptor block, initializes RX/TX descriptor rings, programs SGI HPC PIO/DMA timing, detects EDLC mode, and registers the device. `sgiseeq_open()` requests the IRQ and calls `init_seeq()`, which resets hardware, initializes rings, programs Seeq interrupt modes, points HPC at RX/TX descriptor lists, and starts RX. `sgiseeq_start_xmit()` pads short packets, DMA maps the skb, fills the next TX descriptor, links it by clearing the previous EOX only after the new descriptor is coherent, advances `tx_new`, kicks HPC if idle, and stops the queue when full. `sgiseeq_interrupt()` clears IRQ, drains RX, processes TX completions, and wakes the queue. `sgiseeq_rx()` unmaps received buffers, chooses copybreak or skb replacement, drops looped-back own packets, records errors, remaps buffers, updates EOR, and restarts RX if needed.

State and dependencies: `struct sgiseeq_private` stores noncoherent ring memory, DMA address, uncached descriptor pointers, HPC and Seeq register pointers, RX/TX indices, EDLC control/mode, and `tx_lock`. It depends on SGI platform data (`hpc`, IRQ, MAC), HPC3 descriptor/status bits, DMA mapping/sync APIs, and Seeq register definitions from `sgiseeq.h`.

Risks and test signals: Noncoherent descriptor synchronization and TX chain race ordering are critical. RX buffer purge frees skbs but does not unmap all DMA mappings visibly in this file, so close/remove paths deserve scrutiny. Tests should cover RX copybreak and full-skb paths, allocation failure while refilling RX, TX ring full and restart, HPC idle kick, multicast mode reset, timeout reset, EDLC/non-EDLC init, and DMA API debug on close/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/sgiseeq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/sgiseeq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/sgiseeq.h

Purpose: Defines SGI Seeq8003 register layouts and status/command/control bits used by the SGI HPC3-backed driver.

Important APIs and types: `struct sgiseeq_regs` models banked Seeq registers for station address, multicast bytes, write-side controls, read-side collision/status counters, receive status, and transmit status. Macros define receive status bits, receive command bits, transmit status bits, transmit command bits, Seeq control flags, and SGI Hollywood HPC PIO/DMA/control timing/reset/IRQ flags.

State and dependencies: The header has no runtime state but forms the MMIO layout contract for `sgiseeq.c`. It also mirrors HPC integration bits that must match SGI platform hardware headers.

Risks and test signals: Bit definitions must align with hardware and with `sgiseeq.c` error handling; mistakes can invert receive mode, miss interrupts, or mishandle reset. Tests should include compile coverage on SGI_HAS_SEEQ, register-bank selection for MAC/multicast programming, receive status error accounting, and EDLC control programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/sgiseeq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/Kconfig

Purpose: Defines Kconfig options for Solarflare/Xilinx SFC Ethernet drivers and related optional support.

Important APIs and flow: `NET_VENDOR_SOLARFLARE` gates the vendor menu. `SFC` is a PCI tristate driver for SFC9100 and EF100-family devices; it depends on optional PTP support and selects MDIO, CRC32, and devlink. Optional booleans add MTD flash/EEPROM exposure, firmware-managed hwmon, SR-IOV support with INET and PCI_IOV, and MCDI logging. The file also sources Falcon and Siena subdriver Kconfig files.

State and dependencies: These symbols drive the `sfc/Makefile`, feature compilation inside many SFC sources, and subdirectory inclusion. The MTD/HWMON dependency expressions avoid built-in driver to module dependency inversions.

Risks and test signals: Config dependency drift can create link failures or hide valid feature combinations. Build matrix tests should cover SFC built-in/module, optional MTD/HWMON/SRIOV/MCDI logging on/off, PTP optional configurations, and Falcon/Siena source inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/Makefile

Purpose: Defines object composition for the main `sfc` module and optional Solarflare subdrivers.

Important APIs and flow: `sfc-y` lists the core object files for EF10/EF100, channels, NIC, TX/RX, selftest, ethtool, PTP, MCDI, filters, monitoring, devlink, and reflash. `sfc-$(CONFIG_SFC_MTD)` adds MTD support. `sfc-$(CONFIG_SFC_SRIOV)` adds SR-IOV, representor, MAE, TC, counter, encapsulation, and conntrack support. `obj-$(CONFIG_SFC)` builds `sfc.o`, while Falcon and Siena directories are delegated to their own sub-Makefiles.

State and dependencies: It depends on Kconfig symbols from `sfc/Kconfig` and source files in the same directory. Link order matters because the single `sfc.o` aggregates many feature areas.

Risks and test signals: Adding a source without the right Kconfig guard can break non-SRIOV or non-MTD builds. Build tests should cover minimal SFC, SFC with MTD, SFC with SR-IOV/TC, built-in/module modes, and Falcon/Siena enabled independently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/bitfield.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/bitfield.h

Purpose: Provides Solarflare bitfield manipulation primitives for little-endian 32-bit, 64-bit, and 128-bit hardware words. The SFC drivers use it to build and inspect firmware, descriptor, register, and DMA data structures without relying on native 128-bit integer types.

Important APIs and types: Defines field metadata helpers (`EFX_LOW_BIT`, `EFX_WIDTH`, `EFX_HIGH_BIT`), mask helpers, little-endian wrapper unions `efx_dword_t`, `efx_qword_t`, and `efx_oword_t`, printk format/value macros, extraction macros for 32-bit and 64-bit host word strategies, zero/all-ones tests, populate macros for up to 19 field/value pairs, zero/set helpers, bitwise invert/and/or helpers, read-modify-write field setters, DMA width helper macros, and static initializer `EFX_OWORD32()`.

State and dependencies: The header has no runtime state but encodes an ABI-safe representation of NIC fields in little-endian memory. It depends on kernel endian types, `BITS_PER_LONG`, DMA address width, and the convention that each hardware field has `_LBN` and `_WIDTH` macros.

Risks and test signals: Macro arguments can be evaluated multiple times in some helpers, and widths outside supported ranges can cause invalid shifts if field metadata is wrong. Correctness varies by 32-bit versus 64-bit builds. Tests should compile and exercise extraction, populate, and set macros on both word sizes, fields spanning element boundaries, full-width 32/64 masks, zero/all-ones checks, DMA address width truncation, and representative SFC descriptor/register definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/bitfield.h -->
