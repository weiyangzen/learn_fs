# Research: subset-b-004381

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmgenet.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmgenet.c

## Purpose

`bcmgenet.c` is the main Linux platform/netdev driver for Broadcom GENET Gigabit Ethernet controllers. It binds OF/ACPI platform devices, detects GENET revision-specific register layouts, configures UniMAC, RDMA/TDMA descriptor rings, interrupts, NAPI, ethtool operations, RX classification filters, statistics, power management, and suspend/resume. It integrates with `bcmgenet.h` for register definitions/private state, `bcmmii.c` for PHY/MDIO setup, and `bcmgenet_wol.c` for Wake-on-LAN transitions.

## Important APIs, Types, and Functions

The file exposes the platform driver through `module_platform_driver(bcmgenet_driver)` and installs `bcmgenet_netdev_ops` and `bcmgenet_ethtool_ops`. Important netdev entry points are `bcmgenet_open`, `bcmgenet_close`, `bcmgenet_xmit`, `bcmgenet_timeout`, `bcmgenet_set_rx_mode`, `bcmgenet_set_mac_addr`, `bcmgenet_get_stats64`, and `bcmgenet_change_carrier`. Important ethtool paths cover link settings, pause, EEE, WOL, coalescing, driver stats, and RX NFC rule insertion/deletion.

Hardware abstraction is built around revision-selected `struct bcmgenet_hw_params` instances plus runtime register-offset tables `bcmgenet_dma_regs` and `genet_dma_ring_regs`. `bcmgenet_set_hw_params` chooses GENET v1-v5 register maps, validates the hardware revision from `SYS_REV_CTRL`, records integrated PHY revision hints, and selects descriptor word width. Descriptor helpers `dmadesc_set_addr`, `dmadesc_set_length_status`, and `dmadesc_set` hide 32-bit versus 40-bit DMA address programming.

Key control functions include `init_umac`, `reset_umac`, `bcmgenet_umac_reset`, `bcmgenet_init_dma`, `bcmgenet_init_tx_queues`, `bcmgenet_init_rx_queues`, `bcmgenet_dma_teardown`, `bcmgenet_fini_dma`, `bcmgenet_isr0`, `bcmgenet_isr1`, `bcmgenet_irq_task`, `bcmgenet_resume`, and `bcmgenet_suspend`.

## Control Flow

Probe allocates a multi-queue Ethernet device, maps registers, records IRQs, sets defaults for pause/checksum/scatter-gather features, requests an optional WOL IRQ, enables the main clock long enough to detect hardware parameters, sets the DMA mask, initializes MDIO support, configures queue counts and stats synchronizers, disables carrier, turns the clock back off, and registers the netdev.

Open enables the clock, powers internal PHYs when necessary, clears UniMAC reset, initializes UniMAC, reapplies features and the MAC address, clears/reinitializes the hardware filter block, initializes RX/TX DMA rings, requests the two main IRQs, attaches the PHY through `bcmgenet_mii_probe`, applies pause settings, starts NAPI/MAC/link interrupts/PHY, and starts TX queues. Close follows the reverse order: stop queues and RX, optionally stop/disconnect PHY, disable DMA and NAPI, mask interrupts, cancel deferred IRQ work, reclaim all TX descriptors, free RX/TX control blocks, free IRQs, power down the internal PHY, and disable the clock.

TX maps one SKB head plus frags into descriptors. `bcmgenet_xmit` reserves descriptor space under the per-ring spinlock, prepends a 64-byte transmit status block for checksum metadata, maps all fragments, writes descriptors with SOP/EOP/append-CRC/checksum flags, advances software producer/write pointers, and updates the hardware producer index unless batching through `netdev_xmit_more`. TX completion is NAPI-driven by `bcmgenet_tx_poll`, which calls `__bcmgenet_tx_reclaim` to compare hardware consumer index with software `c_index`, unmap DMA, complete SKBs, update per-ring u64 stats, and wake stopped queues.

RX uses preallocated 2 KB SKBs mapped into RDMA descriptors. `bcmgenet_desc_rx` reads the hardware producer index, tracks hardware discard counters, refills each descriptor before handing the old SKB upward, parses the 64-byte receive status block, validates length/SOP/EOP/error bits, applies checksum-complete metadata, strips status/alignment bytes and optional FCS, updates per-ring stats, and submits packets via `napi_gro_receive`. `bcmgenet_rx_poll` also feeds `net_dim` when adaptive RX coalescing is enabled.

