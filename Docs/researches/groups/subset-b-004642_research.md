# Research: subset-b-004642

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port.c

## Purpose

`mcdi_port.c` is the Siena driver's small port-facing wrapper around Management Controller Driver Interface (MCDI) PHY and MAC services. It wires Linux MDIO callbacks to firmware MDIO commands, checks MAC fault state through `MC_CMD_GET_LINK`, and sequences port probe/remove by delegating the heavy PHY and MAC statistics work to `mcdi_port_common.c`.

## Important APIs, Types, and Functions

The local MDIO callbacks `efx_mcdi_mdio_read()` and `efx_mcdi_mdio_write()` translate `struct mii_bus`-style read/write requests into `MC_CMD_MDIO_READ` and `MC_CMD_MDIO_WRITE` RPCs. Both populate bus, port address, device address, register address, and optionally value fields with `MCDI_SET_DWORD`, then require a firmware status of `MC_CMD_MDIO_STATUS_GOOD`.

Exported driver entry points are `efx_siena_mcdi_mac_check_fault()`, `efx_siena_mcdi_port_probe()`, and `efx_siena_mcdi_port_remove()`. The check-fault path treats any failed `GET_LINK` command as a fault. Probe installs the MDIO callbacks in `efx->mdio`, calls `efx_siena_mcdi_phy_probe()`, and then allocates MAC stats state with `efx_siena_mcdi_mac_init_stats()`. Remove calls `efx_siena_mcdi_phy_remove()` and `efx_siena_mcdi_mac_fini_stats()`.

## Control Flow

Port initialization starts in the NIC type's `probe_port` callback. This file first exposes a Clause 45/Clause 22-emulated MDIO surface backed by the management controller, then asks the common MCDI PHY layer to discover PHY configuration, link state, loopback modes, advertised capabilities, and default flow-control/FEC settings. Only after PHY state exists does it initialize the MAC stats DMA buffer.

Port teardown is straight-line and assumes higher-level code has quiesced the port: PHY private state is freed and the stats buffer is released. There is no local locking here; callers rely on the core driver lifecycle and `mac_lock` sequencing used by the common port layer.

## State and Persistence Behavior

This file mutates `efx->mdio.mode_support`, `mdio_read`, `mdio_write`, and the state created by delegated PHY/stat helpers. MDIO transactions are not cached; every read/write is a firmware RPC. MAC fault state is also read directly from firmware. Persistent resources created through probe include PHY private data and the coherent DMA stats buffer, but ownership is in `efx->phy_data` and `efx->stats_buffer` rather than this file.

## Dependencies and Integration Points

Dependencies include `mcdi.h`/`mcdi_pcol.h` for command encoding, `net_driver.h` for `struct efx_nic`, `mcdi_port_common.h` for the actual PHY and stats implementation, and the Linux MDIO/netdev interfaces. It integrates with ethtool, monitor, link reconfiguration, and stats paths indirectly through the common helpers it initializes.

## Risks and Test Signals

Failure handling is deliberately conservative: failed `GET_LINK` means MAC fault, and MDIO bad status maps to `-EIO`. Probe has an ordering risk: if MAC stats initialization fails after PHY probe succeeds, this function returns the error without calling `efx_siena_mcdi_phy_remove()`, so callers or future edits should verify unwind ownership. Useful tests are MCDI fault injection for MDIO status and RPC errors, probe/remove leak checks, ethtool MDIO access through supported PHYs, and link fault reporting during firmware reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port.h

## Purpose

`mcdi_port.h` is the narrow public header for MCDI-backed Siena port services. It exposes only MAC fault checking and port probe/remove lifecycle hooks to the rest of the driver.

## Important APIs, Types, and Functions

The header includes `net_driver.h` for `struct efx_nic` and declares `efx_siena_mcdi_mac_check_fault()`, `efx_siena_mcdi_port_probe()`, and `efx_siena_mcdi_port_remove()`. There are no local types, constants, or inline helpers.

## Control Flow and Integration

NIC-type implementations include this header when they need a firmware-backed port implementation. The usual control flow is probe via `efx_siena_mcdi_port_probe()`, runtime fault checks through `efx_siena_mcdi_mac_check_fault()`, and cleanup through `efx_siena_mcdi_port_remove()`. The declarations bridge device-specific probe code to `mcdi_port.c` and then to the richer PHY/MAC routines in `mcdi_port_common.c`.

## State and Persistence Behavior

The header itself stores no state. Its functions mutate `struct efx_nic` port fields, MDIO callbacks, `phy_data`, link state, and stats buffer state via their implementations. Callers should treat these as lifecycle and hardware/firmware operations, not pure queries.

## Dependencies and Risks

The main contract risk is that the header hides the fact that probe allocates multiple resources through delegated helpers. Callers must use the matching remove path and must handle probe failure according to the implementation's unwind behavior. Compile tests should catch prototype drift between this header and `mcdi_port.c`; integration tests should cover NIC type tables that reference these hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port_common.c

## Purpose

`mcdi_port_common.c` implements the firmware-backed PHY, link, FEC, module EEPROM, cable test, MAC reconfiguration, MAC statistics, and link event handling used by Siena-style SFC devices. It translates Linux ethtool/netdev concepts into MCDI command payloads and keeps `struct efx_nic` link-related state synchronized with firmware.

## Important APIs, Types, and Functions

