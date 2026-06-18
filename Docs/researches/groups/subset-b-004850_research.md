# subset-b-004850 mt76 / mt7603 Research

Grouped research for the listed mt76 shared core and mt7603 driver files. Each section preserves the source path in the title and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/eeprom.c

## Purpose
Shared mt76 EEPROM, device-tree calibration, MAC-address override, and per-rate/per-path transmit-power-limit support. It abstracts board data from inline DT properties, MTD partitions, nvmem cells, and power-limit child nodes so individual mt76 chipset drivers can initialize EEPROM buffers and compute regulatory/board power caps without duplicating parsing logic.

## Important APIs, Types, And Functions
- `enum mt76_sku_type` classifies plain rate limits, path backoff limits, and beamforming backoff-offset tables.
- `mt76_get_of_data_from_mtd()` reads board EEPROM bytes from a DT `mediatek,mtd-eeprom` phandle plus offset, handles MTD bitflips as success, optional big-endian word conversion, and records testmode MTD metadata when enabled.
- `mt76_get_of_data_from_nvmem()` reads an `eeprom`-style nvmem cell and copies exactly the requested length.
- `mt76_eeprom_init()` allocates `dev->eeprom.data`, sets `dev->eeprom.size`, and returns whether OF/MTD/nvmem data was found.
- `mt76_eeprom_override()` fills `phy->macaddr` from DT, accepts probe deferral, and generates a random address when the result is invalid.
- `mt76_find_power_limits_node()` chooses a `power-limits` child by country (`dev->alpha2`) or DFS region (`dev->region`), with an unqualified fallback node.
- `mt76_find_channel_node()` selects a channel-range child node from a `channels` array.
- `mt76_get_rate_power_limits()` initializes `struct mt76_power_limits` and applies `rates-*`, `paths-*`, RU, MCS, and beamforming arrays from DT.

## Control Flow
EEPROM initialization starts with allocation in `mt76_eeprom_init()`, then `mt76_get_of_eeprom()` tries inline `mediatek,eeprom-data`, MTD, and nvmem in order. Power-limit calculation finds the region/country-specific node, descends into `txpower-2g`, `txpower-5g`, or `txpower-6g`, selects the channel range, reads optional `txs-delta`, then applies array limits to each destination table. `mt76_apply_multi_array_limit()` walks compressed multi-entry arrays whose first byte is a repeat count and calls `mt76_apply_array_limit()` for each logical row.

## State And Persistence
Persistent board data lives in `dev->eeprom.data`, `dev->eeprom.size`, and optionally `dev->test_mtd` for nl80211 testmode. Runtime power-limit output is written into caller-owned `struct mt76_power_limits`; the only lasting side effect in power-limit lookup is OF node refcounting. MAC-address state is stored in `phy->macaddr`, with random generation on invalid input.

## Dependencies And Integration Points
This file depends on Linux OF, MTD, nvmem, etherdevice helpers, mac80211 channel structures, `mt76.h`, and `mt76_connac.h` for chip-family helpers such as `is_mt799x()`. Chip drivers call the exported functions during probe, channel/power setup, and debug/testmode paths. It integrates with device-tree bindings for EEPROM storage and region-specific power tables.

## Risks
The MTD path can fail from missing labels, short reads, or malformed phandle/offset arrays. OF node refcounts are subtle because matching children are returned to callers. Power tables silently fall back to target power when nodes or arrays are missing, which is safe but can hide DT mistakes. The compressed multi-array parser depends on array lengths matching driver expectations; malformed lengths truncate processing. Random MAC fallback is operationally useful but can surprise systems expecting stable identity.

## Test Signals
Probe should succeed with inline EEPROM, MTD EEPROM, nvmem EEPROM, and no OF EEPROM. Test dmesg for MTD read failures, invalid-MAC randomization, and bitflip handling. Validate regulatory power through `iw phy`, channel max power, and chipset-specific debugfs/testmode outputs. DT power-limit changes should alter computed limits for representative 2 GHz, 5 GHz, and 6 GHz channels, including country/regdomain fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mac80211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mac80211.c

## Purpose
Shared mac80211 integration for mt76 devices. It provides channel/rate/SAR tables, PHY/device allocation and registration, RX conversion and aggregation release, station/WCID lifecycle, survey accounting, channel switching, SAR/txpower helpers, scan/offchannel helpers, CSA handling, beacon monitoring, ethtool helpers, and common mac80211 callbacks exported to chipset drivers.

## Important APIs, Types, And Functions
- Static channel/rate tables define 2 GHz, 5 GHz, 6 GHz channels, legacy rates, SAR frequency ranges, and LED throughput triggers.
- `mt76_alloc_device()`, `mt76_register_device()`, `mt76_unregister_device()`, and `mt76_free_device()` own common `struct mt76_dev` allocation, mac80211 registration, worker setup, and teardown.
- `mt76_alloc_phy()`, `mt76_alloc_radio_phy()`, `mt76_register_phy()`, and `mt76_unregister_phy()` support multi-radio or additional PHYs.
- `mt76_phy_init()`, `mt76_init_sband_*()`, and `mt76_set_stream_caps()` populate wiphy capabilities, supported bands, HT/VHT MCS maps, SAR capability, and hardware flags.
- `mt76_rx()`, `mt76_rx_poll_complete()`, and `mt76_rx_complete()` stage driver RX SKBs, validate A-MSDU bursts, apply CCMP PN checks, convert `mt76_rx_status` into `ieee80211_rx_status`, run reorder/GRO, and deliver to mac80211.
- `mt76_sta_state()`, `mt76_wcid_init()`, `mt76_wcid_cleanup()`, and `mt76_sta_pre_rcu_remove()` bridge mac80211 station state transitions to driver WCIDs.
- `__mt76_set_channel()`, `mt76_set_channel()`, `mt76_update_channel()`, `mt76_update_survey()`, and `mt76_get_survey()` manage reset-protected channel changes and channel survey counters.
- `mt76_wcid_key_setup()`, `mt76_check_ccmp_pn()`, `mt76_insert_ccmp_hdr()`, `mt76_get_rate()`, SAR helpers, CSA helpers, offchannel notification, and beacon monitor routines provide common correctness glue.

## Control Flow
Probe calls allocation and registration helpers, which initialize locks, queues, WCID tables, workers, supported bands, LEDs, SAR data, and register the hw with mac80211. RX begins with chipset code filling `struct mt76_rx_status` in `skb->cb` and calling `mt76_rx()`. RX frames are queued per RX ring, released as A-MSDU bursts when complete, then `mt76_rx_poll_complete()` checks station PS/airtime/reorder and `mt76_rx_complete()` converts metadata and delivers the list to mac80211. Channel changes disable the TX worker, drain pending TX, update survey time, set `MT76_RESET`, invoke `dev->drv->set_channel()`, then re-enable scheduling. Station add/remove is driven by mac80211 state transitions and delegates hardware programming to `dev->drv` callbacks.

