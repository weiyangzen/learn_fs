# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/tg3.c lines 1-10167

## Scope

This chunk covers the first 10,167 lines of the Broadcom Tigon3 Ethernet driver. It includes driver metadata and PCI IDs, low-level MMIO/PCI config accessors, APE/ASF management-firmware coordination, PHY and MDIO control, NVRAM and firmware loading helpers, power-management transitions, copper/fiber link setup, PTP clock support, register dumps and error recovery, NAPI/interrupt handling, TX/RX datapaths, ring allocation, multicast/RSS setup, and the beginning of the hardware reset path.

The chunk ends inside `tg3_reset_hw()` while applying device-specific reset workarounds, programming DMA/GRC mode, and starting a Dell 5762 MRRS workaround. Later chunks own the rest of reset programming and higher-level open/probe/ethtool integration.

## Purpose

This code is the hardware-facing core of `tg3`. It turns Linux `net_device`, PHYLIB/MDIO, NAPI, DMA, PTP, PCI, and firmware-loading services into a working network datapath for many Broadcom/Altima/SysKonnect/Apple Tigon3-family PCI and PCIe NICs.

Major responsibilities in this chunk are:

- Define supported PCI device IDs, firmware names, default ring sizes, offload limits, and ethtool statistic/test strings.
- Abstract direct MMIO, indirect PCI-config register windows, mailboxes, and NIC SRAM accesses behind `tw32*()`/`tr32*()` helpers with chip-specific posted-write flushes and hardware bug workarounds.
- Coordinate with APE/ASF management firmware through shared registers, locks, heartbeats, driver-state events, and SRAM mailboxes.
- Initialize and operate MDIO/PHYLIB or legacy PHY control paths for copper, fiber, SGMII/SerDes, EEE, loopback, WOL, low power, and many chip errata.
- Read/write NVRAM/EEPROM and load RX/TX CPU or TSO firmware blobs.
- Allocate, initialize, recycle, and free DMA-coherent TX rings, RX producer rings, RX return rings, status blocks, and hardware stats.
- Run the packet datapath: TX descriptor build, checksum/TSO/vlan/timestamp offloads, DMA bug workarounds, TX completion, RX buffer allocation/recycling, checksum/VLAN/hardware timestamp handling, GRO delivery, and NAPI interrupt moderation.
- Reset, halt, and reinitialize hardware blocks in a sequence that preserves PCI state, statistics, management firmware state, and driver-visible link state.

## Important APIs, Types, and Functions

### Driver Metadata and Flags

- `tg3_pci_tbl[]` lists the large set of supported PCI IDs and per-device `driver_data` flags such as `TG3_DRV_DATA_FLAG_10_100_ONLY` and `TG3_DRV_DATA_FLAG_5705_10_100`.
- `_tg3_flag()`, `_tg3_flag_set()`, `_tg3_flag_clear()`, and `tg3_flag*` macros wrap bit operations on `tp->tg3_flags` using enum names from `tg3.h`.
- Constants in the file define the stable ABI-ish driver version (`3.137`), firmware names (`tigon/tg3.bin`, `tg357766.bin`, `tg3_tso.bin`, `tg3_tso5.bin`), ring sizing, default coalescing/debug behavior, RX copy thresholds, MTU limits, DMA alignment overhead, and reset kinds.
- `ethtool_stats_keys[]` and `ethtool_test_keys[]` define the visible statistic and self-test names used by later ethtool callbacks.

### Register, Mailbox, SRAM, and APE Access

- `tg3_write32()`, `tg3_read32()`, `tg3_write_flush_reg32()`, `tg3_write_indirect_reg32()`, and `tg3_read_indirect_reg32()` provide direct and indirect register access. Indirect access serializes through `tp->indirect_lock`.
- `tg3_write_indirect_mbox()`, `tg3_read_indirect_mbox()`, `tg3_write32_tx_mbox()`, and 5906 mailbox helpers hide mailbox address quirks, duplicated TX mailbox writes, and required readbacks.
- `_tw32_flush()` and `tw32_mailbox_flush()` centralize posted-write flush policy for PCIX/ICH/mailbox-reordering hardware bugs.
- `tg3_write_mem()` and `tg3_read_mem()` access NIC SRAM through either PCI config windows or MMIO memory windows, reset the window base to zero, and special-case 5906 statistics SRAM holes.
- `tg3_ape_lock_init()`, `tg3_ape_lock()`, `tg3_ape_unlock()`, `tg3_ape_event_lock()`, `tg3_ape_send_event()`, and `tg3_ape_driver_state_change()` implement host-driver arbitration and event delivery to the APE management processor. The optional HWMON scratchpad reader uses the same event-status protocol.

