# Research: subset-b-004411

Work item `subset-b-004411` covers Tulip-family Ethernet media, timer, core, and sibling PCI drivers plus D-Link Kbuild metadata. Each section preserves the source path and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/media.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/media.c

Purpose: Implements shared Tulip MII/MDIO access, transceiver selection, duplex negotiation, and PHY discovery for the DEC 21x4x Tulip core and compatible chips.

Important APIs and functions: `tulip_mdio_read()` and `tulip_mdio_write()` bit-bang IEEE 802.3 MDIO over CSR9, with special paths for COMET internal registers and LC82C168 register 0xA0. `tulip_select_media()` interprets parsed EEPROM media-table leaves and programs CSR12 through CSR15 plus `tp->csr6`. `tulip_check_duplex()` reads `MII_BMSR` and `MII_LPA`, derives negotiated duplex with `mii_duplex()`, updates `FullDuplex` and `TxThreshold`, and restarts RX/TX when CSR6 changes. `tulip_find_mii()` probes PHY addresses, builds `tp->phys[]`, initializes advertising, and adjusts BMCR for autonegotiation or forced media.

Control flow: Open/probe paths call `tulip_select_media()` after EEPROM parsing and may call `tulip_find_mii()` during PCI probe. Media timers and link-change handlers later call `tulip_check_duplex()` to keep CSR6 synchronized with link partner capabilities. MDIO operations serialize through `tp->mii_lock`; CSR6 state changes rely on the core helper `tulip_restart_rxtx()`.

State and persistence: Persistent device state is in `struct tulip_private`: `phys[]`, `mii_cnt`, `advertising[]`, `mii_advertise`, `full_duplex`, `full_duplex_lock`, `cur_index`, `mtable`, `csr6`, and `dev->if_port`. The source does not write persistent storage; EEPROM media tables are consumed from memory built by `eeprom.c`.

Dependencies and integration: Depends on Linux MII constants, PCI MMIO helpers, `tulip.h` media capability arrays, `t21142_csr14[]`, and `medianame[]`. It integrates with `tulip_core.c` for startup, `timer.c` for media monitoring, and PNIC/PNIC2 link code for duplex checks.

Risks: MDIO bit-banging is timing-sensitive and chip-specific. Media leaf parsing uses byte layouts from EEPROM and casts unaligned data, so malformed tables can select incorrect CSRs. Link status is sticky and double-read behavior is needed. Restarting RX/TX under the wrong lock could race with interrupts.

Test signals: Exercise PHY probing with MII and no-MII boards, forced media options, COMET and LC82C168 special MDIO paths, link partner duplex changes, missing PHY return `0xffff`, and EEPROM media leaves of types 0 through 6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/media.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/pnic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/pnic.c

Purpose: Provides media negotiation and link monitoring for Lite-On LC82C168 PNIC chips used by the shared Tulip driver.

Important APIs and functions: `pnic_do_nway()` interprets the PNIC PHY status register at 0xB8, chooses `dev->if_port`, updates `tp->nwayset`, duplex, CSR12, CSR6, and restarts RX/TX when the mode changes. `pnic_lnk_change()` handles `TPLnkFail` and `TPLnkPass` interrupts by toggling CSR7 masks, restarting internal autonegotiation, or delegating to `tulip_check_duplex()` for external MII. `pnic_timer()` is the periodic media timer used from `tulip_tbl`.

Control flow: `tulip_core.c` assigns `pnic_lnk_change` for `HAS_PNICNWAY` and uses `pnic_timer` as the chip media timer. Link interrupts call `pnic_lnk_change()`. Timer ticks check whether interrupt masking has been temporarily cleared, then either validate MII duplex or inspect CSR12/CSR5/0xB8 for non-MII media fallback.

State and persistence: Uses `tp->csr6`, `tp->nwayset`, `tp->full_duplex`, `tp->medialock`, `dev->if_port`, `dev_trans_start()`, and `tp->timer`. No disk persistence. Hardware state is kept in CSR6, CSR7, CSR12, and PNIC register 0xB8.