PHY discovery is centered on `efx_mcdi_get_phy_cfg()` and `efx_siena_mcdi_phy_probe()`, which fill `struct efx_mcdi_phy_data`, MDIO addressing, supported media, loopback mask, initial link state, advertising, FEC config, and default flow control. Runtime link paths include `efx_siena_mcdi_phy_poll()`, `efx_siena_mcdi_port_reconfigure()`, `efx_siena_mcdi_phy_get_link_ksettings()`, and `efx_siena_mcdi_phy_set_link_ksettings()`.

Capability conversion helpers include `mcdi_to_ethtool_linkset()`, `ethtool_linkset_to_mcdi_cap()`, `ethtool_fec_caps_to_mcdi()`, and `mcdi_fec_caps_to_ethtool()`. FEC public entry points are `efx_siena_mcdi_phy_get_fecparam()` and `efx_siena_mcdi_phy_set_fecparam()`. Test and module APIs include `efx_siena_mcdi_phy_test_alive()`, `efx_siena_mcdi_phy_run_tests()`, `efx_siena_mcdi_phy_test_name()`, `efx_siena_mcdi_phy_get_module_eeprom()`, and `efx_siena_mcdi_phy_get_module_info()`.

MAC-side APIs are `efx_siena_mcdi_set_mac()`, `efx_siena_mcdi_mac_init_stats()`, `efx_siena_mcdi_mac_fini_stats()`, plus local stats controls `efx_siena_mcdi_mac_start_stats()`, `efx_siena_mcdi_mac_stop_stats()`, and `efx_siena_mcdi_mac_pull_stats()`. Link-change events are decoded by `efx_siena_mcdi_process_link_change()`.

## Control Flow

PHY probe allocates `efx_mcdi_phy_data`, issues `GET_PHY_CFG`, then `GET_LINK`. If autonegotiation is active, firmware capabilities are converted into ethtool advertising; otherwise the forced capability word is saved. Probe validates loopback enum compatibility with compile-time checks, fetches supported loopbacks, decodes current speed/duplex/flow control, records an ethtool-representable FEC mode, and applies default wanted flow control through common link helpers.

Setting link ksettings converts requested autoneg advertisement or forced speed/duplex into an MCDI capability word, ORs in FEC bits derived from current `efx->fec_config`, applies PHY flags for TX-disable/low-power/off modes, and calls `MC_CMD_SET_LINK`. FEC setting follows the same pattern but recomputes the capability word from saved advertising or forced capability, validates that requested FEC maps to supported MCDI bits, updates firmware, and then persists `efx->fec_config`.

Module EEPROM reads identify SFP/QSFP media, calculate page count and starting page, read 128-byte pages with `GET_PHY_MEDIA_INFO`, and tolerate missing upper QSFP pages by zero-filling when appropriate. BIST starts a firmware test, polls up to 10 seconds, records pass/fail, and extracts SFT9001 cable diagnostics when available.

MAC reconfiguration builds `SET_MAC` with current MAC address, MTU-derived max frame length, unicast reject policy, RX-FCS inclusion, and flow control policy. MAC stats allocate a coherent DMA buffer and control periodic or one-shot firmware DMA through `MC_CMD_MAC_STATS`; pull waits briefly for a generation marker to change.

## State and Persistence Behavior

Persistent state includes `efx->phy_data`, `phy_type`, MDIO bus/port/mmd fields, `link_advertising`, `wanted_fc`, `fec_config`, `link_state`, `loopback_modes`, and `stats_buffer`. Firmware state includes link capabilities, PHY mode flags, loopback mode, MAC address/MTU/filter/flow-control settings, and periodic MAC stats DMA. Link-change events update `efx->link_state` outside `mac_lock` based on an explicit ordering assumption: polling only runs after event queues are flushed.

## Dependencies and Integration Points

This file depends heavily on `mcdi_pcol.h` command layouts, `efx_siena_mcdi_rpc*()` transports, ethtool link/FEC/module APIs, MDIO constants, common link helpers in `efx_common.h`, stats buffer helpers from `nic.c`, and `net_driver.h` state definitions. It is called from port probe, ethtool get/set operations, monitor polling, MAC reconfiguration, self-test, and event processing.

## Risks and Test Signals

Risk areas include capability translation drift as new ethtool link modes are added, ambiguous FEC combinations, firmware output-length compatibility, 25G/50G BASER vs RS semantics, and QSFP page read error handling. MAC stats pull is timing-sensitive and relies on the last stat word as a generation marker. Tests should cover autoneg and forced link settings, FEC get/set on 10/25/40/50/100G media, module EEPROM reads across SFP and QSFP variants, BIST polling timeout/failure, link-change events, MAC stats start/pull/stop, and MCDI error injection for short responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port_common.h

## Purpose

`mcdi_port_common.h` declares the common MCDI PHY and MAC services shared by Siena port code. It is the contract between NIC type/ethtool/monitor paths and `mcdi_port_common.c`.

## Important APIs, Types, and Functions

The central type is `struct efx_mcdi_phy_data`, which stores firmware-discovered PHY flags, type, supported capabilities, MCDI channel/port, stats mask, name, media type, MMD mask, revision string, and currently forced capability word.

The declared API covers link advertising, PHY polling/probe/remove, ethtool link ksettings get/set, FEC get/set, PHY alive tests, port reconfiguration, PHY BIST and test names, module EEPROM/info reads, MAC reconfiguration, and MAC stats buffer init/fini.

## Control Flow and Integration