### Interrupts, NAPI, and Locking

- `tg3_disable_ints()`, `tg3_enable_ints()`, `tg3_int_reenable()`, and `tg3_has_work()` manipulate interrupt mask/mailbox state and decide whether pending TX/RX/link work exists.
- `tg3_msi_1shot()`, `tg3_msi()`, `tg3_interrupt()`, and `tg3_interrupt_tagged()` are the primary IRQ handlers for one-shot MSI, MSI, legacy INTx, and tagged-status modes.
- `tg3_poll()` and `tg3_poll_msix()` are NAPI pollers. They process errors/link changes, run TX completion and RX receive work, complete NAPI, re-enable interrupts, and schedule reset work on TX recovery.
- `tg3_irq_quiesce()`, `tg3_full_lock()`, and `tg3_full_unlock()` coordinate the main spinlock with IRQ synchronization during reset/shutdown and PTP operations.
- `tg3_napi_init()`, `tg3_napi_enable()`, `tg3_napi_disable()`, and `tg3_napi_fini()` bind `struct tg3_napi` instances to netdev TX/RX queues and IRQ vectors.

### PHY, MDIO, Link, Power, and Firmware

- `__tg3_readphy()` and `__tg3_writephy()` drive the MAC MI management interface, disable auto-poll around transactions, use APE PHY locks, and poll `MAC_MI_COM` for completion.
- `tg3_mdio_init()`, `tg3_mdio_start()`, and `tg3_mdio_fini()` allocate/register/free a PHYLIB `mii_bus`, determine PHY address for 5717+/SSB/normal devices, and annotate PHY interface/dev_flags based on the PHY ID.
- `tg3_phy_init()`, `tg3_phy_start()`, `tg3_phy_stop()`, and `tg3_phy_fini()` attach and manage PHYLIB devices.
- `tg3_phy_reset()`, `tg3_phy_reset_5703_4_5()`, `tg3_phy_apply_otp()`, `tg3_phy_toggle_apd()`, `tg3_phy_toggle_automdix()`, and `tg3_phy_set_wirespeed()` apply PHY errata, reset sequencing, auto-power-down, Auto-MDIX, one-time-programmed tuning, and jumbo support.
- `tg3_setup_copper_phy()`, `tg3_setup_fiber_phy()`, `tg3_setup_fiber_mii_phy()`, `fiber_autoneg()`, `tg3_fiber_aneg_smachine()`, and `tg3_serdes_parallel_detect()` implement legacy copper and fiber link setup without PHYLIB, including flow-control resolution and SerDes autonegotiation state machines.
- `tg3_adjust_link()` is the PHYLIB link callback, updating MAC port mode, duplex, flow control, TX lengths, and link-report state.
- `tg3_power_up()`, `tg3_power_down_prepare()`, `tg3_power_down()`, `tg3_power_down_phy()`, `tg3_frob_aux_power()`, and `tg3_frob_aux_power_5717()` control PCI power states, Vaux/Vmain GPIO switching, WOL preparation, low-power PHY behavior, and management-firmware handoff.
- `tg3_nvram_read()`, `tg3_nvram_read_be32()`, and `tg3_nvram_write_block()` plus buffered/unbuffered/EEPROM helpers provide NVRAM access with software arbitration and endian normalization.
- `tg3_load_firmware_cpu()`, `tg3_load_5701_a0_firmware_fix()`, `tg3_load_57766_firmware()`, and `tg3_load_tso_firmware()` download firmware fragments into RX/TX CPU scratch memory and start the appropriate CPU.

### Datapath and Ring Management