IRQ instance 1 handles per-ring RX/TX events by masking the ring interrupt and scheduling the corresponding NAPI instance. IRQ instance 0 handles MDIO completion/error wakeups and defers PHY/link events to `bcmgenet_irq_task`.

## State and Persistence Behavior

Persistent runtime state lives in `struct bcmgenet_priv`: mapped base address, revision/flags, queue descriptors/control blocks, RX NFC rules/list, PHY/MDIO pointers, IRQ state, pause/WOL options, clocks, and MIB/software counters. Ring state is held in `struct bcmgenet_tx_ring` and `struct bcmgenet_rx_ring`, including producer/consumer/read/clean pointers, descriptor ownership, NAPI objects, and u64 stats. No disk persistence is involved; state is rebuilt at probe/open/resume and torn down at close/remove/suspend. Wake settings persist only in driver memory (`wolopts`, `sopass`) while the device object exists.

## Dependencies and Integration Points

The file depends on Linux netdev, NAPI, ethtool, phylib, platform device, PM, DMA mapping, clocks, and `unimac.h` register definitions. It calls MDIO/PHY helpers in `bcmmii.c` (`bcmgenet_mii_init`, `bcmgenet_mii_probe`, `bcmgenet_mii_config`, `bcmgenet_phy_pause_set`, `bcmgenet_phy_power_set`) and WOL helpers in `bcmgenet_wol.c`. Device matching is through `brcm,genet-v1` through `brcm,genet-v5`, BCM2711/BCM7712 compatibles, and ACPI ID `BCM6E4E`. It has a soft dependency on `mdio-bcm-unimac`.

## Risks and Edge Cases

The highest-risk areas are descriptor ring accounting, DMA mapping rollback, version-specific register offsets, and PM/WOL resume branches. TX mapping failure rewinds descriptors and unmaps already-mapped fragments; regressions here can leak DMA mappings or corrupt ring pointers. RX refilling occurs before packet validation, so allocation failure drops the packet but still advances consumer state. `bcmgenet_dma_regs` and `genet_dma_ring_regs` are file-scope globals selected at probe time; mixed GENET revisions in one loaded kernel would be risky if multiple devices with different versions coexist. Suspend/resume has two paths: a fast WOL path that preserves RX state and reinitializes TX only, and a full reset path that restores filters, features, DMA, and PHY configuration. RX NFC/HFB programming has version-specific filter enable and queue mapping layouts and only supports masks made from 0x00/0x0f/0xf0/0xff bytes.

## Test Signals

Useful validation signals include successful probe/open/close cycles across GENET revisions, TX/RX traffic with SG and checksum offload enabled, DMA mapping failure injection, TX timeout recovery, ethtool stats/coalescing/pause/EEE/RXNFC operations, multicast/promiscuous filter behavior, PHY link up/down interrupts, suspend/resume with and without WOL, magic-packet wake, wake-filter rules, and 32-bit versus 40-bit DMA mask coverage. Runtime logs to watch include GENET version mismatch warnings, DMA disable timeouts, RX oversize/fragment/error messages, TX DMA map failures, and PHY attach failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmgenet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmgenet.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmgenet.h

## Purpose

`bcmgenet.h` is the shared private header for the Broadcom GENET driver files. It defines descriptor formats, register offsets, interrupt bits, hardware-version flags, queue/ring/private-state structures, accessor macros, and cross-file function prototypes used by `bcmgenet.c`, `bcmmii.c`, and `bcmgenet_wol.c`.

## Important APIs, Types, and Definitions

