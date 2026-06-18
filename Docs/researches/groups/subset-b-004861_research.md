# subset-b-004861 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mcu.c

## Purpose
`mcu.c` is the MT7996/MT7992/MT7990 firmware-control implementation. It owns MCU message formatting, firmware and ROM patch download, asynchronous firmware event dispatch, BSS/STA update TLV construction, channel/radar/thermal/TWT/txpower commands, EEPROM/efuse access, and WA/WM command compatibility shims. Most exported functions are invoked by init, mac80211 callbacks, debugfs, DFS, thermal, and reset paths through prototypes in `mt7996.h`.

## Important APIs, Types, And Functions
The local firmware image types (`mt7996_patch_hdr`, `mt7996_patch_sec`, `mt7996_fw_trailer`, `mt7996_fw_region`) describe ROM patch and RAM firmware layout. `fw_name()` chooses firmware filenames by chip ID and variant. `mt7996_mcu_send_message()` and `mt7996_mcu_parse_response()` install as `mt76_mcu_ops` in `mt7996_mcu_init()`, wrapping Connac MCU TX descriptors and result parsing. `mt7996_mcu_rx_event()` routes unsolicited events to handlers for firmware log, CSA/BSS color countdown, radar detection, all-station stats, thermal notify, and WED RRO BA session events.

The BSS path is built around `__mt7996_mcu_alloc_bss_req()`, `mt7996_mcu_add_uni_tlv()`, and exported operations such as `mt7996_mcu_add_bss_info()`, `mt7996_mcu_update_bss_rfch()`, `mt7996_mcu_set_protection()`, `mt7996_mcu_set_timing()`, `mt7996_mcu_add_beacon()`, and `mt7996_mcu_beacon_inband_discov()`. The STA path uses `__mt76_connac_mcu_alloc_sta_req()` plus many STA_REC TLV helpers for basic state, HT/VHT/HE/EHT capabilities, AMSDU, UAPSD, rate control, beamforming, BA sessions, security keys, header translation, MLD setup, and EMLSR.

Firmware lifecycle functions include `mt7996_mcu_init_firmware()`, `mt7996_load_firmware()`, `mt7996_load_patch()`, `mt7996_load_ram()`, and `mt7996_mcu_exit()`. Runtime control exports include `mt7996_mcu_set_chan_info()`, `mt7996_mcu_rdd_cmd()`, `mt7996_mcu_rdd_background_enable()`, `mt7996_mcu_set_thermal_protect()`, `mt7996_mcu_set_txpower_sku()`, `mt7996_mcu_set_rro()`, `mt7996_mcu_set_ser()`, `mt7996_mcu_rf_regval()`, `mt7996_mcu_wa_cmd()`, and `mt7996_mcu_cp_support()`.

## Control Flow
Initialization starts with driver ownership, optional dual-HIF ownership, firmware download-state polling, ROM patch semaphore acquisition and segmented patch transfer, WM RAM load, optional DSP/WA RAM load, final firmware-ready polling, firmware log disablement, MWDS enablement, RX airtime VOW setup, and WA RED setup. Thereafter `mt76_mcu_send_msg()` calls enter `mt7996_mcu_send_message()`, which chooses FWDL, WM, or WA queues, assigns a nonzero 4-bit sequence, prepends either legacy or UNI descriptors, and sets ACK/query bits. Response parsing validates sequence IDs, handles patch semaphore replies specially, and checks UNI result events by CID.

mac80211 state changes flow into BSS or STA update messages. BSS creation writes the basic TLV first, then security, RF channel, rates, RA, TXCMD, timing, HE basics, MLD, and MBSSID. STA connect writes basic state, header translation, TX processing, beamforming, protocol capability TLVs, rate control, AMSDU, MURU, and MLO TLVs, then assigns a VOW DRR group before sending. Disconnects short-circuit after the basic record. Beacon offload fetches templates from mac80211, checks firmware size limits, writes TXWI via `mt7996_mac_write_txwi()`, appends beacon contents, MBSSID offsets, and countdown state.