- `tg3_tx_avail()`, `tg3_tx_frag_set()`, `tg3_tx_skb_unmap()`, `tigon3_dma_hwbug_workaround()`, `tg3_tso_bug()`, `__tg3_start_xmit()`, and `tg3_start_xmit()` build TX descriptors, map SKB linear/frags, handle checksum/TSO/VLAN/timestamp flags, split descriptors by DMA limits, and use GSO or copy-linear fallbacks for 4GB/40-bit/short-DMA/TSO hardware bugs.
- `tg3_tx()` reclaims TX completions, unmaps DMA, completes hardware TX timestamps immediately or through the PTP aux worker, accounts completed bytes/packets, and wakes stopped queues with memory barriers.
- `tg3_alloc_rx_data()`, `tg3_recycle_rx()`, `tg3_rx()`, `tg3_rx_prodring_xfer()`, and `tg3_rx_data_free()` allocate RX backing memory, recycle descriptors, process RX return entries, validate packet length/errors, apply RX checksum/VLAN/PTP timestamp metadata, deliver SKBs through GRO, and refill producer rings.
- `tg3_rx_prodring_init()`, `tg3_rx_prodring_alloc()`, `tg3_rx_prodring_free()`, `tg3_rx_prodring_fini()`, `tg3_mem_tx_acquire()`, `tg3_mem_rx_acquire()`, `tg3_alloc_consistent()`, `tg3_free_consistent()`, `tg3_init_rings()`, and `tg3_free_rings()` own coherent and streaming-DMA ring lifecycle.
- `tg3_tx_rcbs_init()`, `tg3_rx_ret_rcbs_init()`, `tg3_rings_reset()`, and `tg3_setup_rxbd_thresholds()` program NIC SRAM BDINFO entries, hardware status block addresses, mailboxes, and RX replenishment thresholds.

### PTP, RX Mode, RSS, Reset, and Diagnostics

- `tg3_refclk_read()`, `tg3_refclk_write()`, `tg3_ptp_adjfine()`, `tg3_ptp_adjtime()`, `tg3_ptp_gettimex()`, `tg3_ptp_settime()`, `tg3_ptp_enable()`, `tg3_ptp_ts_aux_work()`, `tg3_ptp_init()`, `tg3_ptp_resume()`, and `tg3_ptp_fini()` expose the hardware reference clock as a PHC, support frequency/time adjustments, one-shot perout, and TX/RX hardware timestamp conversion.
- `tg3_dump_state()` and `tg3_dump_legacy_regs()` snapshot register/status/NAPI state after DMA, flow-attention, MSI, or TX timeout errors.
- `tg3_process_error()` and `tg3_tx_recover()` mark real hardware errors and schedule reset work.
- `tg3_set_loopback()`, `tg3_mac_loopback()`, `tg3_phy_lpbk_set()`, `tg3_fix_features()`, and `tg3_set_features()` implement internal MAC loopback feature toggling and TSO feature masking for jumbo frames on 5780-class devices.
- `__tg3_set_mac_addr()`, `tg3_set_mac_addr()`, `tg3_set_multi()`, `__tg3_set_rx_mode()`, `tg3_rss_check_indir_tbl()`, and `tg3_rss_write_indir_tbl()` program MAC filters, multicast hash filters, promiscuous mode, VLAN tag retention, unicast limits, and RSS indirection.
- `tg3_abort_hw()`, `tg3_chip_reset()`, `tg3_halt()`, and the beginning of `tg3_reset_hw()` stop hardware blocks, preserve/restore PCI state, quiesce interrupts, reset the chip core, reprobe ASF state, reload ring state, and apply many chip-specific reset workarounds.

## Control Flow

The low-level access path is selected through function pointers in `struct tg3`. Most hardware programming calls use `tw32()`, `tw32_f()`, `tw32_mailbox()`, or `tr32()` instead of raw MMIO, so writes can be routed through direct, indirect, flushed, reordered, or 5906 mailbox-specific implementations.

The PHY path is split. PHYLIB-capable devices allocate an MDIO bus in `tg3_mdio_init()`, attach the netdev to the PHY in `tg3_phy_init()`, and use `tg3_adjust_link()` as the asynchronous link callback. Legacy paths call `tg3_setup_phy()`, which dispatches to copper, fiber TBI, or MII-SerDes setup. Link setup updates `tp->mac_mode`, active speed/duplex/flow-control fields, and carrier state; `tg3_link_report()` logs changes and reports them to management firmware.

The packet TX path is `tg3_start_xmit()` -> `__tg3_start_xmit()`. The inner function maps the SKB, prepares offload flags, handles VLAN/TSO/timestamp special cases, detects DMA hardware bug windows, possibly falls back to GSO or copy-linear workarounds, updates software producer index, and returns. The outer wrapper respects `netdev_xmit_more()` and rings the TX producer mailbox when needed.

The RX path is interrupt/NAPI driven. IRQ handlers mask or acknowledge interrupts and schedule NAPI. `tg3_poll()`/`tg3_poll_msix()` call `tg3_poll_work()`, which first reclaims TX and then calls `tg3_rx()` if the hardware status block says RX return entries are pending. RX consumes a separate return/status ring written by the chip, obtains the original buffer through the opaque cookie, either recycles or replaces the producer-ring buffer, builds an SKB, attaches checksum/VLAN/timestamp metadata, and delivers through `napi_gro_receive()`.