Global geometry constants include `GENET_MAX_MQ_CNT`, `TOTAL_DESC`, `DESC_INDEX`, `ENET_MAX_MTU_SIZE`, `DMA_MAX_BURST_LENGTH`, `MAX_NUM_OF_FS_RULES`, and DMA flow-control thresholds. `struct status_64` models the 64-byte RX/TX status block used by checksum offload paths. Descriptor register offsets and bit definitions include `DMA_DESC_LENGTH_STATUS`, `DMA_DESC_ADDRESS_LO`, optional `DMA_DESC_ADDRESS_HI`, `DMA_OWN`, `DMA_SOP`, `DMA_EOP`, `DMA_WRAP`, TX flags such as `DMA_TX_APPEND_CRC` and `DMA_TX_DO_CSUM`, and RX error/classification flags such as `DMA_RX_CRC_ERROR`, `DMA_RX_OV`, `DMA_RX_MULT`, and `DMA_RX_BRDCAST`.

The counter structs (`bcmgenet_pkt_counters`, `bcmgenet_rx_counters`, `bcmgenet_tx_counters`, `bcmgenet_mib_counters`, `bcmgenet_tx_stats64`, `bcmgenet_rx_stats64`) define both hardware MIB layout and software per-ring stats. Register definitions cover UniMAC MIB/MDIO/Magic Packet Detection registers, RBUF/TBUF/HFB blocks, interrupt controller instances, system and external power/RGMII blocks, and DMA control/status/ring fields.

Driver state types are central. `struct enet_cb` binds an SKB, descriptor address, and DMA unmap metadata. `enum bcmgenet_power_mode`, `enum bcmgenet_version`, and `GENET_HAS_*` flags describe power and hardware capabilities. `struct bcmgenet_hw_params` captures version-specific queue counts, filter sizes, register offsets, descriptor width, and queue tag masks. `struct bcmgenet_tx_ring` and `struct bcmgenet_rx_ring` store per-ring software pointers, NAPI objects, stats, and RX DIM state. `struct bcmgenet_rxnfc_rule` holds ethtool flow classifier state. `struct bcmgenet_priv` is the device-wide private state shared by all source files.

The `GENET_IO_MACRO` generates endian-aware inline accessors for named register blocks: `ext`, `umac`, `sys`, `intrl2_0`, `intrl2_1`, `hfb`, `hfb_reg`, and `rbuf`. Capability helpers such as `bcmgenet_has_40bits`, `bcmgenet_has_ext`, `bcmgenet_has_mdio_intr`, `bcmgenet_has_moca_link_det`, and `bcmgenet_has_ephy_16nm` centralize flag checks.

## Control Flow and Integration

This header has no executable top-level control flow. Its role is to make the rest of the driver agree on register layout, bit semantics, and state ownership. `bcmgenet.c` consumes almost every register definition and private field for probe/open/DMA/NAPI/PM. `bcmmii.c` uses PHY, MDIO, RGMII, power, and pause definitions. `bcmgenet_wol.c` uses WOL, HFB, RBUF status, MPD, clock, IRQ, and PHY-state fields.

The cross-file prototypes at the end form the internal module boundary: MII init/probe/config/exit and PHY pause/power/setup functions, WOL get/set and power transition functions, plus `bcmgenet_eee_enable_set`.

## State and Persistence Behavior

The header defines in-memory state only. `struct bcmgenet_priv` persists for the lifetime of the registered netdev and tracks clocks, platform devices, descriptor pools, RX/TX rings, PHY/MDIO objects, IRQ numbers/status, feature settings, WOL options, and counters. Per-ring structures persist across an open instance after DMA initialization, then are torn down and rebuilt during close or reset-style resume. RX NFC rules are stored in the private struct and can be replayed after resume.

## Dependencies

The header depends on kernel networking, spinlock, clock, MII/PHY, VLAN, DIM, and ethtool headers, plus Broadcom UniMAC definitions from `../unimac.h`. Many numeric definitions are hardware-contract values and must stay synchronized with the GENET programming manual and with hardware-version choices in `bcmgenet.c`.

## Risks and Edge Cases

The main risk is layout drift: MIB counter structs are expected to match hardware counter order, descriptor constants must match hardware descriptor word layouts, and register offsets differ across GENET revisions. `struct bcmgenet_hw_params` is explicitly used in hot paths and is expected to remain compact/aligned. The `GENET_IO_MACRO` uses `priv->hw_params` in generated HFB accessor offsets; callers must ensure hardware params are initialized before using those accessors. The file also encodes special cases such as v4 40-bit address support, v5/E PHY flags, and MIPS big-endian raw MMIO behavior.

## Test Signals

