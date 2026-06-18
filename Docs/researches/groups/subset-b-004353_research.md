# Research: subset-b-004353

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcmsysport.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcmsysport.c

Purpose: Implements the Broadcom BCM7xxx SYSTEMPORT/SYSTEMPORT Lite platform Ethernet MAC driver. It registers a platform net_device, drives UniMAC/GIB, RDMA/RBUF receive, TDMA transmit, level-2 interrupts, phylib link management, DSA switch queue mapping, ethtool stats/coalescing/WoL, and suspend/resume.

Important APIs/functions: `bcm_sysport_probe()` allocates `alloc_etherdev_mqs()`, maps MMIO, resolves DT PHY/fixed-link data, registers NAPI, notifier, ethtool and netdev ops. `bcm_sysport_open()` enables clocks, resets/flushes MAC/FIFOs, connects PHY, requests IRQs, initializes TX/RX rings, enables RDMA/TDMA/UniMAC, starts NAPI, PHY and queues. `bcm_sysport_stop()`, `bcm_sysport_suspend()`, and `bcm_sysport_resume()` reverse and rebuild that state. TX path is `bcm_sysport_xmit()` plus `bcm_sysport_insert_tsb()` and `__bcm_sysport_tx_reclaim()`. RX path is `bcm_sysport_rx_isr()` -> `bcm_sysport_poll()` -> `bcm_sysport_desc_rx()`. DSA integration is in `bcm_sysport_netdevice_event()`, `bcm_sysport_map_queues()`, `bcm_sysport_select_queue()`. WoL/filter support is in `bcm_sysport_set_wol()`, `bcm_sysport_suspend_to_wol()`, and RXNFC rule helpers.

Control flow: probe establishes persistent software context but does not allocate live DMA buffers. Open performs full hardware bring-up in strict order: reset/flush, feature programming, PHY attach, interrupt masking/request, TX ring setup, RDMA ring setup, DMA enable, MAC enable, NAPI/PHY/queue start. RX IRQ masks RDMA completion, schedules NAPI, and NAPI replenishes the descriptor before consuming the old packet. TX maps the SKB, writes the two-word descriptor through TDMA ports under `desc_lock`, and per-ring NAPI reclaims completions. Stop/suspend quiesce software first, then PHY, interrupts, DMA engines, rings, and clocks. Resume reconstructs rings and reapplies features and MAC state.

State/persistence: `struct bcm_sysport_priv` stores MMIO base, IRQ masks/status, ring arrays, RX indices, DIM/coalescing values, PHY link cache, checksum/TSB flags, WoL password/options, MIB counters, RX filter bitmaps, and DSA ring mapping. Ring control blocks persist only while the interface is open. Hardware counters are sampled into `priv->mib`; software 64-bit stats are protected by `u64_stats_sync`. WoL state and RX filter locations persist across open/suspend.

Dependencies/integration: Uses platform/OF, phylib/fixed PHY, DSA Broadcom tag helpers, net DIM, NAPI, DMA mapping, ethtool, wakeup IRQs, optional clocks, and register definitions from `bcmsysport.h` and `unimac.h`.

Risks/test signals: High-risk areas are DMA mapping/unmapping balance, ring index wrap, SYSTEMPORT Lite register offset/bit differences, DSA queue map bounds, WoL IRQ enable/disable balance, and suspend/resume ordering. Test with multi-queue TX/RX, SG/checksum/VLAN offloads, DSA user ports, ethtool stats/coalesce toggles, fixed PHY and external PHY, WoL magic/filter wake, runtime ifdown/ifup loops, suspend/resume, and fault injection for SKB/DMA allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcmsysport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcmsysport.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcmsysport.h

Purpose: Defines the hardware contract and driver-private state for the SYSTEMPORT Ethernet MAC implementation. It is the central map of descriptor formats, register offsets, interrupt bits, DMA ring fields, statistics layout, and `struct bcm_sysport_priv`.

