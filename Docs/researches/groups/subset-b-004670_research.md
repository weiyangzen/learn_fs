# subset-b-004670 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_phy.c

Purpose: implements PHY, phylink, PCS, GPIO, I2C, SFP, and cleanup plumbing for the Wangxun TXGBE physical-function driver. The file bridges the PCI register block in `struct wx` to Linux phylink, XPCS, GPIO, software-node, platform-device, clock, MDIO, and SFP subsystems.

Important APIs and functions: `txgbe_init_phy()` is the exported setup entry. It selects AML-specific phylink setup, external copper PHY setup, or SFP/XPCS setup for SP devices. `txgbe_remove_phy()` tears down the matching path. `txgbe_link_irq_handler()` reports link-state changes to either XPCS PCS or phylink MAC. `txgbe_pcs_read()` and `txgbe_pcs_write()` implement Clause 45 MDIO-over-register access through `TXGBE_XPCS_IDA_ADDR/DATA`. `txgbe_phylink_init()` sets MAC capabilities and supported interfaces. GPIO callbacks expose six SFP control/status pins. `txgbe_i2c_register()` creates an `i2c_designware` platform device backed by a regmap over the TXGBE I2C register window; `txgbe_sfp_register()` creates the SFP platform device.

Control flow: non-copper SP setup registers software nodes, registers the XPCS MDIO bus, creates phylink, adds the GPIO chip, registers a fixed I2C clock, registers the I2C platform device, then registers the SFP platform device. Error labels unwind in reverse order. Link-up configures flow control, MAC speed bits, RX enable, packet filter, watchdog, PTP cycle counter, and VF mailbox link notification. Link-down disables TX, resets speed, resets PTP if active, and notifies VFs.

State and persistence: persistent state is in `struct txgbe` and `struct wx`, including `pcs`, `sfp_dev`, `i2c_dev`, `clk`, `clock`, `gpio`, software nodes, `wx->phylink`, `wx->phydev`, `wx->speed`, and PTP timestamps. Hardware state lives in MAC TX/RX config, GPIO DDR/data, XPCS indirection, I2C registers, and port status registers.

Dependencies and integration: depends on shared `libwx` register helpers, PTP, mailbox/SR-IOV status propagation, `pcs-xpcs`, phylink, MDIO, gpiochip, software nodes, clkdev, regmap, DesignWare I2C, and SFP platform drivers. Risks are resource-unwind mismatches, sleeping constraints around platform devices, incorrect software-node GPIO polarity, XPCS access serialization, and link-state drift between PCS and MAC. Test signals include probe/remove on SFP and copper boards, SFP hotplug, link IRQs, PTP reset on speed changes, VF link notifications, and fault injection of each setup step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_phy.h

Purpose: declares the TXGBE PHY-facing entry points shared by the PF driver. It is intentionally small and provides the public contract implemented by `txgbe_phy.c`.

Important APIs: `txgbe_link_irq_handler(int irq, void *data)` is the IRQ callback used by the TXGBE interrupt layer to notify phylink/XPCS of link changes. `txgbe_init_phy(struct txgbe *txgbe)` initializes the appropriate PHY path for the MAC/media type. `txgbe_remove_phy(struct txgbe *txgbe)` releases resources acquired by initialization.

Control flow and integration: the header assumes `struct txgbe` is already visible from `txgbe_type.h` or another include in consumers. The functions are consumed by the main TXGBE driver during probe, remove, and interrupt setup. It keeps phylink details hidden from the caller, allowing the source file to choose AML, external copper PHY, or SFP/XPCS behavior.

State and persistence: no state is defined here. State lives in `struct txgbe` and `struct wx`.

Risks and tests: because this is a narrow declaration header, risks are prototype drift and include-order assumptions. Build coverage with TXGBE enabled is the primary signal; runtime signals come from successful PHY init/remove and link IRQ dispatch in the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_type.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_type.h

