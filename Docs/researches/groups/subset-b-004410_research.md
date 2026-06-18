# subset-b-004410 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/dm9000.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/dm9000.c

## Purpose
Implements the platform/MMIO Davicom DM9000 Fast Ethernet driver. It binds a two-window address/data register device, selects 8/16/32-bit FIFO accessors, probes chip revision and platform data, registers a `net_device`, and provides TX, RX, interrupt, PHY/MII, EEPROM, WoL, checksum, suspend/resume, regulator, reset-GPIO, and device-tree support for DM9000E/A/B variants.

## Important APIs, Types, and Functions
The core state is `struct board_info`, which stores MMIO windows, IRQs, chip type, access callbacks, locking, MII state, delayed PHY polling, WoL state, checksum state, and power supply. Hardware access starts with `ior`, `iow`, `dm9000_reset`, `dm9000_set_io`, and the block I/O helpers. Network entry points are collected in `dm9000_netdev_ops`: `dm9000_open`, `dm9000_stop`, `dm9000_start_xmit`, `dm9000_timeout`, `dm9000_hash_table`, `dm9000_ioctl`, and `dm9000_set_features`. Other significant paths include `dm9000_probe`, `dm9000_init_dm9000`, `dm9000_interrupt`, `dm9000_rx`, `dm9000_tx_done`, EEPROM helpers, PHY helpers, ethtool ops, `dm9000_wol_interrupt`, and PM callbacks.

## Control Flow and State
Probe enables an optional regulator, toggles optional reset GPIO, reads platform data or OF properties, allocates `net_device`, maps separate address/data resources, selects FIFO width, resets the chip, validates the Davicom ID after retrying reads, classifies the chip revision, configures netdev/MII/ethtool operations, reads a MAC address from EEPROM/platform/chip/random fallback, and registers the interface. Open powers the PHY, initializes the MAC, requests the shared IRQ, unmasks device interrupts, starts the queue, and schedules link polling. TX writes packet bytes to the TX SRAM through `DM9000_MWCMD`, supports one in-flight packet and one queued packet, programs checksum mode and length, and starts transmission. IRQ handling masks interrupts, saves/restores the DM9000 address register, clears ISR bits, drains RX packets, completes TX, schedules link work on newer chips, and unmasks interrupts. RX repeatedly tests `DM9000_MRCMDX`, reads `struct dm9000_rxhdr`, validates length/status, allocates an SKB or dumps data, strips CRC, updates stats, and hands packets to `netif_rx`.

## State and Persistence Behavior
Persistent device state is in DM9000 registers, EEPROM, PHY registers, multicast hash registers, WoL registers, and platform power/reset wiring. Software state in `board_info` tracks pending TX count/length/checksum mode, selected chip type, interrupt mask, delayed link polling, wake configuration, and locks. `addr_lock` serializes sleeping EEPROM/PHY operations, while `lock` protects the shared address register and critical MMIO accesses. Suspend uses `in_suspend` to force busy waits, detaches the netdev, and shuts down hardware unless WoL is armed; resume reinitializes and unmasks only when the interface is running and not in wake mode.

## Dependencies and Integration Points
Depends on Linux netdevice, ethtool, MII, platform driver, OF MAC parsing, IRQ, GPIO descriptor, regulator, CRC multicast hash, netpoll, and `linux/dm9000.h` platform data flags/callbacks. The local header supplies register constants. Integration is through `module_platform_driver`, OF compatible `davicom,dm9000`, platform memory resources 0/1 for address/data windows, IRQ 0 for normal interrupts, optional IRQ 1 for wake, and optional platform callbacks overriding block I/O operations.

## Risks and Test Signals
Risks include losing the selected address register without correct locking/save-restore, wrong FIFO width selection, EEPROM wait fallback masking real failures, TX two-packet queue accounting errors, RX packet-ready status corruption causing RX disable, checksum offload assumptions on DM9000A/B, wake IRQ state imbalance, and regulator/resource cleanup mistakes on probe failure. The chip-MAC fallback reads PAR bytes into `addr` but calls `eth_hw_addr_set(ndev, pdata->dev_addr)`, so invalid or absent platform data can defeat that fallback path. Test signals include probe/remove with regulator/reset GPIO combinations, EEPROM/no-EEPROM MAC selection, open/close, TX timeout recovery, RX error counters, multicast/promiscuous hash programming, ethtool EEPROM and link settings, netpoll, suspend/resume with and without WoL, and interrupt storms/link-change events on DM9000E versus A/B.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/dm9000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/dm9000.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/dm9000.h

