# subset-b-004351 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atl2.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atl2.c

Purpose: `atl2.c` is the complete PCI network driver for the Attansic/Atheros L2 Fast Ethernet controller. It registers the `atl2` PCI driver, allocates a private `net_device`, maps BAR0 MMIO, initializes PHY/MAC state, owns TX/RX DMA memory, implements netdev operations, exposes ethtool, and handles suspend/resume plus Wake-on-LAN.

Important APIs, types, and functions: the external integration surface is `atl2_driver`, `atl2_netdev_ops`, and `atl2_ethtool_ops`. Probe/remove and PM are handled by `atl2_probe()`, `atl2_remove()`, `atl2_suspend()`, `atl2_resume()`, and `atl2_shutdown()`. Runtime interface operations are `atl2_open()`, `atl2_close()`, `atl2_xmit_frame()`, `atl2_set_multi()`, `atl2_change_mtu()`, `atl2_set_mac()`, `atl2_ioctl()`, and `atl2_tx_timeout()`. Hardware helpers include `atl2_reset_hw()`, `atl2_init_hw()`, `atl2_configure()`, `atl2_setup_mac_ctrl()`, `atl2_read_phy_reg()`, `atl2_write_phy_reg()`, `atl2_phy_init()`, `atl2_get_speed_and_duplex()`, `atl2_read_mac_addr()`, `atl2_spi_read()`, `atl2_read_eeprom()`, and multicast hash helpers.

Control flow: `atl2_probe()` enables PCI, enforces 32-bit DMA, requests regions, maps MMIO, initializes private software defaults, initializes PHY, resets hardware, reads a MAC address from EEPROM/SPI/BIOS fallback, validates module parameters, initializes timers/workqueues, and registers the netdev. `atl2_open()` allocates one coherent ring block, calls hardware init/configure, restores multicast/VLAN state, requests MSI or shared INTx IRQ, starts the watchdog, triggers a manual interrupt, and enables the interrupt mask. `atl2_intr()` reads and clears `REG_ISR`, dispatches PHY/link, DMA reset, TX completion, and RX events, and schedules reset/link work when interrupt context cannot safely do full recovery. TX copies skb data into a device-owned TXD memory window and advances mailbox pointers; RX copies packet bytes from the RX descriptor memory into newly allocated skbs and passes them to `netif_rx()`.

State and persistence: persistent device configuration lives in PCI config, MMIO registers, PHY registers, optional EEPROM/VPD/SPI flash contents, and module parameters (`TxMemSize`, `RxMemBlock`, `MediaType`, `IntModTimer`, `FlashVendor`). Runtime state is in `struct atl2_adapter`: ring virtual/DMA addresses, ring indices, timers, flags, link state, WOL bits, and statistics. Suspend programs WOL or power-saving PHY state; resume restores PCI state, re-requests IRQs, resets hardware, and reopens the running netdev.

Dependencies and integration points: this file depends on Linux PCI, DMA coherent allocation, netdev, ethtool, MII ioctls, timers/workqueues, VLAN acceleration, interrupt APIs, and low-level register definitions from `atl2.h`/`atlx.h`. It integrates upward through `register_netdev()`, ethtool callbacks, `ndo_eth_ioctl`, netpoll support, and carrier/queue state APIs.

Risks: the driver is copy-based rather than zero-copy for both TX and RX, so buffer size and wrap calculations are critical. EEPROM writing is stubbed as always successful, which makes `set_eeprom` misleading. The fallback hard-coded MAC address is risky if permanent address discovery fails. The code contains old FIXME comments, compatibility paths, direct stats updates, and reset/link work that can race with close/suspend if flags are wrong. Test signals include PCI probe/remove, open/close cycles, TX ring exhaustion/wakeup, RX packet delivery with VLAN tags, PHY link changes, ethtool register/eeprom/WOL operations, suspend/resume with and without WOL, and DMA timeout reset interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atl2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atl2.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atl2.h