Dependencies and integration: Depends on shared Tulip status bits, media capability flags, `tulip_restart_rxtx()`, `tulip_refill_rx()`, and `tulip_tbl[chip_id].valid_intrs`. It is tightly integrated with `interrupt.c`, which may leave CSR7 disabled on work overflow and rely on this timer path to refill RX and restore interrupts.

Risks: Link state transitions rely on raw magic constants and timing against `dev_trans_start()`. The timer disables and enables IRQ around RX refill when CSR7 is zero, which must remain consistent with interrupt handler assumptions. Internal PNIC autonegotiation must not run when external MII is selected.

Test signals: Validate 10/100 and half/full negotiation, remote fault recovery, medialock behavior, CSR7-zero overflow recovery, external MII duplex checking, and repeated link fail/pass interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/pnic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/pnic2.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/pnic2.c

Purpose: Implements PNIC-II autonegotiation, link-change handling, and timer support for Lite-On PNIC-II chips, whose CSR6/CSR12/CSR14 semantics differ from classic 21142/21143 Tulip parts.

Important APIs and functions: `pnic2_timer()` logs negotiation state and reschedules a long media tick. `pnic2_start_nway()` encodes `tp->sym_advertise` into CSR14 advertisement bits, puts CSR6 into NWAY mode, marks `tp->nway`/`tp->mediasense`, clears `tp->lpar`, and writes CSR12 bits 14:12 to start autonegotiation. `pnic2_lnk_change()` processes negotiation completion, maps negotiated partner abilities to `dev->if_port`, sets `tp->full_duplex`, programs CSR14/CSR6, restarts RX/TX, and restarts NWAY on link loss.

Control flow: `tulip_core.c` initializes PNIC2 with all 10/100 half/full capabilities, enables autonegotiation interrupts, calls `pnic2_start_nway()`, and installs `pnic2_lnk_change()`. Interrupt paths call the link-change hook with CSR5. Link failure branches delete and re-add the media timer around renegotiation.

State and persistence: Maintains negotiation state in `tp->sym_advertise`, `tp->lpar`, `tp->nway`, `tp->nwayset`, `tp->mediasense`, `tp->full_duplex`, `tp->csr6`, `dev->if_port`, and the timer. No persistent storage beyond hardware registers.

Dependencies and integration: Depends on `tulip.h` CSR constants, `medianame[]`, `tulip_start_rxtx()`, and `tulip_restart_rxtx()`. It plugs into the Tulip core chip table and shared interrupt link-change dispatch.

Risks: The implementation is based on sparse datasheet knowledge and uses magic masks `0xfe3bd1fd` and `0xfff0ee39`. Incorrect masking can corrupt unrelated CSR bits. Timer deletion from link-change context must avoid timer races. Failure fallback always chooses 10baseT half-duplex when negotiation is inconclusive.

Test signals: Cover successful negotiation for 100FD, 100HD, 10FD, and 10HD, autonegotiation failure fallback, link loss at 100 and 10 Mbps, medialock preventing renegotiation, CSR14 bit 7 clearing after NWAY, and timer rescheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/pnic2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/timer.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/timer.c

Purpose: Contains shared Tulip media-monitoring timer/work handlers for generic media-table devices, Macronix chips, and COMET chips.

Important APIs and functions: `tulip_media_task()` is a workqueue callback scheduled by `tulip_timer()` in `tulip_core.c`; it inspects CSR12 and media-table leaves, switches media when link beat is missing, checks MII duplex, and completes deferred TX timeout recovery. `mxic_timer()` is a minimal periodic Macronix negotiation-status timer. `comet_timer()` polls COMET PHY link status, updates carrier state, and reschedules itself every two seconds.

Control flow: The timer itself schedules work for generic Tulip chips so media transitions do not run directly in timer context. Type 0 and 4 leaves check CSR12 link-sense bits and may cycle `tp->cur_index` to another non-FD media leaf. Type 1 and 3 MII leaves call `tulip_check_duplex()`. At the end, if `tp->timeout_recovery` was set by `tulip_tx_timeout()`, the task calls `tulip_tx_timeout_complete()` under `tp->lock`.