Purpose: central TXGBE PF type and constant definition header. It records PCI IDs, subsystem/media IDs, register offsets, bit masks, Flow Director formats, SFP firmware-command payloads, software-node bookkeeping, IRQ metadata, and the main `struct txgbe` private state.

Important definitions: device IDs cover SP1000/WX1820 and AML variants. Register definitions include reset/status, port status, tunnel ports, XPCS IDA registers, I2C base, Flow Director tables and commands, Amber Lite MAC speed bits, EEPROM locations, queue limits, interrupt masks, and SFP/FEC capability values. `union txgbe_atr_input`, `union txgbe_atr_hash_dword`, `enum txgbe_atr_flow_type`, and `struct txgbe_fdir_filter` define software Flow Director inputs. Firmware HIC structures describe module-info, link-set/get, and I2C-read command payloads.

State and integration: `struct txgbe_nodes` stores software-node names, property arrays, references, and node groups used by `txgbe_phy.c`. `struct txgbe_irq` stores misc IRQ chip/domain data. `struct txgbe` points back to shared `struct wx`, owns PHY/SFP/I2C/clock/GPIO resources, tracks link and GPIO IRQs, stores Flow Director filters and masks, and caches link-mode masks.

Dependencies: includes Linux property/IRQ/PHY APIs and shared `libwx` types. It exports `txgbe_driver_name` and core lifecycle helpers such as `txgbe_down()`, `txgbe_up()`, `txgbe_setup_tc()`, and `txgbe_do_reset()`.

Risks and tests: the highest risk is silent mismatch between bit definitions and hardware/firmware contracts, especially FDIR, EEPROM, SFP/FEC, and MAC speed masks. Compile coverage, ethtool ntuple tests, SFP module probing, firmware mailbox commands, SR-IOV, and register-dump validation are key test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbevf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbevf/Makefile

Purpose: builds the Wangxun TXGBE virtual-function driver object.

Important build rules: `obj-$(CONFIG_TXGBE) += txgbevf.o` ties VF object compilation to `CONFIG_TXGBE`; `txgbevf-objs := txgbevf_main.o` states that the module is currently a single source-file composite object.

Control flow and integration: Kbuild turns this directory rule into `txgbevf.ko` or built-in code depending on the parent Makefile and `CONFIG_TXGBE`. The VF driver shares the same config symbol as the PF driver rather than using a distinct `CONFIG_TXGBEVF`, so enabling TXGBE also selects this object when the directory is descended.

State and persistence: no runtime state. It controls object inclusion only.

Risks and tests: the main risk is configuration coupling: distributions expecting separate PF/VF toggles cannot disable the VF independently from this file. Build tests should verify modular and built-in TXGBE configurations and confirm `txgbevf_main.o` is included exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbevf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbevf/txgbevf_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbevf/txgbevf_main.c

Purpose: PCI virtual-function driver for Wangxun 10/25/40GbE devices. It is a compact adapter around shared `libwx` VF helpers, responsible for PCI enablement, netdevice allocation, BAR mapping, mailbox setup, queue sizing, feature defaults, interrupt scheme setup, and registration.

Important APIs: `txgbevf_pci_tbl` lists VF PCI IDs. `txgbevf_netdev_ops` wires open/stop/start-xmit/MAC-address operations to shared VF helpers. `txgbevf_set_num_queues()` asks the PF for traffic-class/default queue configuration and chooses queue counts using mailbox API level and RSS limits. `txgbevf_init_type_code()` maps device IDs to SP or AML MAC type. `txgbevf_sw_init()` initializes shared software state, mailbox, hardware reset, MAC address, ring/work defaults, and AML feature flags. `txgbevf_probe()` performs PCI resource setup and netdev registration. `txgbevf_remove()` delegates removal to `wxvf_remove()`.

Control flow: probe enables PCI memory access, sets 64-bit DMA, requests BARs, allocates a multiqueue netdev with `struct wx`, maps BAR0 and BAR4, initializes common/VF state, initializes service work, interrupt scheme, firmware version, then registers the netdev and stops TX queues until open. Error paths free interrupt/service/mailbox/common allocations and release PCI resources.