Important APIs/types: `struct bcm_tsb` describes the transmit status block used for checksum/VLAN metadata. `struct bcm_rsb` describes the receive status block prepended by hardware. Register groups cover TOPCTRL, INTRL2, RXCHK, RBUF, TBUF, UMAC, Lite-only GIB, RDMA, and TDMA. `struct bcm_sysport_mib`, `struct bcm_sysport_stats`, and related macros define ethtool statistic mapping. `struct bcm_sysport_cb` tracks SKB and DMA address for RX/TX descriptors. `struct bcm_sysport_tx_ring` models per-queue TDMA state. `struct bcm_sysport_priv` aggregates platform resources, RX/TX rings, PHY state, coalescing/DIM, WoL, filters, stats, and DSA queue map. `BCM_SYSPORT_IO_MACRO()` creates typed MMIO accessors.

Control flow support: The header encodes all offsets and bit masks that `bcmsysport.c` uses to build descriptors, program DMA rings, mask interrupts, detect RX/TX completion, configure checksum parsing, and handle Lite-specific GIB/RDMA/TDMA differences. The statistics macros make array order match the memory layout of both hardware MIB blocks and software fields.

State/persistence: The persistent runtime state is explicitly centralized in `struct bcm_sysport_priv`. RX descriptor backing is MMIO-based, while software `bcm_sysport_cb` arrays remember DMA mappings. TX ring state records descriptor availability and clean/current indices. WoL filters are stored as a bitmap plus location array. `u64_stats_sync` allows lockless stats reads on 32-bit systems.

Dependencies/integration: Includes kernel bitmap, ethtool, VLAN, DIM, and local `unimac.h`; consumers depend on netdevice, phylib, DMA, DSA and platform APIs in the C file. Constants assume Broadcom register layout and 40-bit descriptor addressing.

Risks/test signals: Header changes are risky because structure offsets are used by ethtool stat descriptors and register offsets feed raw MMIO. Validate with compile coverage across big/little endian, 32/64-bit DMA address builds, SYSTEMPORT vs Lite devices, ethtool stats ordering, and packet offload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcmsysport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac-bcma-mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac-bcma-mdio.c

Purpose: Provides MDIO/MII bus support for the `bgmac` driver when the MAC is attached through BCMA. It translates phylib mdiobus reads/writes into Broadcom GMAC PHY access register transactions and performs legacy chipset PHY initialization.

Important APIs/functions: `bcma_mdio_phy_read()` and `bcma_mdio_phy_write()` program PHY control/access registers and wait for `BGMAC_PA_START` to clear. They choose either the GMAC common core for BCM4706 or the MAC core itself for other devices. `bcma_mdio_phy_init()` applies special register sequences for older BCM5356/5357/4749/53572 chipsets, otherwise calls `phy_init_hw()`. `bcma_mdio_phy_reset()` resets the selected PHY. `bcma_mdio_mii_register()` allocates and registers an OF mdiobus and `bcma_mdio_mii_unregister()` tears it down.

Control flow: The BCMA probe path registers this bus before shared `bgmac_enet_probe()` connects phylib. Reads/writes update the external PHY address in PHY control, start an MDIO operation, poll with microsecond delays, and return data or timeout errors. The bus reset hook reinitializes PHY hardware.

State/persistence: The mdiobus owns `bus->priv = bgmac`, a generated bus id, parent device, and phy mask derived from `bgmac->phyaddr`. No persistent stats are maintained here, but hardware register programming affects PHY state.

Dependencies/integration: Depends on BCMA core accessors, Broadcom PHY constants, OF MDIO registration, phylib, and `bgmac.h` register definitions. It exports register/unregister symbols for the BCMA front-end.

Risks/test signals: Risks include wrong core selection on BCM4706, legacy magic PHY sequences, phy mask mistakes, timeout handling, and missing OF child-node cleanup. Test by probing supported BCMA chip IDs, scanning MDIO, reading standard MII registers, reset/autonegotiation, and unload/reload with OF MDIO children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac-bcma-mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac-bcma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac-bcma.c

Purpose: Implements the BCMA bus front-end for the shared Broadcom GMAC core driver. It discovers BCMA GMAC cores, derives MAC/PHY resources from DT or SPROM, sets feature flags by chip/revision/package, registers optional MDIO, and delegates netdev operation to `bgmac.c`.