Callers usually probe PHY state once, then use the ethtool-oriented methods for user configuration and the poll/event methods for link state maintenance. `efx_siena_mcdi_port_reconfigure()` is the narrow runtime hook used when MAC/PHY mode, loopback, FEC, or advertisement state needs to be pushed to firmware. MAC stats init/fini are paired with the port lifecycle, while start/stop/pull stats are implemented in the C file and referenced through NIC type callbacks.

## State and Persistence Behavior

The header defines the shape of `efx->phy_data` for MCDI PHYs. Most APIs mutate long-lived `struct efx_nic` state and firmware link/MAC state. The header itself has no storage, but its functions assume that `efx->phy_data` is valid after successful probe and invalid after remove.

## Dependencies, Risks, and Test Signals

It includes `net_driver.h`, `mcdi.h`, and `mcdi_pcol.h`, so it exposes MCDI-specific details to its consumers. The major contract risk is lifetime: callers must not use link/FEC/module helpers before probe or after remove. Compile coverage should validate prototypes under ethtool and MCDI header changes; integration tests should pair every probe path with remove and exercise each declared ethtool operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mtd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mtd.c

## Purpose

`mtd.c` exposes NIC non-volatile storage partitions through the Linux MTD subsystem. It is a generic wrapper: device-specific read, write, erase, sync, and rename behavior is supplied by `efx->type` callbacks.

## Important APIs, Types, and Functions

`efx_mtd_erase()` and `efx_mtd_sync()` are MTD operation callbacks. `efx_mtd_erase()` calls `efx->type->mtd_erase()`, while sync calls `efx->type->mtd_sync()` and logs partition-specific failures.

`efx_siena_mtd_add()` initializes an array of `struct efx_mtd_partition` objects, fills their `struct mtd_info` fields, calls `mtd_rename()`, registers each partition with `mtd_device_register()`, and adds registered partitions to `efx->mtd_list`. `efx_siena_mtd_remove()` unregisters all partitions and frees the partition array. `efx_siena_mtd_rename()` renames already-registered partitions under RTNL after netdev name changes.

## Control Flow

The NIC-specific MTD probe path prepares partition objects and passes them to `efx_siena_mtd_add()` with count and stride. For each partition, this file sets one-byte writesize, marks erasable partitions writable, connects MTD callbacks, derives a name, registers the MTD device, and then appends it to the NIC list. On partial failure, it walks previously initialized entries in reverse and unregisters them.

Removal requires the netdev not be registered, then repeatedly unregisters each partition. If `mtd_device_unregister()` returns `-EBUSY`, it sleeps and retries until the partition is free. After all list entries are removed, the first partition pointer is freed, relying on the add path's array allocation convention.

## State and Persistence Behavior

State persists in `efx->mtd_list` and each partition's embedded `mtd_info`. Actual flash contents are not cached here; every MTD read/write/erase routes to NIC-type callbacks. Partition names are mutable and derived from current netdev naming. Removal can block indefinitely while users hold MTD devices busy.

## Dependencies and Integration Points

This file depends on `CONFIG_SFC_SIENA_MTD`, Linux MTD APIs, RTNL for rename assertions, `struct efx_mtd_partition` from `net_driver.h`, and NIC type callbacks for storage operations. It integrates with driver probe/remove, netdev rename handling, and user-space MTD tools.

## Risks and Test Signals

The biggest contract risk is ownership of the partition array: `efx_siena_mtd_remove()` frees the first list entry as the base pointer, so NIC-specific allocation must supply one contiguous array and preserve list order. The unregister retry loop can wait forever if a partition remains busy. Tests should cover partial registration failure, rename under RTNL, open-MTD removal behavior, read/write/erase callback propagation, and module unload with active MTD users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mtd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/net_driver.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/net_driver.h

## Purpose

`net_driver.h` is the main shared state and callback contract for the Siena SFC net driver. It defines queue/channel/NIC data structures, feature limits, RX/TX buffer state, RSS/RFS/XDP/PTP/MTD integration fields, link state, flow control flags, and the large `struct efx_nic_type` hardware operation table used to bind common driver code to specific NIC implementations.

## Important APIs, Types, and Functions

Core structures include `struct efx_buffer` for coherent DMA memory, `struct efx_special_buffer` for buffer-table-backed rings, `struct efx_tx_buffer` and `struct efx_tx_queue` for software and hardware TX state, `struct efx_rx_buffer`, `struct efx_rx_page_state`, and `struct efx_rx_queue` for RX descriptors and recycled pages, `struct efx_channel` for event/NAPI/RX/TX grouping, `struct efx_msi_context` for stable IRQ handler context, `struct efx_rss_context`, optional `struct efx_arfs_rule` and `struct efx_async_filter_insertion`, `struct efx_mtd_partition`, and `struct efx_nic`.

`struct efx_nic_type` is the main integration table. It contains lifecycle callbacks, reset, port, MCDI, interrupt, queue, event, filter, MTD, PTP, SR-IOV, VLAN, UDP tunnel, stats, and hardware property callbacks.

Inline helpers provide channel iteration, queue lookup, RX buffer lookup/wrapping, max frame size calculation, timestamp TX flag manipulation, TX fill-level approximations, supported feature union, and TX insert-buffer access with paranoid checks.

## Control Flow

Most driver code takes an `efx_nic` and dispatches through `efx->type` for hardware-specific operations. Channels group one event queue with at most one RX queue and several TX queues. Common code iterates channels with `efx_for_each_channel()`, accesses traffic or XDP channels by offsets, and uses queue type indexes to select checksum/high-priority/XDP TX queues.