Purpose: `atl2.h` is the private hardware and software contract for the `atl2` Fast Ethernet driver. It combines OS-dependent MMIO wrappers, function prototypes for the private hardware helpers implemented in `atl2.c`, L2-specific register offsets and bit fields, descriptor layouts, adapter structures, and driver state bits.

Important APIs/types/functions: the header defines register access macros such as `ATL2_READ_REG()`, `ATL2_WRITE_REG()`, byte/word variants, and array accessors. It declares `struct atl2_hw`, `struct atl2_adapter`, `struct atl2_ring_header`, `struct rx_desc`, `struct tx_pkt_header`, `struct tx_pkt_status`, `struct atl2_spi_flash_dev`, and `enum atl2_state_t`. It also declares static helper prototypes for reset, MAC address, PHY, EEPROM, PCI config, multicast hashing, and power-save operations used by the implementation file.

Control flow: the header itself has no runtime control path, but it shapes almost every path in `atl2.c`. The TX path uses `tx_pkt_header` and `tx_pkt_status` layouts plus ring size fields from `struct atl2_adapter`. The RX path consumes `struct rx_desc` status bitfields. Hardware bring-up uses register constants for descriptor base addresses, DMA engines, flow control, mailbox indices, MAC control, interrupt status/mask bits, and PHY/MDIO control.

State and persistence: `struct atl2_hw` stores persistent-ish hardware identity and configuration values: vendor/device IDs, subsystem IDs, revision, PCI command word, MMIO base, permanent/current MAC addresses, advertised media, PHY configuration flag, flash vendor, interpacket-gap values, retry/duplex fields, frame size, and flow-control thresholds. `struct atl2_adapter` stores Linux runtime state: owning netdev/pci_dev, coherent ring block metadata, TX/RX indices, timers, work items, flags, MSI state, WOL, interrupt moderation, and locks.

Dependencies and integration points: `atl2.h` includes Linux PCI, interrupt, ethernet, atomic, and netdevice headers and includes `atlx.h` for shared Attansic register and PHY definitions. Its macros assume `hw_addr` is an ioremapped MMIO pointer and are used directly by the driver without an abstraction layer.

Risks: this header exposes many static prototypes, which is unusual but consistent with the implementation's single-translation-unit style. Several bitfield structures are hardware ABI-sensitive and depend on compiler layout assumptions. The register and descriptor constants are not self-validating, so mistakes surface only as broken hardware behavior. Test signals are build coverage, endian-sensitive descriptor tests on target hardware, link negotiation, interrupt mask behavior, and RX/TX ring wrap behavior across the declared structure fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atl2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atlx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atlx.c

Purpose: `atlx.c` is a shared helper implementation for Attansic drivers, guarded as an includable C fragment rather than a conventional separately linked object. It provides common netdev callbacks and utility routines for an `atl1`-style adapter: MII ioctl dispatch, MAC address changes, link checking, multicast filter programming, interrupt mask helpers, VLAN feature handling, TX timeout scheduling, and link-change work.

Important APIs/types/functions: the main functions are `atlx_ioctl()`, `atlx_set_mac()`, `atlx_check_for_link()`, `atlx_set_multi()`, `atlx_irq_enable()`, `atlx_irq_disable()`, `atlx_clear_phy_int()`, `atlx_tx_timeout()`, `atlx_link_chg_task()`, `atlx_vlan_mode()`, `atlx_restore_vlan()`, `atlx_fix_features()`, and `atlx_set_features()`. It depends on adapter/hardware types named `struct atlx_adapter` and `struct atl1_hw` and on lower-level helpers `atlx_read_phy_reg()`, `atlx_hash_mc_addr()`, `atlx_hash_set()`, `atlx_set_mac_addr()`, `atlx_mii_ioctl()`, and `atlx_check_link()` supplied by the including driver.

Control flow: netdev operations call into these helpers synchronously for ioctl, MAC address changes, multicast list changes, VLAN feature updates, and TX timeout. Interrupt paths can call `atlx_clear_phy_int()` and `atlx_irq_disable()`; link-down detection reads `MII_BMSR` twice, updates carrier state, and schedules `link_chg_task`, which later calls `atlx_check_link()` under the adapter lock.