Important APIs/functions: Bus callback shims include `bcma_bgmac_read/write()`, IDM accessors, clock enable, chipcommon maskset, bus clock, and common-core PHY control. `bcma_phy_connect()` tries DT `of_phy_get_and_connect()`, then registered MDIO by SPROM PHY address, then fixed PHY. `bgmac_probe()` performs all BCMA-specific setup and calls `bgmac_enet_probe()`. `bgmac_remove()` unregisters MDIO and shared netdev. Module init/exit register a `bcma_driver`.

Control flow: Probe allocates `struct bgmac`, reads MAC address from DT or SPROM, validates common core availability, derives `phyaddr`, possibly registers MDIO, rejects unsupported PCI host setup, computes feature flags, installs callback table, then enters the shared probe. Removal reverses MDIO and shared driver state.

State/persistence: State added here lives inside the shared `struct bgmac`: `bcma.core`, `bcma.cmn`, `dma_dev`, IRQ, `phyaddr`, `has_robosw`, feature flags, callback pointers, and possibly `mii_bus`. SPROM/NVRAM-derived hardware policy persists for the device lifetime.

Dependencies/integration: Integrates Linux BCMA, SPROM, bcm47xx NVRAM indirectly through `bgmac.c`, Broadcom PHY flags, OF net/MDIO, phylib, and exported shared `bgmac` APIs.

Risks/test signals: Feature flag selection is chipset-specific and high risk for regressions. Probe error paths must unregister MDIO correctly. Test DT MAC fallback, SPROM MAC/PHY selection for core units 0-2, BCM4706 common-core path, BCM53573 PHY flags, roboswitch-warning path, module unload, and traffic after suspend/resume via shared core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac-bcma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac-platform.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac-platform.c

Purpose: Implements the platform/OF front-end for the shared `bgmac` Ethernet core, targeting Broadcom AMAC/NSP/NS2 style devices with memory resources rather than BCMA devices.

Important APIs/functions: Platform callbacks perform raw MMIO and optional IDM access: `platform_bgmac_read/write()`, `platform_bgmac_idm_read/write()`, `platform_bgmac_clk_enabled()`, and `platform_bgmac_clk_enable()`. `bgmac_nicpm_speed_set()` programs NICPM pad/IOMUX speed for RGMII and then calls shared link adjustment. `platform_phy_connect()` selects either NICPM-aware link callback or normal `bgmac_adjust_link()`. `bgmac_probe()` maps `amac_base`, optional `idm_base`, optional `nicpm_base`, sets platform feature flags and callbacks, chooses PHY/fixed-link policy, and calls `bgmac_enet_probe()`.

Control flow: Platform probe allocates shared bgmac state, loads MAC address if present, gets IRQ and resources, configures feature flags initially as 4707-like, clears IDM-mask feature if an IDM resource exists, installs callback table, selects OF PHY or fixed 2.5G mode, and delegates to the shared core. Remove calls only `bgmac_enet_remove()` because resources are devm-managed. PM hooks delegate suspend/resume to shared bgmac.

State/persistence: The front-end populates `bgmac->plat.base`, `idm_base`, `nicpm_base`, `dma_dev`, IRQ, feature flags, and callback pointers. NICPM speed writes persist in platform registers and are refreshed by link callback.

Dependencies/integration: Uses platform driver/OF resources, phylib, optional NICPM registers, BCMA constants for IDM register definitions, and shared `bgmac` APIs.

Risks/test signals: Optional resource handling changes behavior substantially, especially `BGMAC_FEAT_IDM_MASK`. NICPM speed programming must match PHY speed and RGMII board wiring. Test compatible strings, resource-name failures, fixed-link fallback, PHY handle path, 10/100/1000 speed changes with NICPM, suspend/resume, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac.c

Purpose: Shared Broadcom iProc/BCMA GMAC Ethernet implementation. Bus-specific files provide accessors and feature flags; this file owns DMA descriptors, RX/TX datapath, MAC reset/init, interrupts, NAPI, netdev operations, phylib link adjustment, ethtool stats, and shared probe/remove/PM helpers.