Compile coverage is an important signal because this header controls cross-file ABI. Runtime signals include successful register access on big-endian MIPS and little-endian platforms, correct descriptor programming on 32-bit and 40-bit DMA systems, stable ethtool stat ordering, RX/TX queue setup matching hardware params, and successful WOL/MDIO/HFB paths that depend on shared offsets and flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmgenet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmgenet_wol.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmgenet_wol.c

## Purpose

`bcmgenet_wol.c` implements Wake-on-LAN support for Broadcom GENET. It bridges ethtool WOL configuration, optional PHY WOL support, MAC Magic Packet Detection, secure magic password programming, ACPI/filter wake mode, wake IRQ enablement, and the power-down/power-up transitions used by `bcmgenet.c` suspend and resume paths.

## Important APIs and Functions

The public internal APIs are `bcmgenet_get_wol`, `bcmgenet_set_wol`, `bcmgenet_wol_power_down_cfg`, and `bcmgenet_wol_power_up_cfg`. `bcmgenet_get_wol` first asks the PHY for its WOL settings, then overlays MAC wake capabilities when the platform device is wake-capable: `WAKE_MAGIC`, `WAKE_MAGICSECURE`, and `WAKE_FILTER`. It reports PHY secure-password data when PHY WOL owns it, otherwise reports the MAC password from `priv->sopass`.

`bcmgenet_set_wol` tries `phy_ethtool_set_wol` first. If the PHY handles a nonzero WOL request, that result is returned. Otherwise it validates MAC-supported options, stores `WAKE_MAGICSECURE` password bytes, toggles `device_set_wakeup_enable`, and balances `enable_irq_wake`/`disable_irq_wake` for the dedicated WOL IRQ and `irq0` through `priv->wol_irq_disabled`.

Private helpers are `bcmgenet_poll_wol_status`, which waits up to roughly 50 ms for `RBUF_STATUS_WOL`, and `bcmgenet_set_mpd_password`, which writes the 6-byte secure-on password into the UniMAC MPD password registers.

## Control Flow

During suspend with MAC WOL enabled, `bcmgenet_wol_power_down_cfg` only accepts `GENET_POWER_WOL_MAGIC`. It enables MPD when magic packet options are set, programs the secure password when requested, enables HFB ACPI mode, waits for WOL-ready status, forces the PHY state to `PHY_READY` to suppress normal link updates, enables the WOL clock, enables CRC forwarding and RX in `UMAC_CMD`, clears software reset if necessary, and unmasks MPD/HFB wake interrupts.

During resume, `bcmgenet_wol_power_up_cfg` disables the WOL clock, clears the cached CRC-forward flag, masks wake interrupts, unmasks MDIO interrupts when supported, disables MPD and ACPI mode, clears CRC forwarding in UniMAC, and restores the PHY state to `PHY_RUNNING` or `PHY_NOLINK` based on current link. It returns `-EPERM` when it detects the MAC was already reset enough that MPD or ACPI bits are gone; the caller uses this as a signal to continue through a fuller reset path.

## State and Persistence Behavior

WOL state is stored in `struct bcmgenet_priv`: `wolopts`, `sopass`, `clk_wol`, `wol_irq`, `irq0`, `wol_irq_disabled`, and `crc_fwd_en`. The driver also changes device wakeup state in the platform device and wake state in IRQ core. Hardware state includes MPD control/password registers, HFB ACPI enable, RBUF WOL status, interrupt masks, and UniMAC RX/CRC-forward bits. There is no persistent storage; ethtool settings live in memory for the netdev/device lifetime.

## Dependencies and Integration Points

This file depends on phylib WOL operations, ethtool WOL flags, platform PM wake APIs, IRQ wake APIs, clocks, UniMAC registers from `unimac.h`, and shared GENET definitions from `bcmgenet.h`. `bcmgenet.c` calls the power transition functions from its suspend/resume noirq flow and exposes get/set WOL through ethtool ops. The code assumes `dev->phydev` is present during WOL power transitions and directly modifies PHY state under the PHY lock.

## Risks and Edge Cases