## Purpose
Defines the DM9000 hardware register map, chip IDs, revision IDs, command ports, bit masks, packet constants, and Davicom-specific MII constants consumed by `dm9000.c`.

## Important APIs, Types, and Functions
This header exports macros for MAC registers (`DM9000_NCR`, `DM9000_RCR`, `DM9000_PAR`, `DM9000_MAR`, `DM9000_ISR`, `DM9000_IMR`), FIFO commands (`DM9000_MRCMDX`, `DM9000_MRCMD`, `DM9000_MWCMD`), EEPROM/PHY command bits (`EPCR_*`), RX/TX status bits (`RSR_*`, `TSR_*`, `NSR_*`), WoL bits (`WCR_*`), checksum bits (`TCCR_*`, `RCSR_*`), interrupt masks, packet-ready/error constants, and DM9000A/B revision values.

## Control Flow and State
There is no runtime control flow. The file is a declarative hardware ABI. It describes persistent state living in DM9000 registers: MAC control, PHY/EEPROM command state, multicast filter RAM, packet FIFO ports, interrupt status/mask, checksum control, wakeup status, and packet size limits.

## Dependencies and Integration Points
`dm9000.c` includes this file for all register and bitfield names. The values also tie into platform data from `linux/dm9000.h`, MII register handling, ethtool EEPROM access, RX/TX FIFO operations, interrupt clearing, and WoL programming.

## Risks and Test Signals
Any wrong register offset or bit mask directly changes hardware behavior and can silently break RX/TX, interrupt acknowledgement, checksum offload, EEPROM writes, or WoL. Test signals are compile coverage, successful chip ID/revision reads, register dumps compared with datasheet expectations, multicast/WoL/checksum functional tests, and RX/TX operation across 8/16/32-bit host bus widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/dm9000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/dm9051.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/dm9051.c

## Purpose
Implements the Davicom DM9051 SPI Fast Ethernet driver. It uses SPI regmap access to control MAC registers and packet FIFOs, exposes an MDIO bus for the internal PHY, connects PHYLIB, registers a netdev, handles RX in a threaded IRQ, handles TX through a bounded SKB queue and work item, and exposes ethtool EEPROM, pause, link, and message-level operations.

## Important APIs, Types, and Functions
Important state types are `struct board_info`, `struct dm9051_rxhdr`, `struct dm9051_rxctrl`, and `struct rx_ctl_mach`. Low-level helpers include `dm9051_set_reg`, `dm9051_update_bits`, `dm9051_set_regs`, `dm9051_get_regs`, `dm9051_write_mem`, `dm9051_read_mem`, `dm9051_nsr_poll`, and `dm9051_epcr_poll`. Device setup flows through `dm9051_map_init`, `dm9051_map_chipid`, `dm9051_map_etherdev_par`, `dm9051_mdio_register`, `dm9051_phy_connect`, and `dm9051_probe`. Runtime entry points are `dm9051_open`, `dm9051_stop`, `dm9051_start_xmit`, `dm9051_set_rx_mode`, `dm9051_set_mac_address`, `dm9051_rx_threaded_irq`, `dm9051_loop_rx`, `dm9051_loop_tx`, and `dm9051_handle_link_change`.

## Control Flow and State
Probe allocates a managed Ethernet device, initializes two regmaps over the SPI device, reads and validates the chip ID, loads the MAC address from `DM9051_PAR` or generates/programs a random address, registers a private MDIO bus, connects the fixed internal PHY at address 1, initializes statistics and TX queue state, and registers the netdev. Open initializes interrupt masks, LED mode, receive control, requests an oneshot threaded IRQ using the DT/SPI IRQ trigger, starts PHYLIB, initializes pause settings, resets/powers the MAC and PHY, and wakes the queue. TX enqueue appends SKBs to `db->txq`, stops the queue at a high-water mark, and schedules `tx_work`; the TX worker serializes SPI access, polls TX completion, writes packet data through `DM_SPI_MWCMD`, programs length registers, and asserts `TCR_TXREQ`. The threaded IRQ disables and clears interrupts, repeatedly drains RX packets and opportunistically transmits queued SKBs, then re-enables interrupts.