State and dependencies: state lives in `struct wx`: `pdev`, `netdev`, BAR mappings, mailbox, `vfinfo`, queue counts, ring counts, RSS key/table, feature flags, service timer/task, and interrupt vectors. Dependencies include PCI, DMA API, netdevice, `libwx` hardware/mailbox/VF/common/ethtool helpers, and PM callbacks.

Risks and tests: mailbox negotiation with PF, PF-reset handling, random MAC fallback, BAR4 mapping, AML merge/head-writeback flags, queue count selection, and cleanup ordering are the main risks. Test with SR-IOV enabled PFs, PF reset while VF probes, API <1.3 and >=1.3, suspend/resume, module unload, and traffic over one and multiple queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbevf/txgbevf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbevf/txgbevf_type.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbevf/txgbevf_type.h

Purpose: defines constants for the Wangxun TXGBE virtual-function driver.

Important definitions: device IDs cover SP1000, WX1820, and AML VF variants. Capacity constants limit MSI-X vectors to 2, RSS and RX/TX queue counts to 4, and default descriptor rings to 128 entries each. Work limits default to 256 for both TX and RX.

Integration: `txgbevf_main.c` consumes these values for PCI matching, netdev allocation, queue sizing, interrupt capability, and ring/work defaults. The constants also define the VF driver's public hardware assumptions relative to shared `libwx` queue/interrupt helpers.

State and persistence: this header defines no runtime storage. It constrains runtime state allocated in `struct wx`.

Risks and tests: risk lies in stale device IDs or hardware capability limits that diverge from PF-advertised resources. Test signals include successful PCI matching for all IDs, correct queue count negotiation, descriptor setup under traffic, and module build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbevf/txgbevf_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/Kconfig

Purpose: Kconfig menu for WIZnet Ethernet drivers.

Important options: `NET_VENDOR_WIZNET` gates the vendor menu and depends on `HAS_IOMEM`. `WIZNET_W5100` enables the W5100 core/platform driver. `WIZNET_W5300` enables the W5300 platform driver. The `WIZNET_BUS_DIRECT`, `WIZNET_BUS_INDIRECT`, and `WIZNET_BUS_ANY` choice controls whether MMIO direct, MMIO indirect, or runtime-selected access code is built. `WIZNET_W5100_SPI` enables SPI support for W5100/W5200/W5500 and depends on `WIZNET_BUS_ANY`, `WIZNET_W5100`, and `SPI`.

Integration: Makefile objects depend directly on these symbols. The bus-mode choice affects compiled function selection and therefore performance, locking, and whether SPI can be selected.

State and persistence: no runtime state, but selected options alter the code paths compiled into `w5100.o`, `w5100-spi.o`, and `w5300.o`.

Risks and tests: `WIZNET_W5100_SPI` is only available with `WIZNET_BUS_ANY`, so static direct/indirect configurations intentionally exclude SPI. Build matrix tests should cover W5100 MMIO direct, indirect, any, SPI, and W5300 combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/Makefile

Purpose: maps WIZnet Kconfig symbols to driver objects.

Important build rules: `CONFIG_WIZNET_W5100` builds `w5100.o`, `CONFIG_WIZNET_W5100_SPI` builds `w5100-spi.o`, and `CONFIG_WIZNET_W5300` builds `w5300.o`.

Control flow and integration: `w5100-spi.o` depends on exported symbols from `w5100.o`, so the Kconfig dependency on `WIZNET_W5100` is important. `w5300.o` is independent and implements its own platform driver.

State and persistence: no runtime state.

Risks and tests: incorrect Kconfig dependencies could produce unresolved symbols for SPI support. Build tests should verify module and built-in configurations for each object and combined W5100 plus W5100-SPI builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/w5100-spi.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/w5100-spi.c