State and persistence: Uses `tp->timer`, `tp->media_work`, `tp->cur_index`, `tp->mtable`, `tp->timeout_recovery`, `dev->if_port`, carrier state, and CSR6/CSR12. State is volatile runtime hardware and driver state.

Dependencies and integration: Depends on `tulip_select_media()`, `tulip_check_duplex()`, `tulip_restart_rxtx()`, and `tulip_tx_timeout_complete()`. Timer functions are selected through `tulip_tbl[]` in `tulip_core.c`.

Risks: Media-table leaf interpretation is hardware-specific. Incorrect link-sense polarity can cause media flapping. The task mixes carrier updates, media switching, and TX timeout recovery, so locking order with interrupt and close paths matters. `mod_timer()` is used to synchronize with interrupt-side timer changes.

Test signals: Validate media cycling with multi-leaf EEPROM tables, MII link loss and restoration, carrier on/off transitions, timeout recovery from scheduled work, COMET duplex polling, and close/suspend races with pending media work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/tulip.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/tulip.h

Purpose: Shared header defining Tulip chip identities, register offsets, descriptor formats, private driver state, media-table structures, prototypes, and inline RX/TX control helpers.

Important APIs and types: `struct tulip_chip_table` drives per-chip capabilities, interrupt masks, media timers, and media work callbacks. `enum chips`, `enum tbl_flag`, `enum status_bits`, `enum tulip_mode_bits`, and CSR enums provide shared hardware vocabulary. `struct tulip_rx_desc` and `struct tulip_tx_desc` describe DMA rings. `struct mediatable` and `struct medialeaf` model parsed EEPROM media descriptions. `struct tulip_private` is the central netdev private state for rings, DMA addresses, locks, timers, NAPI, EEPROM, media selection, PHYs, WOL, and device pointers. Inline helpers `tulip_start_rxtx()`, `tulip_stop_rxtx()`, `tulip_restart_rxtx()`, and `tulip_tx_timeout_complete()` centralize CSR6 start/stop behavior.

Control flow: The header is included by all Tulip submodules. The core driver fills `tulip_private`, selects function pointers from `tulip_chip_table`, and calls media, EEPROM, interrupt, and timer functions declared here. Inline stop waits for transmit/receive process-state bits to clear before changing hardware mode.

State and persistence: `tulip_private` holds all volatile driver state: descriptor rings, skb mappings, `cur_*` and `dirty_*` cursors, locks, media flags, EEPROM bytes, WOL settings, PHY address arrays, media table, timers, work item, PCI device, and MMIO base. EEPROM contents are cached but not modified here.

Dependencies and integration: Depends on Linux netdevice, ethtool, timer, PCI, spinlock, IO, and unaligned helpers. It binds modules `21142.c`, `eeprom.c`, `interrupt.c`, `media.c`, `pnic.c`, `pnic2.c`, `timer.c`, and `tulip_core.c`.

Risks: Chip enum ordering is explicitly used as an array index and must not drift from `tulip_tbl[]`. Descriptor bit definitions are shared across DMA paths, so endian and ownership mistakes have broad impact. `tulip_stop_rxtx()` timeout values assume 10/100 Ethernet frame timing.