## State And Persistence
Common runtime state is in `struct mt76_dev` and `struct mt76_phy`: registration/running/reset bits, `phys[]`, `band_phys[]`, WCID RCU table, TX/RX queues, MCU queues, workers, survey state, scan/offchannel state, beacon monitor timestamps, per-WCID PN/rate/PS state, and SAR frequency-range powers. No disk persistence is performed; persistence is hardware/driver runtime plus mac80211-visible registration state.

## Dependencies And Integration Points
The file sits between mac80211/cfg80211 and chipset-specific `struct mt76_driver_ops`. It also integrates with LED classdev, page_pool, NAPI/GRO, WED/NPU offload checks, testmode, kernel workqueues, RCU, and driver queue/MCU abstractions. Chip drivers supply callbacks for channel setting, TX/RX preparation, survey updates, station programming, PS changes, and TX status.

## Risks
Concurrency is broad: RX runs under spinlocks/NAPI, channel changes under `dev->mutex`, WCID pointers are RCU-protected, and TX status has its own lock. Incorrect state-bit ordering can race channel reset against TX scheduling. A-MSDU validation and CCMP PN checking are security-sensitive. Offchannel nullfunc and beacon monitoring depend on valid MLO link data and RCU dereferences. Missing driver callbacks or inconsistent `phy_idx`/WCID setup can misroute RX/TX status.

## Test Signals
Exercise module probe/remove, interface add/remove, scan, remain-on-channel, channel switch, AP beaconing, STA association, PS transitions, A-MPDU/A-MSDU traffic, CCMP replay rejection, SAR updates, `iw survey dump`, LED trigger registration, and multi-band/multi-link setups. Watch for lockdep splats, RCU warnings, TX drain timeouts, reordered RX loss, and incorrect reported signal/airtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mac80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mcu.c

## Purpose
Common MCU message allocation, synchronous send/response handling, response queueing, retry behavior, and firmware chunk transfer support for mt76 drivers that implement the low-level MCU transport callbacks.

## Important APIs, Types, And Functions
- `__mt76_mcu_msg_alloc()` allocates an SKB with chip-defined headroom/tailroom, zeroes the backing buffer, reserves headroom, and optionally copies payload.
- `mt76_mcu_rx_event()` queues MCU event/response SKBs on `dev->mcu.res_q` and wakes waiters.
- `mt76_mcu_get_response()` waits until a response is queued, timeout expires, or `MT76_MCU_RESET` is set.
- `mt76_mcu_send_and_get_msg()` supports direct `mcu_send_msg` ops or allocates an SKB and delegates to the SKB path.
- `mt76_mcu_skb_send_and_get_msg()` serializes commands with `dev->mcu.mutex`, prepares sequence metadata, sends via driver ops, waits for matching responses, retries if configured, and returns an optional response SKB.
- `__mt76_mcu_send_firmware()` splits large firmware payloads into bounded chunks and optionally cleans the firmware download queue between chunks.

## Control Flow
Callers either pass data to `mt76_mcu_send_msg()` wrappers or build an SKB. The common send path locks the MCU mutex, lets the chip driver prepare a command and sequence number, sends via `mcu_skb_send_msg`, and, when a response is required, waits on `dev->mcu.wait`. Responses from RX are pushed through `mt76_mcu_rx_event()`. The chip-specific parser returns success, retry-needed `-EAGAIN`, timeout, or command errors. Firmware upload loops over chunks without waiting for per-chunk responses unless the chip op implements that behavior.

## State And Persistence
State is transient: `dev->mcu.msg_seq`, `timeout`, response SKB queue, and waitqueue. The MCU mutex provides command serialization. No persistent storage is written; firmware bytes are streamed to hardware queues.

## Dependencies And Integration Points
This code depends on chip-provided `struct mt76_mcu_ops`, mt76 queue ops for firmware TX cleanup, SKB queues, waitqueues, mutexes, and device state bits. Chip RX paths must classify MCU events and call `mt76_mcu_rx_event()`.

## Risks
If the chip parser does not discard nonmatching responses correctly, stale events can starve the current command. Retry uses `orig_skb` only when prepare ops created a reusable original; ownership is delicate because send ops consume SKBs. Timeout behavior marks failures but depends on chip code setting reset bits. Firmware chunking assumes `max_len` aligns with MCU expectations.

## Test Signals
Probe firmware load, command response matching, injected timeout/retry, reset during wait, and firmware download with queue cleanup. Validate no SKB leaks with kmemleak or debug counters and ensure MCU event RX wakes blocked command senders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mmio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mmio.c

## Purpose
MMIO bus backend for mt76 devices. It implements register read/write/read-modify-write, copy helpers, register-pair helpers, IRQ-mask synchronization, and bus initialization for memory-mapped chipsets.

## Important APIs, Types, And Functions
- `mt76_mmio_rr()`, `mt76_mmio_wr()`, and `mt76_mmio_rmw()` perform traced `readl`/`writel` accesses through `dev->mmio.regs`.
- `mt76_mmio_write_copy()` and `mt76_mmio_read_copy()` transfer little-endian 32-bit words to/from MMIO windows with aligned length.
- `mt76_mmio_wr_rp()` and `mt76_mmio_rd_rp()` write/read arrays of `struct mt76_reg_pair`.
- `mt76_set_irq_mask()` updates `dev->mmio.irqmask` under `irq_lock` and writes either WED IRQ mask or the provided device register.
- `mt76_mmio_init()` installs the static `MT76_BUS_MMIO` ops table, stores the base pointer, and initializes IRQ locking.

## Control Flow
Chip probe maps registers, allocates `struct mt76_dev`, then calls `mt76_mmio_init()`. Thereafter generic macros route through `dev->bus`. IRQ mask callers specify bits to clear/set; the helper updates the cached mask and immediately pushes it to hardware when an address is supplied.

## State And Persistence
State is the MMIO base pointer, bus ops pointer, IRQ spinlock, and cached IRQ mask. Hardware registers persist only as device runtime state.

## Dependencies And Integration Points
Depends on Linux I/O accessors, mt76 tracing, WED offload helpers, and `struct mt76_bus_ops`. Chip drivers may wrap these ops for address remapping, as mt7603 does.

## Risks
The copy helpers round length up to 4 bytes and assume the backing buffer is safe for rounded access. IRQ-mask updates must be the only writer of `dev->mmio.irqmask` to avoid lost bits. WED-active devices bypass direct register writes, so offload mask state must remain synchronized.