Purpose: SPI bus frontend for WIZnet W5100, W5200, and W5500 chips. It implements chip-specific SPI register access callbacks and then delegates netdevice creation and operation to the shared `w5100_probe()` core.

Important APIs: W5100 uses opcode/address byte commands with byte-at-a-time bulk loops. W5200 uses 4-byte command headers and supports bulk SPI transfers with a cacheline-aligned command buffer protected by `cmd_lock`. W5500 uses encoded block-select/control bytes and bulk transfer helpers protected similarly. `w5100_spi_probe()` obtains an optional DT MAC address, selects `w5100_spi_ops`, `w5200_ops`, or `w5500_ops` from match data, passes per-chip private size to `w5100_probe()`, and uses the SPI IRQ. `w5100_spi_remove()` calls `w5100_remove()`.

Control flow: SPI device matching comes from OF compatibles and SPI IDs. Per-chip ops expose `may_sleep = true`, so the core avoids NAPI hot-path register accesses and schedules workqueue-based RX/TX/restart operations. W5200/W5500 init functions initialize mutexes for the shared command buffers.

State and dependencies: per-device SPI state is the underlying `spi_device` plus optional `w5200_spi_priv` or `w5500_spi_priv` stored after the core netdev private data. Depends on SPI, OF, OF MAC parsing, netdevice, and the exported W5100 core symbols.

Risks and tests: risks include wrong command framing, block-selection bugs on W5500 32-bit encoded addresses, serialized command-buffer races, and sleeping in IRQ context if `may_sleep` is not honored. Test with SPI loopback or hardware register reads, RX/TX traffic, OF and SPI-ID matching, module unload, and large bulk transfers crossing socket buffer boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/w5100-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/w5100.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/w5100.c

Purpose: shared W5100/W5200/W5500 Ethernet core for MMIO platform devices and SPI frontends. It uses socket 0 in MACRAW mode and ignores the chips' TCP/IP offload, presenting a Linux Ethernet netdevice.

Important APIs: low-level MMIO direct and indirect operations implement the `w5100_ops` contract. `w5100_readbuf()` and `w5100_writebuf()` handle circular RX/TX memory wrapping. `w5100_hw_reset()`, memory configuration functions, `w5100_hw_start()`, and `w5100_hw_close()` program the chip. Netdev callbacks include open/stop, xmit, timeout, RX mode, MAC address, and ethtool register dumps. `w5100_probe()` and `w5100_remove()` are exported for SPI and used by the platform driver.

Control flow: probe allocates an etherdev with optional bus-private tailroom, selects socket register and buffer layout by chip ID, registers the netdev, creates a transfer workqueue, initializes ops, resets hardware, requests the main IRQ, and optionally requests a link GPIO IRQ. TX stops the queue, writes the frame to chip TX memory, advances the write pointer, sends `S0_CR_SEND`, and wakes on SENDOK. RX reads chip RX size, pulls a two-byte length header, allocates an skb, copies data, advances RX pointer, issues RECV, and hands skb to the stack. SPI paths run TX/RX via workqueue because register operations may sleep; MMIO paths use NAPI for RX.

State and dependencies: `struct w5100_priv` holds chip layout, IRQs, link GPIO, NAPI, workqueue, pending TX skb, promisc flag, and message level. Dependencies include platform data, GPIO, interrupt, NAPI, ethtool, exported SPI frontend hooks, and Kconfig-selected bus mode.

Risks and tests: key risks are circular buffer wrap math, sleeping versus atomic register access, workqueue teardown with pending `tx_skb`, IRQ masking, link GPIO polarity, and the hardware RTR probe used as presence check. Test direct/indirect/SPI bus modes, W5100/W5200/W5500 layout selection, promiscuous toggles, tx timeout recovery, suspend/resume, no-link-GPIO behavior, and register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/w5100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/w5100.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/w5100.h

Purpose: shared interface between the W5100 core and alternate bus frontends such as SPI.