The NIC state structure is organized by write frequency: rarely written configuration and lifecycle fields first, then frequently updated monitor, interrupt, stats, and drop counters. Locking contracts are documented in field comments: RTNL serializes device state, `mac_lock` protects port/MAC/PHY fields, `filter_sem` protects filter table existence, RFS has mutex/spinlock split, and stats updates use `stats_lock`.

## State and Persistence Behavior

This header defines nearly all long-lived in-memory driver state: PCI mapping, interrupt mode, queue arrays, DMA ring dimensions, RSS context, firmware vport ID, IRQ status, MCDI state, port/link/PHY state, XDP program pointer, filter table state, queue flush counters, SR-IOV counters, PTP data, VPD serial, and node/no-descriptor drop accounting. It also defines per-queue producer/consumer counters that persist across NAPI cycles and reset only during queue lifecycle operations.

## Dependencies and Integration Points

It includes Linux netdevice, ethtool, VLAN, PCI, workqueue, MTD, busy-poll, and XDP headers plus local `enum.h`, `bitfield.h`, and `filter.h`. Because most translation units include it, changes here affect TX, RX, event handling, ethtool, MCDI, PTP, MTD, SR-IOV, reset, and probe paths.

## Risks and Test Signals

The file's risk is structural coupling: field layout, callback semantics, and inline assumptions are used throughout the driver. Queue index helpers rely on correctly dimensioned channel offsets; incorrect `n_channels`, `tx_channel_offset`, or XDP channel counts can silently route to the wrong queues. Locking mistakes around `port_enabled`, `xdp_prog`, filter state, or RFS arrays can race with NAPI/workqueue paths. Test signals include all-config builds, sparse/lockdep/KCSAN runs, queue/channel dimension tests, XDP attach/detach, PTP channel allocation, MTD enabled/disabled builds, RFS enabled/disabled builds, and reset/open/close stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/net_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/nic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/nic.c

## Purpose

`nic.c` provides generic Siena/Falcon-architecture NIC support that is not tied to one queue operation: coherent DMA buffer helpers, interrupt request/free, self-test event/IRQ triggers, ethtool register dump sizing and collection, generic stats description/conversion, and correction of no-descriptor drop statistics.

## Important APIs, Types, and Functions

`efx_siena_alloc_buffer()` and `efx_siena_free_buffer()` allocate/free coherent DMA buffers used by interrupt status, stats, PTP sync flags, and similar firmware/hardware shared areas. Self-test helpers are `efx_siena_event_present()`, `efx_siena_event_test_start()`, and `efx_siena_irq_test_start()`.

Interrupt lifecycle is handled by `efx_siena_init_interrupt()` and `efx_siena_fini_interrupt()`. Register dump support is built from local `struct efx_nic_reg`, `struct efx_nic_reg_table`, `efx_nic_regs[]`, and `efx_nic_reg_tables[]`, with public `efx_siena_get_regs_len()` and `efx_siena_get_regs()`. Stats helpers are `efx_siena_describe_stats()`, `efx_siena_update_stats()`, and `efx_siena_fix_nodesc_drop_stat()`.

## Control Flow

Interrupt initialization first distinguishes legacy from MSI/MSI-X. Legacy mode requests one shared IRQ using the NIC type's legacy handler. MSI/MSI-X mode optionally allocates an RX CPU rmap for accelerated RFS, then requests one IRQ per channel using stable `efx_msi_context` entries. On failure, it frees the rmap and any IRQs already hooked. Finalization mirrors that path and clears `efx->irqs_hooked`.

Register dumping computes length by filtering static register and register-table lists against `efx->type->revision`. Collection reads single oword registers and table rows using access size implied by the table stride: 32-bit SRAM, 64-bit SRAM, 128-bit table entries, or interleaved 128-bit entries.

Stats conversion iterates an enabled mask, skips unnamed or width-zero entries as appropriate, reads little-endian 16/32/64-bit DMA fields from a stats buffer, and either stores or accumulates into caller-provided counters. No-descriptor drop correction subtracts drops observed while the netdev is down or on the first update after coming up.

## State and Persistence Behavior

This file mutates coherent buffer descriptors, `efx->irqs_hooked`, `net_dev->rx_cpu_rmap`, `last_irq_cpu`, per-channel `event_test_cpu`, and no-descriptor drop accounting fields. Register dump state is read-only hardware state. Stats conversion writes caller-owned arrays but does not allocate. Interrupt handlers themselves are supplied by the NIC type table.

## Dependencies and Integration Points

It depends on PCI DMA APIs, Linux IRQ APIs, optional `CONFIG_RFS_ACCEL` CPU rmap APIs, local bitfield/register definitions, `io.h` register accessors, and `struct efx_nic_type` callbacks. It integrates with self-tests, ethtool `get_regs`, stats collection, probe/open/close interrupt setup, and MCDI MAC stats allocation.

## Risks and Test Signals

Interrupt setup can partially succeed; failure unwind must match exactly the IRQ count already requested. RFS rmap setup adds another failure point after IRQ registration. Register dump tables intentionally skip write-only/read-clear/huge regions; changes to hardware register definitions need revision guards updated. Stats DMA width mismatches can corrupt ethtool output. Tests should cover legacy/MSI/MSI-X request failures, RFS rmap failures, ethtool register length vs payload size, stats conversion for all widths, and no-descriptor drops across interface down/up transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/nic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/nic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/nic.h