## State and Persistence Behavior
Persistent hardware state includes MAC/PHY registers, packet FIFO pointers, EEPROM, hash table, pause/flow-control bits, LED mode, and interrupt polarity/mask. Software state records regmaps, SPI/register mutexes, PHYLIB device, TX queue, cached RX filter, pause settings, counters for RX/TX/fifo-reset errors, and current interrupt/LED settings. `spi_lockm` serializes threaded IRQ, TX work, and RX-control work across SPI transfers; regmap callbacks use `reg_mutex`. RX errors or oversized packets trigger `dm9051_all_restart`, which resets the core, re-enables interrupts, reapplies RX filter, and restores flow control.

## Dependencies and Integration Points
Depends on SPI, regmap, netdevice, ethtool, PHYLIB, MDIO bus, IRQ trigger metadata, CRC multicast hashing, SKB queues, workqueues, and the local register header. It binds via `module_spi_driver`, OF compatible `davicom,dm9051`, and SPI ID `dm9051`. PHY integration uses an internal MDIO bus named from the SPI device and `phy_connect` with `PHY_INTERFACE_MODE_MII`; ethtool link settings delegate to PHYLIB.

## Risks and Test Signals
Risks include regmap locking mistakes between normal and bulk/no-increment accesses, TX queue overflow or lost wakeups around high/low watermarks, IRQ exits that skip interrupt re-enable after error paths, RX FIFO pointer desynchronization, allocation failure paths that dump but must preserve FIFO state, EEPROM/PHY EPCR timeout handling, and pause autoneg updates racing with link changes. Test signals include SPI probe at different IRQ polarities, chip ID and MAC reads, open/stop with pending work, RX drain under burst and allocation failure, TX under queue pressure, link changes and pause negotiation, ethtool EEPROM read/write, multicast/promiscuous changes, and injected regmap timeout/error returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/dm9051.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/dm9051.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/dm9051.h

## Purpose
Defines DM9051 register offsets, SPI command flags, bit masks, packet constants, FIFO thresholds, EEPROM magic, RX-header size, and the netdev-private accessor used by the SPI driver.

## Important APIs, Types, and Functions
The header defines `DM9051_ID`, MAC/PHY/EEPROM registers, SPI FIFO commands (`DM_SPI_MRCMDX`, `DM_SPI_MRCMD`, `DM_SPI_MWCMD`, `DM_SPI_WR`), network control/status bits (`NCR_*`, `NSR_*`, `TCR_*`, `RCR_*`, `RSR_*`), flow-control bits, EPCR bits, GPIO/PHY power bits, interrupt bits, queue watermarks, maximum packet size, and `to_dm9051_board(struct net_device *)`.

## Control Flow and State
Runtime logic is limited to the inline `to_dm9051_board` cast. The rest is declarative state layout for DM9051 hardware registers, packet FIFO commands, interrupt status, PHY access, EEPROM command state, receive filtering, flow control, and queue sizing used by the C file.

## Dependencies and Integration Points
Includes Linux `bits.h`, `netdevice.h`, and `types.h` for bit macros and the `net_device` type. It is consumed by `dm9051.c` for regmap register accesses, MDIO transactions, RX/TX FIFO operations, IRQ handling, ethtool EEPROM operations, and netdev-private state lookup.

## Risks and Test Signals
Risks are hardware-ABI drift: incorrect offsets, masks, or FIFO command values can break SPI transactions, packet reads/writes, interrupt clearing, or PHY/EEPROM operations. Test signals are compile coverage, successful SPI chip ID read, RX/TX through FIFO commands, interrupt clear/mask behavior, pause and multicast register programming, and EEPROM/MDIO access using the defined EPCR/EPAR/EPDR fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/davicom/dm9051.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/Kconfig

## Purpose
Provides the top-level Kconfig gate for Digital Equipment Corporation Ethernet drivers and includes the Tulip-family Kconfig when the vendor group is enabled.

