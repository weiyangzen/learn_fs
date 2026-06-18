# subset-b-004625 research: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/farch_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/farch_regs.h

## Purpose
`farch_regs.h` is the Falcon/Siena hardware register, table, descriptor, and event bitfield catalogue used by the Solarflare `sfc/falcon` driver. It contains no executable logic; instead it defines the address offsets, row counts, strides, bit low-bit numbers, widths, and enumerated values consumed by register accessor and datapath code. The naming scheme encodes the hardware family and revision applicability, for example `FR_AZ_*` for register addresses, `FRF_*` for register fields, `FSF_*` for host-memory/event descriptor fields, and `FSE`/`FFE` for enumerators.

## Important APIs, Types, And Definitions
The major register groups cover PCI/BIU initialization and interrupts (`FR_AZ_INT_EN_KER`, `FR_AZ_INT_ADR_KER`, `FR_AZ_FATAL_INTR_KER`), SPI/VPD access (`FR_AB_EE_SPI_*`, `FR_AB_EE_VPD_*`), reset and GPIO control (`FR_AB_GLB_CTL`, `FR_AB_GPIO_CTL`), event queues and timers (`FR_BZ_EVQ_RPTR*`, `FR_AZ_EVQ_CTL`, `FR_BZ_TIMER_TBL`), RX/TX datapath setup (`FR_AZ_RX_CFG`, `FR_AZ_TX_CFG`, descriptor update registers, descriptor pointer tables), buffer table entries (`FR_BZ_BUF_FULL_TBL`, `FR_BZ_BUF_HALF_TBL`), hardware filters (`FR_BZ_RX_FILTER_TBL0`, `FR_CZ_RX_MAC_FILTER_TBL0`, `FR_CZ_TX_FILTER_TBL0`, `FR_CZ_TX_MAC_FILTER_TBL0`), MAC/PHY management (`FR_AB_MD_*`, `FR_AB_MAC_CTRL`, GMAC/XGMAC/XAUI blocks), MSI-X tables, and event/descriptor layouts (`EVENT_ENTRY`, `RX_EV`, `TX_EV`, `RX_KER_DESC`, `TX_KER_DESC`, user descriptors).

Several pseudo-fields make raw hardware definitions safer or more convenient for C code: descriptor-update dword addresses use `BUILD_BUG_ON_ZERO` to ensure Falcon A/B aliases stay equal, split 48-bit MAC filter fields are exposed as low/high 32-bit pieces, combined frame-size fields abstract low/high hardware splits, and all-lane XAUI status aliases combine per-lane fields.

## Control Flow
There is no runtime control flow in this header. It supports control flow elsewhere by giving common code stable constants for register tests, register dumps, queue setup, interrupt handling, filter programming, MDIO transactions, and event decoding. Revision suffixes are critical control inputs: callers such as register dump code select entries based on `efx->type->revision` and must not use fields outside their hardware range.

## State And Persistence
The file defines persistent hardware state locations rather than driver-owned state. Writes to these addresses affect NIC configuration, DMA queue state, event queue pointers, SRAM buffer tables, MAC state, PHY-management transactions, VPD/SPI contents, and filter tables. Descriptor and event field definitions describe persistent DMA memory contracts between host and NIC.

## Dependencies And Integration Points
This header is included by Falcon architecture code such as `nic.c`, low-level queue/event/filter implementations, MAC/PHY code, and register self-tests. It depends on the bitfield helper layer for constructing and extracting fields by `_LBN` and `_WIDTH` pairs. Its constants also integrate with Linux ethtool register dumps, interrupt setup, MTD/SPI support, MDIO management, RSS, RFS, and network queue programming.

## Risks
The primary risk is silent hardware corruption from incorrect offsets or field widths: many registers are wide, revision-specific, write-only, read-clear, or table-mapped. Misusing A/B/C revision constants can read undefined state or write an incompatible control bit. Descriptor-update aliases and pseudo-fields are especially sensitive because they encode hardware workarounds. Register dumps must avoid write-only and read-clear registers; this file documents many such cases through names and comments but relies on callers to honor them.

## Test Signals
Useful validation comes from register self-tests, ethtool register dumps, interrupt tests, queue flush tests, RX/TX datapath traffic, RSS/filter tests, MDIO read/write tests, and MAC statistic DMA checks. Compile-time validation through `BUILD_BUG_ON_ZERO` catches some descriptor alias assumptions, while runtime failures typically appear as timeout, interrupt, queue ownership, RX/TX checksum, filter miss, or MAC link faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/farch_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/filter.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/filter.h