## Purpose

`nic.h` is the Siena/Falcon-architecture hardware interface header. It declares PHY type IDs, Siena MAC stat indexes, Siena-specific private NIC state, the exported Siena NIC type, and the farch queue/event/filter/interrupt/global-resource helper APIs implemented across the driver.

## Important APIs, Types, and Functions

The PHY enum names firmware PHY types such as TXC43128, 88E1111, SFX7101, QT202x, PM8358, and SFT9001. The Siena stat enum extends generic software stats with MAC TX/RX counters and ends at `SIENA_STAT_COUNT`.

`struct siena_nic_data` holds hardware-specific state behind `efx->nic_data`: back pointer, WoL filter ID, stats array, and optional SR-IOV state including VFs, VFDI channel/status buffer, VF buffer table base, local address broadcast lists, a mutex, and peer work.

The header declares farch TX/RX/event operations, filter table operations, interrupt handlers, DMA queue flush/reset helpers, stats controls, resource dimensioning, RSS indirection push/pull, register tests, and software event generation.

## Control Flow and Integration

NIC type tables use these prototypes to populate `struct efx_nic_type`. Common wrappers in `nic_common.h` then dispatch queue/event/filter operations through `efx->type`, landing in farch implementations declared here. Higher-level probe, reset, self-test, SR-IOV, RX, TX, and ethtool code include this header when they need Siena-specific operation names or private state.

## State and Persistence Behavior

The header defines persistent Siena private state and stat array size but does not store data itself. Many declared functions mutate hardware descriptor rings, event queues, filter tables, interrupt enable registers, flush counters, SRAM resource dimensions, WoL filters, and stats state.

## Dependencies, Risks, and Test Signals

It includes `nic_common.h` and `efx.h`, making it part of the cross-driver include graph. Risk comes from prototype drift and enum-index coupling: stat descriptors and arrays must match `SIENA_STAT_COUNT`, and NIC type callbacks must match declared signatures. Tests are mostly compile/integration: all Siena build configs, SR-IOV enabled/disabled, RFS enabled/disabled, register self-test, queue flush during reset, and filter insert/remove/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/nic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/nic_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/nic_common.h

## Purpose

`nic_common.h` provides architecture-neutral inline wrappers and declarations for common NIC operations. It bridges high-level driver code to `efx->type` callbacks for TX, RX, event queues, interrupts, buffers, register dumps, and stats while also defining revision IDs and low-level descriptor/event helpers.

## Important APIs, Types, and Functions

Revision constants include `EFX_REV_SIENA_A0`, `EFX_REV_HUNT_A0`, and `EFX_REV_EF100`; `efx_nic_rev()` returns `efx->type->revision`. Descriptor/event helpers include `efx_event()`, `efx_event_present()`, `efx_tx_desc()`, `efx_rx_desc()`, `efx_nic_tx_is_empty()`, and `efx_nic_may_push_tx_desc()`.

Wrapper groups dispatch to NIC type callbacks: `efx_nic_probe_tx()`, `efx_nic_init_tx()`, `efx_nic_remove_tx()`, `efx_nic_push_buffers()`, `efx_nic_probe_rx()`, `efx_nic_init_rx()`, `efx_nic_remove_rx()`, `efx_nic_notify_rx_desc()`, `efx_nic_generate_fill_event()`, `efx_nic_probe_eventq()`, `efx_nic_init_eventq()`, `efx_nic_fini_eventq()`, `efx_nic_remove_eventq()`, `efx_nic_process_eventq()`, and `efx_nic_eventq_read_ack()`.

It also declares interrupt lifecycle, coherent buffer helpers, register dump functions, stats helpers, and `EFX_MAX_FLUSH_TIME`.

## Control Flow

Common code uses this header instead of calling hardware implementations directly. Queue probe/init/remove/write and event queue operations become a single inline callback dispatch, allowing farch, EF10-like, or future hardware types to share upper-layer code. The TX push helper encodes a Siena/Falcon hardware-bug-aware rule: only push one descriptor when the completion path's empty marker suggests the NIC saw the queue empty.

## State and Persistence Behavior

Inline helpers read and write queue counters such as `empty_read_count`, descriptor ring buffers, event queue buffers, and event read pointers. They do not allocate resources directly except through callback dispatch. `efx_update_diff_stat()` enforces monotonic synthetic counters by only storing positive deltas.

## Dependencies, Risks, and Test Signals

The event-present helper intentionally checks both dwords for all-ones because DMA may not atomically write a full 64-bit event. Any optimization here risks event reordering bugs. The TX empty/push logic depends on producer/consumer counters and hardware errata. Tests should include event queue processing under DMA stress, TX completion/push paths, descriptor ring wraparound, all NIC type callback tables, interrupt self-tests, stats monotonicity, and flush timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/nic_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ptp.c

## Purpose

`ptp.c` implements hardware timestamping and PTP clock support for Siena-family SFC devices. It coordinates firmware-assisted PTP over MCDI, optional MAC TX timestamps, RX timestamp matching or inline timestamp reconstruction, PHC registration, PPS notification, timestamp configuration, PTP multicast filters, and workqueue-based deferred processing so slow MCDI operations do not run in the datapath.

## Important APIs, Types, and Functions