## Important APIs, Types, and Functions
Defines `NET_VENDOR_DEC` as a boolean vendor menu option, defaults it to `y`, constrains it to PCI/EISA/CardBus-capable builds, and sources `drivers/net/ethernet/dec/tulip/Kconfig` inside `if NET_VENDOR_DEC`.

## Control Flow and State
There is no runtime flow. Build-time state is whether DEC vendor questions are visible. Disabling this option hides subordinate DEC/Tulip driver choices without directly compiling code itself.

## Dependencies and Integration Points
Integrated into the kernel networking Kconfig tree. It depends on bus families that can host DEC Ethernet devices and delegates all actual driver symbols to the tulip subdirectory Kconfig.

## Risks and Test Signals
Risks are build visibility regressions: too-strict dependencies can hide drivers, while too-loose defaults expose irrelevant menus. Test signals are `menuconfig` visibility for PCI/EISA/CardBus targets, absence on unsupported bus configs, and correct inclusion of Tulip-family symbols when `NET_VENDOR_DEC=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/Makefile

## Purpose
Routes DEC Ethernet build output into the Tulip-family subdirectory when the Tulip vendor family is enabled.

## Important APIs, Types, and Functions
Contains one build rule: `obj-$(CONFIG_NET_TULIP) += tulip/`.

## Control Flow and State
No runtime flow. Build-time state is controlled by `CONFIG_NET_TULIP`; enabling it descends into `drivers/net/ethernet/dec/tulip/`.

## Dependencies and Integration Points
Integrated with Kbuild. It expects the child `tulip/Makefile` to select individual object files for DE2104X, Tulip, DMFE, Winbond, ULi, and Xircom drivers.

## Risks and Test Signals
Risks are limited to build routing: a wrong symbol or path prevents all DEC Tulip-family drivers from compiling. Test signals are allmodconfig/allyesconfig object generation and that disabling `NET_TULIP` skips the subdirectory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/21142.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/21142.c

## Purpose
Implements DC21142/DC21143-specific media selection, NWay autonegotiation startup, media polling, and link-change handling for the shared Tulip driver.

## Important APIs, Types, and Functions
Exports `t21142_media_task`, `t21142_start_nway`, and `t21142_lnk_change`. It uses static CSR programming tables `t21142_csr13`, exported `t21142_csr14`, and `t21142_csr15`, plus shared Tulip state such as `struct tulip_private`, `tp->csr6`, `tp->nway`, `tp->nwayset`, `tp->mediasense`, `tp->lpar`, `tp->mtable`, and `dev->if_port`.

## Control Flow and State
The media work item reads CSR12/CSR14, normalizes unreliable link bits during autonegotiation, checks MII duplex when in MII mode, respects locked or already negotiated media, and otherwise alternates between 10 Mbps and 100 Mbps tests before restarting RX/TX and rearming the timer. `t21142_start_nway` programs CSR13/14/15, sets advertised capabilities into CSR14, updates `csr6`, and triggers NWay through CSR12. `t21142_lnk_change` handles link interrupts: it records partner abilities, picks the negotiated media/duplex, selects a matching media-table leaf when available, starts RX/TX, or restarts NWay when link fails.

## State and Persistence Behavior
Persistent hardware state is written into Tulip CSRs 6, 12, 13, 14, and 15. Software state persists in `tulip_private` media flags, selected media index, cached link partner advertisement, full-duplex flag, and the media timer. Timer deletion/re-addition is used around NWay restart paths to avoid stale media polling.

## Dependencies and Integration Points
Depends on `tulip.h` definitions, shared Tulip media names/capability tables, `tulip_check_duplex`, `tulip_select_media`, `tulip_start_rxtx`, and `tulip_restart_rxtx`. It is compiled into the multipart `tulip.o` driver and called from timer/work setup and interrupt link-change handling.

## Risks and Test Signals
Risks include incorrect interpretation of CSR12 while NWay is active, timer races around `timer_delete_sync`, bad CSR6 bit preservation during media switch, stale `dev->if_port`, and link flapping when media-table leaves are missing or wrong. Test signals include 10/100 half/full negotiation, forced media locks, MII versus non-MII cards, link-fail/pass interrupt handling, timer-driven fallback between media types, and register traces showing expected CSR13/14/15 sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/21142.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/Kconfig

## Purpose
Defines build-time configuration for the DEC Tulip family and related PCI/CardBus Ethernet drivers.

## Important APIs, Types, and Functions
Defines the group gate `NET_TULIP`, individual driver symbols `DE2104X`, `TULIP`, `WINBOND_840`, `DM9102`, `ULI526X`, and `PCMCIA_XIRCOM`, plus tuning symbols `DE2104X_DSL`, `TULIP_MWI`, `TULIP_MMIO`, `TULIP_NAPI`, `TULIP_NAPI_HW_MITIGATION`, and SPARC helper `TULIP_DM910X`. Driver options select needed library symbols such as `CRC32` and `MII`.

## Control Flow and State
There is no runtime flow. Build-time control chooses which drivers compile, whether the main Tulip driver uses MMIO, NAPI, hardware interrupt mitigation, memory-write-invalidate configuration, and descriptor skip length for early DE2104X hardware.

## Dependencies and Integration Points
Consumed by Kbuild and the parent DEC vendor Kconfig. Symbols are referenced by `dec/tulip/Makefile` and by driver source conditionals such as `CONFIG_TULIP_NAPI`, `CONFIG_TULIP_NAPI_HW_MITIGATION`, `CONFIG_DE2104X_DSL`, and `CONFIG_TULIP_DM910X`.

## Risks and Test Signals
Risks include wrong bus dependencies, missing `select CRC32/MII`, invalid descriptor skip ranges, or enabling experimental Tulip options on unsupported builds. Test signals are `oldconfig` prompts, allyesconfig/allmodconfig builds, NAPI and non-NAPI compile coverage, SPARC DM910X symbol behavior, and successful module names matching help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/Makefile

## Purpose
Builds Tulip-family Ethernet driver modules and declares the multipart object composition for the main `tulip` driver.

## Important APIs, Types, and Functions
Sets `ccflags-$(CONFIG_NET_TULIP) := -DDEBUG`, maps config symbols to objects (`xircom_cb.o`, `dmfe.o`, `winbond-840.o`, `de2104x.o`, `tulip.o`, `uli526x.o`), and defines `tulip-objs` as `eeprom.o interrupt.o media.o timer.o tulip_core.o 21142.o pnic.o pnic2.o`.

## Control Flow and State
No runtime flow. Build-time state determines which modules are produced and which translation units are linked into `tulip.o`.

## Dependencies and Integration Points
Integrated with the child Kconfig symbols. The multipart `tulip.o` links the source files that share `tulip.h` and the common `struct tulip_private` runtime state, while standalone drivers such as `dmfe.o` and `de2104x.o` build separately.

## Risks and Test Signals
Risks include omitting a required object from `tulip-objs`, compiling stale DEBUG flags unexpectedly, or mapping a config symbol to the wrong module. Test signals are successful modular and built-in builds for every symbol, symbol resolution across `tulip-objs`, and expected module file names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/de2104x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/de2104x.c

## Purpose
Implements a standalone PCI Ethernet driver for early Intel/Digital 21040/21041 Tulip chips. It handles PCI probing, MMIO CSR access, DMA descriptor rings, RX/TX completion, setup-frame multicast filtering, media/SIA programming, ethtool register/EEPROM/link settings, timeout recovery, power management, and shutdown.

## Important APIs, Types, and Functions
Central state is `struct de_private`, containing descriptor rings, SKB metadata, MMIO base, PCI device, media tables, EEPROM data, lock, and timer. Hardware structures include `struct de_desc`, `struct ring_info`, `struct media_info`, and SROM parsing structs. Key runtime functions include `de_init_one`, `de_open`, `de_close`, `de_start_xmit`, `de_interrupt`, `de_rx`, `de_tx`, `de_set_rx_mode`, `de_init_hw`, `de_reset_mac`, `de_tx_timeout`, `de21040_media_timer`, `de21041_media_timer`, `de_media_interrupt`, `de21040_get_mac_address`, `de21041_get_srom_info`, and ethtool helpers.

## Control Flow and State
Probe enables PCI, claims MMIO BAR 1, maps CSRs, wakes and resets the adapter, reads the MAC/media description from 21040 ROM or 21041 SROM, registers the netdev, sets bus mastering, and puts the adapter back to sleep until open. Open allocates coherent RX/TX descriptor memory, fills RX buffers, requests IRQ, initializes hardware rings/CSRs/media/filtering, starts the queue, and arms the media timer. TX maps an SKB into the TX ring, sets first/last/ring-end/software-interrupt flags, advances `tx_head`, possibly stops the queue, and polls transmit demand. IRQ acks status, drains RX, cleans TX completions under lock, handles media link interrupts, and logs PCI errors. RX either copies small packets or hands up the ring SKB, then installs a replacement buffer and returns descriptor ownership. Timeout stops hardware, updates stats, cleans and reinitializes rings/hardware, and wakes the queue.

## State and Persistence Behavior
Persistent hardware state lives in PCI config power-management bits, CSR bus mode, CSR6/MacMode, SIA CSR13-15 media settings, descriptor base registers, interrupt mask/status, setup-frame filter contents, and self-clearing missed-frame counter. Software state persists ring indices (`tx_head`, `tx_tail`, `rx_tail`), DMA mappings, media support/advertisement/current lock state, copied SROM, timer state, and carrier status. PM suspend detaches the device, stops hardware, cleans rings, and sleeps the adapter; resume reinitializes rings and hardware if needed.

## Dependencies and Integration Points
Depends on PCI, MMIO, DMA mapping/coherent allocation, netdevice, ethtool, CRC32 multicast hashing, timers, RTNL during PM, and legacy link-mode conversion helpers. Binds PCI IDs for DEC Tulip and Tulip Plus through `module_pci_driver`. Kconfig `DE2104X_DSL` changes descriptor layout and bus mode descriptor-skip bits.

## Risks and Test Signals
Risks include DMA mapping failure not being checked consistently, descriptor ownership/order barrier mistakes, setup-frame errata handling with dummy TX descriptors, timer/media transitions racing with IRQ and ethtool changes, stale missed-frame counter reads, timeout recovery not fully resetting PCI error state, and SROM fallback media tables being too permissive. Test signals include probe/open/close on 21040 and 21041, RX copybreak and zero-copy paths, TX ring full/wakeup behavior, multicast/promiscuous setup-frame programming, media timer fallback between TP/AUI/BNC, ethtool forced link settings, TX timeout recovery, suspend/resume, and PCI error interrupt logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/de2104x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/dmfe.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/dmfe.c

## Purpose
Implements the Davicom DM9102/DM9132/DM980x PCI Fast Ethernet driver. It manages PCI I/O BAR resources, descriptor and TX buffer pools, chained RX/TX descriptors, SROM and MII bit-banged access, media/autonegotiation, HomePNA programming, multicast filters, interrupt handling, dynamic reset, ethtool WoL reporting, suspend/resume, and legacy module-parameter tuning.

## Important APIs, Types, and Functions
Primary state is `struct dmfe_board_info`, which contains PCI/MMIO data, CR register shadows, descriptor pools and pointers, TX/RX counters, media/PHY/HPNA state, timer, statistics, WoL mode, and SROM data. Hardware descriptors are `struct tx_desc` and `struct rx_desc`. Key entry points are `dmfe_init_one`, `dmfe_open`, `dmfe_stop`, `dmfe_start_xmit`, `dmfe_interrupt`, `dmfe_timer`, `dmfe_dynamic_reset`, `dmfe_init_dm910x`, `dmfe_descriptor_init`, `allocate_rx_buffer`, `dmfe_rx_packet`, `dmfe_free_tx_pkt`, `dmfe_set_filter_mode`, `send_filter_frame`, `dm9132_id_table`, SROM/MII helpers, HPNA programming helpers, PM callbacks, and module init/exit.

## Control Flow and State
Module init normalizes module parameters and registers the PCI driver. Probe optionally skips SPARC onboard DM910x devices handled by the generic Tulip driver, allocates a netdev, enforces 32-bit DMA, enables PCI, claims I/O BAR 0, allocates coherent descriptor and TX buffer pools, maps I/O registers, reads SROM words, uses SROM offset 20 for the MAC, registers the netdev, and enables bus mastering. Open requests a shared IRQ, initializes CR shadows and counters, chooses normal or RX CRC-check mode, calls `dmfe_init_dm910x`, wakes the queue, and starts a periodic timer. TX copies SKB data into a preallocated TX buffer, fills a TX descriptor, either hands it to hardware or queues it, polls TX demand, and frees the SKB. IRQ acks CR5, disables CR7, flags fatal bus errors for timer reset, drains RX, refills RX descriptors, completes TX, performs delayed mode-check transition, and restores CR7. The timer handles first-callback chip quirks, RX idle reset detection, TX kick/timeout, dynamic reset, carrier/media sensing via chip and PHY status, and HPNA remote command checks.

## State and Persistence Behavior
Persistent hardware state is maintained in CR0/CR5/CR6/CR7/CR15, descriptor base registers, SROM contents, PHY registers, HPNA PHY registers, multicast filter tables or setup frames, and optional WoL mode. Software state tracks descriptor insertion/removal/ready pointers, queued and active TX counts, RX availability, interval RX count, operation mode, PHY capability, reset causes, and module-wide defaults. Dynamic reset stops TX/RX, disables interrupts, frees RX buffers, resets counters and carrier, reinitializes the chip, and wakes the queue.

## Dependencies and Integration Points
Depends on PCI, I/O-port mapping, coherent DMA, netdevice, ethtool, timers, CRC32, spinlocks, optional netpoll, and optional OF detection on SPARC. It binds vendor/device IDs for DM9132, DM9102, DM9100, and DM9009. Kconfig `DM9102` selects this standalone module, while `TULIP_DM910X` affects SPARC onboard handling.

## Risks and Test Signals
Risks include legacy fixed-size packet and descriptor assumptions, copying TX data into coherent buffers instead of mapping SKBs, missing DMA mapping error checks for RX reuse/allocation, dynamic reset while IRQ/timer paths share state, multicast allmulti path changing CR6 without immediately writing hardware in one branch, endian-sensitive CRC comparison in RX check mode, HPNA side effects from module parameters, and suspend/resume behavior not gated by `netif_running`. Test signals include PCI probe/remove for all IDs/revisions, SROM MAC reads, open/stop cycles, RX allocation failure and CRC-check mode, TX queue full/wakeup and timeout reset, link up/down media changes, forced modes and HomePNA modes, multicast/promiscuous filtering, netpoll, suspend/resume, and bus-error interrupt reset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/dmfe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/eeprom.c

## Purpose
Provides EEPROM/SROM support for the shared Tulip driver: reading serial EEPROM words, detecting/fixing old SROM layouts, building media tables, carrying multiport board media data forward, and optionally synthesizing media-table data for HPPA/GSC cards.

## Important APIs, Types, and Functions
Exports `tulip_parse_eeprom` and `tulip_read_eeprom`. Internal data includes `eeprom_fixups`, `block_name`, and `tulip_build_fake_mediatable`. It constructs `struct mediatable` and `struct medialeaf` instances stored in `tp->mtable`, fills flags such as `has_mii`, `has_nonmii`, `has_reset`, and may update `tp->sym_advertise`, `tp->csr12_shadow`, and CSR15 defaults.

## Control Flow and State
Parsing starts by detecting old-style EEPROMs where early bytes mirror station-address data. Missing EEPROMs can reuse the previous multiport board mediatable; known OUI/layout fixups patch substitute media-control data into EEPROM bytes. New-style tables are found through offset byte 27, then the code reads default media, optional CSR12 direction, leaf count, and each media block. Compact 21140 blocks and extended blocks are decoded differently, with special handling for reset blocks, MII blocks, Davicom delay blocks, Davicom media numbering, and custom CSR15 values. `tulip_read_eeprom` bit-bangs CSR9 with chip select, clock, command/address bits, and 16 data reads, returning swapped data for boards flagged with swapped SEEPROM.

## State and Persistence Behavior
The EEPROM is persistent board firmware data. Runtime persistence is the allocated media table under devres, cached previous mediatable/static EEPROM pointer for multiport boards, selected advertisement mask, and optional fake mediatable state for GSC hardware. The parser mutates the in-memory EEPROM copy when applying fixups but does not write EEPROM.

## Dependencies and Integration Points
Depends on `tulip.h`, PCI device devres allocation, unaligned access helpers, Tulip flags, media names, and CSR9 register semantics. The main Tulip probe path reads EEPROM bytes and calls this parser so media selection, timer, and link-change code have `tp->mtable` and advertisement state.

## Risks and Test Signals
Risks include malformed SROM lengths advancing beyond available data, static multiport state being reused incorrectly, old-board fixups matching the wrong OUI variant, Davicom block skipping changing leaf counts unexpectedly, and bit-banged EEPROM timing/address-size errors. Test signals include old-style EEPROM boards, missing EEPROM behavior, multiport cards, GSC fake media table, MII and non-MII media leaves, swapped EEPROM flag, and media selection logs matching expected table leaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/interrupt.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/interrupt.c

## Purpose
Implements RX buffer refill, optional NAPI polling, non-NAPI RX processing, PHY interrupt acknowledgement for HPPA, and the main interrupt handler for the shared Tulip driver.

## Important APIs, Types, and Functions
Exports `tulip_rx_copybreak`, `tulip_max_interrupt_work`, `tulip_refill_rx`, optional `oom_timer` and `tulip_poll`, and `tulip_interrupt`. Internal helpers include non-NAPI `tulip_rx`, `phy_interrupt`, and the optional interrupt mitigation table. The code operates on `struct tulip_private` descriptor rings, `rx_buffers`, `tx_buffers`, CSR registers, NAPI state, timers, interrupt masks, and netdev stats.

## Control Flow and State
`tulip_refill_rx` allocates SKBs, maps them for DMA, writes RX descriptor buffer addresses, and returns ownership to hardware; LC82C168 RX-stopped state is explicitly restarted. NAPI mode masks RX interrupts in `tulip_interrupt`, schedules `tulip_poll`, drains descriptors up to budget, acks RX events, copies small packets or passes up ring SKBs, refills, toggles hardware interrupt mitigation, and handles out-of-memory by arming `oom_timer` without re-enabling RX interrupts. Non-NAPI mode performs similar descriptor processing directly in interrupt context. The main interrupt handler acks status, handles RX/NAPI scheduling, cleans completed TX descriptors, frees SKBs and DMA mappings, wakes the queue, restarts TX/RX on selected errors, calls link-change callbacks, handles system errors, masks excessive work, and accounts missed RX frames from CSR8.

## State and Persistence Behavior
Persistent hardware state includes Tulip CSR5 interrupt status, CSR7 mask, CSR8 missed counter, CSR11 timer/mitigation control, descriptor ownership bits, and chip-specific CSR12 PHY status. Software state includes ring cursors (`cur_rx`, `dirty_rx`, `cur_tx`, `dirty_tx`), DMA mappings, NAPI poll state, `mit_on`, out-of-memory timer, interrupt count, timeout timer state, and carrier/link-change callbacks. Descriptor ownership and DMA sync/unmap calls are the central persistence boundary between CPU and device.

## Dependencies and Integration Points
Depends on `tulip.h`, PCI DMA mapping, netdevice/SKB APIs, optional `CONFIG_TULIP_NAPI`, optional `CONFIG_TULIP_NAPI_HW_MITIGATION`, optional HPPA PHY IRQ handling, timer APIs, and the chip table `tulip_tbl`. It is linked into `tulip.o` and is invoked by the main Tulip open path as the IRQ and NAPI handler.

## Risks and Test Signals
Risks include descriptor ownership races, lost RX events around NAPI ack/mask sequencing, DMA sync/unmap mistakes between copy and pass-up paths, out-of-memory polling deadlocks, interrupt mitigation latency tradeoffs, too-much-work masking that hides events, link-change callbacks that delete timers, and recovery from `0xffffffff` hardware disappearance. Test signals include NAPI and non-NAPI builds, high-rate RX, RX allocation failure, TX completion/error counters, queue wake on TX cleanup, LC82C168 RX no-buffer restart, link pass/fail interrupts, system-error logging, netpoll/IRQ sharing behavior, and missed-frame counter accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/interrupt.c -->