## Purpose
`filter.h` defines the NIC-independent hardware filter specification API used by Falcon-architecture and later Solarflare filter implementations. It models what a packet filter matches, its priority, whether it applies to RX or TX, and the queue/RSS behavior to apply when a packet matches.

## Important APIs, Types, And Functions
`enum ef4_filter_match_flags` describes matchable fields: remote/local IP host, remote/local MAC, remote/local ports, EtherType, inner/outer VLAN ID, IP protocol, and local MAC I/G bit for default unicast or multicast filters. `enum ef4_filter_priority` establishes replacement policy from hints through required filters. `enum ef4_filter_flags` records RX RSS, RX scatter, automatic-filter override, and direction bits. `struct ef4_filter_spec` is a compact 64-byte specification containing bitfield metadata, RSS context, DMA queue ID, VLANs, MACs, EtherType, protocol, IPv4/IPv6-sized address arrays, and ports.

The inline constructors `ef4_filter_init_rx()` and `ef4_filter_init_tx()` zero the structure, set direction, priority, default RSS context, and queue. Setter helpers build common match forms: `ef4_filter_set_ipv4_local()`, `ef4_filter_set_ipv4_full()`, `ef4_filter_set_eth_local()`, `ef4_filter_set_uc_def()`, and `ef4_filter_set_mc_def()`.

## Control Flow
Callers must initialize a spec with the RX or TX constructor before setting match fields. Each setter mutates `match_flags` and the corresponding fields, returning `0` unless the Ethernet-local setter is asked to match neither VLAN nor MAC, in which case it returns `-EINVAL`. Hardware-specific filter operations later validate and translate the abstract spec into Falcon or Siena filter-table entries.

## State And Persistence
The header itself keeps no state. `ef4_filter_spec` values are transient request objects passed into the NIC type's `filter_insert`, `filter_remove_safe`, `filter_get_safe`, RFS, and clear/count/list operations. Once accepted, the persistent state lives in `efx->filter_state` and in hardware filter tables.

## Dependencies And Integration Points
The file depends on Linux type definitions, Ethernet address helpers, byte-order helpers, and `ETH_ALEN`/`ETH_P_IP`. It is included by `net_driver.h`, making the spec type part of the central `struct ef4_nic_type` filter operation contract. It integrates with RX queue selection, RSS contexts, accelerated RFS, automatic MAC-list filters, user-required filters, and TX source filtering on Siena-class hardware.

## Risks
The main correctness risk is creating a spec whose `match_flags` combination is unsupported by the active NIC type. The comments explicitly note that Falcon supports only a narrower subset than Siena or later hardware. Queue IDs are 12-bit fields, and `EF4_FILTER_RX_DMAQ_ID_DROP` uses the all-ones hardware value, so callers must avoid accidental queue/drop confusion. Byte order is also important: VLANs, EtherType, IP addresses, and ports are stored in network order.

## Test Signals
Signals include successful insertion/removal by hardware-specific filter code, RX packet steering to expected queues, drop-filter behavior, RSS distribution for RSS-marked filters, multicast/unicast default filter behavior, RFS acceleration expiry, and negative tests for invalid Ethernet-local filters or unsupported match combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/io.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/io.h

## Purpose
`io.h` provides inline MMIO and SRAM accessors for Falcon-architecture NICs. It centralizes the Bus Interface Unit locking rules for 128-bit CSRs and 64-bit SRAM, while allowing special fast-path dword writes for descriptor doorbells and event/timer page registers.

## Important APIs, Types, And Functions
Raw helpers `_ef4_writeq()`, `_ef4_readq()`, `_ef4_writed()`, and `_ef4_readd()` wrap unformatted MMIO reads/writes against `efx->membase`. Public accessors include `ef4_writeo()`/`ef4_reado()` for 128-bit CSRs, `ef4_writed()`/`ef4_readd()` for 32-bit CSRs, `ef4_sram_writeq()`/`ef4_sram_readq()` for mapped 64-bit SRAM, and table helpers `ef4_writeo_table()`/`ef4_reado_table()`. Page-mapped helpers use `EF4_VI_PAGE_SIZE` and `EF4_PAGED_REG()` for per-VI registers, including `_ef4_writeo_page()`, `_ef4_writed_page()`, and `_ef4_writed_page_locked()`.