State and persistence: the file mutates `adapter->hw.mac_addr`, `adapter->link_speed`, `adapter->phy_timer_pending`, `adapter->int_enabled`, netdev carrier state, and hardware registers such as `REG_MAC_CTRL`, `REG_RX_HASH_TABLE`, and `REG_IMR`. No persistent storage is written here; changes are runtime hardware/netdev state and are expected to be restored after reset by including-driver code.

Dependencies and integration points: this file sits between Linux netdev APIs and shared Attansic register definitions from `atlx.h`. It uses spinlocks, workqueues, `netdev_for_each_mc_addr()`, VLAN feature flags, MII definitions, and MMIO `ioread32`/`iowrite32`. Because it is included like a header, symbol visibility and type availability depend on inclusion order.

Risks: the file advertises its includable-C style as a temporary hack, which makes dependencies implicit and fragile. Link work scheduling while locks are held or while devices are closing must be coordinated by the including driver. Multicast hash programming clears both hash registers before rebuilding, so callers need stable address lists. Test signals include set-MAC rejection while running, multicast/promisc/allmulti transitions, VLAN feature toggling, PHY link-down notification, and IRQ mask/unmask behavior around close/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atlx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atlx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atlx.h

Purpose: `atlx.h` is the shared hardware definition header for Attansic/Atheros Ethernet drivers. It centralizes common error codes, speed/duplex/media constants, PCI/PM/VPD/SPI/TWSI/MDIO/MAC/WOL/register offsets, PHY bit definitions, wake flags, and a shared SPI flash command descriptor used by `atlx.c` and concrete drivers such as `atl2.c`.

Important APIs/types/functions: it is primarily macro data rather than callable code. Important groups include `REG_MASTER_CTRL`, `REG_MDIO_CTRL`, `REG_MAC_CTRL`, `REG_RX_HASH_TABLE`, `REG_WOL_CTRL`, interrupt/mask-related constants, MII advertisement and PHY status constants, WOL flags such as `ATLX_WUFC_MAG`, and `struct atlx_spi_flash_dev`. It also defines canonical speed values and error codes (`ATLX_ERR_PHY`, `ATLX_ERR_PHY_SPEED`, `ATLX_ERR_PHY_RES`) consumed by hardware helper functions.

Control flow: the constants guide reset, PHY MDIO transactions, MAC configuration, multicast filtering, EEPROM/SPI probing, WOL setup, link speed detection, and feature toggling in implementation files. For example, the `REG_MDIO_CTRL` bit fields encode read/write transactions; `REG_MAC_CTRL` bits govern TX/RX enablement, VLAN stripping, promiscuous/all-multicast modes, duplex, CRC, padding, and broadcast acceptance.

State and persistence: no state is stored in the header, but many constants address persistent or semi-persistent hardware areas: PCI power-management registers, VPD, SPI flash, TWSI, MAC station address, and WOL state. The header also defines the hardware vocabulary for runtime state stored in driver-private structures.

Dependencies and integration points: `atlx.h` depends only on basic Linux module/types headers and is included by both shared helper code and L2-specific code. It bridges netdev/PHY concepts to raw register bits and therefore must match hardware documentation closely.

Risks: the header contains a placeholder `TWSI_CTRL_SMB_SLV_ADDR` macro with a FIXME and no value, which would be unsafe if used in expressions. Any incorrect bit mask here affects multiple drivers. Because the header is broad and hardware-facing, test signals are mostly integration tests on real devices: MDIO read/write completion, MAC enable/disable, multicast hash acceptance, WOL wake, SPI/VPD reads, and link speed resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atlx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/Kconfig

Purpose: this Kconfig file defines the Broadcom Ethernet driver menu and all selectable Broadcom network driver symbols in this subtree. It controls whether the configurator exposes Broadcom devices and which individual drivers can be built in or as modules.