Important APIs/functions: DMA helpers include `bgmac_dma_alloc()`, `bgmac_dma_init()`, `bgmac_dma_cleanup()`, `bgmac_dma_tx_add()`, `bgmac_dma_tx_free()`, and `bgmac_dma_rx_read()`. Chip paths include `bgmac_chip_reset()`, `bgmac_chip_init()`, `bgmac_enable()`, `bgmac_mac_speed()`, and `bgmac_miiconfig()`. Netdev ops are `bgmac_open()`, `bgmac_stop()`, `bgmac_start_xmit()`, `bgmac_set_mac_address()`, and `bgmac_change_mtu()`. Exported APIs include `bgmac_alloc()`, `bgmac_enet_probe/remove()`, `bgmac_enet_suspend/resume()`, `bgmac_adjust_link()`, and `bgmac_phy_connect_direct()`.

Control flow: Shared probe validates/assigns MAC, enables core clock, resets chip, allocates coherent DMA rings, installs NAPI, connects PHY through the front-end callback, sets offload features, registers the netdev, and leaves carrier off. Open resets/init hardware, initializes RX buffers and TX rings, enables MAC/interrupts, requests IRQ, enables NAPI/PHY, and starts the queue. IRQ disables interrupts and schedules NAPI. NAPI acknowledges status, reclaims TX, reads RX frames, and re-enables interrupts when budget is not exhausted. Stop and suspend disable PHY/NAPI/queue, reset chip, and clean DMA.

State/persistence: `struct bgmac` stores ring descriptors, per-slot SKB/buffer mappings, MIB snapshots, interrupt mask, current MAC speed/duplex, feature flags, PHY address, and callback table. RX uses allocated fragments with poison headers to detect DMA failures; TX tracks start/end ring indices modulo slot count.

Dependencies/integration: Uses netdevice/NAPI/DMA APIs, phylib/fixed PHY, ethtool, bcm47xx NVRAM for some chip reset policy, local `unimac.h`, and callback operations supplied by BCMA/platform wrappers.

Risks/test signals: High-risk areas are DMA error unwinding for fragmented TX, RX buffer replacement before unmapping old buffers, unaligned DMA ring handling, interrupt mask policy, feature-flag reset sequences, and queue stop/wake. Test SG/checksum TX, RX under load, ring wrap, DMA allocation failure, IRQ storms, all supported chip feature combinations, MTU changes, ethtool stats, phylib speed/duplex changes, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac.h

Purpose: Defines the register layout, descriptor format, feature flags, shared state, and exported API contract for the Broadcom GMAC driver family. It lets BCMA and platform front-ends plug into the shared `bgmac.c` core.

Important APIs/types: Register constants cover device control/status, interrupts, PHY access, DMA engines, MIB counters, UniMAC base, BCMA IOCTL/IOST, chipcontrol interface types, and descriptor control bits. `struct bgmac_dma_desc` is the 64-bit DMA descriptor; `struct bgmac_dma_ring` tracks descriptor memory, MMIO base, unaligned index base, and slots. `struct bgmac` stores bus-specific unions, device pointers, netdev/NAPI, mdiobus, DMA rings, stats, IRQ state, link state, PHY address, feature flags, and callback pointers. Exported functions are shared lifecycle/PHY helpers.

Control flow support: Inline wrappers dispatch register, IDM, clock, chipcommon, bus-clock, common-core, and PHY connection operations through front-end callbacks. This separates bus mechanics from shared MAC/DMA logic.

State/persistence: The header defines one persistent per-device `struct bgmac`. DMA ring slots carry either SKBs or RX buffers plus DMA addresses. Feature flags persist from probe and gate reset/init behavior. MIB arrays can store counter snapshots, though stats update is mostly direct reads in the implementation.

Dependencies/integration: Includes netdevice and local `unimac.h`; uses BCMA constants from included build context and phylib types through consumers. Front-ends must initialize all callback pointers before `bgmac_enet_probe()`.