## Test Signals
Trace register access during probe, verify IRQ enable/disable paths, ensure WED and non-WED IRQ masks behave identically, and run suspend/remove paths under interrupt load to catch stale mask or register-base use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76.h

## Purpose
Central mt76 core header defining bus abstractions, queues, MCU ops, driver callbacks, PHY/device state, WCID/station state, RX/TX metadata, testmode structures, WED/NPU helpers, inline register/queue wrappers, and exported prototypes used across mt76 chip families.

## Important APIs, Types, And Functions
- Bus and queue abstractions: `struct mt76_bus_ops`, `struct mt76_queue_ops`, queue IDs, RXQ/TXQ/MCUQ enums, WED/NPU queue flag helpers, and MMIO/USB/SDIO bus-type predicates.
- Core data model: `struct mt76_dev`, `struct mt76_phy`, `struct mt76_wcid`, `struct mt76_vif_data`, `struct mt76_vif_link`, `struct mt76_queue`, `struct mt76_rx_status`, `struct mt76_tx_cb`, and `struct mt76_txwi_cache`.
- Callback contracts: `struct mt76_driver_ops`, `struct mt76_mcu_ops`, and `struct mt76_testmode_ops`.
- Capability/state enums and flags: cipher types, PHY types, DFS states, WCID flags, driver flags, device state bits, and station event types.
- Inline helpers wrap register access, queue allocation, chip/revision extraction, WCID lookup, SKB control data, rate/power helpers, page-pool allocation, token IDR operations, VIF/link helpers, and testmode/NPU stubs.
- Prototypes expose shared implementations from mac80211, TX, RX aggregation, MCU, EEPROM, DMA, USB, SDIO, WED, NPU, scan, and channel-context files.

## Control Flow
The header itself has no standalone runtime flow, but it defines how chip drivers call into common code. Typical flow is: allocate `mt76_dev`, initialize a bus, attach DMA/queues, set `drv` and `mcu_ops`, initialize EEPROM, register with mac80211, then use callback/inline wrappers for TX/RX, station lifecycle, channel updates, MCU commands, and teardown.

## State And Persistence
`struct mt76_dev` is the root runtime state: hw pointer, PHY array, locks, WCID RCU table, queues, MCU response state, workers, tokens, scan/beacon state, debugfs blobs, bus-specific union, and offload objects. `struct mt76_phy` carries per-radio state such as channel, survey counters, chainmask, bands, TX queues, LED state, testmode, and RX A-MSDU assembly. `struct mt76_wcid` is per peer/link transmission, security, PN, stats, and polling state. All state is in-memory driver state.

## Dependencies And Integration Points
Includes Linux kernel primitives, mac80211, page_pool, MediaTek WED, Airoha offload, mt76 utilities, and testmode definitions. It is consumed by all bus and chip drivers in the mt76 tree, so layout stability and helper semantics are cross-cutting.

## Risks
Because this header defines shared structure layout, small field or flag changes affect many chipsets. Inline wrappers assume embedding conventions, such as chip structs containing `mt76` and `mphy` members. RCU/lock expectations are embedded in helpers like `mt76_dereference()` and WCID accessors. Queue flag helpers overload bitfields for WED/NPU and must stay consistent with DMA code. The `skb->cb` layout assertions protect but do not eliminate metadata misuse by chip drivers.

## Test Signals
Full-tree compile coverage across PCI/USB/SDIO chip families is the primary signal. Runtime smoke tests should cover MMIO and non-MMIO devices, WED/NPU-disabled builds, testmode-disabled builds, station add/remove, TX token exhaustion/release, RX status conversion, SAR, scan/ROC, and debugfs access. Lockdep and KASAN are valuable for helper misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/Kconfig

## Purpose
Kconfig entry for the MT7603E PCIe and MT76x8 SoC WLAN driver.

## Important APIs, Types, And Functions
- `config MT7603E` defines a tristate driver option named "MediaTek MT7603E (PCIe) and MT76x8 WLAN support".
- It selects `MT76_CORE` and depends on `MAC80211` and `PCI`.
- Help text documents support for MT7603E PCIe devices and MT7628/MT7688 WLAN core devices, with 802.11n 2x2 up to 300 Mbps.

## Control Flow
Build-time only. Enabling this option causes the Makefile to build `mt7603e.o` and include the mt7603 driver in-kernel or as a module.

## State And Persistence
No runtime state. The chosen Kconfig value persists in the kernel build configuration.

## Dependencies And Integration Points
Integrates with the kernel wireless stack through `MAC80211`, with PCI support, and with the mt76 core selected by `MT76_CORE`.

## Risks
The hard `depends on PCI` means pure SoC users still need PCI enabled in this tree even though the help mentions MT7628/MT7688 SoC WLAN. Misconfigured builds will omit the driver entirely.

## Test Signals
Validate `allyesconfig`, module build, and target platform configs. Confirm `CONFIG_MT7603E=m` builds `mt7603e.ko` and pulls in mt76 core dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/Makefile