Important APIs/types/functions: the top-level symbol is `NET_VENDOR_BROADCOM`, gating the menu. Individual symbols include legacy and modern Broadcom drivers such as `B44`, `BCM4908_ENET`, `BCM63XX_ENET`, `BCMGENET`, `BNX2`, `CNIC`, `SB1250_MAC`, `TIGON3`, `BNX2X`, `BGMAC`, `SYSTEMPORT`, `BNXT`, `BNGE`, and `BCMASP`. `BCMASP` is the relevant symbol for the ASP2 files: it is tristate, depends on `ARCH_BRCMSTB || COMPILE_TEST`, defaults on for `ARCH_BRCMSTB`, depends on `OF`, and selects `PHYLIB`, `MDIO_BCM_UNIMAC`, and `PAGE_POOL`.

Control flow: Kconfig has no runtime flow; its build-time flow determines which object files are reachable by Makefiles. Enabling `NET_VENDOR_BROADCOM` allows selection of the driver symbols. Enabling `BCMASP` causes the Broadcom ASP2 module to be built by the Makefiles and brings in PHY, MDIO, and page-pool dependencies.

State and persistence: selected values persist in the kernel `.config`. These choices affect compile-time inclusion, module availability, and dependency closure, not runtime driver state.

Dependencies and integration points: this file integrates with the Linux kernel Kconfig system and with `drivers/net/ethernet/broadcom/Makefile`. It also encodes architecture, bus, optional PTP, HWMON, DCB, devlink, page-pool, and auxiliary bus dependencies used by drivers in the directory.

Risks: dependency mistakes produce build failures or silently hide drivers from expected platforms. For `BCMASP`, OF and page-pool support are mandatory; missing `ARCH_BRCMSTB` requires `COMPILE_TEST`. Test signals include `olddefconfig`, allmodconfig/allyesconfig builds, COMPILE_TEST coverage for `BCMASP`, and checking that selected helper subsystems are included when the driver is modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/Makefile

Purpose: this Makefile maps Broadcom Kconfig symbols to built objects and subdirectories. It is the build-system dispatch layer for all drivers under `drivers/net/ethernet/broadcom`.

Important APIs/types/functions: the file uses standard kernel `obj-$(CONFIG_...) += ...` assignments. The relevant ASP2 entry is `obj-$(CONFIG_BCMASP) += asp2/`, which delegates object construction to the `asp2/Makefile`. Other entries build single objects (`b44.o`, `tg3.o`, `bgmac.o`) or subdirectories (`genet/`, `bnx2x/`, `bnxt/`, `bnge/`).

Control flow: at build time, kbuild evaluates each `CONFIG_*` symbol and descends into enabled subdirectories or compiles enabled objects. Runtime control flow is unaffected except that unavailable objects cannot register their drivers.

State and persistence: no runtime state exists. The persistent input is the configured kernel `.config`; the output is object/module inclusion in the build tree.

Dependencies and integration points: this file integrates directly with `Kconfig` symbols and lower-level Makefiles, especially `broadcom/asp2/Makefile` for `CONFIG_BCMASP`. It must stay synchronized with file locations and module object names.

Risks: stale object names or missing directory entries cause drivers to disappear from builds despite enabled Kconfig symbols. For ASP2, the parent Makefile only delegates to `asp2/`; the child Makefile must define the actual module object. Test signals include `make M=drivers/net/ethernet/broadcom`, `CONFIG_BCMASP=m` module builds, and allmodconfig link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/Makefile

Purpose: this child Makefile defines the Broadcom ASP2 module composition. It turns `CONFIG_BCMASP` into a `bcm-asp.o` composite object.

Important APIs/types/functions: `obj-$(CONFIG_BCMASP) += bcm-asp.o` declares the module/built-in target, and `bcm-asp-objs := bcmasp.o bcmasp_intf.o bcmasp_ethtool.o` lists the three implementation objects linked into that target.