## Control Flow
Wide CSR/SRAM reads and writes take `efx->biu_lock`, perform ordered dword or qword operations depending on `BITS_PER_LONG`, then release the lock. Dword writes intentionally avoid the lock because 32-bit registers and special descriptor-update high-dword writes are safe without it. The page-write macros include compile-time register filters using `BUILD_BUG_ON_ZERO` so only known safe page-mapped registers are accepted. `TIMER_COMMAND` page zero is locked because of a BIU collector bug.

## State And Persistence
The accessors mutate or read hardware state in PCI BAR space and mapped SRAM. They also serialize access through `efx->biu_lock`, preventing interleaved wide writes from corrupting the BIU collector. No software state is persisted except debug logging and the lock's synchronization effect.

## Dependencies And Integration Points
This file depends on Linux MMIO primitives, spinlocks, `netif_vdbg`, and the driver's bitfield word types from surrounding headers. It is the foundation for register dump code, queue setup, buffer table programming, interrupt/event operations, filter programming, MAC/PHY management registers, and statistic DMA controls.

## Risks
The largest risk is violating the BIU collector semantics by using an unlocked wide access or the wrong accessor width. The special descriptor-update path is intentionally narrow: writing the wrong dword can be discarded or write zero to unintended bits. Page helpers hard-code register-address allowances; adding a new page-mapped register requires revisiting these compile-time guards. Endianness and raw access also matter because the helper casts between little-endian driver word types and CPU raw IO values.

## Test Signals
Relevant tests include register self-tests, queue doorbell traffic, RX/TX descriptor updates, event queue read-pointer updates, timer moderation behavior, register dumps under load, and stress tests with concurrent queues. Hardware symptoms of access bugs include lost writes, stuck queues, missing interrupts, queue flush timeouts, and inconsistent register dump values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/mdio_10g.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/mdio_10g.c

## Purpose
`mdio_10g.c` implements shared helpers for IEEE 802.3 Clause 45 10G PHY management. The code is not specific to one PHY model; it handles MMD reset, presence checks, link checks under loopback policy, low-power and TX-disable state, autonegotiation reconfiguration, ethtool link setting changes, pause resolution, and PHY liveness tests.

## Important APIs, Types, And Functions
`ef4_mdio_id_oui()` reorders PHY ID bits into conventional OUI form. Reset and discovery helpers include `ef4_mdio_reset_mmd()`, `ef4_mdio_wait_reset_mmds()`, and `ef4_mdio_check_mmds()`, with the internal `ef4_mdio_check_mmd()` validating `MDIO_STAT2_DEVPRST`. Link and mode helpers include `ef4_mdio_links_ok()`, `ef4_mdio_transmit_disable()`, `ef4_mdio_phy_reconfigure()`, and `ef4_mdio_set_mmds_lpower()`. User-facing configuration helpers include `ef4_mdio_set_link_ksettings()`, `ef4_mdio_an_reconfigure()`, `ef4_mdio_get_pause()`, and `ef4_mdio_test_alive()`.

## Control Flow
Reset routines write reset bits, sleep in bounded loops, and poll control/status registers until reset clears or times out. MMD checks read device-present bitmaps from `DEVS1`/`DEVS2`, compare against the expected mask, then validate each required MMD. Link checks first apply driver loopback and PHY-mode exclusions, then defer to `mdio45_links_ok()`. Link settings are accepted only when they differ from current settings, both old and new ports are twisted pair, autonegotiation remains enabled, and requested advertising is supported. Autonegotiation writes base-page pause capability, asks the PHY operation to set next-page advertising, then enables/restarts AN.

## State And Persistence
The code persists configuration in PHY MDIO registers: reset, low-power, transmit disable, loopback, AN advertisement, and AN restart bits. It reads and updates driver state such as `efx->link_advertising`, `wanted_fc`, `phy_mode`, `loopback_mode`, and `efx->mdio.mmds`. `ef4_mdio_test_alive()` serializes ID probing and MMD checks with `efx->mac_lock`.

## Dependencies And Integration Points
It depends on Linux MDIO, ethtool link mode conversion, MII flow-control resolution, sleep/delay APIs, driver logging, `net_driver.h`, `mdio_10g.h`, and loopback/workaround definitions. PHY-specific operation tables call these helpers for common behavior, while ethtool settings, link polling, and monitor paths use their results.