Risks/test signals: Callback-pointer completeness and feature flag correctness are critical. Changes to descriptor constants affect RX/TX hardware directly. Validate compile coverage for BCMA and platform builds, 32/64-bit DMA addresses, fixed PHY and MDIO PHY, ethtool stats size/order, and all feature-flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/Makefile

Purpose: Declares how the Broadcom `bng_en` driver is built when `CONFIG_BNGE` is enabled.

Important APIs/types/functions: It produces `bng_en.o` from core, devlink, HWRM, resource-memory, resource, netdev, ethtool, auxiliary RDMA, TX/RX, and link objects: `bnge_core.o`, `bnge_devlink.o`, `bnge_hwrm.o`, `bnge_hwrm_lib.o`, `bnge_rmem.o`, `bnge_resc.o`, `bnge_netdev.o`, `bnge_ethtool.o`, `bnge_auxr.o`, `bnge_txrx.o`, and `bnge_link.o`.

Control flow: Build-time only. It determines which compilation units are linked into the single module/object and therefore which symbols can satisfy cross-file calls used by the researched files.

State/persistence: No runtime state. Build composition persists through Kbuild dependency evaluation.

Dependencies/integration: Depends on Kconfig symbol `CONFIG_BNGE` and the listed sibling source files. The researched files rely on unlisted siblings for HWRM, netdev, resources, TX/RX, and link behavior.

Risks/test signals: Missing an object here would surface as link errors or absent runtime functionality. Test with `CONFIG_BNGE=m` and `=y`, clean incremental builds, and modpost symbol export checks for auxiliary RDMA functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge.h

Purpose: Main private header for the Broadcom ThorUltra `bng_en` NIC driver. It defines driver identity, board enum, firmware capability flags, enable flags, RSS/resource constants, `struct bnge_dev`, and doorbell helpers used across core, devlink, ethtool, auxiliary RDMA, netdev, TX/RX, resource, and HWRM files.

Important APIs/types: `struct bnge_dev` is the persistent PCI function context: device/P PCI/netdev pointers, DSN/VPD strings, BARs, doorbell geometry, HWRM command state, firmware version/capability data, PF info, driver state bits, context memory, resource limits, RSS config, ring counts, auxiliary RDMA resources, MTU/stat sizes, traffic-class mapping, IRQ table, aux device pointers, link info, and PHY flags. Helpers include `bnge_is_roce_en()`, `bnge_is_agg_reqd()`, `bnge_writeq()`, `bnge_db_write()`, `bnge_aux_registered()`, and `bnge_aux_get_msix()`.

Control flow support: Probe fills `bnge_dev`, HWRM updates capabilities/resources, netdev alloc attaches `bd->netdev`, aux and ethtool read the same state, and TX/RX code uses doorbell helpers to notify hardware.

State/persistence: This header defines most persistent driver state. Firmware capabilities (`fw_cap`), enabled features (`flags`), RSS tables, IRQ accounting, aux device state, VPD strings, link info, and HWRM sequence/lock state remain for device lifetime. On 32-bit systems, `db_lock` protects atomic 64-bit doorbell writes.

Dependencies/integration: Includes Linux ethernet helpers, firmware HSI header, and local resource/aux headers. It references `struct bnge_net` and many macros from sibling headers not in this work item, showing that this file is a cross-module contract.

Risks/test signals: Field layout and flag semantics are shared widely. Doorbell writes are especially sensitive to 32-bit atomicity and ring index/epoch masking. Test compile with 32-bit and 64-bit, HWRM probe paths, RSS sizing, RoCE enable/disable, jumbo/TPA aggregation conditions, and TX/RX doorbell behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_auxr.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_auxr.c

Purpose: Implements `bnge` auxiliary-bus integration for RDMA/RoCE clients and exposes a firmware-message bridge for the auxiliary driver.

Important APIs/functions: `bnge_rdma_aux_device_init()` allocates IDA id, auxiliary device, `bnge_auxr_dev`, and `bnge_auxr_info`, initializes the aux device, populates shared hardware info, and clears RoCE flags on failure. `bnge_rdma_aux_device_add()`, `bnge_rdma_aux_device_del()`, and `bnge_rdma_aux_device_uninit()` manage auxiliary bus lifetime. `bnge_register_dev()` grants requested MSI-X vectors after checking resources and fills `bnge_msix_info`. `bnge_unregister_dev()` clears allocation state. `bnge_send_msg()` sends arbitrary HWRM command payloads through the L2 driver's request path.