Control flow: kbuild includes this file only when the parent Broadcom Makefile descends into `asp2/`. It then compiles and links the core platform driver, per-interface netdev implementation, and ethtool support into one module.

State and persistence: there is no runtime state. Build state is derived from `CONFIG_BCMASP` and the object list.

Dependencies and integration points: this file must match exported/internal symbols across `bcmasp.c`, `bcmasp_intf.c`, `bcmasp_ethtool.c`, and declarations in `bcmasp.h`. `bcmasp_ethtool_ops` is defined in the ethtool object and referenced by interface creation; IRQ/filter/clock helpers are defined in the core object and used by the interface object.

Risks: omitted objects produce unresolved symbols or missing netdev capabilities. Renaming `bcm-asp.o` or its components must be coordinated with module aliases and Kconfig help. Test signals are a clean module build and `modinfo`/link checks showing `bcmasp.o`, `bcmasp_intf.o`, and `bcmasp_ethtool.o` included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp.c

Purpose: `bcmasp.c` is the core Broadcom ASP 2.0 platform driver. It owns platform probing/removal, top-level IRQ handling, ASP core clock control, global RX filter hardware programming, Wake-on-LAN interrupt management, MDA/network filter allocation, platform-version data, and system suspend/resume orchestration across all child Ethernet ports.

Important APIs/types/functions: public helpers used by `bcmasp_intf.c` and `bcmasp_ethtool.c` include `bcmasp_enable_phy_irq()`, `bcmasp_enable_tx_irq()`, `bcmasp_enable_rx_irq()`, `bcmasp_flush_rx_port()`, `bcmasp_set_promisc()`, `bcmasp_set_allmulti()`, `bcmasp_set_broad()`, `bcmasp_set_oaddr()`, `bcmasp_set_en_mda_filter()`, `bcmasp_disable_all_filters()`, `bcmasp_core_clock_set_intf()`, `bcmasp_netfilt_get_init()`, `bcmasp_netfilt_check_dup()`, `bcmasp_netfilt_release()`, `bcmasp_netfilt_get_active()`, `bcmasp_netfilt_get_all_active()`, `bcmasp_netfilt_suspend()`, and `bcmasp_enable_wol()`. Driver entry points are `bcmasp_probe()`, `bcmasp_remove()`, `bcmasp_suspend()`, and `bcmasp_resume()`.

Control flow: probe allocates `bcmasp_priv`, maps the platform resource, sets a 40-bit DMA mask, enables clocks, selects the main clock domain, masks/clears interrupts, registers the main IRQ, populates MDIO children, initializes core RX/EDPKT/filter state, initializes WOL IRQ support, creates interfaces from `ethernet-ports` child nodes, drops clocks, then registers each netdev. The main ISR reads unmasked ASP_INTR2 status, clears it, and dispatches per-interface RX NAPI, TX NAPI, and PHY events. Suspend asks each interface to suspend, disables shared TX/main clocks as appropriate, and switches to the slow clock; resume reverses this and reinitializes core/filter hardware before resuming interfaces.

State and persistence: `bcmasp_priv` stores the platform device, clock, IRQ mask, WOL IRQ/mask, platform data callbacks and capacities, MMIO base, interface list, MDA filter table, network filter table, and locks. Filter rules are maintained in software and wake filters are only programmed to hardware during suspend. Platform data for ASP v2.1/v2.2/v3.0 controls clock-selection implementation, filter counts, TX channel offset, RX control offset, and EEE fixup behavior.

Dependencies and integration points: the file integrates with platform driver and OF matching (`brcm,asp-v2.1`, `brcm,asp-v2.2`, `brcm,asp-v3.0`), Linux clocks, `of_platform_populate()` for MDIO children, device wakeup APIs, PHY interrupt forwarding, ethtool RX classification data structures, and MMIO helpers from `bcmasp.h`.