## Risks
Timeout constants are intentionally conservative but still represent hardware assumptions. Passing reset spins and sleep time in the wrong units is guarded only by a paranoid debug check. Some paths assume at least one MMD bit is present for `__ffs()`. `ef4_mdio_set_link_ksettings()` uses legacy advertising conversion, so unsupported combinations must be rejected carefully. MDIO read errors must stay negative; treating them as register values would corrupt state decisions.

## Test Signals
Test signals include PHY probe success, MMD presence errors on missing devices, reset timeout logs, ethtool speed/duplex/autoneg rejection and acceptance, pause resolution from AN partner state, loopback-specific link status, low-power/TX-disable behavior, and `test_alive` reporting invalid all-zero/all-ones PHY IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/mdio_10g.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/mdio_10g.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/mdio_10g.h

## Purpose
`mdio_10g.h` declares and partially implements the common Clause 45 MDIO interface used by Falcon PHY drivers. It exposes small inline wrappers around the NIC's `mdio_if_info` callbacks and prototypes the common reset, link, power, autonegotiation, and liveness helpers implemented in `mdio_10g.c`.

## Important APIs, Types, And Functions
Inline ID helpers `ef4_mdio_id_rev()`, `ef4_mdio_id_model()`, and `ef4_mdio_id_oui()` decode PHY IDs. `ef4_mdio_read()` and `ef4_mdio_write()` call `efx->mdio.mdio_read` and `mdio_write` with the current `prtad`. `ef4_mdio_read_id()` combines `MDIO_DEVID1` and `MDIO_DEVID2`. `ef4_mdio_phyxgxs_lane_sync()` double-reads PHYXS lane status and reports XAUI/XGXS alignment. The header also declares MMD reset/check/link helpers, TX disable, loopback reconfigure, low-power control, ethtool link setting update, AN restart, pause resolution, reset waiting, flag setting, and alive testing.

## Control Flow
Most call paths are thin wrappers around the active MDIO bus implementation. `ef4_mdio_phyxgxs_lane_sync()` performs two lane-status reads before checking `MDIO_PHYXS_LNSTAT_ALIGN`, matching common latched-status semantics. `ef4_mdio_set_flag()` delegates to the kernel `mdio_set_flag()` helper using the driver's bus information.

## State And Persistence
The header does not own state. Its inlines read and write external PHY registers through `efx->mdio`, and therefore persist state in the PHY's MMD registers. The effective target is controlled by `efx->mdio.prtad` and the supplied device address/register pair.

## Dependencies And Integration Points
It depends on Linux `<linux/mdio.h>`, driver `efx.h`, `struct ef4_nic`, and logging helpers. It is used by generic MDIO code and by PHY implementations such as QT202x to avoid open-coding Clause 45 access patterns. It also bridges the driver's PHY operation table with Linux ethtool and MDIO helper APIs.

## Risks
The inline wrappers assume the `efx->mdio` callbacks and `prtad` have been initialized during PHY probe. `ef4_mdio_phyxgxs_lane_sync()` declares `lane_status` without an explicit initial value but always assigns it in the fixed two-iteration loop; changing that loop would create risk. Negative MDIO read results are not handled in every inline, so callers must choose helpers appropriate for error-sensitive paths.

## Test Signals
Signals include correct PHY ID reporting, lane-sync debug logs when alignment is absent, successful MDIO flag toggles, and callers observing consistent behavior across PHY implementations. Compile coverage from all PHY drivers is important because this header is a shared interface boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/mdio_10g.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/mtd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/mtd.c

## Purpose
`mtd.c` adapts NIC-specific nonvolatile storage operations to the Linux MTD subsystem. It registers and unregisters per-NIC MTD partitions, wires generic erase/read/write/sync callbacks to `struct ef4_nic_type` operations, and renames partitions when the network device name changes.

## Important APIs, Types, And Functions
`ef4_mtd_erase()` calls `efx->type->mtd_erase()`, while `ef4_mtd_sync()` calls `mtd_sync()` and logs failures with the partition's device/type names. `ef4_mtd_add()` initializes each `struct ef4_mtd_partition`'s embedded `struct mtd_info`, sets `_erase`, `_read`, `_write`, and `_sync`, invokes the NIC type's `mtd_rename()`, registers each partition with `mtd_device_register()`, and records it in `efx->mtd_list`. `ef4_mtd_remove()` unregisters all partitions and frees the allocated partition array. `ef4_mtd_rename()` reapplies type-specific names under RTNL.