Unsolicited MCU events are dispatched by option/eid/ext_eid. Radar events choose the affected phy or background detector and call cfg80211/mac80211 radar notifications. Countdown events iterate active interfaces atomically and finish CSA or color-change operations for matching band/OMAC. All-station events update `mt76_wcid` rates and counters. WED RRO events update RX TID session IDs or enqueue session deletion work.

## State And Persistence
The file mostly mutates in-memory driver and mac80211 state. It sets `MT76_STATE_MCU_RUNNING`, recovery restart flags, `dev->hw_pattern`, `phy->rdd_tx_paused`, thermal throttle state, current txpower, beacon fixed-rate state, WED RRO session lists, WCID rate/stat counters, WCID AMSDU/header-translation flags, and EEPROM buffer contents. Firmware and EEPROM are persistent external inputs loaded via `request_firmware()` or read from efuse/ext EEPROM; `mt7996_mcu_set_eeprom()` pushes the local EEPROM image to firmware in pages. No filesystem state is written.

## Dependencies And Integration Points
This file depends heavily on mt76 Connac helpers, Linux firmware loading, mac80211/cfg80211 station/BSS APIs, skb/TLV primitives, DFS/thermal subsystems, debugfs firmware logging hooks, `mac.c` TXWI/WTBL helpers, and register/variant helpers from `regs.h`, `eeprom.h`, and `mt7996.h`. It integrates with PCI/MMIO initialization through `mt7996_mcu_init()`, with DMA/RRO through WED RRO commands and events, with init through EEPROM/txbf/RRO setup, and with reset recovery through timeout and SER commands.

## Risks
The largest risk is firmware ABI drift: TLV lengths, tag values, field ordering, endian conversions, and tag ordering must match WM/WA firmware exactly. MLO paths use RCU-protected link state and can silently skip missing links, so races or partial link teardown may produce incomplete firmware state. Several message builders use fixed maximum skb sizes; new TLVs can overrun assumptions if size constants are not kept in sync. Firmware loading trusts trailer/region metadata after basic size checks, and bad offsets could fail late during transfer. Direct WTBL writes for fixed GI must remain synchronized with firmware rate-control behavior. RRO BA delete events allocate in atomic context and queue work; memory pressure can drop cleanup requests.

## Test Signals
Useful signals are successful probe firmware logs showing patch/WM/DSP/WA versions, absence of MCU command timeouts, working AP/STA bring-up across 2/5/6 GHz, successful CSA and BSS color countdown completion, DFS radar detection including background radar, thermal zone reads and throttling notifications, beacon/FILS/unsolicited probe response offload behavior, fixed rate and txpower SKU programming, MLO station add/remove and EMLSR operation, WED RRO BA session creation/deletion, and debugfs firmware logging. Negative tests should force missing firmware, bad EEPROM reads, MCU timeout/reset, oversized beacon templates, and unsupported ciphers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mcu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mcu.h

## Purpose
`mcu.h` is the firmware ABI contract for `mcu.c`. It defines packed MCU RX/event records, command TLVs, enums, constants, and maximum message-size formulas used when constructing MT7996-family UNI and legacy MCU messages. It is intentionally hardware/firmware-facing: fields are endian-annotated, packed, and often mirror exact TLV payloads consumed or emitted by WM/WA firmware.

## Important APIs, Types, And Functions
The receive-side core is `mt7996_mcu_rxd`, which describes firmware event headers with EID, sequence, option, ext EID, and source/destination index. `mt7996_mcu_uni_event` carries generic UNI command result status. Event payload structures cover thermal notifications, countdown notifications, radar reports with pulse arrays, all-station rate/stat responses, and WED RRO BA session events.

Command payload types are grouped by subsystem. BSS TLVs include rate, RA, RLM channel, color, in-band discovery, beacon content/countdown/MBSSID, security, timing, MLD, protection, and MLD link operation. STA TLVs include HT, BA, EHT, security keys, RA, fixed RA, header translation, MLD setup, EHT MLD, and fixed-rate control. Other structures cover EEPROM update/access, background chain/offchannel scan, thermal control, VOW RX airtime, beamforming control, RRO settings, SER commands, RF register access, and txpower table control.