Important APIs and types: the chip ID enum identifies W5100, W5200, and W5500 layouts. `struct w5100_ops` describes bus operations: byte, 16-bit, bulk read/write, optional reset, optional init, `may_sleep`, and chip ID. `w5100_ops_priv()` returns bus-private memory placed after the core private data. `w5100_probe()` creates and registers a W5100-family netdev from supplied ops, MAC, IRQ, and optional link GPIO. `w5100_remove()` tears it down. `w5100_pm_ops` is exported for bus drivers.

Control flow and integration: bus drivers provide ops and private size, then call `w5100_probe()`. The core stores the ops pointer and uses it for all register and memory access when runtime bus selection is enabled.

State and persistence: no direct state beyond the ops contract; state is allocated by `w5100_probe()`.

Risks and tests: the ABI between bus frontend and core must stay consistent, particularly `may_sleep`, private-data sizing/alignment, and chip ID selection. Build and module tests should cover SPI plus core as modules and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/w5100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/w5300.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/w5300.c

Purpose: platform netdevice driver for the WIZnet W5300 chip. Like the W5100 driver, it uses MACRAW mode and not the on-chip TCP/IP stack, but it is implemented separately around the W5300 16-bit register/FIFO model.

Important APIs: direct and indirect 16-bit register access functions are selected by Kconfig or runtime memory-resource size. `w5300_read32()` and `w5300_write32()` combine 16-bit accesses. `w5300_hw_reset()` resets the chip, configures indirect mode if needed, writes MAC address, splits 128K internal memory into 64K RX and 64K TX, and sets memory type. `w5300_hw_start()` opens socket 0 in filtered or promiscuous MACRAW mode and enables interrupts. Netdev callbacks handle TX FIFO writes, NAPI RX, link GPIO, RX mode, MAC address, open/stop, and ethtool register dumps.

Control flow: probe allocates and registers the netdev, then hardware probe maps registers, chooses direct or indirect mode, validates `W5300_IDR`, requests IRQs, and optionally registers a link GPIO IRQ. TX writes skb bytes into the TX FIFO, writes TX size, issues SEND, and wakes on SENDOK. RX NAPI reads RX FIFO length and per-frame length, allocates skb, drains FIFO into skb, and re-enables interrupts when polling completes.

State and dependencies: `struct w5300_priv` holds MMIO base, indirect lock, selected read/write functions, IRQs, link GPIO, NAPI, promisc flag, message level, and netdev. Dependencies include platform data, GPIO, NAPI, ethtool, and Kconfig bus mode.

Risks and tests: odd-length frame handling, FIFO drain on allocation failure, runtime direct/indirect selection, W5300 ID probing, link GPIO handling, and suspend/resume are risk points. Note that resume checks `if (!netif_running(ndev))`, which is unusual compared with suspend and may deserve targeted review. Test direct and indirect resources, RX/TX traffic, promisc changes, register dumps, tx timeout reset, and PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/w5300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/Kconfig

Purpose: Kconfig menu for Xilinx Ethernet drivers.

Important options: `NET_VENDOR_XILINX` gates the vendor menu. `XILINX_EMACLITE` enables 10/100 Ethernet Lite and selects PHYLIB. `XILINX_AXI_EMAC` enables AXI Ethernet, depends on `HAS_IOMEM` and `XILINX_DMA`, and selects PHYLINK and DIMLIB. `XILINX_LL_TEMAC` enables the LocalLink TEMAC driver and selects PHYLIB.

Integration: the Makefile uses these symbols to build `xilinx_emaclite.o`, `xilinx_emac.o`, and `ll_temac.o`. Dependency selection determines whether PHYLIB, PHYLINK, and DIM support are available to the corresponding sources.

State and persistence: no runtime state; selected options affect compiled objects and helper subsystem availability.

Risks and tests: the main risk is dependency drift with driver code, especially AXI EMAC's phylink/DIM requirements and LL TEMAC's PHYLIB path. Build matrix tests for each symbol as module and built-in are the key signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/Makefile

Purpose: maps Xilinx Ethernet Kconfig symbols to objects.