Risks: network wake filters consume pairs of hardware filters and are programmed lazily at suspend, so runtime ethtool state can diverge from hardware until suspend. Shared filter and clock state must be protected by the correct mutex/spinlock. This snapshot contains suspicious duplicate lines in places such as `bcmasp_netfilt_rd()` and a duplicate local declaration in `bcmasp_core_clock_set_intf()`, which should be compile-checked. Test signals include OF probe with multiple ports, IRQ masking, RX/TX NAPI scheduling, WOL IRQ wake, suspend/resume with filter wake rules, all supported compatible strings, and filter capacity/duplicate handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp.h

Purpose: `bcmasp.h` is the shared internal contract for the Broadcom ASP2 driver. It defines top-level ASP register offsets, interrupt/wakeup/filter/EDPKT/control constants, descriptor formats, TX callback state, per-interface and global private structures, MMIO accessor generators, packet-offload command layout, and cross-object function prototypes.

Important APIs/types/functions: key structures are `struct bcmasp_tx_cb`, `struct bcmasp_res`, `struct bcmasp_desc`, `struct bcmasp_intf_stats64`, `struct bcmasp_mib_counters`, `struct bcmasp_intf`, `struct bcmasp_net_filter`, `struct bcmasp_mda_filter`, `struct bcmasp_plat_data`, `struct bcmasp_priv`, and `struct bcmasp_pkt_offload`. Inline accessors generated by `BCMASP_IO_MACRO`, `BCMASP_FP_IO_MACRO`, `BCMASP_FP_IO_MACRO_Q`, `BCMASP_CORE_IO_MACRO`, and `BCMASP_CORE_IO_MACRO_OFFSET` provide relaxed 32-bit/64-bit MMIO access for per-interface and core regions.

Control flow: the header does not execute control flow, but it defines how the implementation files coordinate. `bcmasp.c` owns global filters, IRQs, clocks, WOL, and platform lifecycle using `bcmasp_priv`. `bcmasp_intf.c` owns datapath rings and per-port netdev lifecycle using `bcmasp_intf`. `bcmasp_ethtool.c` uses the same structures for stats, WOL, EEE, and RX filter control.

State and persistence: `bcmasp_intf` holds per-port runtime state: channel/port/index, TX/RX NAPI, descriptor rings, DMA pointers, streaming RX ring, page pool, resources, PHY nodes, old link values, stats, MIB counters, WOL options, and SecureOn password. `bcmasp_priv` holds global state: platform resources, clocks, IRQ masks, WOL irq state, filter tables, interface list, and synchronization primitives. No persistent storage is written by the header, but WOL options and filters are kept in memory across open/close and pushed to hardware on suspend.

Dependencies and integration points: it includes netdevice, PHY, non-atomic 64-bit I/O, ethtool UAPI, and page-pool helpers. It exposes `extern const struct ethtool_ops bcmasp_ethtool_ops` and prototypes used across the three linked objects. Register constants align with `bcmasp_intf_defs.h`, which supplies per-interface offsets.

Risks: descriptor bit fields and 40-bit DMA address masks are hardware ABI-critical. Relaxed MMIO access requires explicit barriers in datapath code. The header duplicates some `ASP_RX_FILTER_MDA_*` macro definitions, which is harmless if identical but a maintenance smell. Test signals include sparse/build checks for inline accessors, 40-bit DMA tests, descriptor flag interpretation, page-pool integration, and compile/link checks across the composite module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp_ethtool.c

Purpose: `bcmasp_ethtool.c` implements the ethtool surface for Broadcom ASP2 netdevs. It reports driver info, message level, custom statistics, MAC/RMON/control counters, timestamp capabilities, link settings through PHYLIB, EEE through PHYLIB, Wake-on-LAN configuration, and RX network classifier rules used for wake filters.

Important APIs/types/functions: the exported integration point is `const struct ethtool_ops bcmasp_ethtool_ops`. Important helpers are `bcmasp_get_sset_count()`, `bcmasp_get_strings()`, `bcmasp_update_mib_counters()`, `bcmasp_get_ethtool_stats()`, `bcmasp_get_drvinfo()`, `bcmasp_get_wol()`, `bcmasp_set_wol()`, `bcmasp_flow_insert()`, `bcmasp_flow_delete()`, `bcmasp_flow_get()`, `bcmasp_set_rxnfc()`, `bcmasp_get_rxnfc()`, `bcmasp_get_eee()`, `bcmasp_set_eee()`, `bcmasp_get_eth_mac_stats()`, `bcmasp_get_rmon_stats()`, and `bcmasp_get_eth_ctrl_stats()`.