Important enums define UNI tags and command sub-actions: firmware logging, TWT agreement operations, WA parameter commands, MMPS modes, header translation TLVs, rate-control fields, beamforming actions, channel-switch tags, band config tags, RDD/efuse/VOW/MIB/power/TWT/RRO/SR/thermal/txpower/reg/SER/SDO tag IDs, and patch security modes. Size constants such as `MT7996_BSS_UPDATE_MAX_SIZE`, `MT7996_STA_UPDATE_MAX_SIZE`, `MT7996_MAX_BSS_OFFLOAD_SIZE`, and `MT7996_MAX_BEACON_SIZE` constrain skb allocation in `mcu.c`.

## Control Flow
This header has no executable control flow, but it shapes runtime control by defining how message builders append TLVs and how event handlers cast skb payloads. `mcu.c` allocates a command skb, writes a fixed header such as `bss_req_hdr` or `uni_header`, appends one or more structures from this header through `mt7996_mcu_add_uni_tlv()` or `mt76_connac_mcu_add_tlv()`, and sends the skb through mt76 MCU ops. Receive handlers pull `mt7996_mcu_rxd`, then inspect EID/tag values from this header to decide which packed payload to parse.

## State And Persistence
The header itself stores no state. It defines the wire representation for state that lives in firmware, hardware tables, and driver objects: BSS indices, WCID indices, EEPROM pages, RRO session IDs, thermal thresholds, radar pulse data, MLD IDs, RA state, beacon offload templates, and security key material. Because many structures contain flexible arrays or unions, caller-side length and tag validation is the real state-safety boundary.

## Dependencies And Integration Points
`mcu.h` includes `../mt76_connac_mcu.h`, so it extends shared Connac MCU definitions rather than replacing them. It is consumed primarily by `mcu.c`, but exported function declarations in `mt7996.h` expose many operations whose payloads are described here. It also depends on Linux/mac80211 constants such as `IEEE80211_NUM_ACS`, cipher IDs, HE/EHT capability shapes, and endian types.

## Risks
The main risk is ABI mismatch. Packed structure layout, reserved bytes, endian conversion, tag IDs, and maximum message sizes must match firmware exactly. Some structs expose flexible arrays and unioned payload interpretations; an incorrect tag or length can cause parser confusion or truncated copies. Size macros can become stale when new TLVs are added, producing allocation underruns in command builders. The header also carries key material layouts, including beacon protection modes, so cipher ID mistakes can break security behavior.

## Test Signals
Compile-time coverage should catch missing type/tag names and many size changes. Runtime signals include successful MCU command acknowledgements, valid all-station and thermal events, correct beacon/offload operation, successful EEPROM/efuse queries, WED RRO BA status processing, and stable behavior across MT7996, MT7992, and MT7990 variants. ABI regressions typically surface as firmware command failures, invalid status events, broken station setup, or command timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mmio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mmio.c

## Purpose
`mmio.c` provides the memory-mapped bus layer for MT7996-family PCIe devices. It selects chip-specific register bases, offset tables, and physical-to-MMIO maps; wraps mt76 bus read/write/rmw callbacks with dynamic remap handling; initializes optional MediaTek WED hardware offload integration; drives interrupt masking and the irq tasklet; allocates the mt76 device; and registers/unregisters the PCI drivers at module load/unload.

## Important APIs, Types, And Functions
The register data tables are `mt7996_reg_base`, chip-specific offset arrays (`mt7996_offs`, `mt7992_offs`, `mt7990_offs`), and address maps (`mt7996_reg_map`, `mt7990_reg_map`). `mt7996_reg_map_l1()`, `mt7996_reg_map_l2()`, and `mt7996_reg_map_cbtop()` program HIF remap registers for addresses outside the directly mapped window. `__mt7996_reg_addr()` searches static maps, while `__mt7996_reg_remap_addr()` chooses L1/L2/CBTOP remapping for infra, WFSYS, CBTOP, and fallback ranges.