Wake IRQ balancing is delicate: `priv->wol_irq_disabled` prevents unbalanced wake enable/disable calls, but wrong initialization or partial request failure could leave wake state inconsistent. MAC and PHY WOL capabilities are merged, and PHY WOL takes precedence for supported nonzero options, so testing must cover mixed PHY/MAC support. The power-down path rolls back MPD and HFB ACPI bits if WOL-ready polling times out. CRC forwarding is deliberately enabled during WOL so received wake frames include FCS handling expectations; resume must clear it. The `-EPERM` resume cases are not generic permission failures; they signal that hardware was already reset and that the main driver should take the full reinitialization path.

## Test Signals

Useful signals include `ethtool -s wol g` and secure magic password programming, PHY-only WOL versus MAC WOL behavior, disabling WOL after enabling it and checking wake IRQ balance, suspend/resume with magic packet wake, WAKE_FILTER/HFB wake rules from `bcmgenet.c`, polling timeout behavior, and resume after firmware or hardware reset where MPD/ACPI bits are already cleared. Runtime diagnostics include "polling wol mode timeout" and invalid/unsupported mode errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmgenet_wol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmmii.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmmii.c

## Purpose

`bcmmii.c` implements GENET MDIO bus registration, PHY discovery/attachment, PHY interface selection, link-change programming, pause negotiation, internal PHY power sequencing, MoCA fixed-link handling, and MDIO interrupt waiting. It is the PHY-side companion to the main GENET netdev/DMA driver in `bcmgenet.c`.

## Important APIs and Functions

The internal APIs exported to the rest of the GENET driver are `bcmgenet_mii_init`, `bcmgenet_mii_exit`, `bcmgenet_mii_probe`, `bcmgenet_mii_config`, `bcmgenet_mii_setup`, `bcmgenet_phy_pause_set`, and `bcmgenet_phy_power_set`.

`bcmgenet_mac_config` programs UniMAC speed, duplex, pause-ignore bits, RGMII link state, and clears software reset when needed after a PHY reports link up. `bcmgenet_mii_setup` is the phylib adjust-link callback; it calls `bcmgenet_mac_config` on link up, clears `RGMII_LINK` on link down, syncs EEE through `bcmgenet_eee_enable_set`, and prints PHY status.

`bcmgenet_mii_config` chooses `SYS_PORT_CTRL` mode and RGMII out-of-band settings from `priv->phy_interface`, supporting internal PHY, MoCA, external MII, reverse MII, and RGMII variants. It also applies max-speed restrictions for MII/reverse MII and sets `priv->ext_phy`. `bcmgenet_mii_probe` attaches the netdev to a DT PHY, ACPI-discovered UniMAC MDIO PHY, or existing direct PHY, applies Broadcom PHY flags, handles legacy RGMII delay interpretation quirks, configures the port mux after PHY capabilities are known, assigns MAC interrupts for internal PHYs when valid, marks PHY PM as MAC-managed, and enables EEE support except on GENET v1.

`bcmgenet_mii_register` creates a child `mdio-bcm-unimac` platform device over the UniMAC MDIO command registers and passes `unimac_mdio_pdata`, including a wait callback. `bcmgenet_mii_wait` waits on `priv->wq` until `MDIO_START_BUSY` clears, using either MDIO interrupts or timeout. DT setup is handled by `bcmgenet_mii_of_init`, including fixed-link registration and MoCA link-down initialization.

## Control Flow

Probe-time initialization runs through `bcmgenet_mii_init`: register the UniMAC MDIO child device, then initialize bus/PHY interface metadata from OF or ACPI. Netdev open later calls `bcmgenet_mii_probe`, which attaches to the actual PHY and runs `bcmgenet_mii_config`. Link changes from phylib call `bcmgenet_mii_setup`, which updates MAC and RGMII state. Close/remove call `bcmgenet_mii_exit`, deregistering fixed links, dropping `phy_dn`, and unregistering the child MDIO platform device.

Internal PHY power sequencing is split from PHY attachment. `bcmgenet_phy_power_set` manipulates `EXT_GPHY_CTRL` for GENET v4 or 16 nm EPHY variants, with ordered clock, IDDQ, power-down, and reset delays. Main probe/open/suspend/resume code calls this through `bcmgenet_power_up`/`bcmgenet_power_down`.

## State and Persistence Behavior