Important build rules: `ll_temac-objs := ll_temac_main.o ll_temac_mdio.o` creates the LocalLink TEMAC composite object. `CONFIG_XILINX_LL_TEMAC` builds `ll_temac.o`, `CONFIG_XILINX_EMACLITE` builds `xilinx_emaclite.o`, and `CONFIG_XILINX_AXI_EMAC` builds `xilinx_emac.o` from `xilinx_axienet_main.o` and `xilinx_axienet_mdio.o`.

Integration: this file defines module composition and makes the MDIO support part of each composite driver where needed.

State and persistence: no runtime state.

Risks and tests: missing an object would produce unresolved references such as TEMAC MDIO setup/teardown or AXI MDIO helpers. Build tests should cover all three Xilinx drivers as modules and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/ll_temac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/ll_temac.h

Purpose: shared definitions for the Xilinx LocalLink TEMAC driver and its MDIO companion.

Important definitions: the header defines frame sizes, option bits, LocalLink DMA register indexes and status bits, direct and indirect TEMAC register offsets, MDIO access bits, descriptor status/control flags, checksum feature flags, and multicast table size. `struct cdmac_bd` models the LocalLink DMA descriptor. `struct temac_local` is the main private data: netdev/device, PHY/MDIO fields, TEMAC and DMA register accessors, IRQs, locks, options, descriptor rings, indices, coalescing values, RX skb array, and restart work.

Control flow and integration: the main driver uses this header for DMA ring setup, TX/RX processing, option programming, PHY attachment, and register access. The MDIO file uses `temac_local`, indirect access helpers, and MDIO register constants. The macros `temac_ior()` and `temac_iow()` dispatch through endian-selected function pointers.

State and persistence: `temac_local` persists across probe and holds both software queue state and mapped hardware resources. Descriptor rings are coherent DMA memory; RX skb ownership alternates between DMA and network stack.

Risks and tests: risks include endian and DCR/MMIO mode mismatch, descriptor bit endianness, shared indirect-lock correctness between TEMAC instances, and max frame sizing. Compile tests plus hardware TX/RX, MDIO, multicast, coalescing, and endian-specific platforms are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/ll_temac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/ll_temac_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/ll_temac_main.c

Purpose: main Xilinx LocalLink TEMAC Ethernet platform driver. It handles register access, indirect TEMAC configuration, LocalLink DMA descriptor rings, PHY connection, TX/RX datapath, IRQs, ethtool controls, sysfs register dump, and probe/remove.

Important APIs: indirect access helpers wait on `XTE_RDY0_HARD_ACS_RDY_MASK` and serialize through `indirect_lock`. DMA accessors support big/little-endian MMIO and optional PowerPC DCR. `temac_dma_bd_init()` and release manage coherent descriptor rings and RX skb DMA mappings. `temac_device_reset()` resets MAC and DMA, allocates rings, sets default options, MAC address, and multicast table. `temac_start_xmit()` maps skb head/frags into descriptors and kicks TX tail. `temac_start_xmit_done()` frees completed TX descriptors. `ll_temac_recv()` drains completed RX descriptors, handles optional checksum complete, replenishes RX buffers, and advances DMA tail. `temac_open()` connects PHY, resets hardware, and requests TX/RX IRQs. `temac_probe()` maps resources, chooses endian/DMA mode, parses DT or platform data, sets checksum and coalescing defaults, registers MDIO, creates sysfs, and registers netdev.

Control flow: probe prepares software state only; open performs hardware reset and IRQ request. TX and RX are interrupt-driven through LocalLink DMA status registers, with delayed restart work to recover when RX descriptors become scarce. PHY link changes update TEMAC speed bits through indirect registers.

State and dependencies: persistent state is `struct temac_local`: descriptor rings, skb arrays, DMA indices, coalescing config, PHY/MDIO handles, locks, IRQs, feature bits, and register function pointers. Dependencies include PHYLIB, OF/platform data, DMA mapping, interrupts, sysfs, ethtool, and optional DCR.