The exported `mt7996_memcpy_fromio()` supports bulk MMIO reads with the same remap lock discipline. `mt7996_rr()`, `mt7996_wr()`, and `mt7996_rmw()` replace the mt76 bus ops after `mt7996_mmio_init()`. `mt7996_mmio_wed_init()` configures `struct mtk_wed_device` fields for primary and secondary HIF, including WPDMA interrupt/mask/ring addresses, RRO rings, token sizing, TXFREE routing, RX buffer sizing, and callbacks. `mt7996_dual_hif_set_irq_mask()`, `mt7996_irq_handler()`, and `mt7996_irq_tasklet()` manage interrupt masking and NAPI scheduling.

`mt7996_mmio_probe()` allocates the device with mt76 driver ops and initializes bus mapping, tasklet, and initial IRQ state. Module init registers `mt7996_hif_driver` first and `mt7996_pci_driver` second; module exit unregisters them in reverse.

## Control Flow
During PCI probe, `pci.c` calls `mt7996_mmio_probe()` with BAR0. The function calls `mt76_alloc_device()`, then `mt7996_mmio_init()`, which initializes the base MMIO bus, sets the chip-specific register descriptor, clones the original bus ops, overrides rr/wr/rmw, and records the ASIC revision. Runtime register access first attempts direct static mapping; if no mapping is found it acquires `dev->reg_lock`, programs the appropriate remap window, performs the access, and releases the lock.

Interrupt flow starts in `mt7996_irq_handler()`, which masks primary and optional secondary HIF interrupts and schedules the mt76 irq tasklet after initialization. The tasklet reads interrupts either through active WED devices or raw interrupt source CSRs, merges HIF2 status when present, traces the interrupt, disables active RX/MCU TX bits, schedules TX NAPI or RX NAPI per queue, and handles MCU error/watchdog command bits by recording recovery state and invoking `mt7996_reset()`. RX poll completion re-enables either NPU WLAN IRQs or normal MT_INT_RX bits.

## State And Persistence
This file initializes and mutates `dev->reg`, `dev->bus_ops`, `dev->mt76.bus`, `dev->mt76.mmio.irqmask`, `dev->mt76.hwrro_mode`, WED device structs, DMA device selection, token sizes, irq tasklet state, and hardware interrupt mask/source registers. All state is runtime-only hardware/driver state; module parameters `wed_enable` and WED attach success decide whether WED state is active.

## Dependencies And Integration Points
`mmio.c` integrates mt76 MMIO, Linux PCI/module APIs, MediaTek WED (`CONFIG_NET_MEDIATEK_SOC_WED`), optional NPU queues, `trace_dev_irq`, DMA/RRO callbacks, and reset/SER routines in `mcu.c` and `mac.c`. Its driver ops connect mac80211-facing operations (`mt7996_ops`) to DMA/TX/RX/channel callbacks implemented in other files. The PCI drivers it registers are defined in `pci.c`.

## Risks
Register remap programming is serialized only for unmapped accesses; any caller bypassing bus ops could race remap windows. Chip-specific map/offset errors can send reads/writes to wrong hardware blocks. WED setup has many variant-dependent ring offsets and interrupt bits, especially with dual HIF and MT7992/MT7990 differences. Interrupt masking must stay balanced with NAPI completion; missed re-enable paths can stall RX, while premature unmasking can storm interrupts. WED reset temporarily drops RTNL, so reset completion and state bits must be robust.

## Test Signals
Probe should log the expected ASIC revision and succeed on MT7996, MT7992, and MT7990. Register reads through mapped and remapped ranges should return sane values. Traffic should schedule the expected RX/TX NAPI queues on single-HIF, dual-HIF, WED, and non-WED configurations. MCU watchdog/error interrupts should trigger recovery. WED attach/detach, RRO traffic, and NPU RX queue interrupt re-enable are key integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mt7996.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mt7996.h

## Purpose
`mt7996.h` is the central driver header for the MT7996 family. It defines chip IDs, firmware and EEPROM filenames, queue/ring sizing, hardware constants, variant enums, per-VIF/per-STA/per-PHY/per-device structures, helper accessors, interrupt helpers, and function prototypes spanning PCI/MMIO, DMA, MCU, MAC, EEPROM, DFS, debugfs, RRO, WED, and optional NPU support.