This file populates and consumes `struct bcmgenet_priv` fields `phy_interface`, `internal_phy`, `ext_phy`, `phy_dn`, `mdio_dn`, `mii_bus`, `mii_pdev`, `gphy_rev`, `wq`, and pause flags indirectly. It modifies `dev->phydev` state and capabilities, including `dev_flags`, IRQ mode, `mac_managed_pm`, EEE support, advertising pause bits, and fixed-link update callbacks. State is device-lifetime memory and phylib state, not disk-persistent.

## Dependencies and Integration Points

Dependencies include phylib, fixed PHY support, OF/ACPI helpers, OF MDIO, Broadcom PHY flags, platform-device child registration, and `mdio-bcm-unimac` platform data. It relies on shared register definitions and accessors from `bcmgenet.h` and UniMAC command bits from `unimac.h`. Link setup integrates with `bcmgenet.c` netdev open/resume and ethtool pause/EEE paths.

## Risks and Edge Cases

The PHY interface matrix is hardware-sensitive. Wrong `phy-mode` values can program the wrong port mode or RGMII delay behavior. There is a documented legacy quirk that reverses RGMII/RGMII_TXID meanings for dedicated PHY drivers; changing that risks breaking existing device trees. Fixed-link MoCA uses a custom link update callback based on UniMAC mode bits. Internal PHY interrupt handling avoids GENET v5 10 Mbps link-up interrupt issues by falling back to polling. The child MDIO platform device must be unregistered on all init failure paths to avoid leaked devices or node references.

## Test Signals

Test signals include DT and ACPI probing, fixed-link registration/removal, all supported `phy-mode` values, internal PHY power on/off ordering, RGMII link up/down, pause autoneg/manual override through ethtool, EEE enable/disable, MDIO reads/writes with interrupt and timeout wait behavior, PHY attach failures, and suspend/resume around MAC-managed PHY PM. Logs to watch include invalid PHY mode, missing MDIO child, unable-to-find-PHY, and "configuring instance for ..." messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmmii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/sb1250-mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/sb1250-mac.c

## Purpose

`sb1250-mac.c` is a Linux platform driver for Broadcom SiByte SoC built-in Gigabit Ethernet MACs. It predates GENET and implements a standalone netdev driver with SiByte-specific MMIO registers, descriptor rings, bit-banged MDIO, PHY integration, NAPI receive polling, interrupt coalescing, multicast/perfect filters, and platform probe/remove.

## Important APIs, Types, and Functions

Important private types are `struct sbdmadscr` for 128-bit DMA descriptors, `struct sbmacdma` for one TX/RX DMA channel context, and `struct sbmac_softc` for the netdev-private MAC state. State enums model link speed (`sbmac_speed`), duplex (`sbmac_duplex`), flow control (`sbmac_fc`), and channel state (`sbmac_state`).

MDIO is implemented directly through `sbmac_mii_sync`, `sbmac_mii_senddata`, `sbmac_mii_read`, and `sbmac_mii_write`, registered as an `mii_bus`. DMA setup and servicing is handled by `sbdma_initctx`, `sbdma_channel_start`, `sbdma_channel_stop`, `sbdma_add_rcvbuffer`, `sbdma_add_txbuffer`, `sbdma_emptyring`, `sbdma_fillring`, `sbdma_rx_process`, and `sbdma_tx_process`. MAC configuration and lifecycle is handled by `sbmac_initctx`, `sbmac_channel_start`, `sbmac_channel_stop`, `sbmac_set_channel_state`, `sbmac_set_speed`, `sbmac_set_duplex`, `sbmac_promiscuous_mode`, `sbmac_set_iphdr_offset`, `sbmac_setmulti`, `sbmac_open`, `sbmac_close`, `sbmac_poll`, `sbmac_intr`, `sbmac_start_tx`, `sbmac_tx_timeout`, `sbmac_init`, `sbmac_probe`, and `sbmac_remove`.

The driver registers `sbmac_netdev_ops`, supports optional netpoll, exposes module parameters for debug level and coalescing packet/time thresholds, and binds through `module_platform_driver(sbmac_driver)`.

## Control Flow