Risks and tests: descriptor ownership/barriers, RX allocation failure recovery, DMA mapping unwind for fragmented TX, indirect-register timeouts, PHY disconnect ordering, ringparam changes only while down, and endian/DCR selection are high-risk areas. Test with traffic including fragmented skbs and jumbo frames, link speed changes, MDIO scans, interrupt coalescing changes, ringparam changes, error IRQ injection, and remove after open/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/ll_temac_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/ll_temac_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/ll_temac_mdio.c

Purpose: MDIO bus implementation for the Xilinx LocalLink TEMAC driver.

Important APIs: `temac_mdio_read()` writes PHY address/register to `XTE_LSW0_OFFSET`, reads `XTE_MIIMAI_OFFSET` through the locked indirect helper, and returns the PHY register value. `temac_mdio_write()` writes the value to `XTE_MGTDR_OFFSET` and initiates a write through `XTE_MIIMAI_OFFSET`. `temac_mdio_setup()` computes an MDIO clock divisor from DT `clock-frequency` or platform data, enables MDIO in `XTE_MC_OFFSET`, allocates/configures an `mii_bus`, derives a bus ID from resource or platform ID, and registers it with `of_mdiobus_register()`. `temac_mdio_teardown()` unregisters the bus.

Control flow and integration: setup is called from `temac_probe()` before PHY lookup/connection. MDIO transactions share `lp->indirect_lock` with other indirect TEMAC register access because the hardware supports only one indirect operation at a time.

State and dependencies: stores the bus pointer in `lp->mii_bus`. Depends on PHYLIB, OF MDIO, OF address parsing, platform data, and indirect access helpers from `ll_temac_main.c`.

Risks and tests: risks include divisor underflow/overflow, missing bus ID for unusual platform data, sleeping expectations around spin-locked indirect access, and teardown when setup failed. Test MDIO scan, PHY read/write via ethtool, DT and platform-data configurations, and concurrent link adjustment plus MDIO access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/ll_temac_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/xilinx_axienet.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/xilinx_axienet.h

Purpose: shared definitions for the Xilinx AXI Ethernet driver and its MDIO/main sources.

Important definitions: frame size and option constants, AXI DMA channel and descriptor offsets, DMA IRQ/coalescing masks, AXI Ethernet MAC register offsets, VLAN/filter/statistics/MDIO masks, PHY type values, checksum/status feature bits, PCS/PMA switching constants, and the exact hardware statistics counter enum. `struct axidma_bd` defines the aligned AXI DMA descriptor, including 64-bit address fields and SKB pointer. `struct skbuf_dma_descriptor` supports dmaengine mode. `struct axienet_local` is the driver private state for phylink, clocks, MDIO, MAC/DMA mappings, NAPI, DIM, DMA rings, stats accounting, error work, IRQs, PHY mode, options, features, frame limits, and dmaengine channels/rings.

Inline APIs: `axienet_ior()` and `axienet_iow()` access MAC registers. `axienet_dma_out32()` and `axienet_dma_out_addr()` write DMA registers and support 64-bit DMA when configured. `axienet_lock_mii()` and `axienet_unlock_mii()` serialize MDIO users through the bus lock. Prototypes expose `axienet_mdio_setup()` and teardown.

State and dependencies: this header defines the persistent state model used by the AXI Ethernet implementation. It depends on phylink, DIM, netdevice, spinlocks, VLAN, skbuff, interrupts, clocks, DMA descriptors, and optional 64-bit MMIO writes.

Risks and tests: risks include duplicated descriptor mask definitions, 64-bit DMA address handling, stats sequence synchronization, phylink/PCS state, DIM/coalescing setup, and mismatch between `enum temac_stat` order and hardware counter layout. Test AXI DMA ring operation, dmaengine mode, 64-bit DMA systems, phylink modes, MDIO setup, statistics overflow, checksum offload, VLAN/multicast options, and suspend/remove paths in implementation files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/xilinx_axienet.h -->