Reset/shutdown control begins with `tg3_halt()` or `tg3_reset_hw()`. Both stop management firmware communication, write ASF/APE state signatures, disable interrupts, stop DMA/MAC/RCV/SND hardware blocks, reset the core through `tg3_chip_reset()`, restore MAC addresses and PCI state, save statistics across resets, rebuild rings, and then continue into later reset initialization outside this chunk.

## State and Persistence Behavior

The central runtime state is `struct tg3 *tp`, which stores memory-mapped BARs, PCI device pointers, flags, PHY flags, MAC/RX/TX mode shadow registers, link configuration, ring counts, coalescing parameters, DMA control words, NVRAM geometry, APE heartbeat counters, PTP adjustment, firmware pointers, per-vector `struct tg3_napi` arrays, and previous statistics snapshots.

Persistent driver-visible state in this chunk includes:

- `tp->tg3_flags` and `tp->phy_flags`, which gate most chip-family behavior, errata paths, offloads, management firmware integration, and power decisions.
- Shadowed register values such as `tp->mac_mode`, `tp->rx_mode`, `tp->tx_mode`, `tp->grc_mode`, `tp->pci_clock_ctrl`, `tp->grc_local_ctrl`, and `tp->dma_rwctrl`.
- Link state in `tp->link_up`, `tp->old_link`, `tp->link_config.active_*`, `tp->link_config.rmt_adv`, and EEE settings in `tp->eee`.
- Ring cursors in `struct tg3_napi`: `tx_prod`, `tx_cons`, `rx_rcb_ptr`, producer-ring indices, mailbox addresses, status block pointers, and per-vector dropped counters.
- DMA mappings and backing allocations in TX buffer arrays, RX `ring_info` arrays, RX/TX descriptor rings, status blocks, and `tp->hw_stats`.
- Management-firmware state in NIC SRAM mailboxes, APE host segment registers, heartbeat count, and function/Vaux GPIO message bits.
- NVRAM write state through `tp->nvram_lock_cnt`, flash page geometry, and the software-arbitration registers.
- PTP state in the hardware reference clock, `tp->ptp_adjust`, `tp->pre_tx_ts`, `tp->tx_tstamp_skb`, and retry counters.

Hardware and firmware state is intentionally rederived on reset. `tg3_halt()` saves net and ethtool stats before clearing hardware stats, while `tg3_chip_reset()` restores PCI command/cacheline/latency/MSI/PCI-X state and reprobes ASF enablement from SRAM. Ring memory is persistent only for the lifetime of the device open state and is rebuilt by `tg3_init_rings()` after hardware reset.

## Dependencies and Integration Points

This chunk depends on `tg3.h` for register definitions, descriptor layouts, flag enums, firmware header types, chip revision helpers, and `struct tg3`/`struct tg3_napi` fields.

Kernel subsystem integration points include:

- PCI core: config space access, power state transitions, PCIe capability access, MSI capability restoration, device presence/error-state checks, and DMA APIs.
- Netdev core: `struct net_device`, TX queues, carrier state, NAPI, GRO, checksum offloads, VLAN accel tags, multicast/unicast address lists, feature toggles, and TX timeout callbacks.
- PHY/MDIO: `mii_bus`, `phy_device`, PHYLIB attach/start/stop/disconnect, MII register helpers, Broadcom PHY flags, and EEE linkmode conversion helpers.
- Firmware loader: `struct firmware` data is parsed as `struct tg3_firmware_hdr` fragments and written to device CPU scratch areas.
- PTP/timestamping: `ptp_clock_info`, `ptp_clock_register` users in later code, system timestamp bracketing, SKB timestamp APIs, and hardware timestamp feature flags.
- Workqueues and interrupts: reset scheduling through `tp->reset_task`, IRQ synchronization, NAPI scheduling, and optional netpoll controller.
- SSB and platform quirks: SSB GigE PHY address lookup, DMI/PCI subsystem IDs, ROBOSWITCH, APE/NCSI/HWMON conditionals, and chip-family workarounds.

The code also integrates with management firmware through ASF/APE SRAM mailboxes and host/APE shared registers. Power-down and reset paths are careful to signal driver start/unload/WOL states so side-band management and WOL can survive host driver transitions.

## Risks and Edge Cases