Platform probe maps the MMIO resource, checks whether firmware left a nonzero Ethernet address in `R_MAC_ETHERNET_ADDR`, allocates an Ethernet device, stores the mapped base, and calls `sbmac_init`. Initialization reads and clears the firmware-provided hardware address, initializes register pointers and DMA contexts, configures netdev ops/NAPI/IRQ/MTU, detects hardware checksum support, creates/registers the MDIO bus, registers the netdev, and logs address/checksum details.

Open clears pending interrupt status, requests the MAC IRQ, resets cached link state, attaches the first PHY on the MDIO bus with GMII mode, starts the channel, starts the TX queue, programs RX mode, starts the PHY, and enables NAPI. Close disables NAPI, stops and disconnects the PHY, stops the channel, stops TX queueing, frees the IRQ, and empties TX/RX rings.

`sbmac_channel_start` clears filters/tables, programs MAC config/FIFO/frame registers, writes station address and perfect filter slot 0, starts RX and TX DMA channel registers, applies cached speed/duplex/flow control, fills the RX ring, enables DMA/MAC, enables coalesced or channel interrupts, accepts unicast/broadcast traffic, marks state on, programs multicast filters, and reapplies promiscuous mode if needed. `sbmac_channel_stop` disables filters/interrupts/MAC, stops both DMA channels, and frees queued SKBs.

TX is single-descriptor per SKB. `sbmac_start_tx` queues the SKB under `sbm_lock` with `sbdma_add_txbuffer`; if the ring is full it stops the queue and returns busy. Completion is processed by `sbdma_tx_process`, which compares software removal pointer with hardware current descriptor, frees completed SKBs, updates netdev stats, advances the removal pointer, and wakes the queue when packets completed. RX processing compares software and hardware descriptor indices, accounts FIFO drops, replaces each completed good receive buffer before passing the old SKB to the stack, handles hardware IPv4/TCP checksum status when supported, updates stats, and either uses `netif_receive_skb` under NAPI or `netif_rx` outside polling.

## State and Persistence Behavior

Device state is all in memory. `struct sbmac_softc` stores mapped register pointers, current speed/duplex/flow-control/link values, cached netdev flags, hardware address, PHY/MDIO handles, NAPI object, spinlock, DMA contexts, and checksum capability. Each DMA context owns aligned descriptor memory, a context table of SKBs, physical descriptor base, add/remove pointers, and coalescing settings. Firmware-provided MAC address is consumed from hardware during init; on init failure the probe path restores it. No persistent disk state exists.

## Dependencies and Integration Points

The driver is specific to SiByte MIPS SoCs and depends on architecture headers under `asm/sibyte`, raw 64-bit MMIO access, platform resources, phylib, MII bus registration, netdev/NAPI, and optional netpoll. It uses `UNIT_INT()` macros derived from SoC configuration to pick MAC IRQs and supports either BCM1x80 or SB1250/BCM112x register/interrupt definitions. PHY interrupts use `K_INT_PHY` if available, otherwise polling.

## Risks and Edge Cases

Descriptor memory is allocated with `kzalloc` and translated with `virt_to_phys`, not the generic DMA mapping API, which is tied to the target architecture's cache/DMA assumptions. RX buffers are carefully cache-line aligned because the MAC writes whole cache lines; changing allocation/alignment can corrupt adjacent memory. RX replacement failure re-adds the old SKB and stops processing, so sustained allocation pressure can stall RX. The multicast implementation uses only perfect filters and does not use the hash filter on overflow, so excess multicast addresses are silently not programmed unless all-multicast is enabled. The PHY link callback restarts the channel under lock when speed/duplex/flow control changes. `sbmac_probe` skips devices whose firmware MAC address register is zero, which is a platform contract.

## Test Signals

Useful validation includes boot/probe on supported SiByte SoCs, firmware MAC address detection and zero-address skip, MDIO read/write/PHY attach, link changes across 10/100/1000 and half/full duplex, flow-control negotiation, TX queue stop/wake under ring-full conditions, RX under allocation pressure, NAPI interrupt masking/re-enable, coalescing module parameters, multicast/all-multicast/promiscuous modes, hardware checksum enable on pass2+ hardware, netpoll when configured, and clean remove after register_netdev failure paths. Runtime counters to watch include `rx_fifo_errors`, `rx_dropped`, `rx_errors`, `tx_errors`, and TX timeout warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/sb1250-mac.c -->