Control flow: PCI probe initializes aux state after doorbell BAR mapping and adds the aux device after netdev allocation. RDMA client registration occurs later through exported symbols, under `netdev_lock()` and aux mutex. Removal deletes the aux device before freeing netdev/IRQs, then uninitializes it.

State/persistence: `bnge_dev` keeps `aux_priv` and `auxr_dev`; `bnge_auxr_dev` stores PCI/net/bar/doorbell/RoCE/stat/PF data and a lock; `bnge_auxr_info` stores client handle and MSI-X request count. IDA ids persist until device release.

Dependencies/integration: Uses Linux auxiliary bus, PCI drvdata, netdev locking, HWRM request helpers, IRQ table/resource checks from sibling files, and exports symbols for the RDMA auxiliary driver.

Risks/test signals: Lifetime ordering is delicate: delete/uninit/release must not race RDMA clients or netdev teardown. `bnge_send_msg()` trusts caller payload lengths and response buffer size. Test RoCE disabled/enabled probe, auxiliary add failure, RDMA register/unregister, insufficient resources, removal while client loaded, HWRM timeout path, and IDA leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_auxr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_auxr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_auxr.h

Purpose: Defines the public contract between the `bnge` L2 NIC driver and its RDMA/RoCE auxiliary device.

Important APIs/types: `struct bnge_msix_info` describes vector, ring index, and doorbell offset handed to the aux driver. `struct bnge_fw_msg` wraps firmware command/response buffers and timeout for `bnge_send_msg()`. `struct bnge_auxr_info` stores client handle and allocated MSI-X count. `struct bnge_auxr_dev` is the shared aux-device payload containing netdev, PCI device, BAR0, MSI-X array, RoCE capability flags, doorbell sizes/offset, chip/stat/PF metadata, enable state, resource counts, and a mutex. Exported functions cover aux lifecycle, client register/unregister, and firmware send.

Control flow support: Core probe initializes and adds the auxiliary device; the RDMA client later calls register/unregister and send-message hooks. The header also defines minimum RoCE ring/stat context requirements and max MSI-X vectors.

State/persistence: Aux state persists while the auxiliary device exists. Capability flags record RoCE v1/v2 support and MSI-X allocation. `en_state` mirrors `bnge_dev` driver state for client visibility.

Dependencies/integration: Depends on Linux auxiliary bus and shared `struct bnge_dev`; consumers also rely on firmware HSI structures and PCI/netdev context supplied in the C implementation.

Risks/test signals: Any ABI-like change affects the auxiliary RDMA client. Validate struct field expectations with the RDMA module, vector count limits, RoCE v1/v2 flag propagation, locking around aux operations, and removal ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_auxr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_core.c

Purpose: Main PCI lifecycle and firmware registration module for the Broadcom ThorUltra `bng_en` driver. It identifies BCM57708 devices, enables PCI, maps BARs, allocates devlink/HWRM resources, registers with firmware, configures defaults, initializes netdev/RDMA aux/IRQs, and tears everything down.

Important APIs/functions: `bnge_probe_one()` is the central probe path. It validates non-bridge/MSI-X device, handles kdump FLR, enables PCI, allocates devlink-backed `bnge_dev`, maps BAR0, initializes HWRM, registers with firmware, registers devlink, sets IRQ resource maximum, initializes default aux/net config, maps doorbell BAR, initializes RDMA aux, allocates IRQs, allocates netdev, adds aux device, and saves PCI state. `bnge_remove_one()` reverses this. Firmware setup is split into `bnge_fw_register_dev()`, `bnge_func_qcaps()`, `bnge_func_qrcaps_qcfg()`, and `bnge_fw_unregister_dev()`. PCI helpers handle enable/disable, BAR unmap, doorbell BAR map, and MSI-X table size.