## Control Flow
Add walks a caller-provided array with a configurable element size, registers partitions in order, and unwinds already-registered partitions if any registration fails. Removal first checks that the netdev is not registered, then repeatedly tries to unregister each partition; `-EBUSY` causes a one-second sleep/retry loop. The list order matters because `ef4_mtd_remove()` assumes the first list entry is the base allocation returned by the type-specific probe.

## State And Persistence
Persistent state is in `efx->mtd_list`, each embedded `mtd_info`, and the NIC's NVRAM/flash behind type-specific callbacks. The code does not manipulate flash contents directly except through delegated erase/read/write/sync operations. Partition names are mutable driver-visible state tied to the netdev name.

## Dependencies And Integration Points
This file depends on Linux MTD, module ownership, slab allocation, RTNL assertions, `net_driver.h`, and the `ef4_nic_type` MTD callback set compiled under `CONFIG_SFC_FALCON_MTD`. It integrates NIC flash/EEPROM storage with userspace MTD tooling while preserving hardware-specific implementation in NIC type code.

## Risks
The unregister loop can wait indefinitely while users hold MTD devices open. `ef4_mtd_remove()` assumes all partitions live in one allocation and that list order was preserved by `ef4_mtd_add()`. Add failure returns `-ENOMEM` for any registration failure, which may hide more specific MTD errors. Calling remove while the netdev is still registered triggers a warning and risks userspace races.

## Test Signals
Signals include MTD partition creation, correct partition names before and after netdev rename, read/write/erase/sync behavior on supported hardware, clean unregister after users close devices, and unwind behavior when a later partition fails to register. Kernel warnings around registered netdev removal or failed unregisters are important failure indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/mtd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/net_driver.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/net_driver.h

## Purpose
`net_driver.h` is the central shared data-model and operation-contract header for the Falcon `ef4` network driver. It defines queue, channel, NIC, PHY, statistics, filter, MTD, interrupt, and feature abstractions used across probe, datapath, reset, ethtool, and hardware-specific implementations.

## Important APIs, Types, And Definitions
The header establishes limits and constants such as `EF4_MAX_CHANNELS`, TX queue type flags, MTU bounds, RX buffer sizing, flow-control bits, and interrupt modes. Core structures include DMA buffers (`ef4_buffer`, `ef4_special_buffer`), TX/RX buffer and queue rings (`ef4_tx_buffer`, `ef4_tx_queue`, `ef4_rx_buffer`, `ef4_rx_queue`), event-processing channels (`ef4_channel`, `ef4_channel_type`), interrupt context (`ef4_msi_context`), link state (`ef4_link_state`), PHY operations (`ef4_phy_operations`), hardware statistic descriptors, multicast hash storage, MTD partitions, the master `struct ef4_nic`, and the controller vtable `struct ef4_nic_type`.

Inline helpers retrieve channels and queues, iterate channels and per-channel queues, compute maximum frame length, combine fixed and configurable netdev features, and safely get TX insert buffers. The `ef4_nic_type` vtable is large and defines the hardware contract for probe/remove/init/fini, reset, port/MAC/PHY handling, stats, IRQs, TX/RX/event queues, filters, MTD, MAC address handling, register bases, DMA masks, RSS prefix information, scatter support, interrupt limits, and offload features.

## Control Flow
Most runtime control flow in the driver is mediated by the structures defined here. Generic code stores hardware state in `ef4_nic`, then dispatches hardware-specific behavior through `efx->type` and `efx->phy_op`. Iteration macros assume the `channel[]` array is densely populated up to `n_channels`. TX helpers account for paired offload/non-offload queues and optional high-priority queues. State fields distinguish uninitialized, ready, disabled, and PCI-error recovery phases.

## State And Persistence
`struct ef4_nic` persists nearly all driver state: PCI mappings, interrupt configuration, resource dimensions, RSS tables, queue/channel pointers, IRQ status DMA buffer, MTD list, NIC-specific private data, locks, port/link state, filter state, flush counters, VPD serial number, monitor work, statistics, and RX drop counters. Queue structs persist software ring indices, DMA descriptors, page recycle state, and completion statistics. Locking annotations in comments define ownership across RTNL, MAC lock, TX locks, spinlocks, and workqueues.

## Dependencies And Integration Points
The header depends heavily on Linux networking, PCI, ethtool, MDIO, I2C, MTD, workqueue, timer, and busy-poll APIs, plus local `enum.h`, `bitfield.h`, and `filter.h`. It is included by most driver files and is the primary integration point between generic netdev code, hardware-specific Falcon architecture code, PHY drivers, ethtool operations, MTD support, and interrupt/event datapaths.