Local state is held in `struct efx_ptp_data`, which contains the PTP channel, RX/TX SKB queues, receive event pools, workqueues, multicast filter IDs, current `kernel_hwtstamp_config`, mode/enabled flags, time conversion callbacks, timestamp correction values, event fragments, synchronization DMA buffer, PHC clock info, PPS work, stats, and transmit function pointer. Matching/event structs are `struct efx_ptp_match`, `struct efx_ptp_event_rx`, and `struct efx_ptp_timeset`.

Public APIs include `efx_siena_ptp_defer_probe_with_channel()`, `efx_siena_ptp_channel()`, `efx_siena_ptp_is_ptp_tx()`, `efx_siena_ptp_tx()`, `efx_siena_ptp_get_mode()`, `efx_siena_ptp_change_mode()`, timestamp config/info getters/setters, `efx_siena_ptp_event()`, `efx_siena_time_sync_event()`, `__efx_siena_rx_skb_attach_timestamp()`, `efx_siena_ptp_start_datapath()`, `efx_siena_ptp_stop_datapath()`, stats describe/update, and `efx_siena_ptp_nic_to_kernel_time()`.

Time conversion helpers support seconds+nanoseconds, seconds+27-bit fraction, and seconds+quarter-nanoseconds formats. PHC operations are `efx_phc_adjfine()`, `efx_phc_adjtime()`, `efx_phc_gettime()`, `efx_phc_settime()`, and `efx_phc_enable()`.

## Control Flow

Probe is deferred through an extra PTP channel. `efx_siena_ptp_defer_probe_with_channel()` first checks support by issuing PTP disable; if it succeeds, it installs `efx_ptp_channel_type`. Channel pre-probe allocates `efx_ptp_data`, a coherent start flag buffer, workqueues, queues, event objects, conversion attributes, timestamp corrections, and, for primary functions, a PHC and PPS workqueue.

Starting PTP inserts required multicast filters for PTP event and general UDP ports, enables firmware PTP mode, resets event assembly, and resets frequency adjustment state. Mode changes disable/re-enable as needed, then require a baseline synchronization before marking the mode enabled.

Synchronization issues `MC_CMD_PTP_OP_SYNCHRONIZE` asynchronously with a DMA start flag. The driver waits briefly for firmware readiness, repeatedly writes compact host time into NIC memory for a bounded period, finishes the MCDI request, parses multiple timesets, rejects invalid or too-large/too-small windows, and derives the host PPS timestamp from the best firmware sample.

TX PTP packets are queued to a workqueue. Depending on hardware capability, the worker transmits through a dedicated timestamped TX queue or linearizes/checksums/copies the packet into `MC_CMD_PTP_OP_TRANSMIT` and returns the firmware timestamp to the socket. RX PTP packets are queued by the extra channel's `receive_skb` hook. For non-inline timestamping, firmware PTP events are assembled from fragments, placed in an event list, matched by UUID/sequence, and delivered when matched or timed out. For inline timestamping, RX SKB timestamp attachment reconstructs full time from packet minor timestamp plus the latest sync event major/minor.

## State and Persistence Behavior

Persistent state lives in `efx->ptp_data`, `efx->extra_channel_type[EFX_EXTRA_CHANNEL_PTP]`, PTP multicast filter IDs, PHC registration, MCDI firmware PTP enable state, queued SKBs/events, timestamp corrections, synchronization stats, and per-channel sync event state. Workqueues serialize slow TX/RX/timing tasks. Datapath stop temporarily disables sync events, stops PTP, flushes queued RX/TX packets, and returns pending event objects to the free list.

## Dependencies and Integration Points

This file depends on Linux PTP clock/PPS APIs, skb timestamp APIs, IPv4/UDP parsing, MCDI PTP commands, filter insertion/removal, TX enqueue helpers, RX timestamp attachment in `rx.c`, event processing in farch code, and NIC type callbacks for host-time writes, timestamp sync events, and timestamp config validation.

## Risks and Test Signals

Risk areas include event fragment ordering, RX packet/event matching races, bounded event pool overflow, timestamp wrap reconstruction from partial MAC timestamps, synchronization quality filtering, PPS workqueue lifetime, PHC registration only on primary functions, and mode changes during netdev stop/start. Tests should cover PTP unsupported firmware, primary/secondary functions, V1/V2/enhanced matching, event-before-packet and packet-before-event ordering, timeout delivery without timestamp, MAC TX vs MC TX paths, PHC adjfine/adjtime/get/set, PPS enable, reset/restart, and timestamp config validation across supported filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ptp.h

## Purpose

`ptp.h` declares the Siena driver's PTP and hardware timestamping interface. It lets the rest of the driver probe PTP channels, configure timestamping, route PTP packets/events, attach RX timestamps, and start or stop datapath timestamp services.

## Important APIs, Types, and Functions

The header declares probe/channel access (`efx_siena_ptp_defer_probe_with_channel()`, `efx_siena_ptp_channel()`), timestamp config/info operations, PTP TX classification and queuing, mode get/change, MCDI PTP event and time-sync event handling, PTP stats describe/update, RX SKB timestamp attachment, datapath start/stop, MAC TX timestamp capability detection, and TX queue NIC-time conversion.

`efx_rx_skb_attach_timestamp()` is the one inline helper: it calls the heavier attachment function only when `channel->sync_events_state == SYNC_EVENTS_VALID`.

## Control Flow and Integration