## Important APIs, Types, And Functions
Important constants include device IDs for primary and secondary PCI functions, firmware/ROM patch names for MT7996/MT7992/MT7990 variants, EEPROM defaults, EEPROM/efuse sizes, token/ring sizes, WTBL sizing helpers, TWT limits, RRO table sizes, thermal thresholds, and queue IDs. Variant enums describe RAM firmware type, chip variant, FEM type, EEPROM mode, TX queue IDs, RX queue IDs, and RDD commands/indices.

Core state types are `mt7996_twt_flow`, `mt7996_sta_link`, `mt7996_sta`, `mt7996_vif_link`, `mt7996_vif_link_info`, `mt7996_vif`, `mt7996_crash_data`, `mt7996_hif`, RRO address/session/page structures, `mt7996_phy`, and `mt7996_dev`. `mt7996_dev` embeds `mt76_dev`/`mt76_phy` first, tracks registered radios, HIF2, register descriptors, queue masks, MLD index masks, recovery work/state, coredump, station/TWT lists, EEPROM mode, RRO buffers/work/list/locks, NPU TX descriptor DMA addresses, debugfs state, firmware debug settings, register lock, WTBL sizing, and variant data.

Inline helpers include `mt7996_get_rdd_idx()`, `mt7996_hw_dev()`, `mt7996_phy2()`, `mt7996_phy3()`, `mt7996_band_valid()`, `mt7996_band_phy()`, VIF/link accessors, `mt7996_has_hwrro()`, `mt7996_max_interface_num()`, `mt7996_wtbl_size()`, `mt7996_irq_enable()`, `mt7996_irq_disable()`, `mt7996_rx_chainmask()`, `mt7996_has_wa()`, and `mt7996_has_ext_eeprom()`. Optional NPU prototypes are replaced with zero-return stubs when `CONFIG_MT7996_NPU` is disabled.

## Control Flow
This header has no top-level execution, but it defines the call graph shared by the driver. PCI probe enters `mt7996_mmio_probe()`, then `mt7996_register_device()`, which initializes EEPROM, DMA, MCU, PHYs, thermal, txbf, RRO, and optional NPU paths through prototypes declared here. mac80211 operations use the MCU and MAC prototypes for BSS/STA/beacon/channel/rate/TWT/key changes. Interrupt helpers call either dual-HIF mask handling or raw mt76 mask writes, then schedule the irq tasklet.

## State And Persistence
The primary persistent external artifacts named here are firmware and EEPROM files. Runtime state is carried by the structures in this header: phy thermal and radar pause state, WCID/link/TWT state, MLD masks, recovery counters, RRO DMA allocations and deletion lists, debugfs relay state, register-remap lock state, and variant selection. Many structs are embedded into mac80211 or mt76 private areas and rely on first-member layout compatibility with mt76 base structs.

## Dependencies And Integration Points
`mt7996.h` includes `../mt76_connac.h` and `regs.h`, binding it to mt76 Connac helpers and the local register definitions. It declares external `mt7996_ops`, PCI driver objects, and most cross-file functions. It also integrates Linux interrupt, thermal, ktime, debugfs, relay, RCU, DMA, mac80211, cfg80211, WED, and optional Airoha NPU concepts indirectly through included mt76/kernel headers.

## Risks
Because this is the shared contract, layout changes can break container casts, mt76 private data sizing, firmware filename selection, queue indexing, and WTBL arithmetic. Queue ID definitions are variant-sensitive; wrong IDs can corrupt DMA or NAPI routing. Inline helpers hide policy such as MT7990 lacking WA firmware or non-MT7996 having fewer bands, so new chips need careful updates. Size constants affect allocations and hardware limits across files. Conditional NPU stubs can mask missing offload behavior in non-NPU builds.

## Test Signals
Build coverage across `CONFIG_MT7996_NPU`, `CONFIG_NET_MEDIATEK_SOC_WED`, debugfs, and coredump options is important. Runtime signals include correct firmware file requests for each variant, successful single/dual-band/tri-band registration, correct WTBL and interface limits, working IRQ enable/disable on single and dual HIF, valid RRO/NPU queue setup when enabled, and stable MLO station/VIF behavior using the declared link structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mt7996.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/npu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/npu.c