Control flow: Probe uses linear staged initialization with labeled unwinds. Firmware registration gets version/NVM, resets function, sets FW time, queries function and queue capabilities, allocates context memory, registers driver with firmware, then queries resources/config/VNIC caps and sets default RSS hash. Remove deletes aux, frees netdev/IRQs, uninitializes defaults, unregisters devlink and firmware, cleans HWRM, unmaps BARs, frees devlink, and disables PCI.

State/persistence: `bnge_dev` is allocated as devlink private data and stored in PCI drvdata. Persistent state includes BAR mappings, firmware version/capability/resource data, doorbell mapping, IRQ table, default RSS, netdev, aux device, and HWRM resources. Shutdown disables the PCI device and optionally enters D3hot for poweroff.

Dependencies/integration: Uses PCI, devlink, HWRM/resource/netdev/link/aux helpers from sibling files, crash dump handling, MSI-X config, DMA mask, and module PCI driver registration.

Risks/test signals: Probe unwind order is critical because firmware, devlink, netdev, IRQs, aux, BARs, and PCI resources overlap. `dma_set_mask_and_coherent()` return is not checked. Test probe failure injection at each stage, kdump path, MSI-X absent, BAR mapping failure, firmware registration failure, doorbell BAR sizing, remove after partial client registration, shutdown poweroff, and module reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_db.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_db.h

Purpose: Defines 64-bit doorbell record encoding used by `bnge` queue/ring notification paths.

Important APIs/types: Doorbell bit constants define epoch, toggle, XID, L2 path, valid bit, and SQ/SRQ/CQ/NQ type encodings. `struct bnge_db_info` stores the MMIO doorbell pointer, fixed key bits, ring mask, epoch mask, and epoch shift. `DB_EPOCH()` and `DB_RING_IDX()` compose the dynamic index bits used by `bnge_db_write()` in `bnge.h`.

Control flow: TX/RX and completion paths construct per-ring `bnge_db_info`, then doorbell hardware with `db_key64 | DB_RING_IDX(db, idx)`. Epoch bits allow hardware to distinguish wrapped ring indices.

State/persistence: Doorbell geometry persists per ring and is derived from hardware/resource setup. No standalone runtime state exists outside the struct embedded elsewhere.

Dependencies/integration: Included by `bnge.h`; consumed by TX/RX and queue resource files. It assumes 64-bit MMIO writes through `bnge_writeq()`.

Risks/test signals: Incorrect masks or shifts cause missed or misdirected hardware notifications. Test ring wrap, queue start/stop, SQ/CQ/NQ arm paths, 32-bit atomic write behavior through caller, and hardware generation compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_devlink.c

Purpose: Provides devlink allocation, registration, and `devlink info` reporting for the `bnge` PCI driver.

Important APIs/functions: `bnge_devlink_alloc()` creates a devlink instance with `bnge_dev` as private data, stores PCI drvdata, records device pointers, reads PCI DSN, and caches VPD board part/serial via `bnge_vpd_read_info()`. `bnge_devlink_info_get()` reports serial, board id, ASIC id/revision, running firmware package/management API/NCSI/RoCE versions, and stored firmware versions from NVM. `bnge_dl_info_put()` routes fixed/running/stored version keys and suppresses NCSI/RoCE version strings. `bnge_devlink_register/unregister/free()` wrap devlink lifecycle.

Control flow: Core probe allocates devlink before BAR/HWRM setup, registers it after firmware registration populates version data, and unregisters/frees during removal or probe unwind. The info callback reads `bd->ver_resp`, `bd->nvm_cfg_ver`, VPD strings, and HWRM NVM data at request time.

State/persistence: `board_partno`, `board_serialno`, DSN, firmware version fields, and HWRM version response are cached in `bnge_dev`. VPD data is temporary and freed after parsing.

Dependencies/integration: Uses PCI VPD helpers, devlink API, unaligned DSN formatting, firmware HSI structures, and `bnge_hwrm_nvm_dev_info()`.