- Many routines are sequencing-sensitive hardware code. Missing `tw32_f()`, `wmb()`, `rmb()`, `smp_wmb()`, or delay calls can create races between CPU, PCI posted writes, DMA engines, and hardware status blocks.
- Several helper comments say `tp->lock is held`; violating this can corrupt PHY, SRAM, NVRAM, reset, PTP, or firmware state because many hardware windows and shadow fields are not independently synchronized.
- APE lock acquisition writes the grant register to revoke a failed request. If APE firmware or hardware semantics differ, lock recovery could interact badly with concurrent management firmware.
- `tg3_load_firmware_cpu()` trusts firmware header lengths enough to walk fragments within `tp->fw->data`; malformed firmware could risk out-of-bounds reads if earlier validation is incomplete.
- `tg3_nvram_write_block_unbuffered()` mutates `offset` by whole pages after copying only `size = min(len, pagesize)`, which relies on callers providing dword-aligned lengths and offsets and on page-local writes being intended.
- `tg3_tx()` treats unexpected NULL SKBs or descriptor reuse as evidence of mailbox/MMIO reordering and schedules recovery. False positives reset the NIC; false negatives could leave TX stuck.
- Hardware TX timestamping stores only one outstanding timestamp SKB in `tp->tx_tstamp_skb`; concurrent timestamp requests are serialized by `pre_tx_ts` checks but dropped/delayed behavior depends on timing.
- RX small-packet copy path recycles the old DMA buffer before allocating/copying into a new SKB. Allocation failure increments drop counters but relies on recycling already having preserved ring capacity.
- RSS refill uses vector 1 as a refill worker and moves producer-ring entries back to the hardware ring. Ordering between `rx_refill`, producer index copies, and NAPI scheduling is subtle.
- `tg3_start_xmit()` writes the producer mailbox even when the inner transmit returned `NETDEV_TX_BUSY` if prior packets were queued and `netif_xmit_stopped()` is true. This is intentional for progress but should be preserved carefully.
- The code contains many chip-revision-specific branches; changing generic paths can regress old PCI/PCI-X, 5701/5704/5705, 5780, 57765, 5717/5719/5720, 5762, 5906, SSB, SerDes, FET, or APE-equipped devices differently.
- Reset code temporarily clears `CHIP_RESETTING` and synchronizes IRQs while memory-enable or MSI bits may be unstable. Any additional register access in IRQ paths must respect that flag.
- The requested chunk ends mid-function in `tg3_reset_hw()`, so any conclusions about full reset behavior must be reconciled with the next chunk.

## Test Signals

Useful validation signals for this chunk include:

- Probe/init on representative chips should select the right direct/indirect/MMIO mailbox accessors and complete `tg3_mdio_init()` with the expected PHY address and interface mode.
- Link tests should cover PHYLIB copper, legacy copper, hardware fiber autoneg, software fiber autoneg, MII-SerDes SGMII, forced speed/duplex, EEE enabled/disabled, WOL low-power advertisement, and parallel-detect fallback.
- TX tests should exercise checksum offload, TSO/GSO fallback, VLAN-tagged TSO/checksum software fallback, fragmented SKBs, `netdev_xmit_more()`, queue stop/wake, DMA mapping failure, and 4GB/40-bit/short-DMA workaround paths.
- RX tests should cover standard and jumbo rings, RX copy threshold behavior, checksum-valid and checksum-invalid descriptors, VLAN stripping, MTU oversize rejection, PTP RX timestamps, GRO delivery, refill thresholds, and RSS refill transfer.
- Interrupt tests should cover INTx, MSI, one-shot MSI, tagged status, shared interrupt no-work paths, netpoll polling, interrupt disable/enable around reset, and NAPI completion races.
- Reset/power tests should cover normal reset, TX timeout reset, DMA/error-attention reset, suspend/shutdown with WOL, no-WOL powerdown, APE/ASF enabled state changes, PCI channel offline, and stat preservation across reset.
- NVRAM tests should cover EEPROM fallback reads/writes, NVRAM software arbitration timeout, buffered and unbuffered flash writes, Atmel address translation, write-protect GPIO handling, and endian-correct `tg3_nvram_read_be32()`.
- PTP tests should verify PHC read/set/adjfine/adjtime, one-shot perout validation, TX timestamp retry completion, RX timestamp conversion, and clock reinitialization after `tg3_ptp_resume()`.
- Diagnostics should produce register dumps on TX timeout or real DMA/MSI/flow-attention errors and should suppress dumps when PCI channel state reports an error.