## Purpose
`npu.c` implements optional Airoha NPU offload setup and teardown for MT7996-family WLAN devices. It programs the NPU with WLAN PCIe register addresses, descriptor counts, token sizing, RX/TX descriptor bases, TX buffer-space DMA bases, TX-done event rings, and interrupt enablement so selected traffic/RRO paths can be offloaded from host processing.

## Important APIs, Types, And Functions
The chip-specific TX/RX setup functions are `mt7996_npu_txrx_offload_init()` and `mt7992_npu_txrx_offload_init()`. `mt7996_npu_offload_init()` reads the NPU firmware version, configures PCIe port type, delegates chip-specific ring setup, sets token ID size, and updates `dev->mt76.token_start`. RX descriptor base functions are split as `mt7996_npu_rxd_init()` and `mt7992_npu_rxd_init()`. `mt7996_npu_txd_init()` retrieves NPU TX ring descriptor bases and sends per-band TX buffer-space base addresses from `dev->npu_txd_addr`.

Additional setup helpers configure TX-done event handling (`mt7996_npu_rx_event_init()`), RRO RX PCIe addresses (`mt7996_npu_set_pcie_addr()`), and TX-done/reset inode addresses (`mt7996_npu_tx_done_init()`). Exported entry points are `mt7996_npu_rx_queues_init()`, `__mt7996_npu_hw_init()`, `mt7996_npu_hw_init()`, and `mt7996_npu_hw_stop()`.

## Control Flow
`mt7996_npu_hw_init()` first allocates coherent DMA memory for groups of three TX descriptor/buffer regions per offloaded band and records the DMA addresses in `dev->npu_txd_addr`. Under `dev->mt76.mutex`, `__mt7996_npu_hw_init()` obtains the RCU-protected `airoha_npu`, initializes offload parameters, writes RX descriptor bases into mt76 queue register blocks, writes TX descriptor bases into per-phy TX queues, configures TX-done and PCIe addresses, then enables two NPU WLAN IRQs.

`mt7996_npu_rx_queues_init()` initializes mt76 NPU RX queues only when an NPU device is active. Stop flow locks the mt76 mutex, disables a TX/RX inode address, polls NPU info up to ten times waiting for quiescence, then clears a second inode address; failure logs `npu stop failed`.

## State And Persistence
NPU setup mutates `dev->npu_txd_addr[]`, mt76 RX/TX queue descriptor-base registers, `dev->mt76.token_start`, NPU firmware-side descriptor counts and PCIe addresses, and active NPU IRQ state. It uses DMA-coherent allocations owned by `dmam_alloc_coherent()`, so lifetime is device-managed rather than manually freed in this file. No persistent filesystem state is written.

## Dependencies And Integration Points
The file depends on `linux/soc/airoha/airoha_offload.h`, mt76 NPU helpers (`mt76_npu_send_msg`, `mt76_npu_get_msg`, `mt76_npu_rx_queue_init`, `mt76_npu_device_active`), MMIO physical base addresses from `dev->mt76.mmio`, queue/register constants from `regs.h` and `mt7996.h`, and device mutex/RCU synchronization from mt76. It is compiled only when enabled by `CONFIG_MT7996_NPU`; otherwise `mt7996.h` supplies no-op stubs.

## Risks
The code is highly dependent on magic NPU function IDs, ring IDs, and per-chip queue mappings. Incorrect offsets or band-to-phy mapping can point the NPU at the wrong WFDMA ring. DMA allocation sizes differ between MT7996 and MT7992 paths and must match NPU firmware expectations. `writel()` updates queue descriptor bases directly, so calling order relative to mt76 DMA setup matters. Stop polling has a bounded timeout and may leave offload partially enabled on failure.

## Test Signals
Important signals are NPU firmware version logs, successful `mt76_npu_send_msg()`/`get_msg()` calls, initialized `MT_RXQ_NPU0/1`, valid descriptor-base writes for RRO/MSDU/IND/TX rings, traffic through NPU offload without RX/TX stalls, correct behavior on MT7996 versus MT7992 mappings, clean stop without timeout, and recovery after reset or NPU absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/npu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/pci.c