RX delivery calls the inline timestamp helper after building an SKB. TX paths use `efx_siena_ptp_is_ptp_tx()` to decide whether a UDP PTP event packet should be diverted to the PTP worker. Event queue processing calls `efx_siena_ptp_event()` for PTP events and `efx_siena_time_sync_event()` for sync events. Netdev timestamp ioctls/ethtool use the config/info methods, while open/close/reset paths use datapath start/stop.

## State and Persistence Behavior

The header exposes no storage but assumes `efx->ptp_data` and channel sync timestamp fields are maintained by `ptp.c`. Its inline helper intentionally avoids work on channels without valid sync events.

## Dependencies, Risks, and Test Signals

It includes `linux/net_tstamp.h` and `net_driver.h`, making it dependent on timestamp config types and channel/NIC state. Contract risks are lifetime and feature gating: callers must handle `-EOPNOTSUPP` when `ptp_data` is absent and must only attach inline RX timestamps when sync state is valid. Tests should compile PTP callers under relevant configs and exercise TX diversion, RX timestamp attachment, event dispatch, and datapath stop/start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/rx.c

## Purpose

`rx.c` is the Siena receive packet processing path. It consumes completed RX descriptors after event handling, validates packet lengths/fragments, DMA-syncs data, pipelines prefetch and delivery, runs XDP when attached, builds SKBs or GRO fragments, attaches hardware timestamps, handles loopback self-test packets, and updates RX error/XDP counters.

## Important APIs, Types, and Functions

`efx_siena_rx_packet()` is called by NIC-specific event code when a packet completion arrives. It records flags, validates length and fragment count, handles explicit discard, syncs DMA buffers, adjusts offsets past the RX prefix, syncs tail fragments, recycles pages, and stores a pending packet in `channel->rx_pkt_*` after flushing the previously pending packet.

`__efx_siena_rx_packet()` is the second-stage delivery function. It reads prefix length if needed, diverts loopback self-test packets, runs `efx_do_xdp()`, clears checksum flags if RX checksum offload is disabled, chooses GRO for TCP packets without a special channel receiver, or calls `efx_rx_deliver()` to allocate and submit an SKB.

Local helpers include `efx_rx_packet__check_len()`, `efx_rx_mk_skb()`, `efx_rx_deliver()`, and `efx_do_xdp()`.

## Control Flow

The RX path is deliberately pipelined. Completion of packet N first calls `efx_rx_flush_packet()` so packet N-1 is delivered after its header prefetch had time to complete. The newly completed packet is stored in channel fields for the next flush. Multi-fragment packets are validated against `EFX_RX_MAX_FRAGS`, `efx->rx_dma_len`, and `efx->rx_scatter`.

XDP runs only for single-fragment packets. On `XDP_PASS`, any data pointer offset is reflected in RX buffer offset/length and the saved RX prefix is restored before the shifted Ethernet header. `XDP_TX` converts the XDP buffer to a frame and submits through `efx_siena_xdp_tx_buffers()`. `XDP_REDIRECT` calls `xdp_do_redirect()`. Drop/abort/invalid actions free the RX buffer and update counters.

SKB delivery copies header bytes into a linear SKB area and appends remaining page fragments. It sets checksum state, RX queue index, NAPI ID, optional timestamp, and either hands the SKB to a channel-specific receiver such as PTP or to `netif_receive_skb()`. GRO uses `napi_get_frags()` and fills skb frags directly.

## State and Persistence Behavior

This file updates `rx_queue->rx_packets`, RX buffer flags/lengths/offsets/page ownership, per-channel pending packet fields, RX error counters, XDP counters, `efx->n_rx_noskb_drops`, and SKB timestamp/checksum/hash metadata. Page ownership transfers to SKB, XDP TX/redirect, recycle ring, or free paths depending on action.

## Dependencies and Integration Points

It depends on RX queue allocation/refill/recycle helpers from `rx_common.c`, XDP and BPF APIs, TX XDP helper declarations, PTP timestamp attachment from `ptp.h`, loopback self-test hooks, NAPI/GRO, Linux checksum/SKB helpers, and NIC type RX prefix layout fields in `struct efx_nic_type`.

## Risks and Test Signals

Risk areas include page ownership on every XDP outcome, prefix restoration after XDP data adjustment, multi-fragment validation, checksum flag consistency, GRO fragment accounting, and timestamp attachment only when sync events are valid. Tests should cover single and scattered RX, overlength completions, explicit discard completions, XDP PASS/DROP/ABORTED/TX/REDIRECT including failure injection, RX checksum toggling, PTP channel receive hook, loopback self-test, and memory leak checks around SKB allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/rx_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/rx_common.c

## Purpose

`rx_common.c` implements shared Siena RX queue lifecycle, page allocation/recycling, descriptor refill, GRO fragment delivery support, RSS indirection defaults, filter spec hashing/equality, filter table probe/remove, and optional accelerated RFS rule insertion/expiry. It is the resource-management counterpart to packet delivery in `rx.c`.

## Important APIs, Types, and Functions

RX queue lifecycle APIs are `efx_siena_probe_rx_queue()`, `efx_siena_init_rx_queue()`, `efx_siena_fini_rx_queue()`, and `efx_siena_remove_rx_queue()`. Buffer/page helpers include `efx_siena_recycle_rx_pages()`, `efx_siena_discard_rx_packet()`, `efx_siena_free_rx_buffers()`, `efx_siena_rx_slow_fill()`, `efx_siena_rx_config_page_split()`, and `efx_siena_fast_push_rx_descriptors()`.