## Risks
Because this header defines shared state contracts, layout or semantic changes have broad blast radius. Important risks include cacheline-sharing regressions in fast-path queue fields, mismatched vtable implementations, incorrect channel/queue dimensioning, lock-order violations around `mac_lock`/RTNL/TX locks, stale filter or MTD state, and misuse of queue iteration macros when channels are sparse. Several inline helpers use paranoid assertions only under debug builds.

## Test Signals
Good signals include successful probe/remove, channel and queue allocation, RX/TX traffic with multiple queue types, MSI/MSI-X/legacy interrupt modes, reset and recovery flows, ethtool stats and register dumps, PHY operations, MTD operations, filter insertion/RFS behavior, busy-poll/NAPI operation, and lockdep or KASAN coverage for lifecycle and ring-buffer mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/net_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/nic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/nic.c

## Purpose
`nic.c` implements generic NIC support shared by Falcon-architecture devices: coherent DMA buffer allocation, event and IRQ self-test triggers, interrupt request/free logic, ethtool register dump layout and collection, and generic hardware statistic description/update helpers.

## Important APIs, Types, And Functions
`ef4_nic_alloc_buffer()` and `ef4_nic_free_buffer()` allocate/free coherent DMA memory for interrupt status, statistics, and similar fixed buffers. `ef4_nic_event_present()`, `ef4_nic_event_test_start()`, and `ef4_nic_irq_test_start()` support self-tests. `ef4_nic_init_interrupt()` and `ef4_nic_fini_interrupt()` hook and unhook legacy, MSI, or MSI-X handlers, with optional RFS CPU-rmap setup. Register dump support is driven by `struct ef4_nic_reg`, `struct ef4_nic_reg_table`, `ef4_nic_regs[]`, and `ef4_nic_reg_tables[]`, with `ef4_nic_get_regs_len()` computing size and `ef4_nic_get_regs()` reading the selected registers/tables. Statistics helpers are `ef4_nic_describe_stats()` and `ef4_nic_update_stats()`.

## Control Flow
Interrupt initialization chooses legacy if MSI is not in use, otherwise optionally allocates an RX CPU rmap for MSI-X and requests one IRQ per channel. Failures unwind already-requested IRQs and free the rmap. Register dump functions filter register and table definitions by `efx->type->revision`; table reads switch on stride to choose 32-bit MMIO/SRAM, 64-bit SRAM, 128-bit table, or interleaved 128-bit table access. Stat updates iterate a mask and convert little-endian 16/32/64-bit DMA fields into `u64` values, either replacing or accumulating.

## State And Persistence
DMA buffer helpers persist kernel virtual and DMA addresses in `struct ef4_buffer`. Interrupt setup persists IRQ registrations and `net_dev->rx_cpu_rmap`. Self-tests write `event_test_cpu` and `last_irq_cpu` with memory barriers before requesting hardware-generated test signals. Register dumps are snapshots of hardware state, not persistent driver state. Stat helpers update caller-owned `u64` arrays.

## Dependencies And Integration Points
This file depends on Linux DMA, interrupt, PCI, module, seq/cpu-rmap APIs, local `net_driver.h`, `bitfield.h`, `efx.h`, `nic.h`, `farch_regs.h`, `io.h`, and workaround definitions. It integrates directly with the hardware vtable for IRQ handlers and test generation, with `io.h` for register access, with ethtool register/stat APIs, and with RFS acceleration support.

## Risks
IRQ setup has several partial-failure paths where cleanup order matters. Register dump arrays must avoid write-only or read-clear registers; comments mark many exclusions but future additions could accidentally disturb hardware. The register dump buffer is advanced as a `void *`, relying on compiler support. `ef4_nic_update_stats()` trusts descriptor offsets and DMA widths; a mismatched descriptor can read the wrong DMA buffer bytes or silently report zero after `WARN_ON`.

## Test Signals
Signals include successful IRQ request/free across legacy, MSI, and MSI-X modes, RFS CPU-rmap creation, self-test interrupts/events arriving on recorded CPUs, ethtool `get_regs` length matching the emitted dump, stable register dumps on each supported revision, and correct ethtool statistic names and values from 16/32/64-bit DMA fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/nic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/nic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/nic.h