Test signals: Compile coverage across MMIO/PIO, NAPI/non-NAPI, Tulip chip variants, descriptor ring wrap behavior, RX/TX stop timeouts, and consistency between enum chip values and `tulip_tbl[]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/tulip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/tulip_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/tulip_core.c

Purpose: Main PCI/netdevice driver for Digital 21x4x Tulip and many compatible Ethernet chips. It owns module parameters, PCI ID matching, probe/remove, open/close, ring allocation, TX, multicast filtering, media startup, WOL, and power management.

Important APIs and functions: `tulip_tbl[]` maps chip IDs to names, I/O sizes, valid interrupts, flags, media timers, and work callbacks. `tulip_init_one()` performs PCI enablement, resource mapping, DMA ring allocation, EEPROM/MAC reading, media option setup, EEPROM parsing, MII probing, netdev registration, and initial transceiver setup. `tulip_open()`, `tulip_up()`, `tulip_close()`, and `tulip_down()` manage IRQs, NAPI, timers, RX/TX rings, interrupts, and power state. `tulip_start_xmit()` queues TX descriptors. `tulip_tx_timeout()` and `tulip_tx_timeout_complete()` recover from stuck TX. `set_rx_mode()` builds hash/perfect setup frames or programs hash registers. Ettool and private MII ioctls expose WOL and PHY state.

Control flow: Module init copies parameters into interrupt globals and registers `tulip_driver`. Probe builds `struct tulip_private`, reads hardware identity, applies chip quirks, and registers a netdev. Open initializes rings, requests IRQ, calls `tulip_up()`, then starts the queue. Runtime TX/RX completion is handled in `interrupt.c`; this file supplies TX enqueue and teardown. Timers/media work adapt link settings. Suspend tears down active devices and configures wake events; resume restores IRQ and restarts hardware.

State and persistence: Runtime state lives in `tulip_private`, netdev stats, descriptor rings, skb mappings, EEPROM cache, module arrays `options[]`, `full_duplex[]`, `mtu[]`, and WOL options. Hardware state spans CSR0/CSR3/CSR4/CSR5/CSR6/CSR7 and chip-specific CSRs. No source-controlled persistence.

Dependencies and integration: Uses Linux PCI managed resources, DMA APIs, netdevice, ethtool, MII, CRC, NAPI optionally, and submodules declared in `tulip.h`. Integrates with `eeprom.c`, `media.c`, `timer.c`, `pnic*.c`, `21142.c`, and `interrupt.c`.

Risks: Large hardware matrix with many vendor quirks. EEPROM absence and multiport MAC derivation can generate fake addresses. TX setup frames share the TX ring with packets. DMA mapping/unmapping, queue stopping, and descriptor ownership ordering are critical. WOL support is COMET-specific. PM paths free IRQs and depend on netif state correctness.

Test signals: PCI probe for each ID class, EEPROM-present and missing cases, forced media/module options, MII ioctl reads/writes, TX timeout recovery, multicast perfect/hash modes, NAPI and non-NAPI builds, suspend/resume with and without WOL, and remove while interface is down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/tulip_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/uli526x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/uli526x.c

Purpose: Standalone PCI Fast Ethernet driver for ULi M5261/M5263 Tulip-like controllers. It does not use `struct tulip_private`; it implements its own descriptor rings, PHY access, media timer, interrupt handler, and PM callbacks.

Important APIs and functions: `uli526x_init_one()` enables PCI, allocates coherent descriptor and TX buffer pools, maps I/O, reads SROM or ID-table MAC address, selects CR9 or CR10 PHY operations, and registers the netdev. `uli526x_open()` initializes hardware, requests IRQ, starts queue, and arms a one-second timer. `uli526x_init()` resets MAC, discovers PHY, resets PHY, programs media, initializes descriptors, sends a setup frame, and enables interrupts/RX/TX. `uli526x_start_xmit()` copies skb data into preallocated TX buffers. `uli526x_interrupt()` handles RX, TX completion, and bus errors. Timer logic handles dynamic reset, TX kick/timeout, link state, and speed/duplex sensing.

Control flow: Probe sets static device resources. Open resets and starts hardware. TX packets are copied into descriptor-owned buffers, then DCR1 is kicked. Interrupts drain RX and TX descriptors while holding `db->lock`. The periodic timer may reset and reinitialize the NIC on CR8 anomalies or TX timeout, and updates carrier state based on PHY registers.

State and persistence: `struct uli526x_board_info` stores I/O base, PCI device, CR register shadows, descriptor pool pointers and DMA addresses, ring cursors, TX/RX counters, media state, PHY ops/address, reset counters, SROM cache, and timer. Module parameters `debug`, `mode`, and `cr6set` set globals used at open/init. No persistent writes.

Dependencies and integration: Uses Linux PCI, netdevice, ethtool, DMA, timers, spinlocks, SROM bit-banging, and MII-like PHY access. PCI IDs bind vendor 0x10B9 devices 0x5261 and 0x5263.

Risks: TX copies into fixed `TX_BUF_ALLOC` buffers and rejects frames over 1514 bytes, so VLAN/jumbo handling is limited. RX DMA unmap/free paths use hand-managed descriptor state. `phy_readby_cr10()` busy-waits without an explicit timeout. Dynamic reset runs from timer under lock and reinitializes rings.

Test signals: Probe both 5261 and 5263 PHY-access paths, absent SROM fallback, forced and auto media modes, link up/down timer messages, TX timeout reset, RX allocation failures, multicast setup frame generation, suspend/resume, and netpoll builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/uli526x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/winbond-840.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/winbond-840.c

Purpose: Standalone PCI Ethernet driver for Winbond W89c840 and compatible Compex/TX9882 boards. The chip is Tulip-like but has station/filter registers and a documented broken TX FIFO, so the driver maintains separate state and workarounds.

Important APIs and functions: `w840_probe1()` enables PCI, maps I/O, reads EEPROM MAC, initializes `struct netdev_private`, probes one MII PHY, and registers the netdev. `netdev_open()` requests IRQ, allocates coherent RX/TX rings, initializes registers, starts queue, and starts media timer. `start_tx()` maps skb data, uses one or two descriptor buffers for the 1 KB TX buffer limit, accounts `tx_q_bytes`, and stops the queue for ring/FIFO pressure. `intr_handler()` loops over interrupt status, handling RX, TX completion, errors, and interrupt mitigation. `netdev_rx()`, `netdev_tx_done()`, `tx_timeout()`, and `netdev_error()` own packet receive, TX completion, reset recovery, and abnormal events. Ettool and ioctl use `mii_if_info`.

Control flow: Probe is static setup. Open resets hardware and starts rings. TX descriptor ownership is set after `cur_tx` update under lock to avoid races with interrupts. Interrupts acknowledge status, process RX/TX, and throttle on work limits. Timer polls MII link every 10 seconds and applies CSR6 changes through `update_csr6()`.

State and persistence: `struct netdev_private` stores rings, DMA addresses, skb arrays, stats, timer, lock, PCI device, CSR6 shadow, MII info, PHY address, RX/TX cursors, FIFO byte accounting, and `tx_full`. No persistent storage beyond EEPROM reads.

Dependencies and integration: Includes `tulip.h` for shared descriptor/status constants but is otherwise standalone. Uses Linux PCI, DMA, netdevice, MII library helpers, CRC multicast hash, timers, and PM callbacks.

Risks: The broken TX FIFO workaround depends on `tx_q_bytes` and queue thresholds; mistakes can silently corrupt traffic. PM synchronization is complex and documented in-file. RX buffer unmap lengths depend on skb lengths. MII absent devices may not operate correctly. `tx_timeout()` performs full software reset with IRQ disabled.

Test signals: High-load ping/large packets for FIFO bug, TX queue stop/wake thresholds, MII link changes including Davicom PHY parallel detection, RX refill under allocation failure, multicast filter modes, suspend/resume with running and stopped device, and interrupt work-limit throttling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/winbond-840.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/xircom_cb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/xircom_cb.c

Purpose: Standalone CardBus Ethernet driver for tulip-like Xircom cards. It uses very small coherent descriptor/buffer pages and CardBus-specific register setup rather than the shared Tulip core.

Important APIs and functions: `xircom_probe()` enables PCI/CardBus resources, disables power management, allocates 8 KiB coherent RX and TX areas, maps I/O, initializes hardware, reads MAC tuples from boot ROM space, sets up descriptors, registers the netdev, and starts transceiver setup. `xircom_open()` requests IRQ and calls `xircom_up()`. `xircom_start_xmit()` frees completed descriptors, copies skb data into one of four fixed TX buffers, gives ownership to hardware, and triggers transmit. `xircom_interrupt()` handles shared IRQ filtering, link changes, clears status, and scans TX/RX descriptors. Descriptor helper functions process completed RX/TX. CSR helpers activate/deactivate RX/TX and enable interrupts.

Control flow: Probe performs more hardware setup than typical netdev drivers, including descriptor setup and transceiver initialization before open. Open enables interrupts and queues. Runtime TX and RX use four descriptors at offsets inside coherent pages. Interrupts scan all descriptors on every handled event and return RX descriptors to hardware immediately.

State and persistence: `struct xircom_private` stores RX/TX coherent buffers, DMA handles, four TX skb pointers, MMIO base, open flag, next TX descriptor index, spinlock, PCI device, and netdev. Hardware state lives in CSR0 through CSR16 and PCI power-management config. No persistent writes.

Dependencies and integration: Uses Linux PCI, CardBus vendor ID matching, netdevice, coherent DMA, spinlocks, and optional netpoll. It does not integrate with `tulip.h` despite Tulip-like CSRs.

Risks: TX/RX are copied through fixed 1536-byte buffers, so large or VLAN-sized frames are risky. The interrupt handler clears status with `0xffffffff` despite a FIXME. Promiscuous mode is always enabled in `xircom_up()`. Error packet discard is TODO in RX. `deactivate_transmitter()` appears to clear bit 1 rather than bit 13, matching a likely bug or hardware oddity. Probe-time transceiver setup can start hardware before netdev open.

Test signals: Card insertion/removal, IRQ sharing and hot unplug status `0xffffffff`, link change carrier updates, four-descriptor TX queue pressure, RX packet length clamping, open/close descriptor removal, netpoll, and first-packet behavior noted by TODO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/xircom_cb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/Kconfig

Purpose: Kconfig menu for D-Link Ethernet drivers under `drivers/net/ethernet/dlink`.

Important configuration entries: `NET_VENDOR_DLINK` is a bool vendor gate, defaults to `y`, and depends on `PCI`; disabling it hides the D-Link submenu without directly removing core kernel functionality. `DL2K` is a tristate for DL2000/TC902x/IP1000A Gigabit Ethernet support, depends on `PCI`, selects `CRC32`, and builds module `dl2k`. `SUNDANCE` is a tristate for Sundance Alta chips, depends on `PCI`, selects `CRC32` and `MII`. `SUNDANCE_MMIO` is a bool subordinate to `SUNDANCE` that opts into memory-mapped I/O; help text warns PIO is safer by default for some chips.

Control flow: Kconfig controls compilation symbols consumed by the D-Link Makefile. The `if NET_VENDOR_DLINK` block scopes all device-specific prompts under the vendor gate.

State and persistence: Configuration state persists in the kernel `.config`, not in this source file. The file itself defines dependency and select relationships only.

Dependencies and integration: Integrated with the kernel networking Kconfig tree and the adjacent Makefile. `DL2K` maps to `dl2k.o`; `SUNDANCE` maps to `sundance.o`; selected libraries ensure CRC32 and MII helpers are available.

Risks: `select` forces dependencies on, so those helper symbols must remain valid. Defaulting the vendor gate to `y` exposes prompts broadly. Enabling `SUNDANCE_MMIO` can regress hardware where PIO avoids chip bugs.

Test signals: Kconfig menu visibility with `PCI=n`, module/built-in combinations for `DL2K` and `SUNDANCE`, correct helper symbols selected, and Makefile objects emitted for each tristate value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/Makefile

Purpose: Kbuild object list for D-Link Ethernet drivers.

Important build rules: `obj-$(CONFIG_DL2K) += dl2k.o` includes the DL2000/TC902x/IP1000A driver when `CONFIG_DL2K` is built-in or module. `obj-$(CONFIG_SUNDANCE) += sundance.o` does the same for the Sundance Alta driver.

Control flow: Kbuild expands `obj-y` entries into built-in objects and `obj-m` entries into modules based on the tristate values produced by Kconfig. This file has no conditionals beyond the standard `obj-$()` pattern.

State and persistence: Build state is driven by `.config`; no runtime state exists in this Makefile.

Dependencies and integration: Directly paired with `sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/Kconfig`. It assumes source files `dl2k.c` and `sundance.c` exist in the same directory and that Kconfig selects needed helper libraries.

Risks: Symbol/name drift between Kconfig and Makefile would silently drop a driver from builds. Object names must match actual source filenames. There is no aggregate object or subdirectory recursion here.

Test signals: Build with `CONFIG_DL2K=y/m`, `CONFIG_SUNDANCE=y/m`, both disabled, and mixed built-in/module configurations; verify generated objects/modules include only the selected drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/Makefile -->