Control flow: ethtool stats requests optionally refresh hardware MIB values when the interface is running, then copy values from `intf->mib`. WOL get merges PHY WOL capabilities with MAC WOL capabilities when the device can wake; WOL set tries PHY WOL first and falls back to MAC-managed WOL options guarded by `priv->wol_lock`. RXNFC insertion accepts only wake filters (`RX_CLS_FLOW_WAKE`) for selected flow types, rejects duplicates, allocates one or two software filter slots through core helpers, and defers hardware programming until suspend.

State and persistence: `intf->msg_enable`, `intf->wolopts`, `intf->sopass`, `intf->mib`, and `priv->net_filters` are the main state touched here. WOL settings persist in driver memory until changed and affect suspend behavior. RX classifier rules persist in the software filter table and are exposed by get/list operations.

Dependencies and integration points: the file depends on ethtool, PHYLIB ethtool helpers, unaligned access for stats layout, netdevice, and the core filter/WOL helpers declared in `bcmasp.h`. It reads UniMAC and RX control registers using MMIO accessors and delegates link operations to `phy_ethtool_*`.

Risks: only wake filters are supported; non-wake classifier inserts return `-EOPNOTSUPP`. Wake filters consume paired slots for 256-byte matching, so location and capacity behavior is stricter than generic ethtool users may expect. The stats table must match `struct bcmasp_mib_counters` order exactly. Test signals include `ethtool -S`, WOL get/set with PHY and MAC combinations, SecureOn password behavior, RX classifier insert/delete/list/get, EEE get/set, and MAC/RMON counter reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp_intf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp_intf.c

Purpose: `bcmasp_intf.c` implements each ASP2 Ethernet interface as a Linux netdev. It owns per-port resource mapping, PHY connection, MAC/RGMII setup, TX/RX descriptor rings, NAPI polling, page-pool backed RX skb construction, netdev open/stop, multicast/unicast filter programming, link adjustment, stats64, and per-interface suspend/resume including WOL mode.

Important APIs/types/functions: externally used functions are `bcmasp_interface_create()`, `bcmasp_interface_destroy()`, `bcmasp_interface_suspend()`, and `bcmasp_interface_resume()`. Netdev operations are provided by `bcmasp_netdev_ops`: `bcmasp_open()`, `bcmasp_stop()`, `bcmasp_xmit()`, `bcmasp_tx_timeout()`, `bcmasp_set_rx_mode()`, `bcmasp_get_phys_port_name()`, `phy_do_ioctl_running`, `eth_mac_addr`, and `bcmasp_get_stats64()`. Datapath helpers include `bcmasp_csum_offload()`, `bcmasp_tx_reclaim()`, `bcmasp_tx_poll()`, `bcmasp_rx_poll()`, `bcmasp_alloc_buffers()`, `bcmasp_init_rx()`, and `bcmasp_init_tx()`.

Control flow: `bcmasp_interface_create()` parses `reg`, `brcm,channel`, PHY mode, fixed-link/phy-handle, MAC address, feature flags, and maps per-port/per-channel register windows. `bcmasp_open()` allocates RX streaming memory, RX/TX descriptor rings, TX callbacks, enables the parent clock, connects PHY, configures port mode, initializes UniMAC, rings, NAPI, IRQs, filters, and queue state. TX maps skb head/frags into descriptors, optionally prepends hardware checksum-offload commands, advances the valid DMA pointer, and wakes hardware. TX NAPI reclaims descriptors and frees skbs. RX NAPI follows hardware descriptor valid/read pointers, copies packet bytes from the streaming DMA ring into a page-pool skb, handles checksum/FCS/alignment details, and feeds GRO.