## Purpose
`nic.h` is the Falcon-specific internal interface layered on top of `net_driver.h`. It declares Falcon revision constants, event/descriptor helpers, PHY type IDs, board and SPI data structures, Falcon hardware statistics, Falcon NIC-private state, data-path wrappers, Falcon architecture operation prototypes, interrupt/global resource helpers, register tests, stats helpers, and event generation.

## Important APIs, Types, And Functions
Inline helpers include `ef4_nic_rev()`, `ef4_nic_is_dual_func()`, `ef4_event()`, `ef4_event_present()`, `ef4_tx_desc()`, `ef4_tx_queue_partner()`, `ef4_nic_may_push_tx_desc()`, and `ef4_rx_desc()`. Board and hardware-private types include `struct falcon_board_type`, `struct falcon_board`, `struct falcon_spi_device`, and `struct falcon_nic_data`. The file exports `falcon_a1_nic_type` and `falcon_b0_nic_type`, wrappers that dispatch TX/RX/event operations through `efx->type`, and prototypes for Falcon architecture queue/event/filter/interrupt/reset/stat functions.

## Control Flow
The inline dispatch wrappers are used by generic driver code to call the active NIC type's queue and event operations without exposing the whole vtable at every call site. Event presence checks treat all-ones dwords as empty and avoid a single 64-bit comparison because event DMA writes may not be atomic. TX push eligibility clears `empty_read_count` and only allows a descriptor push when the NIC-visible queue was empty and exactly one descriptor is pending, avoiding known Falcon/Siena push hazards.

## State And Persistence
`struct falcon_nic_data` persists Falcon-private hardware state: optional secondary PCI function, board data, hardware stats array, stats-disable nesting, pending stats DMA, stats timer, SPI flash/EEPROM descriptors, SPI and MDIO locks, and whether XMAC polling is required. Descriptor helpers expose persistent DMA rings owned by TX/RX queue structures. Board/SPI structures persist per-board peripheral and NVRAM information.

## Dependencies And Integration Points
The header depends on timestamping, I2C bit-bang APIs, `net_driver.h`, and `efx.h`. It integrates generic driver code with Falcon-specific implementations in files such as queue/event/filter/MAC/SPI/board code, PHY drivers, and ethtool register/stat logic. PHY type constants connect probe-time hardware identification to operation tables in `phy.h` and PHY implementation files.

## Risks
The event-present algorithm relies on the event-clearing convention that both dwords are all ones and on valid events never having all ones in either dword. TX push logic is a latency optimization with hardware bug constraints; changing empty-count semantics can reintroduce lost or unsafe pushes. Many prototypes are hardware-facing and require callers to hold the correct locks or be in the correct lifecycle phase, but those requirements are spread across implementation files.