Delivery support includes `efx_siena_rx_packet_gro()` and `efx_siena_set_default_rx_indir_table()`. Filter helpers are `efx_siena_filter_is_mc_recipient()`, `efx_siena_filter_spec_equal()`, `efx_siena_filter_spec_hash()`, `efx_siena_probe_filters()`, and `efx_siena_remove_filters()`. Under `CONFIG_RFS_ACCEL`, it adds ARFS hash/rule helpers, `efx_siena_filter_rfs()`, worker `efx_filter_rfs_work()`, and `__efx_siena_filter_rfs_expire()`.

## Control Flow

Queue probe rounds requested RX entries up to a power-of-two minimum, allocates the software buffer ring, and delegates hardware descriptor allocation to `efx_nic_probe_rx()`. Init resets producer/consumer counters, creates the recycle ring, computes max fill and refill trigger based on `rx_refill_threshold`, registers XDP RXQ info, and initializes the hardware RX queue.

Fast refill checks fill level against `fast_fill_trigger`, allocates batches of pages, maps them for DMA, slices pages into one or more RX buffers with XDP headroom and alignment, marks the last buffer in each page, and notifies hardware when `added_count` advances. If allocation or mapping fails in atomic context, it schedules a slow-fill timer that generates a refill event later.

Page recycling stores only fully consumed pages whose last buffer has completed. Reuse requires `page_count(page) == 1`; otherwise the DMA mapping is unmapped and the page reference dropped. Queue finalization deletes slow-fill timers, frees outstanding descriptor pages, drains the recycle ring, and unregisters XDP RXQ info.

Filter probe holds `mac_lock` and `filter_sem`, delegates hardware filter table probe, and optionally allocates per-channel RFS flow-id arrays. RFS insertion dissects skb flow keys, builds an RX filter spec, reserves an in-flight slot, records/updates an ARFS hash rule, schedules asynchronous insertion, and later records filter IDs per channel for expiry.

## State and Persistence Behavior

Persistent state includes RX buffer arrays, descriptor rings, page recycle rings and counters, fill thresholds, slow-fill timers, XDP RXQ registration, RSS indirection table contents, filter table state, per-channel RFS arrays/counters, and `efx->rps_slot_map`/hash table. DMA mappings are held in `struct efx_rx_page_state` at the start of each allocated page.

## Dependencies and Integration Points

It depends on page allocator and DMA APIs, XDP RXQ registration, NAPI GRO, RPS/RFS APIs, flow dissector, filter APIs from `filter.h`, NIC type RX/filter callbacks, and queue/channel definitions in `net_driver.h`. It integrates with `rx.c`, farch event completion, netdev RFS hooks, XDP attach lifecycle, and reset/open/close queue management.

## Risks and Test Signals

Risk areas include page reference accounting, recycle ring wrap logic, DMA unmap exactly once per page, partial page insertion on refill failure, slow-fill timer cancellation, XDP RXQ unregister on init failure, RFS in-flight slot leaks, and filter hash equality staying aligned with `struct efx_filter_spec`. Tests should include RX refill under memory pressure, IOMMU DMA mapping errors, queue fini with outstanding descriptors, page recycle reuse/failure/full counters, RFS concurrent insert/expire/remove, filter table probe failure unwind, and XDP attach/detach around RX queue reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/rx_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/rx_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/rx_common.h

## Purpose

`rx_common.h` declares shared RX queue, buffer, refill, GRO, RSS, filter, and RFS helpers for the Siena driver. It is the public interface between NIC-specific event code, packet delivery, queue lifecycle, and filter management.

## Important APIs, Types, and Functions

Constants include `EFX_RX_PREFERRED_BATCH`, `EFX_RX_MAX_FRAGS`, and `EFX_RECYCLE_RING_SIZE_10G`. Inline helpers are `efx_rx_buf_va()` for page+offset virtual addresses, `efx_rx_buf_hash()` for reading the RX prefix hash with aligned or byte-wise access, and `efx_sync_rx_buffer()` for DMA sync before CPU access.

The declared API covers slow-fill events, page recycling/discard, RX queue probe/init/fini/remove, freeing RX buffers, page split configuration, fast descriptor pushing, GRO delivery, default RSS indirection setup, filter recipient/equality/hash helpers, optional RFS helpers, and filter table probe/remove.

## Control Flow and Integration

RX queue lifecycle code calls probe/init/fini/remove in order. Event processing calls packet completion in `rx.c`, then refill logic uses `efx_siena_fast_push_rx_descriptors()`. Delivery code calls recycle/free/GRO helpers. Filter table setup and optional RFS hooks use the filter helpers declared here.

## State and Persistence Behavior

The header itself has no storage but exposes helpers that mutate RX queue counters, buffer page ownership, DMA sync state, RSS context tables, and filter/RFS state. Inline hash reading depends on `efx->rx_packet_hash_offset` being valid for NICs that provide a prefix hash.

## Dependencies, Risks, and Test Signals

The header depends on `net_driver.h` definitions and compile-time unaligned access support. Risks include misuse of `efx_rx_buf_hash()` when no valid prefix hash exists, incorrect fragment-count assumptions from `EFX_RX_MAX_FRAGS`, and callers forgetting that descriptor refill needs external serialization. Tests should cover builds with and without efficient unaligned access, RX hash extraction, queue refill serialization, and `CONFIG_RFS_ACCEL` prototype coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/rx_common.h -->