## Purpose
`pci.c` is the PCI probe/remove layer for MT7996-family devices. It binds primary WLAN PCI functions and secondary HIF functions, coordinates discovery of optional HIF2, enables PCI resources and DMA masks, creates the MMIO/mt76 device, initializes WFSYS/NPU/WED/IRQ plumbing, registers the full WLAN device, and advertises required firmware blobs to the kernel module loader.

## Important APIs, Types, And Functions
Two PCI ID tables split primary devices (`MT7996_DEVICE_ID`, `MT7992_DEVICE_ID`, `MT7990_DEVICE_ID`) from secondary HIF devices (`*_DEVICE_ID_2`). A global `hif_list`, `hif_lock`, and `hif_idx` track probed secondary HIFs. `mt7996_pci_hif2_probe()` allocates and registers an `mt7996_hif` object with BAR0 regs, IRQ, and PCIe bandwidth data. `mt7996_pci_init_hif2()` stamps a recognition ID into the primary device and searches the HIF list via `mt7996_pci_get_hif2()`.

The main entry point is `mt7996_pci_probe()`. Remove paths are split into `mt7996_hif_remove()` for secondary functions and `mt7996_pci_remove()` for primary devices. Driver objects `mt7996_hif_driver` and `mt7996_pci_driver` are registered by `mmio.c`.

## Control Flow
Probe enables the PCI device, maps BAR0, sets bus mastering, installs 36-bit streaming and 32-bit coherent DMA masks, and disables ASPM through mt76. If the probed ID is a secondary HIF, it only records HIF metadata and returns. For primary functions, it calls `mt7996_mmio_probe()`, resets WFSYS, tries to find HIF2, initializes NPU metadata, initializes WED for primary HIF or allocates IRQ vectors, requests the primary IRQ, disables interrupt masks, and enables the PCIe MAC interrupt master switch.

If HIF2 is present, the probe repeats WED/IRQ setup for the secondary PCI device, requests a shared interrupt using the same `mt7996_irq_handler()`, disables HIF2 masks, and enables the secondary PCIe interrupt master switch. Finally it calls `mt7996_register_device()`. Error labels unwind HIF2 IRQ/WED/vector references, primary IRQ/WED/vectors, HIF device references, and mt76 allocation.

## State And Persistence
Runtime state includes the global HIF list, reference counts on secondary HIF devices, `dev->hif2`, `dev->hif2->irq`, PCI IRQ vectors, WED attachment state, NPU MMIO physical base/type, interrupt enable registers, and the mt76 device registered as PCI driver data. No persistent data is written. Module firmware declarations identify firmware names for udev/kernel loading.

## Dependencies And Integration Points
`pci.c` integrates Linux PCI managed APIs, mt76 PCI helpers, DMA mask APIs, WED initialization from `mmio.c`, IRQ handling from `mmio.c`, WFSYS reset and device registration from init/reset code, NPU setup from mt76/NPU paths, and firmware filenames from `mt7996.h`. The secondary HIF handshake depends on `MT_PCIE_RECOG_ID` registers and the separate HIF PCI driver being registered before the primary driver.

## Risks
Dual-HIF discovery is order-sensitive and uses a global incrementing recognition ID plus a shared list. Reference handling must remain correct across probe failures and remove. The use of `pci_get_device()` in the HIF2 existence check can affect device references if not balanced by PCI core expectations. Error unwinding mixes WED detach, IRQ vector freeing, devm IRQ freeing, and HIF references; new failure points need careful placement. Shared IRQs for primary/HIF2 rely on the common handler correctly masking both interrupt domains.

## Test Signals
Probe should succeed for each primary chip ID with and without a secondary HIF device present. Logs and sysfs should show the device registered after firmware load. Dual-HIF systems should request both IRQs and route band-specific traffic without interrupt stalls. Failure tests should cover WED attach failure, IRQ allocation failure, request_irq failure, register-device failure, and removal of primary/secondary functions without leaked references or stale HIF list entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/pci.c -->