## Test Signals
Signals include event queue polling and clearing correctness, TX push counters and low-latency single-packet behavior, RX/TX descriptor ring indexing, Falcon A dual-function behavior, SPI flash/EEPROM detection, board initialization, Falcon filter operations, interrupt tests, DMA queue flushes, register self-tests, and hardware stats monotonicity via `ef4_update_diff_stat()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/nic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/phy.h

## Purpose
`phy.h` is a small Falcon PHY interface header that exposes operation tables and board-control helpers for supported external PHY families: 10Xpress/SFX7101, AMCC/Quake QT202x, and Transwitch CX4 retimer devices.

## Important APIs, Types, And Definitions
It declares `falcon_sfx7101_phy_ops`, `falcon_qt202x_phy_ops`, and `falcon_txc_phy_ops` as `struct ef4_phy_operations` instances. Helper declarations include `tenxpress_set_id_led()`, `falcon_qt202x_set_led()`, `falcon_txc_set_gpio_dir()`, and `falcon_txc_set_gpio_val()`. Quake LED constants describe LED modes (`QUAKE_LED_LINK_STAT`, `QUAKE_LED_LINK_ACT`, `QUAKE_LED_OFF`, `QUAKE_LED_ON`, and others) and whether a LED tracks TX or RX link. TXC GPIO direction constants distinguish input and output.

## Control Flow
This header contains declarations and constants only. Control flow is provided by PHY-specific implementation files and selected through `efx->phy_op` after hardware detection. Board or PHY code calls the LED/GPIO helpers to drive external status LEDs or retimer pins.

## State And Persistence
There is no local state. Persistent effects occur when implementations write PHY LED control registers, board GPIOs, or retimer state. The exported operation tables become persistent driver configuration once assigned to `efx->phy_op`.

## Dependencies And Integration Points
The header assumes `struct ef4_nic`, `enum ef4_led_mode`, and `struct ef4_phy_operations` are already visible through surrounding includes. It integrates the board layer, PHY probe logic, and generic link/ethtool code with concrete PHY implementations.

## Risks
Because constants map directly to hardware control states, wrong LED mode or GPIO direction values can misrepresent link status or affect board control pins. The header does not enforce include ordering by itself; users must include it in contexts where `net_driver.h` or equivalent definitions are present.

## Test Signals
Signals include successful PHY operation table selection, LED identify/default behavior, QT202x LED register writes, TXC GPIO direction/value behavior, and link-state reporting through the selected PHY implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/qt202x_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/qt202x_phy.c

## Purpose
`qt202x_phy.c` implements the `ef4_phy_operations` backend for AMCC/Quake QT202x SFP+/XFP PHYs, including QT2022C2 and QT2025C variants. It handles PHY probe/init/reset, firmware readiness, QT2025C mode switching, link polling, TX-disable/loopback reconfiguration, module EEPROM exposure, LED control, and PHY-private cleanup.

## Important APIs, Types, And Functions
The public helper `falcon_qt202x_set_led()` writes Quake LED mode registers. Private `struct qt202x_phy_data` stores the last PHY mode, bug-17190 workaround state/timer, and QT2025C firmware version. Firmware/reset helpers include `qt2025c_wait_heartbeat()`, `qt2025c_wait_fw_status_good()`, `qt2025c_restart_firmware()`, `qt2025c_wait_reset()`, and `qt2025c_firmware_id()`. Link recovery and mode control are handled by `qt2025c_bug17190_workaround()` and `qt2025c_select_phy_mode()`. The operation table uses `qt202x_phy_probe()`, `qt202x_phy_init()`, `qt202x_phy_reconfigure()`, `qt202x_phy_poll()`, `qt202x_phy_get_link_ksettings()`, `qt202x_phy_remove()`, `qt202x_phy_get_module_info()`, and `qt202x_phy_get_module_eeprom()`.

## Control Flow
Probe allocates PHY-private state, sets required MMDs, declares Clause 45/C22-emulation support, and publishes supported loopbacks. Init resets the PHY, performs board-specific PHY initialization, reads/logs PHY ID, and records QT2025C firmware information. QT2025C reset waits for firmware heartbeat and good microcontroller status, with a one-time firmware restart workaround if status stalls. Reconfigure optionally switches QT2025C operating mode based on loopback, applies static TX disable for low-power or loopback cases, or resets older QT202x PHYs when TX is re-enabled, then calls common MDIO loopback reconfiguration. Poll updates 10G full-duplex link state and runs the QT2025C PCS-stuck workaround.

## State And Persistence
The driver persists private state in `efx->phy_data`. Hardware state is persisted through MDIO writes to PMA/PMD and PCS vendor registers, LED registers, TX static-disable bits, loopback bits, operating-mode registers, firmware control registers, and module EEPROM windows. Link state is stored in `efx->link_state`, and supported loopbacks/MMD masks are set during probe.

## Dependencies And Integration Points
The file depends on Linux slab/timer/delay APIs, `efx.h`, common MDIO helpers, `phy.h`, and `nic.h`. It integrates with board revision data through `falcon_board(efx)`, with generic PHY/link code through `falcon_qt202x_phy_ops`, with ethtool through link settings and module EEPROM/info callbacks, and with common MDIO liveness/settings helpers.

## Risks
The QT2025C mode-switch sequence is a long vendor-specific register script that varies by board revision; mistakes can break firmware/module I2C recovery or leave the PHY in the wrong operating mode. Timeouts around heartbeat and firmware status are hardware-sensitive and include user-facing diagnostics for non-compliant direct-attach cables. The bug-17190 workaround deliberately toggles PMA/PMD loopback after a persistent bad state; false positives could disturb link. EEPROM reads are byte-by-byte MDIO operations and rely on the correct MMD/base for the PHY variant.

## Test Signals
Signals include successful probe allocation and MMD mask setup, PHY reset completion, firmware version log for QT2025C, mode switching when entering/leaving loopback, TX disable under low-power or loopback, stable 10G full-duplex link polling, recovery from PCS-down/PMA-up bad states, ethtool module EEPROM reads, LED control behavior, and cleanup freeing `efx->phy_data`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/qt202x_phy.c -->