State and persistence: runtime state is primarily in `struct bcmasp_intf`: TX/RX indices and DMA pointer shadows, coherent descriptor rings, streaming RX ring, page pool, PHY state, old link/duplex/pause values, CRC forwarding flag, MIB counters, stats64, WOL options, and SecureOn password. Hardware state is programmed into UniMAC, RGMII, TX SPB, RX EDPKT, UMAC2FB, and wake registers. No nonvolatile state is written.

Dependencies and integration points: this file integrates with netdev, NAPI, DMA mapping, page pool, PHYLIB/OF MDIO/fixed-link, Broadcom PHY flags, checksum helpers, PTP classify headers, and core ASP helpers for filters, clocks, IRQs, and WOL. It relies heavily on register offsets from `bcmasp_intf_defs.h`.

Risks: descriptor pointer arithmetic and valid/read off-by-one handling are high risk. RX copies from a streaming ring into page-pool skbs, so DMA sync, padding, and FCS trimming must stay correct. This snapshot shows duplicate `bcmasp_csum_offload()` invocation and a duplicate `PHY_BRCM_IDDQ_SUSPEND` line, which should be build/runtime reviewed. Stop/suspend deinitializes NAPI and later open/resume adds it again, so lifecycle ordering matters. Test signals include multi-frag TX, checksum offload for IPv4/IPv6 TCP/UDP, ring full/wakeup, RX checksum/FCS paths, multicast filter overflow fallback to promiscuous mode, PHY link speed/EEE changes, open/stop loops, suspend/resume with and without WOL, and fixed-link/internal PHY configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp_intf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp_intf_defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp_intf_defs.h

Purpose: `bcmasp_intf_defs.h` is the per-interface register map for the Broadcom ASP2 driver. It defines offset formulas and bit fields for UniMAC, UMAC-to-forwarding-buffer, RGMII, TX SPB DMA/control/top, TX EPKT core, TX pause, RX EDPKT DMA/config, RX SPB, RX pause, and ring sizing.

Important APIs/types/functions: this header is macro-only. Major groups are `UMC_OFFSET()`, `UMC_CMD` and UniMAC MIB counters, `UMAC2FB_OFFSET`/`UMAC2FB_CFG`, `RGMII_OFFSET()` plus EPHY/OOB/port/LED controls, `TX_SPB_DMA_OFFSET()`, `TX_SPB_CTRL_OFFSET()`, `TX_EPKT_C_OFFSET()`, `RX_EDPKT_DMA_OFFSET()`, `RX_EDPKT_CFG_OFFSET()`, and constants `NUM_4K_BUFFERS`, `RING_BUFFER_SIZE`, `DESC_RING_COUNT`, `DESC_SIZE`, and `DESC_RING_SIZE`.

Control flow: the implementation uses these constants during interface resource mapping, MAC reset/init, link adjustment, TX/RX channel initialization, PHY power control, and statistics collection. For example, `UMC_CMD` speed/duplex/pause bits are updated from PHY link state, TX SPB offsets program descriptor DMA windows, and RX EDPKT offsets configure the streaming RX data ring and descriptor ring.

State and persistence: the header stores no state, but it describes where per-interface state resides in hardware. Ring sizing constants define the amount of coherent descriptor memory and streaming RX memory that `bcmasp_intf.c` allocates and programs.

Dependencies and integration points: it assumes Linux bit macros and is included by all ASP2 implementation files. It complements `bcmasp.h`, which defines core/global registers and structures, while this file provides per-port/per-channel register layout.

Risks: offset formulas depend on `port` and `channel` values parsed from device tree; invalid DT values can point an interface at wrong hardware windows. Ring constants are coupled to descriptor layout and RX buffer mode. Test signals include interface creation for each supported port/channel, TX/RX descriptor base/end/valid programming, RGMII/internal PHY mode switching, UniMAC MIB reads, and compile-time use across all ASP2 objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp_intf_defs.h -->