Risks/test signals: Risks include devlink info before firmware fields are initialized, VPD string termination/length assumptions, suppressed NCSI/RoCE output despite computed versions, and unhandled HWRM NVM errors before checking flags. Test `devlink dev info`, missing VPD, zero DSN, older/newer firmware version formats, stored firmware invalid flag, and probe unwind after devlink allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_devlink.h

Purpose: Declares the devlink interface used by `bnge_core.c` and implemented in `bnge_devlink.c`.

Important APIs/types: `enum bnge_dl_version_type` selects fixed, running, or stored devlink version namespaces. Functions allocate/free devlink-backed `bnge_dev` and register/unregister the devlink instance.

Control flow support: Core probe calls alloc early, register after firmware data is available, unregister during teardown, and free after all users are gone.

State/persistence: No state is stored here; the header defines lifecycle entry points for devlink-private state in `struct bnge_dev`.

Dependencies/integration: Requires `struct bnge_dev` and `struct pci_dev` declarations from including context. It is part of the internal driver contract, not an external UAPI.

Risks/test signals: Signature changes must stay synchronized with core/devlink implementation. Compile-test probe/unwind paths and `devlink dev info` availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_ethtool.c

Purpose: Implements ethtool operations for the `bnge` netdev, covering link settings hooks, driver info, pause/autoneg restart, string/stat export, standard MAC/PHY/control/pause/RMON stat groups, and pause parameter updates.

Important APIs/functions: `bnge_set_ethtool_ops()` installs `bnge_ethtool_ops`. `bnge_nway_reset()` restarts link negotiation through HWRM when supported. Stat sizing/string/data paths are `bnge_get_num_stats()`, `bnge_get_sset_count()`, `bnge_get_strings()`, and `bnge_get_ethtool_stats()`. Standardized stat callbacks are `bnge_get_eth_phy_stats()`, `bnge_get_eth_mac_stats()`, `bnge_get_eth_ctrl_stats()`, `bnge_get_pause_stats()`, and `bnge_get_rmon_stats()`. Pause configuration is handled by `bnge_get_pauseparam()` and `bnge_set_pauseparam()`.

Control flow: ethtool queries compute dynamic counts based on ring counts, TPA support, port-stat flags, extended stat sizes returned by firmware, and priority-to-COS mapping. Data retrieval walks NQ/ring software stats, then port and extended stats arrays. Pause changes update cached link info and call HWRM only if the interface is running, rolling back on failure.

State/persistence: Reads `bnge_net` and `bnge_dev` state: ring counts, `bnapi` NQ stats, port stats backing stores, firmware stat sizes, flags, `eth_link_info`, PHY flags, firmware version, and PCI bus name. `bnge_set_pauseparam()` mutates requested flow-control/autoneg state.

Dependencies/integration: Depends on sibling link helpers (`bnge_get_link_ksettings`, `bnge_set_link_ksettings`, `bnge_get_link`, HWRM pause/link setters), HSI stat layouts, `bnge_net` private state, and ethtool netlink/stat APIs.

Risks/test signals: Dynamic stat counts must match string/data writes exactly; priority arrays assume 8 entries and valid `pri2cos_idx`. Pause/autoneg validation must align with firmware capabilities. Test `ethtool -S`, JSON/netlink stats groups, TPA on/off, port/ext stat flags, shared-channel vs separate TX ring indexing, pause get/set/nway reset with link up/down, no-pause PHYs, and firmware stat-size truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_ethtool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_ethtool.h

Purpose: Minimal internal header declaring ethtool setup for the `bnge` netdev.

Important APIs/types/functions: Exposes `bnge_set_ethtool_ops(struct net_device *dev)`, implemented in `bnge_ethtool.c`, for netdev initialization code to attach the driver's ethtool operation table.

Control flow support: The netdev allocation/configuration path calls this once after creating a `struct net_device` so later ethtool commands dispatch into the bnge handlers.

State/persistence: No state here; the call mutates `dev->ethtool_ops`.

Dependencies/integration: Requires `struct net_device` from Linux networking headers in the including translation unit.

Risks/test signals: Low risk, but missing this call leaves users without bnge ethtool features. Compile-test header inclusion and verify `ethtool -i`, `-S`, pause, and link settings are available after netdev registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_ethtool.h -->