## Purpose
Build composition for the `mt7603e` kernel object.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_MT7603E) += mt7603e.o` ties the module/object to the Kconfig option.
- `mt7603e-y` lists implementation units: `pci.o`, `soc.o`, `main.o`, `init.o`, `mcu.o`, `core.o`, `dma.o`, `mac.o`, `eeprom.o`, `beacon.o`, and `debugfs.o`.

## Control Flow
Build-time only. Kbuild compiles and links the listed objects into one driver object when `CONFIG_MT7603E` is enabled.

## State And Persistence
No runtime state. Build output is determined by Kconfig and Kbuild.

## Dependencies And Integration Points
Integrates mt7603 bus frontends (`pci.o`, `soc.o`) with shared mt7603 runtime logic and the parent mt76 build.

## Risks
Missing a new source file from `mt7603e-y` causes unresolved symbols or omitted functionality. Ordering is generally not semantic, but link-time symbol availability depends on all units being listed.

## Test Signals
Run kernel module build for `CONFIG_MT7603E=y` and `m`; inspect `modinfo` for the final module and ensure both PCI and SoC probe objects are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/beacon.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/beacon.c

## Purpose
MT7603 beacon and buffered broadcast/multicast handling around pre-TBTT interrupts. It refreshes beacon frames, prepares CAB traffic, programs beacon timers, and includes recovery for stuck beacon queues.

## Important APIs, Types, And Functions
- `struct beacon_bc_data` collects buffered broadcast/multicast SKBs, per-interface tail pointers, and frame counts.
- `mt7603_mac_stuck_beacon_recovery()` periodically toggles DMA scheduler/TMAC/ARB state when the beacon queue appears stuck.
- `mt7603_update_beacon_iter()` obtains a fresh beacon via `ieee80211_beacon_get()`, flushes target beacon/BMC hardware queues through `MT_DMA_FQCR0`, and queues it on `MT_TXQ_BEACON`.
- `mt7603_add_buffered_bc()` drains mac80211 buffered BC/MC frames, marks sequence assignment and More Data, and stores counts.
- `mt7603_pre_tbtt_tasklet()` is the pre-TBTT tasklet that flushes old CAB/beacon frames, updates beacons, checks CSA completion, sends CAB frames, and starts hardware CAB release.
- `mt7603_beacon_set_timer()` enables/disables per-BSS beacon masks, TBTT/PRE_TBTT registers, beacon queue opmode, MAC IRQ3 mask bits, and sub-BSS timing.

## Control Flow
AP beaconing is enabled from `bss_info_changed()` through `mt7603_beacon_set_timer()`. Hardware PRE_TBTT triggers `mt7603_irq_handler()`, which schedules the tasklet. The tasklet skips offchannel operation, flushes old beacon/CAB content, increments stuck-beacon counters if the beacon queue remains occupied, refreshes beacon frames under the beacon queue lock, checks CSA, drains up to a small batch of buffered BC/MC frames, queues them to CAB, writes per-BSS CAB counts, and starts CAB transmission.

## State And Persistence
State lives in `dev->mt76.beacon_mask`, `dev->mt76.beacon_int`, `dev->beacon_check`, TX queue occupancy, per-interface beacon bits, and hardware TBTT/CAB registers. SKBs are transient and owned by TX queues after enqueue.

## Dependencies And Integration Points
Depends on mac80211 beacon/CAB APIs, mt76 TX queue helpers, mt7603 register definitions, tasklets, and CSA helpers from the shared mt76 mac80211 layer. It integrates with `core.c` IRQ handling and `main.c` BSS change callbacks.

## Risks
Tasklet concurrency with interface removal and channel changes is handled by explicit tasklet disable in callers; missing that can race with queue/register updates. If `MT_DMA_FQCR0` does not clear, the watchdog is forced through `beacon_check`. CAB batching is capped, so unusual buffering patterns need validation. CSA returns early after beacon update to avoid sending CAB during channel switch.

## Test Signals
Run AP mode with one and multiple BSSIDs, buffered multicast under sleeping stations, CSA/channel switch, interface removal during beaconing, and offchannel scans while AP is active. Monitor reset cause "Beacon stuck", PRE_TBTT/TBTT interrupts, CAB delivery, and absence of stale More Data flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/beacon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/core.c

## Purpose
MT7603 interrupt dispatch and register remapping helpers.

## Important APIs, Types, And Functions
- `mt7603_rx_poll_complete()` re-enables RX-done interrupts after NAPI completes an RX queue.
- `mt7603_irq_handler()` acknowledges interrupt sources, filters them through `dev->mt76.mmio.irqmask`, schedules tasklets/NAPI for MAC IRQ3, TX done, and RX done rings, and handles CSA finish on TBTT.
- `mt7603_reg_map()` programs the PCIe remap register and returns the local remap-window address for high physical register addresses.

## Control Flow
The IRQ handler reads and writes `MT_INT_SOURCE_CSR` to acknowledge all pending bits, ignores interrupts until `MT76_STATE_INITIALIZED` is set, masks by cached IRQ mask, handles MAC IRQ3 substatus by acknowledging `MT_HW_INT_STATUS(3)`, schedules pre-TBTT work, disables TX/RX done interrupts before scheduling NAPI, and returns handled. Register-map callers write the high address base to `MT_MCU_PCIE_REMAP_2` before accessing the remap window.

## State And Persistence
State includes `dev->mt76.mmio.irqmask`, NAPI scheduling state, `dev->rx_pse_check`, tasklet scheduling, and the hardware remap register. No durable persistence exists.

## Dependencies And Integration Points
Integrates with mt76 MMIO ops, tracepoints, mt7603 IRQ enable/disable helpers, NAPI instances initialized by DMA code, pre-TBTT tasklet in `beacon.c`, and CSA helpers in shared mac80211 code.

## Risks
Interrupt acknowledgement before initialization can drop early interrupts by design. Remap register access is not independently locked here, so callers must avoid concurrent conflicting high-address accesses when necessary. IRQ bits are disabled before NAPI; missing re-enable in poll completion stalls traffic.

## Test Signals
Verify RX/TX NAPI scheduling under load, interrupt mask toggling, pre-TBTT beacon tasklet execution, CSA completion on TBTT, and register accesses above the direct window. Use trace IRQ output to confirm masked bits and status acknowledgements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/debugfs.c

## Purpose
Debugfs diagnostics and knobs for MT7603 aggregation statistics, transmit queues, EDCCA behavior, watchdog reset testing, reset causes, radio sensitivity, and dynamic sensitivity control.

## Important APIs, Types, And Functions
- `mt7603_reset_read()` reports reset-cause counters by human-readable reason.
- `mt7603_radio_read()` reports current sensitivity and false CCA counts.
- `mt7603_edcca_set()` and `mt7603_edcca_get()` back the writable `edcca` debugfs attribute and reinitialize EDCCA under `dev->mt76.mutex`.
- `mt7603_ampdu_stat_show()` displays aggregation length bucket boundaries and counters from `dev->mphy.aggr_stats`.
- `mt7603_init_debugfs()` registers the mt76 debugfs root plus `ampdu_stat`, `xmit-queues`, `edcca`, `reset_test`, `reset`, `radio`, `sensitivity_limit`, and `dynamic_sensitivity`.

## Control Flow
Device registration calls `mt7603_init_debugfs()` after mac80211 registration. Reads format live driver state through seq_file helpers. Writes to `edcca` alter `ed_monitor_enabled`, derive active `ed_monitor` from ETSI region, and call `mt7603_init_edcca()`.

## State And Persistence
Debugfs exposes mutable runtime fields: `ed_monitor_enabled`, `reset_test`, `sensitivity_limit`, and `dynamic_sensitivity`. Other files read counters and sensitivity state. Debugfs settings are not persistent across driver reload.

## Dependencies And Integration Points
Depends on mt76 debugfs registration, seq_file, debugfs attribute helpers, and runtime state updated by `mac.c` watchdog/sensitivity logic and `main.c` regulatory notifier.

## Risks
Debugfs writes can affect radio behavior and trigger watchdog test resets. Values are lightly constrained because debugfs is for privileged diagnostics. EDCCA changes depend on mutex serialization with channel/MAC work.

## Test Signals
Mount debugfs, read each file after probe and under traffic, toggle `edcca`, adjust `dynamic_sensitivity` and `sensitivity_limit`, and set `reset_test` to force each reset cause. Confirm no use-after-free during device removal while debugfs entries exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/dma.c

## Purpose
MT7603 DMA ring setup, RX packet dispatch, TX completion NAPI, power-save loopback buffering, and DMA cleanup.

## Important APIs, Types, And Functions
- `wmm_queue_map` maps mac80211 access categories to hardware TX ring indices.
- `mt7603_rx_loopback_skb()` handles MCU/RX loopback packets used for station power-save buffering, rewrites queue indices, marks mac80211 buffered state, and stores frames in per-station `psq`.
- `mt7603_queue_rx_skb()` classifies RX descriptors as TX status, MCU event, normal frame, or loopback frame and dispatches to `mt7603_mac_add_txs()`, `mt76_mcu_rx_event()`, `mt7603_mac_fill_rx()`, or free.
- `mt7603_init_rx_queue()` allocates an RX ring and enables the matching RX-done IRQ.
- `mt7603_poll_tx()` cleans MCU and data TX queues, re-enables TX-done interrupts, polls station airtime, and schedules the common TX worker.
- `mt7603_dma_init()` attaches mt76 DMA, resets WPDMA indices, resets PSE client, allocates data/PSD/MCU/beacon/CAB TX queues and MCU/main RX queues, initializes mt76 queues, and enables TX NAPI.
- `mt7603_dma_cleanup()` disables DMA and calls common cleanup.

## Control Flow
Hardware init calls `mt7603_dma_init()`. RX NAPI dequeues DMA buffers and calls this file's RX callback. MCU ring frames that are events enter the common MCU response queue; normal data frames are parsed in `mac.c` and delivered to shared mt76 RX. TX-done interrupts schedule `mt7603_poll_tx()`, which performs cleanup twice around `napi_complete_done()` to catch completions racing with IRQ re-enable.

## State And Persistence
State includes hardware queues in `dev->mphy.q_tx[]`, `dev->mt76.q_mcu[]`, `dev->mt76.q_rx[]`, NAPI state, station PS queues, `dev->tx_dma_check`, and `dev->rx_pse_check`. No durable persistence exists.

## Dependencies And Integration Points
Depends on common mt76 DMA helpers, mt7603 descriptors from `mac.h`, queue ops from `../dma.h`, MCU response handling, and MAC RX/TX status parsers. Power-save queueing integrates with `main.c` station PS callbacks.

## Risks
Descriptor type parsing must reject malformed lengths before dereference. Loopback buffering caps per-station `psq` at 64 by dropping oldest frames; traffic loss is expected under excessive sleeping-station backlog. IRQ/NAPI re-enable ordering is critical to avoid stuck queues. DMA reset/cleanup must coordinate with watchdog reset logic.

## Test Signals
Run bidirectional traffic across all ACs, firmware command traffic, TX status reporting, sleeping STA buffered frames, RX malformed/FCS frames, and driver remove. Check queue debugfs, TX/RX NAPI counters, PS frame release, and absence of IRQ storms or disabled-ring stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/eeprom.c

## Purpose
MT7603-specific EEPROM/efuse initialization. It reads OTP efuse data, optionally merges calibration-free OTP fields into external EEPROM, validates chip IDs, derives MAC address and antenna capabilities, and invokes common MAC override handling.

## Important APIs, Types, And Functions
- `mt7603_efuse_read()` reads a 16-byte efuse block through `MT_EFUSE_CTRL` and `MT_EFUSE_RDATA()`, returning all `0xff` for invalid rows.
- `mt7603_efuse_init()` allocates `dev->mt76.otp.data` and reads the full `MT7603_EEPROM_SIZE` when efuse is not empty.
- `mt7603_has_cal_free_data()` checks required OTP fields for cal-free merge validity.
- `mt7603_apply_cal_free_data()` merges selected OTP calibration bytes into EEPROM only when DT has `mediatek,eeprom-merge-otp`, with MT7628-specific skips.
- `mt7603_eeprom_load()` delegates external EEPROM allocation/loading to `mt76_eeprom_init()` and then reads efuse.
- `mt7603_check_eeprom()` accepts chip IDs `0x7628`, `0x7603`, and `0x7600`.
- `mt7603_eeprom_init()` decides whether OTP supplements or replaces EEPROM, sets 2 GHz capability, copies MAC, computes 1SS/2SS antenna mask, sets chainmask, and calls `mt76_eeprom_override()`.

## Control Flow
Hardware init calls `mt7603_eeprom_init()`. It loads external EEPROM and efuse. If OTP exists and external EEPROM validates, optional cal-free bytes are merged; if external EEPROM is invalid, OTP becomes the EEPROM image. Then the driver initializes PHY capabilities from EEPROM fields and SoC revision probes, and applies OF MAC override/random fallback.

## State And Persistence
Persistent board/calibration data is held in `dev->mt76.eeprom.data`; raw OTP is held in `dev->mt76.otp.data` for debugfs/diagnostics. Runtime PHY fields set here include `dev->mphy.cap.has_2ghz`, `macaddr`, `antenna_mask`, and `chainmask`.

## Dependencies And Integration Points
Depends on common mt76 EEPROM helpers, OF property checks, efuse register definitions, chip helpers such as `is_mt7628()`, and `mt76_eeprom_override()`. Later MCU and txpower code consumes the populated EEPROM buffer.

## Risks
Efuse reads use polling and fixed 16-byte rows; timeout blocks probe. Cal-free merge is gated by DT and validity checks, but wrong DT can blend incompatible calibration. Invalid external EEPROM is silently replaced by OTP when available. `is_mt7688()` reads an efuse register directly and affects antenna count, so incorrect detection reduces throughput.

## Test Signals
Probe devices with external flash EEPROM, efuse-only data, cal-free merge enabled/disabled, MT7628/MT7688 variants, and invalid MAC/chip IDs. Validate debugfs EEPROM/OTP blobs, antenna count reported by `iw phy`, and firmware txpower programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/eeprom.h

## Purpose
MT7603 EEPROM field map and bit definitions used by EEPROM loading, MCU calibration upload, txpower setup, and antenna detection.

## Important APIs, Types, And Functions
- `enum mt7603_eeprom_field` defines offsets for chip ID, version, MAC address, NIC config, RSSI offsets, Wi-Fi RF settings, 2 GHz/5 GHz power groups, rate power deltas, ELAN fields, temperature compensation, crystal calibration, and CP/FT version.
- `MT_TX_POWER_GROUP_SIZE_5G` and `MT_TX_POWER_GROUPS_5G` document 5 GHz power array geometry.
- `enum mt7603_eeprom_source` names PROM, efuse, and flash sources.
- `MT_EE_NIC_CONF_0_RX_PATH` and `MT_EE_NIC_CONF_0_TX_PATH` extract path counts from NIC config byte.

## Control Flow
Header-only constants are consumed by `eeprom.c`, `mcu.c`, and `init.c` to index the EEPROM byte array. There is no runtime flow in this file.

## State And Persistence
No state. It describes persistent EEPROM layout that is loaded into `dev->mt76.eeprom.data`.

## Dependencies And Integration Points
Includes `mt7603.h` for common chip definitions and bit macros. Its offsets must match firmware expectations for `MCU_EXT_CMD_EFUSE_BUFFER_MODE` and `MCU_EXT_CMD_SET_TX_POWER_CTRL`.

## Risks
Incorrect offsets corrupt calibration, MAC address, antenna mask, txpower, and firmware setup. Some fields are byte arrays while others are little-endian words, so callers must use the right accessor.

## Test Signals
Validate EEPROM dumps against known board data, firmware calibration success, expected antenna mask, target txpower, RSSI offsets, and no regression in MT7628/MT7688 variant detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/init.c

## Purpose
MT7603 device initialization and registration. It defines mt76 driver callbacks, initializes scheduler/PHY/MAC hardware, wraps bus ops for register remapping, sets LED behavior, computes initial txpower, registers with mac80211, and tears down the device.

## Important APIs, Types, And Functions
- `mt7603_drv_ops` connects common mt76 callbacks to MT7603 implementations for TX prepare/complete, RX dispatch, survey, channel setting, station events, and PS.
- `mt7603_dma_sched_init()`, `mt7603_phy_init()`, and `mt7603_mac_init()` program PSE scheduler quotas, stream counts, AGC snapshots, aggregation, DMA RX/TX selection, WTBL defaults, security, MBSSID, retry, and beacon timing offsets.
- `mt7603_init_hardware()` orders EEPROM init, DMA init, MAC DMA start, WTBL reset, MCU firmware init, scheduler, EEPROM upload, PHY init, and MAC init.
- LED callbacks `mt7603_led_set_config()`, `mt7603_led_set_blink()`, and `mt7603_led_set_brightness()` program LED registers through the remap window.
- `mt7603_rr()`, `mt7603_wr()`, and `mt7603_rmw()` wrap parent bus ops to remap addresses above the direct window.
- `mt7603_regd_notifier()` stores DFS region and enables ED monitor only for ETSI when user-enabled.
- `mt7603_init_txpower()` derives initial target power from EEPROM, external PA fields, rate offsets, and antenna count, then updates channel max/original power.
- `mt7603_register_device()` performs full runtime registration; `mt7603_unregister_device()` disables tasklets, unregisters, restarts MCU download mode, cleans DMA, and frees mt76.

## Control Flow
Probe code from PCI/SoC frontends creates the device and calls `mt7603_register_device()`. That function clones and overrides bus ops for remapping, initializes locks/work/tasklets/defaults, runs hardware init, fills mac80211 capability fields, installs optional LED callbacks and regulatory notifier, calls `mt76_register_device()`, initializes debugfs, and computes txpower. Unregister disables pre-TBTT work before common unregister and hardware cleanup.

## State And Persistence
Runtime state initialized here includes `bus_ops`, `ps_lock`, delayed `mac_work`, pre-TBTT tasklet, slot time, sensitivity defaults, dynamic sensitivity, `rxfilter`, `MT76_STATE_INITIALIZED`, global reserved WCID, `dev->tx_power_limit`, `mphy.txpower_cur`, LED callbacks, and wiphy capabilities. Hardware register state is extensively programmed but not persistent across reset.

## Dependencies And Integration Points
Depends on EEPROM, DMA, MCU, MAC, beacon, debugfs, mt76 common registration, mac80211, LED classdev, regulatory notifications, and chip-specific register definitions. It is the main integration point between bus probe units and the common mt76 stack.

## Risks
Initialization order is strict: EEPROM informs antenna/power, DMA must exist for firmware commands, firmware must run before MCU channel/power commands, and WTBL/PSE setup must precede traffic. Bus op wrapping must preserve original ops in `dev->bus_ops`; recursion or missing remap breaks high-register access. Error paths after partial hardware init rely on caller cleanup. Txpower parsing handles signed EEPROM encodings that are easy to misinterpret.

## Test Signals
Probe/remove repeatedly, including failure injection at EEPROM, DMA, firmware, and register stages. Verify firmware loads, mac80211 registration, LED behavior, debugfs creation, regulatory notifier updates, txpower/channel max values, WTBL reserved entry, and traffic after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mac.c

## Purpose
MT7603 low-level MAC, WTBL, RX/TX descriptor, rate-control, security, airtime, DMA control, watchdog reset, EDCCA, CCA, and sensitivity implementation.

## Important APIs, Types, And Functions
- TX arbitration helpers stop/start AC queues; `mt7603_mac_start()`, `mt7603_mac_stop()`, and `mt7603_mac_dma_start()` control MAC and WPDMA operation.
- WTBL management: `mt7603_wtbl_init()`, `mt7603_wtbl_clear()`, `mt7603_wtbl_update_cap()`, `mt7603_wtbl_set_smps()`, `mt7603_wtbl_set_ps()`, `mt7603_filter_tx()`, `mt7603_wtbl_set_rates()`, and `mt7603_wtbl_set_key()`.
- Block-ack helpers: `mt7603_mac_rx_ba_reset()` and `mt7603_mac_tx_ba_reset()`.
- RX parsing: `mt7603_mac_fill_rx()` decodes RX descriptors/RXV groups, security state, A-MPDU metadata, RSSI, rate/band/frequency, padding, and CCMP header reinsertion.
- TX building/status: `mt7603_mac_write_txwi()`, `mt7603_tx_prepare_skb()`, `mt7603_fill_txs()`, `mt7603_mac_add_txs_skb()`, `mt7603_mac_add_txs()`, and `mt7603_tx_complete_skb()`.
- Recovery and maintenance: `mt7603_pse_client_reset()`, `mt7603_pse_reset()`, `mt7603_mac_watchdog_reset()`, DMA busy/hang checks, `mt7603_mac_work()`, `mt7603_update_channel()`, `mt7603_cca_stats_reset()`, EDCCA, and dynamic sensitivity adjustment.

## Control Flow
Normal TX enters through common mt76 queues into `mt7603_tx_prepare_skb()`, which handles PS wake conditions, aggregation sequence checks, TX-status PID allocation, optional probe-rate WTBL update, and TXWI construction. Hardware TX status frames are parsed by DMA RX dispatch into `mt7603_mac_add_txs()`, which matches SKBs by PID or emits no-SKB status. Normal RX frames are parsed by `mt7603_mac_fill_rx()` and passed to shared mt76 RX. Station setup and rate updates program WTBL records. Periodic `mt7603_mac_work()` updates surveys, EDCCA, aggregation stats, false-CCA sensitivity, and watchdog counters; on persistent hangs it performs a full MAC/DMA/PSE reset and restarts queues/NAPI/tasklets.

## State And Persistence
State spans WTBL hardware entries, per-station `struct mt7603_sta` fields (`ps`, `smps`, rate sets, airtime counters, `psq`), `dev->mphy.aggr_stats`, RX A-MPDU timestamp/reference, RSSI offsets, reset-cause counters, sensitivity/EDCCA fields, DMA indices, watchdog counters, `tx_power_limit`, and queue/NAPI state. Security keys are written into WTBL key memory. All state is runtime hardware/driver state.

## Dependencies And Integration Points
Depends on mt76 core TX/RX/status/reorder helpers, mac80211 station/rate/key APIs, mt7603 descriptor definitions from `mac.h`, register definitions from `mt7603.h`, beacon and DMA paths, and debugfs readers. Firmware/MCU channel and txpower state complements but does not replace MAC register setup.

## Risks
This is the highest-risk file in the subset. Descriptor parsing must validate group lengths before `skb_pull()`. TX status reconstruction relies on rate-set TSF heuristics and can misreport after delayed status or rapid probe changes. WTBL programming stops TX around sensitive writes; missing stop/update/poll can corrupt peer state. PS handling moves frames between hardware loopback, per-station queues, and raw TX queues under `ps_lock`. Watchdog reset disables workers, tasklets, NAPI, IRQs, queues, and DMA; ordering mistakes can deadlock or lose interrupts. Security handling supports limited ciphers and writes raw keys into hardware memory.

## Test Signals
Stress STA/AP traffic with aggregation, rate probing, fixed-rate frames, PS/UAPSD, multicast buffering, key install/remove, TKIP/CCMP, RX FCS/MIC errors, monitor mode, channel changes, EDCCA toggling, and watchdog reset injection. Check TX status accuracy, airtime accounting, `ampdu_stat`, reset counters, no lockdep/KASAN warnings, and traffic recovery after each reset cause.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mac.h

## Purpose
Descriptor bitfield definitions and packet-type enums for MT7603 RX descriptors, RX vector groups, TX descriptors, TX rate encoding, and TX status records.

## Important APIs, Types, And Functions
- `enum rx_pkt_type` classifies hardware RX entries as TX status, RXV, normal RX, duplicate RFB, timing report, retrieve/loopback, or MCU event.
- `MT_RXD*` macros decode normal RX descriptor fields: length/type, optional groups, BSSID, payload/hdr flags, channel index, key ID, unicast/multicast, errors, security mode, TID, and WLAN index.
- `MT_RXV*` macros decode PHY vector fields for mode, rate, SGI, LDPC, STBC, bandwidth, RSSI/RCPI, noise, and validity.
- `enum mt7603_tx_header_format` and `MT_TXD*` macros define TXWI layout, queue/WCID/vif/TID/protection/rate/PN/status fields.
- `MT_TX_RATE_*` macros encode fixed/probed hardware rates.
- `MT_TXS*` macros decode TX status including timeout reasons, ack state, final rate, timestamp, WCID, retry count, AMPDU state, PID, bandwidth, and sequence/TSSI fields.

## Control Flow
Header-only definitions are consumed by `dma.c` and `mac.c`. RX descriptor macros drive packet dispatch and status construction. TX descriptor macros drive `mt7603_mac_write_txwi()`. TX status macros drive rate/status reporting in `mt7603_fill_txs()`.

## State And Persistence
No direct state. It defines the binary contract between host driver memory and MT7603 hardware/firmware descriptors.

## Dependencies And Integration Points
Depends on Linux bitfield macros (`GENMASK`, `BIT`, `FIELD_GET`, `FIELD_PREP`) via included headers. Must stay synchronized with MT7603 hardware documentation and firmware behavior.

## Risks
Wrong bit definitions cause silent RX drops, bad security metadata, incorrect rate/status reporting, DMA queue corruption, or malformed TX descriptors. Some fields overlap or have format-dependent meaning, so consumers must use the correct packet type and optional group checks.

## Test Signals
Descriptor-level validation comes from RX/TX traffic across CCK/OFDM/HT rates, 20/40 MHz, encrypted frames, fragmented CCMP, AMPDU, TX status with retries/timeouts, and MCU event dispatch. Hardware trace dumps should match expected field decodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/main.c

## Purpose
MT7603 mac80211 operations, module entry/exit, interface lifecycle, channel/power/filter/BSS configuration, station/key/AMPDU/rate handling, power-save frame release, and TX entrypoint.

## Important APIs, Types, And Functions
- `mt7603_start()` and `mt7603_stop()` control running state, counters, MAC start/stop, and periodic MAC work.
- `mt7603_add_interface()` and `mt7603_remove_interface()` allocate/free interface indices, program MAC/BSSID registers, create per-vif reserved WCIDs, and manage beacon timers.
- `mt7603_set_channel()` stops beaconing/MAC, updates bandwidth, sends MCU channel command, loads RSSI offsets, writes channel frequency index, restarts MAC/work, resets survey/CCA/EDCCA, and restores beaconing.
- `mt7603_config()`, `mt7603_configure_filter()`, `mt7603_bss_info_changed()`, and `mt7603_set_sar_specs()` handle mac80211 config changes.
- Station operations `mt7603_sta_add()`, `mt7603_sta_event()`, `mt7603_sta_remove()`, and `mt7603_sta_ps()` manage WTBL allocation, caps, polling, PS, and queued frames.
- `mt7603_release_buffered_frames()` releases per-station PS queue entries and falls back to common mt76 buffering.
- `mt7603_set_key()` supports TKIP/CCMP hardware keys with software fallback for unsupported/per-STA GTK cases.
- `mt7603_conf_tx()`, `mt7603_ampdu_action()`, `mt7603_sta_rate_tbl_update()`, `mt7603_set_coverage_class()`, and `mt7603_tx()` implement QoS, BA, rate, timing, and TX routing.
- `mt7603_ops` is the mac80211 callback table; module init registers platform and PCI drivers.

## Control Flow
mac80211 calls `start`, then interface/station/key/config callbacks as network state changes. TX selects the WCID from control STA, VIF, or global reserved WCID and calls common `mt76_tx()`. Channel changes route through shared `mt76_update_channel()` to this file's set-channel implementation. Module init registers the SoC platform driver first, then PCI if enabled; exit unregisters in reverse.

## State And Persistence
State includes `dev->mt76.vif_mask`, per-vif indices/WCIDs, MAC/BSSID hardware registers, `dev->rxfilter`, slottime, coverage class, station WTBL/PS/rate state, beacon timer state, SAR frequency powers, `mphy.state`, survey time, and delayed MAC work. No durable state is written.

## Dependencies And Integration Points
Integrates mac80211 with lower-level `mac.c`, `mcu.c`, `beacon.c`, common mt76 station/TX/RX helpers, PCI and platform frontends, cfg80211 SAR/regulatory APIs, and Kconfig-selected module registration.

## Risks
VIF index allocation uses `__ffs64(~vif_mask)` and must stay bounded by `MT7603_MAX_INTERFACES`. BSS/beacon changes disable tasklets around timer updates; missing serialization can race pre-TBTT. Channel changes must restore MAC/beacon state even on failures. Hardware key limitations require correct `-EOPNOTSUPP` fallback. Empty `flush()` means mac80211 flush requests rely on common queue draining elsewhere.

## Test Signals
Test station, AP, P2P, adhoc/mesh where enabled, multi-BSSID AP up to limits, start/stop, channel/power/SAR updates, monitor filters, key fallback, AMPDU start/stop, rate updates, PS release, and module load/unload for PCI and platform paths. Watch for leaked vif_mask bits and stale WCIDs after interface removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mcu.c

## Purpose
MT7603 MCU protocol implementation: command framing, response parsing, firmware selection/download/start, MCU teardown, EEPROM/calibration upload, channel switch commands, and transmit-power control commands.

## Important APIs, Types, And Functions
- `struct mt7603_fw_trailer` describes firmware version/build date/download length trailer.
- `mt7603_mcu_parse_response()` validates response sequence, reports timeouts, and feeds watchdog MCU-hang state.
- `mt7603_mcu_skb_send_msg()` prepends an MCU TXD, assigns nonzero 4-bit sequence numbers, selects firmware or normal port queue, handles legacy negative command IDs vs extended commands, and queues raw SKBs on `MT_MCUQ_WM`.
- `mt7603_mcu_init_download()`, `mt7603_mcu_start_firmware()`, and `mt7603_mcu_restart()` wrap ROM/firmware commands.
- `mt7603_load_firmware()` selects firmware by chip/revision, requests it, logs version/build time, switches scheduler bypass mode, downloads if ROM is ready and firmware is not already running, starts firmware, waits for ready bit, and records wiphy firmware version.
- `mt7603_mcu_init()` installs `mt76_mcu_ops` and loads firmware; `mt7603_mcu_exit()` requests restart download mode and purges responses.
- `mt7603_mcu_set_eeprom()` builds an efuse buffer-mode request from selected EEPROM offsets and sends it to firmware.
- `mt7603_mcu_set_tx_power()` sends EEPROM-derived target/rate/channel/temp compensation power fields.
- `mt7603_mcu_set_channel()` sends control/center channel, bandwidth, streams, SAR-limited txpower array, then sends txpower control.

## Control Flow
Hardware init calls `mt7603_mcu_init()` after DMA queues exist. Firmware load may skip download if a running bit is already set; otherwise it initializes target address/length, streams firmware chunks through common mt76 MCU helpers, starts firmware, and waits for initialization. Later init uploads EEPROM fields. Channel changes call `mt7603_mcu_set_channel()` and then `mt7603_mcu_set_tx_power()`. Exit sends restart-download and clears queued responses.

## State And Persistence
State includes `dev->mcu_running`, `dev->mcu_hang`, `dev->mt76.mcu_ops`, `dev->mt76.mcu.msg_seq`, `dev->mphy.txpower_cur`, and `hw->wiphy->fw_version`. Firmware is requested from the filesystem but not modified. EEPROM bytes are copied into request buffers and sent to firmware.

## Dependencies And Integration Points
Depends on Linux firmware loader, common mt76 MCU helpers, mt7603 firmware names/revision helpers, EEPROM offsets, DMA MCU queue allocation, and SAR/txpower helpers from mt76 core. RX event dispatch in `dma.c` must deliver MCU responses to common queues.

## Risks
Firmware selection by chip/revision must match available firmware files. The response parser only checks sequence, so command-specific status interpretation is minimal. Sequence space is 4 bits and skips zero; stale responses can cause `-EAGAIN` loops until timeout. EEPROM upload uses a fixed 0xff-entry request buffer and selected offsets, including unknown fields, so offset mistakes affect firmware calibration. Channel txpower subtracts 6 half-dBm for 2-chain operation and clamps to EEPROM limit; incorrect units break regulatory power.

## Test Signals
Probe all supported chip revisions with correct/missing/invalid firmware, verify firmware version string, command timeout behavior, MCU hang reset counter, channel switch across 20/40 MHz, SAR changes, txpower limits, and EEPROM upload success. Confirm teardown purges response queues and restart command does not hang remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mcu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mcu.h

## Purpose
MT7603 MCU command/response descriptor definitions, packet constants, firmware download address, command IDs, extended command IDs, and extended event IDs.

## Important APIs, Types, And Functions
- `struct mt7603_mcu_txd` defines the packed command header: length, port/queue, command ID, packet type, set/query mode, sequence, extended command fields, and reserved words.
- `struct mt7603_mcu_rxd` defines response/event fields used for sequence matching and extended event identification.
- `MCU_PKT_ID`, `MCU_PORT_QUEUE`, `MCU_PORT_QUEUE_FW`, and `MCU_FIRMWARE_ADDRESS` define packet routing and firmware target address.
- Query mode enum defines query, set, reserved, and not-applicable values.
- Base command enum includes target address/length, firmware start/scatter/restart, patch commands, loopback/channel privilege, register access, and extended command wrapper.
- Extended command/event enums name channel switch, efuse buffer mode, txpower control, power saving, beacon update, EDCA, thermal, and related firmware operations.

## Control Flow
Header-only constants are consumed by `mcu.c` when framing commands and interpreting responses. Negative command IDs in `mcu.c` map to base commands; positive IDs are wrapped as `MCU_CMD_EXT_CID`.

## State And Persistence
No direct state. It defines the host/firmware ABI for command SKBs and response SKBs.

## Dependencies And Integration Points
Used by mt7603 MCU implementation and indirectly by DMA RX event routing. It must align with firmware command ABI and firmware image expectations.

## Risks
Packed layout or command-ID mistakes can make firmware ignore commands or misparse payloads. Response sequence field position is critical for timeout/retry logic. Reused command value `0x20` for loopback/channel privilege requires context-sensitive use.

## Test Signals
Firmware download/start, extended channel switch, efuse buffer upload, txpower command, and teardown restart are the main ABI tests. Trace raw MCU headers if firmware command timeouts appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mcu.h -->
