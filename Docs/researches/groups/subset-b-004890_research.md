# Research: subset-b-004890

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/sw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/sw.c

## Purpose
This file is the PCI driver registration and rtlwifi HAL binding layer for the Realtek RTL8192EE 802.11n PCIe chipset. It initializes module parameters and software state, requests `rtlwifi/rtl8192eefw.bin`, exposes the PCI device table, and binds chip-specific callbacks into the shared rtlwifi PCI/mac80211 core through `struct rtl_hal_ops` and `struct rtl_hal_cfg`.

## Important APIs, Types, And Functions
`rtl92ee_init_aspm_vars()` seeds PCIe ASPM policy constants, including device/host ASPM masks, radio-off D3 behavior, and module-controlled ASPM support. `rtl92ee_init_sw_vars()` initializes Bluetooth coexistence, MSI support, dynamic-management defaults, transmit/receive configuration, interrupt masks, power-save defaults, early-mode state, firmware buffer allocation, and asynchronous firmware loading through `request_firmware_nowait()`. `rtl92ee_deinit_sw_vars()` releases the firmware buffer. `rtl92ee_get_btc_status()` advertises Bluetooth coexistence support.

The central data objects are `rtl8192ee_hal_ops`, `rtl92ee_mod_params`, `rtl92ee_hal_cfg`, `rtl92ee_pci_ids`, and `rtl92ee_driver`. The HAL ops table connects the generic rtlwifi core to RTL8192EE-specific EEPROM, interrupt, init, power, channel, descriptor, security, BB/RF, H2C, Bluetooth coexistence, and C2H rate-report handlers. The HAL config maps generic rtlwifi register and interrupt identifiers to 8192EE register constants and rate constants.

## Control Flow
Kernel module loading registers `rtl92ee_driver` via `module_pci_driver()`. PCI probe is handled by the shared `rtl_pci_probe()` using `rtl92ee_hal_cfg` from the matching PCI id. During software initialization, the file programs default state before hardware init: receive filter bits, interrupt masks, power-save policy, current band, MAC/PHY mode, and firmware storage. Firmware loading is asynchronous and handled by the shared `rtl_fw_cb`, so init must tolerate callback-driven firmware availability.

## State And Persistence
Persistent runtime state is stored in shared `rtl_priv`, `rtl_pci`, `rtl_hal`, `rtl_dm`, and `rtl_ps_ctl` objects. The file sets long-lived module parameters such as `swenc`, `ips`, `swlps`, `fwlps`, `msi`, `dma64`, `aspm`, `debug_level`, `debug_mask`, and `disable_watchdog`. The firmware buffer is allocated with `vzalloc(0x8000)` and freed only in deinit. Hardware register state itself is replayed through HAL callbacks during probe, resume, and restart rather than persisted here.

## Dependencies And Integration Points
This module integrates with Linux PCI, firmware loader, module parameter APIs, mac80211 through rtlwifi core, rtlwifi PCI transport, Realtek Bluetooth coexistence (`../btcoexist/rtl_btc.h`), and all sibling chip modules (`hw`, `phy`, `dm`, `fw`, `trx`, `led`, `table`). Firmware name and max size must match the blob expected by `fw.c`.

## Risks
The most important risks are registration-table drift and firmware lifetime bugs. If any HAL callback is mismatched with the descriptor or register layout, the generic rtlwifi core will call the wrong chip-specific behavior. The asynchronous firmware request means the firmware buffer must remain valid until callback completion. `dma64` defaults false despite 64-bit descriptor helpers elsewhere, so enabling it must be tested with the PCI transport. ASPM defaults and power-save module parameters can cause platform-specific wake, RF kill, or resume regressions.

## Test Signals
Useful signals include successful module load/probe on PCI id `0x818B`, firmware request completion for `rtlwifi/rtl8192eefw.bin`, correct registration of rtlwifi ops, interrupts arriving through configured masks, MSI on/off behavior, suspend/resume through `rtl_pci_suspend()` and `rtl_pci_resume()`, and clean unload without leaked firmware buffer. Runtime tests should exercise TX/RX, scan, association, Bluetooth coexistence paths, LPS/IPS, hardware crypto, and watchdog-disabled module option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/table.c

## Purpose
This file contains static register-programming tables for RTL8192EE MAC, baseband, RF path A/B, per-rate power group, and AGC initialization. The arrays are consumed by the RTL8192EE PHY/configuration code to replay vendor-provided register sequences during device bring-up and calibration.

## Important APIs, Types, And Functions
There are no functions. The exported data arrays are `RTL8192EE_PHY_REG_ARRAY`, `RTL8192EE_PHY_REG_ARRAY_PG`, `RTL8192EE_RADIOA_ARRAY`, `RTL8192EE_RADIOB_ARRAY`, `RTL8192EE_MAC_ARRAY`, and `RTL8192EE_AGC_TAB_ARRAY`. Most arrays are address/value pairs. `RTL8192EE_PHY_REG_ARRAY_PG` is organized as power-group records containing band/RF-path/rate-section selectors, register address, bitmask, and value fields. The tables include conditional marker pairs such as `0xFF010718` with `0xABCD`/`0xDEAD` and `0xCDCDCDCD`, which the table parser must interpret rather than treating as ordinary registers.

## Control Flow
The control flow is external: PHY/MAC configuration iterates these arrays in order and writes each register or masked field to hardware. The MAC table programs byte-addressed MAC defaults. PHY and AGC tables program BB/AGC registers. Radio A/B arrays program RF6052 path-specific register sequences. The power group table stores and applies per-rate transmit-power offsets.

## State And Persistence
The arrays are immutable built-in module data. Their effects are persistent only in hardware registers until reset, suspend, IPS, or module unload. On every hardware initialization, the same table sequences are replayed, often combined with EFUSE-derived channel power data and later dynamic-management adjustments.

## Dependencies And Integration Points
The arrays are declared in `table.h` and consumed by RTL8192EE PHY code. Their register constants and marker grammar must match the PHY parser and the `reg.h` layout. The data also indirectly depends on EFUSE interpretation because power-group defaults are combined with device-specific calibration data.

## Risks
The risk is data correctness rather than algorithmic behavior. Incorrect lengths, ordering, marker handling, or register values can break RF bring-up, transmit power, AGC sensitivity, or regulatory behavior. The conditional markers make naive iteration unsafe. Because these values are vendor calibration data, changes should be treated like hardware enablement changes and validated on real devices.

## Test Signals
Test signals are successful BB/MAC/RF configuration without parser warnings, stable association and throughput on 2.4 GHz channels, sane RSSI/noise readings, correct transmit power across channels and MCS rates, and absence of firmware/hardware register access failures during init. Regression testing should include cold boot, warm reboot, resume, and RF power-cycle paths that replay these tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/table.h

## Purpose
This header declares the RTL8192EE hardware initialization arrays and their element counts for use by PHY/MAC/RF setup code. It is the contract between `table.c` and the chip-specific configuration logic.

## Important APIs, Types, And Functions
The header exports length macros and `extern u32` declarations for `RTL8192EE_PHY_REG_ARRAY`, `RTL8192EE_PHY_REG_ARRAY_PG`, `RTL8192EE_RADIOA_ARRAY`, `RTL8192EE_RADIOB_ARRAY`, `RTL8192EE_MAC_ARRAY`, and `RTL8192EE_AGC_TAB_ARRAY`. The macros define element counts, not byte sizes.

## Control Flow
There is no executable control flow. Consumers include this file, select the table matching the configuration phase, and iterate according to the matching length macro and table record shape.

## State And Persistence
The header has no state. It exposes immutable static data whose effects are written into device registers by other modules during initialization and reconfiguration.

## Dependencies And Integration Points
It depends only on `<linux/types.h>`, but semantically it depends on the table parser in RTL8192EE PHY code using the same element-count semantics. Any new table in `table.c` must be reflected here or it remains inaccessible to the rest of the driver.

## Risks
Length mismatches are the main risk. If a macro is too short, hardware programming silently omits part of a sequence; if too long, the parser may read beyond the intended table. Because power-group tables have a different stride from address/value tables, consumers must not assume a uniform pair layout for every declaration.

## Test Signals
Build coverage should catch missing symbols. Runtime validation should check that MAC/BB/RF/AGC setup uses the expected number of entries, and that init succeeds after changes to any table length or declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/trx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/trx.c

## Purpose
This file implements RTL8192EE PCIe transmit and receive descriptor handling. It maps mac80211 packets into 8192EE TX descriptors and buffer descriptors, translates RX descriptors and PHY status into `rtl_stats` and `ieee80211_rx_status`, manages DMA pointer accounting, and exposes descriptor helpers to the shared rtlwifi PCI layer.

## Important APIs, Types, And Functions
RX processing centers on `rtl92ee_rx_query_desc()`, `_rtl92ee_translate_rx_signal_stuff()`, and `_rtl92ee_query_rxphystatus()`. These parse RX descriptor fields, detect C2H/TX report packets, set mac80211 RX metadata, handle hardware decryption flags, calculate CCK/OFDM RSSI/PWDB/EVM, update CFO tails and beacon/non-BE counters, and report wake pattern/magic/unicast matches.

TX processing centers on `rtl92ee_tx_fill_desc()`, `rtl92ee_pre_fill_tx_bd_desc()`, `_rtl92ee_map_hwqueue_to_fwqueue()`, `_rtl92ee_insert_emcontent()`, and `rtl92ee_tx_fill_cmddesc()`. These fill packet descriptors, optional early-mode headers, DMA mappings, PCIe buffer descriptors, aggregation fields, RTS/CTS fields, bandwidth/subcarrier bits, security type, rate fallback controls, rate ids, MAC ids, BMC flags, and H2C command descriptors.

Descriptor ring integration uses `rtl92ee_set_desc()`, `rtl92ee_get_desc()`, `rtl92ee_is_tx_desc_closed()`, `rtl92ee_get_available_desc()`, `rtl92ee_rx_desc_buff_remained_cnt()`, `rtl92ee_rx_check_dma_ok()`, and `get_desc_addr_fr_q_idx()`.

## Control Flow
On TX, the generic PCI layer passes a prepared skb and descriptor slot into `rtl92ee_tx_fill_desc()`. The function derives a firmware queue selector from frame type, asks the rtlwifi core for a `rtl_tcb_desc`, optionally prepends early-mode bytes, DMA-maps the skb, fills buffer descriptors for PCIe DMA, then fills the packet descriptor with segmentation, aggregation, sequence, rate, security, queue, and station fields. Ownership and write-pointer advancement are later handled through `rtl92ee_set_desc(HW_DESC_OWN)`.

On RX, the PCI layer calls `rtl92ee_rx_query_desc()` for a completed descriptor. It extracts length, driver-info size, shift, CRC/ICV, decryption state, rate, AMPDU, timestamp, MAC id, packet report type, and channel metadata. If PHY status is present, it locates `rx_fwinfo`, derives signal information, then calls `rtl_process_phyinfo()`. It also fills TX report 2 valid MAC-id bitmaps when the RX packet is actually a firmware report.

## State And Persistence
The file updates ring state in `rtlpci->tx_ring[].cur_tx_wp`, `cur_tx_rp`, and `rtlpci->rx_ring[].next_rx_rp`; updates PHY/DM state such as `dm.cfo_tail`, `dm.packet_count`, beacon query counts, and non-BE packet counts; and relies on skb control block metadata from the core. DMA mappings are embedded in descriptors and later retrieved by `rtl92ee_get_desc()`. Register write/read pointers are the hardware source of truth for descriptor availability and closure.

## Dependencies And Integration Points
It depends on rtlwifi PCI ring structures, mac80211 TX/RX status types, `rtl_get_tcb_desc()`, `rtl_set_tx_report()`, `rtlwifi_rate_mapping()`, PHY/statistics helpers, Realtek register definitions, descriptor bitfield helpers in `trx.h`, and PCI DMA APIs. It integrates with firmware C2H reporting, WoWLAN wake matches, CAM hardware crypto state, aggregation/rate adaptation, and the generic rtlwifi interrupt/RX/TX loops.

## Risks
DMA and descriptor ownership ordering are high risk. Failed `dma_map_single()` returns without fully completing descriptor state, so callers must not hand the slot to hardware. `rtl92ee_pre_fill_tx_bd_desc()` assumes PCIe buffer descriptor layout and 64-bit DMA policy match module settings. RX pointer accounting uses hardware read/write registers and a static `start_rx` flag, so stale register reads can suppress or miscount completions. Robust management frames intentionally clear `RX_FLAG_DECRYPTED` despite hardware saying decrypted; regressions here affect 802.11w. Early-mode skb push changes data pointer and length, which must remain consistent with DMA and descriptor packet sizes.

## Test Signals
Relevant tests include sustained TX/RX under all access categories, management/control/data frames, AMPDU aggregation, 20/40 MHz operation, multicast/broadcast traffic, hardware crypto with WEP/TKIP/CCMP and robust management frames, WoWLAN wake-pattern reporting, firmware TX report handling, descriptor ring wraparound, DMA mapping failure injection, and suspend/unload while queues are active. Debug signals include correct register write pointers, no DMA API warnings, sane RSSI/EVM values, and no stuck TX descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/trx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/trx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/trx.h

## Purpose
This header defines the RTL8192EE TX/RX descriptor bitfield accessors, descriptor constants, PHY-status layouts, and exported TX/RX descriptor APIs. It is the low-level hardware descriptor contract used by `trx.c` and the rtlwifi PCI layer.

## Important APIs, Types, And Functions
The header defines descriptor sizes and offsets such as `TX_DESC_SIZE`, `RX_DESC_SIZE`, `RX_DRV_INFO_SIZE_UNIT`, `USB_HWDESC_HEADER_LEN`, and `MAX_RECEIVE_BUFFER_SIZE`. Inline setters/getters manipulate TX descriptor fields for packet size, offsets, BMC/HTC, first/last segment, ownership, MAC id, queue select, rate id, security type, aggregation, RTS/CTS, bandwidth, fallback limits, sequence, DMA address, and next-descriptor address.

Separate inline helpers operate on PCIe TX buffer descriptors and RX buffer descriptors, including 64-bit DMA high-address handling gated by `dma64`. RX status helpers parse packet length, CRC/ICV, driver-info size, shift, PHY status, software decryption, MAC id, aggregation, report type, MCS, WoWLAN match bits, TSF, buffer address, and TX report 2 bitmaps. `struct phy_status_rpt`, `struct rx_fwinfo`, `struct tx_desc`, and `struct rx_desc` document packed hardware layouts. Function prototypes expose the chip descriptor operations to `sw.c` HAL ops.

## Control Flow
There is no independent runtime control flow, but every TX/RX path in `trx.c` flows through these inline accessors. They perform little-endian bit replacement/extraction directly on memory shared with the device, so callers must provide correctly aligned descriptor buffers and apply ownership changes at the correct point in the ring lifecycle.

## State And Persistence
The header defines how state is stored in descriptor memory. Descriptor contents persist until the driver clears or rewrites the ring entry and until hardware consumes or produces it. Packed PHY-status structs describe transient RX metadata delivered alongside a received frame.

## Dependencies And Integration Points
It depends on Linux endian/bitfield helpers available through included rtlwifi headers and on rate constants such as `DESC_RATE1M` through `DESC_RATEMCS*`. It must match the RTL8192EE hardware manual, PCI ring allocation sizes, and `trx.c` parser/filler assumptions.

## Risks
Bitfield mistakes are severe because they directly change hardware DMA behavior. The `set_tx_desc_data_bw()` helper writes into dword 4 while its comment places it under dword 5, so maintainers must follow code and hardware spec, not comments alone. `set_tx_desc_next_desc_address()` writes `pdesc + 12` despite a dword 11 comment, reflecting the 64-byte layout and reserved fields; changing it casually would corrupt rings. Packed bitfield structs are documentation/legacy conveniences and are sensitive to endian assumptions; active code mostly uses safer le32 helpers.

## Test Signals
Build testing catches missing helpers; runtime coverage should verify descriptor ownership, DMA address recovery, ring wraparound, RX length/shift parsing, 64-bit DMA mode, WoWLAN match extraction, and TX/RX under all rates and aggregation modes. Sparse/endian checks and DMA API debug are useful companions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/trx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/Makefile

## Purpose
This Makefile declares how the RTL8192SE PCI driver object is built inside the Linux kernel rtlwifi tree. It aggregates the chip-specific source files into `rtl8192se.o` and enables that object when `CONFIG_RTL8192SE` is selected.

## Important APIs, Types, And Functions
There are no C APIs. The key build variables are `rtl8192se-objs`, listing `dm.o`, `fw.o`, `hw.o`, `led.o`, `phy.o`, `rf.o`, `sw.o`, `table.o`, and `trx.o`, and `obj-$(CONFIG_RTL8192SE) += rtl8192se.o`.

## Control Flow
Kbuild uses `rtl8192se-objs` to link the component objects into one module or built-in object. The resulting driver registration comes from `sw.o`; the rest of the objects provide symbols referenced by its HAL operations and sibling modules.

## State And Persistence
The file has no runtime state. Its persistent effect is the composition of the kernel object and which chip modules are linked into it.

## Dependencies And Integration Points
It depends on the parent Kconfig selecting `CONFIG_RTL8192SE` and on every listed object compiling with matching symbol names. Removing an object from this list can produce link errors or missing runtime behavior.

## Risks
Build composition drift is the main risk. For example, omitting `table.o` breaks PHY table symbols, omitting `trx.o` breaks descriptor callbacks, and omitting `fw.o` breaks firmware download and H2C commands. Adding a new source file requires adding it here or wiring it elsewhere in Kbuild.

## Test Signals
The relevant signal is successful kernel/module build with `CONFIG_RTL8192SE=m` and `=y`, followed by module load resolving all chip symbols. Clean rebuilds after touching any listed source should validate dependency tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/def.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/def.h

## Purpose
This header defines RTL8192SE queue constants, descriptor bitfield helpers, RX PHY-info structures, and firmware command identifiers used by the 8192SE TX/RX, firmware, dynamic-management, PHY, and hardware code. It is the older 8192SE descriptor and firmware-command vocabulary.

## Important APIs, Types, And Functions
Constants define RX queues, short/non-short slot timing, firmware queue-select values, and descriptor sizes (`TX_DESC_SIZE_RTL8192S`, `TX_CMDDESC_SIZE_RTL8192S`, `RX_STATUS_DESC_SIZE`). Inline helpers set TX descriptor packet size, offset, first/last segment, OWN, MAC id, queue, security type, aggregation, sequence, RTS/CTS, bandwidth, short GI, rate, buffer size/address, and next descriptor address. RX helpers parse packet length, CRC/ICV, driver-info size, shift, PHY status, decryption, OWN, aggregation, MCS/HT, short preamble, bandwidth, TSF, and buffer address.

`enum rf_optype`, `enum ic_inferiority`, and `enum fwcmd_iotype` describe RF access mode, silicon class, and firmware command categories. `struct rx_fwinfo` and `struct phy_sts_cck_8192s_t` describe PHY status payloads used by RX signal processing.

## Control Flow
The header itself has no control flow. Runtime flows in `trx.c`, `fw.c`, `phy.c`, and `dm.c` use these helpers to encode/decode descriptor memory and select firmware command behavior. `CLEAR_PCI_TX_DESC_CONTENT()` preserves the next-descriptor pointer area while clearing the rest of a chained PCI descriptor.

## State And Persistence
The header defines the format of descriptor-ring state shared by driver and hardware. Firmware command enum values persist in `rtlhal->fwcmd_iomap`, `rtlhal->fwcmd_ioparam`, WFM registers, and command packets as interpreted by firmware.

## Dependencies And Integration Points
It depends on Linux endian/bit helpers via surrounding driver includes and on Realtek register/rate constants. It is shared across 8192SE TX/RX, firmware command dispatch, dynamic management, and PHY scan/power flows, so enum changes affect multiple modules.

## Risks
Descriptor bitfield errors directly corrupt DMA behavior. The TX descriptor clear macro intentionally preserves bytes beyond `TX_DESC_NEXT_DESC_OFFSET` because descriptors are pre-chained; replacing it with a full memset would break ring traversal. Firmware command enum values are part of an implicit ABI with multiple firmware versions, so renumbering or reusing values is unsafe. The packed PHY structs contain bitfields and are endian-sensitive.

## Test Signals
Good signals include stable TX/RX ring operation, correct queue selection, RX status parsing, firmware command success across firmware versions, and no descriptor-owner stalls. Static analysis should include endian/sparse checks, while runtime should include DMA API debug and RF/power command coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/dm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/dm.c

## Purpose
This file implements RTL8192SE dynamic management. It periodically adjusts EDCA turbo settings, transmit-power tracking, rate-adaptive masks, baseband MRC, false-alarm/DIG initial gain, and dynamic TX power based on link state, traffic direction, RSSI/PWDB, RF type, firmware version, and counters.

## Important APIs, Types, And Functions
Public entry points are `rtl92s_dm_init()`, `rtl92s_dm_watchdog()`, and `rtl92s_dm_init_edca_turbo()`. Internal workers include `_rtl92s_dm_check_edca_turbo()`, `_rtl92s_dm_check_txpowertracking_thermalmeter()`, `_rtl92s_dm_txpowertracking_callback_thermalmeter()`, `_rtl92s_dm_refresh_rateadaptive_mask()`, `_rtl92s_dm_switch_baseband_mrc()`, `_rtl92s_dm_false_alarm_counter_statistics()`, `_rtl92s_dm_initial_gain_sta_beforeconnect()`, `_rtl92s_dm_ctrl_initgain_byrssi()`, and `_rtl92s_dm_dynamic_txpower()`.

Static EDCA tables provide vendor-specific uplink/downlink BE parameters for peers identified by `mac->vendor`. DIG and rate-adaptive state use shared `rtlpriv->dm`, `rtlpriv->dm_digtable`, `rtlpriv->ra`, and `rtlpriv->falsealm_cnt`.

## Control Flow
`rtl92s_dm_init()` sets driver-controlled DM, initializes dynamic TX power, EDCA turbo, RA mask state, thermal tracking, DIG thresholds, and enables firmware CCA checking. `rtl92s_dm_watchdog()` runs the periodic policy sequence: EDCA turbo, thermal tracking, initial gain, dynamic TX power, RA refresh, and MRC switch.

EDCA turbo compares unicast TX/RX byte deltas against previous watchdog counters, chooses uplink or downlink BE parameters, and resets to normal AC parameters when non-BE traffic is seen. Thermal tracking alternates between triggering RF thermal measurement and reading/reporting it to firmware. DIG reads false-alarm counters, decides connected/disconnected state, disables/enables firmware DIG as needed, and writes OFDM initial gains. Dynamic TX power lowers transmit power in near-field conditions by recalculating channel power when thresholds cross.

## State And Persistence
Persistent state includes static previous TX/RX counters in EDCA logic, `dm.current_turbo_edca`, `dm.is_cur_rdlstate`, `dm.txpowercount`, `dm.tm_trigger`, `dm.thermalvalue`, `dm.useramask`, `dm.dynamic_txhighpower_lvl`, `dm.last_dtp_lvl`, DIG thresholds and previous values, and MRC switch state. Register writes to EDCA, BB AGC, CCA, RF thermal meter, and WFM firmware command registers persist until changed by watchdog, scan backup/restore, power transitions, or reinitialization.

## Dependencies And Integration Points
This file depends on rtlwifi statistics, mac80211 link/opmode state, PHY RF helpers, firmware command helpers in `phy.c`, rate table updates in `hw.c`, EFUSE thermal calibration, and BB register definitions. It integrates with scan paths via firmware DM pause/resume commands and with RX processing because RSSI/PWDB and non-BE counters drive decisions.

## Risks
Static counters in EDCA turbo are shared across device instances, which can be risky if multiple 8192SE devices are present. Firmware-version branches choose different command mechanisms; unsupported or failed firmware commands leave DM state stale. DIG directly writes initial gain and toggles firmware control, so scan, link transition, or RF-off races can affect sensitivity. Dynamic TX power is disabled for 2T2R but active for other RF types; bad thresholds can reduce throughput or violate expected power behavior. `useramask` is computed then forcibly disabled in init, making RA mask code mostly dormant unless changed.

## Test Signals
Signals include watchdog running without register-command timeouts, EDCA changes only for BE-dominated traffic, stable throughput in uplink/downlink tests, thermal tracking WFM completion, correct RA refresh on RSSI transitions, MRC toggling for 1T2R RSSI differences, and no DIG oscillation during scan/connect/disconnect. RF-off and scan stress should verify watchdog does not write invalid registers while stopped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/dm.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/dm.h

## Purpose
This header declares the RTL8192SE dynamic-management states, thresholds, flags, and public DM entry points. It provides the vocabulary used by `dm.c`, `hw.c`, and related PHY/firmware paths.

## Important APIs, Types, And Functions
Enums classify DIG algorithms (`dm_dig_alg`), two-port DIG algorithms (`dm_dig_two_port_alg`), debug mode, DIG on/off state, and rate-adaptive RSSI state (`dm_ratr_sta`). Macros define driver-vs-firmware DM type, high-power levels, disable flags, near-field TX power thresholds, DIG high-power thresholds, and minimum netcore value. Public functions are `rtl92s_dm_watchdog()`, `rtl92s_dm_init()`, and `rtl92s_dm_init_edca_turbo()`.

## Control Flow
The header has no executable flow. `sw.c` wires `rtl92s_dm_watchdog()` into HAL ops, `hw.c` calls `rtl92s_dm_init()` after hardware init, and QoS changes call `rtl92s_dm_init_edca_turbo()`.

## State And Persistence
The declarations map to state in shared rtlwifi structures, especially `rtlpriv->dm`, `rtlpriv->dm_digtable`, and `rtlpriv->ra`. Threshold macros are compile-time policy constants.

## Dependencies And Integration Points
It depends on `struct ieee80211_hw` and shared rtlwifi DM structures from included driver headers. Changing enum values or thresholds affects watchdog behavior, firmware command selection, rate table updates, and power behavior.

## Risks
Threshold changes can alter RF sensitivity, transmit power, and rate adaptation. Enum values may be stored or compared across modules; changing their order can break logic that assumes exact numeric states. Duplicate-looking high-power level macros (`TX_HIGH_PWR_LEVEL_*` and `TX_HIGHPWR_LEVEL_*`) require care when maintaining code.

## Test Signals
Build coverage should catch missing declarations. Runtime tests should verify watchdog invocation, EDCA reset on QoS changes, DIG threshold behavior, and dynamic TX power transitions after any enum or macro change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/fw.c

## Purpose
This file implements RTL8192SE firmware download and host-to-controller command submission. It splits the firmware image into IMEM, EMEM, and DMEM/private-header phases, sends each phase through the TX command queue, polls firmware readiness bits, and constructs H2C command packets for power mode, join-BSS report, and WoWLAN-related command ids.

## Important APIs, Types, And Functions
The public functions are `rtl92s_download_fw()`, `rtl92s_set_fw_pwrmode_cmd()`, and `rtl92s_set_fw_joinbss_report_cmd()`. Internal helpers include `_rtl92s_fw_set_rqpn()` for queue-page setup, `_rtl92s_firmware_enable_cpu()`, `_rtl92s_firmware_get_nextstatus()`, `_rtl92s_firmware_header_map_rftype()`, `_rtl92s_firmwareheader_priveupdate()`, `_rtl92s_cmd_send_packet()`, `_rtl92s_firmware_downloadcode()`, `_rtl92s_firmware_checkready()`, `_rtl92s_fill_h2c_cmd()`, `_rtl92s_get_h2c_cmdlen()`, and `_rtl92s_firmware_set_h2c_cmd()`.

## Control Flow
Firmware download starts with `rtl92s_download_fw()`, which validates the firmware buffer, parses `struct fw_hdr`, records firmware version, copies IMEM and EMEM sections into staging arrays, then advances from `FW_STATUS_INIT` through LOAD_IMEM, LOAD_EMEM, LOAD_DMEM, and READY. Each stage sends bytes as command-queue skbs through `_rtl92s_firmware_downloadcode()` and verifies readiness in `_rtl92s_firmware_checkready()`. EMEM completion enables the firmware CPU; DMEM completion waits for `FWRDY`/`LOAD_FW_READY`, normalizes TCR/RCR loopback and append flags, and restores normal loopback mode.

H2C flow maps a high-level `FW_H2C_*` command to a firmware command element id and structure length, allocates an skb, writes an 8-byte aligned H2C header/payload, sends it via TXCMD queue, and polls the TX command queue. Power-mode and join-report builders fill command structures from mac80211 BSS configuration, DTIM/beacon intervals, association id, BSSID, and power-save policy.

## State And Persistence
Firmware state is stored in `struct rt_firmware` inside `rtlhal->pfirmware`: parsed header pointer, firmware status, version, IMEM/EMEM buffers and lengths, raw temporary buffer, and H2C sequence. Hardware state includes RQPN queue allocation, TCR readiness bits, RCR append flags, loopback mode, and command queue descriptors. H2C sequence state persists in `rtlhal->h2c_txcmd_seq`.

## Dependencies And Integration Points
It depends on the firmware blob already copied into `rtlhal->pfirmware` by `sw.c`, PCI TX command rings, `fill_tx_cmddesc` from `trx.c`, firmware/register constants in `reg.h` and `fw.h`, mac80211 BSS configuration, rtlwifi power-save state, and queue polling from the HAL ops table. `hw.c` calls `rtl92s_download_fw()` during init before PHY/RF configuration.

## Risks
The staged download is ordering-sensitive: CPU enable occurs only after EMEM validation, and DMEM uses a modified header-private region with RF type patched in. Size checks guard IMEM/EMEM buffers, but a malformed header can still create unusable firmware state. `_rtl92s_cmd_send_packet()` ignores the `last` argument and does not check descriptor availability, relying on surrounding init timing. H2C builder pointer arithmetic is compact and alignment-sensitive. Power-mode builders assume `mac->vif` and BSS fields are valid.

## Test Signals
Signals include successful IMEM/EMEM/DMEM polling, `FWRDY` set, no TXCMD ring stalls, valid firmware version logged, successful RA/DM commands after init, working LPS power-mode command, and correct join report after association. Negative tests should include missing firmware, oversized/malformed firmware, command queue saturation, and suspend/resume firmware reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/fw.h

## Purpose
This header defines RTL8192SE firmware image limits, firmware/private-header structures, firmware status states, H2C command payload structures, command ids, and firmware command register macros. It is the shared contract for `fw.c`, `phy.c`, `dm.c`, and hardware initialization.

## Important APIs, Types, And Functions
Important constants include firmware size limits, firmware header sizes, TX command header length, max transmit buffer size, and firmware DM control bits for register `0x364`/LBUS state. `struct fw_priv` describes the private DMEM header fields patched before DMEM download. `struct fw_hdr` describes the firmware file header. `struct rt_firmware` stores parsed firmware status and buffers.

H2C structures include `h2c_set_pwrmode_parm`, `h2c_joinbss_rpt_parm`, `h2c_wpa_ptk`, and `h2c_wpa_two_way_parm`. `enum h2c_cmd` selects higher-level command classes, while `enum fw_h2c_cmd` maps to firmware element ids. Macros such as `FW_CMD_IO_SET`, `FW_CMD_IO_CLR`, `FW_CMD_PARA_SET`, and query macros update firmware command map/parameter registers and cached `rtlhal` state. Public prototypes expose firmware download and H2C helpers.

## Control Flow
The header has no executable control flow, but it defines the state transitions and command ids used by firmware download and firmware-command paths. Firmware progresses through INIT, LOAD_IMEM, LOAD_EMEM, LOAD_DMEM, and READY. DM commands are encoded either as H2C packets or as firmware command-map/register updates using the macros.

## State And Persistence
`struct rt_firmware` persists in `rtlhal->pfirmware` while the driver is loaded. The command-map macros persist both in hardware registers (`LBUS_MON_ADDR`, `LBUS_ADDR_MASK`) and in cached `rtlhal->fwcmd_iomap`/`fwcmd_ioparam`. H2C sequence counters persist in `rtlhal`.

## Dependencies And Integration Points
It depends on chip register names from `reg.h` for macro writes and on firmware ABI compatibility. The RF type in `fw_priv` is patched from PHY state, so firmware header layout must match the blob. Power-save, WoWLAN, and join-report flows depend on these structure layouts matching firmware expectations exactly.

## Risks
Structure packing/alignment is critical; comments note 8-byte alignment requirements but not every struct is explicitly packed. Command IDs and DM control bits are firmware ABI values and must not be renumbered. The macros perform hardware writes and cached state updates with delays, so using them in the wrong context can block or race with other firmware command submissions. Some comments contain encoding oddities, but the field semantics are clear from usage.

## Test Signals
Compile-time structure-size checks would be valuable. Runtime signals include successful firmware version parsing, H2C power/join commands accepted, WFM/firmware command bits clearing, WoWLAN command paths building expected sizes, and firmware compatibility across known 8192SE firmware versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/hw.c

## Purpose
This file implements RTL8192SE hardware control: register get/set callbacks, security CAM programming, firmware-era MAC initialization, full hardware bring-up and shutdown, interrupt control, beacon configuration, EFUSE/EEPROM parsing, rate table programming, RF kill handling, key installation, and suspend/resume PCI quirks.

## Important APIs, Types, And Functions
Public HAL callbacks include `rtl92se_get_hw_reg()`, `rtl92se_set_hw_reg()`, `rtl92se_enable_hw_security_config()`, `rtl8192se_gpiobit3_cfg_inputmode()`, `rtl92se_hw_init()`, `rtl92se_card_disable()`, `rtl92se_interrupt_recognized()`, `rtl92se_set_beacon_related_registers()`, `rtl92se_set_beacon_interval()`, `rtl92se_update_interrupt_mask()`, `rtl92se_read_eeprom_info()`, `rtl92se_update_hal_rate_tbl()`, `rtl92se_update_channel_access_setting()`, `rtl92se_gpio_radio_on_off_checking()`, `rtl92se_set_key()`, `rtl92se_suspend()`, and `rtl92se_resume()`.

Important internal helpers include `_rtl92se_macconfig_before_fwdownload()`, `_rtl92se_macconfig_after_fwdownload()`, `_rtl92se_hw_configure()`, `_rtl92se_set_media_status()`, `_rtl92s_phy_set_rfhalt()`, `_rtl92se_power_domain_init()`, `_rtl92se_read_adapter_info()`, `rtl92se_update_hal_rate_table()`, and `rtl92se_update_hal_rate_mask()`.

## Control Flow
`rtl92se_hw_init()` is the main bring-up sequence. It marks initialization active, temporarily enables local IRQs because init may take hundreds of milliseconds, disables ASPM, performs pre-firmware MAC/power/descriptor-address setup, detects chip cut, configures GPIO3, downloads firmware, applies post-firmware MAC defaults, captures firmware command map state, programs MAC/BB/RF tables, reads RF channel values, enables CCK/OFDM, configures retry/min-spacing/aggregation, stores original PHY register values, applies channel transmit power, writes MAC address, initializes firmware RA behavior, applies EPHY/ASPM workaround, clears/enables security CAM state, sets EDCA defaults, turns on MRC for 1T2R, lights LED, and initializes dynamic management.

Shutdown and RF-off paths call `rtl92se_card_disable()` and `_rtl92s_phy_set_rfhalt()`, which stop link state, set media status to no link, pause TX/CCA, power down BB/RF/MAC blocks, switch clock/control path, configure low-power LED/GPIO state, and mark halt power-save level. RF kill checking may temporarily power up the domain to read GPIO3, then re-halt it if nothing changed.

## State And Persistence
This file owns substantial driver-visible state: `rtlpci->receive_config`, interrupt masks and enabled flag, `rtlpci->being_init_adapter`, `rtlhal->version`, firmware command map/parameter cache, `rtlphy->rf_mode`, `rfreg_chnlval`, RF type, min-space config, EFUSE-derived MAC address, channel power tables, regulatory fields, thermal/crystal values, `ppsc` RF power/hardware radio flags, CAM key buffers/lengths, and rate-adaptive indices in station private state. Hardware register state is persistent until reset/power-down and is replayed during init/resume.

## Dependencies And Integration Points
It depends on rtlwifi PCI transport, EFUSE helpers, regulatory helpers, CAM helpers, power-save helpers, firmware download from `fw.c`, PHY configuration from `phy.c`/`rf.c`, dynamic management from `dm.c`, LED control, mac80211 station/vif state, and shared register definitions. `sw.c` wires these functions into the HAL ops table used by the generic rtlwifi core.

## Risks
Hardware bring-up is highly order-sensitive. Descriptor base addresses must be programmed before firmware download; firmware must be ready before MAC/PHY/RF tables and RA commands; RCR is rewritten after MAC config to avoid throughput and Cisco AP association issues. `rtl92se_hw_init()` enables local IRQs inside a caller context that may have disabled them, so reentrancy assumptions must remain valid before device interrupts are enabled. Power-domain and RF kill flows use sleeps/delays and shared `rf_ps_lock` state; races can leave the NIC powered up or halted incorrectly. EFUSE parsing trusts many offsets and has unusual index selection for OFDM diff (`0x11` for channel 4-8), so table bounds deserve scrutiny. CAM key setup branches differently for AP, station, adhoc, WEP/default keys, and group keys.

## Test Signals
Test cold boot, warm reboot, suspend/resume, IPS/LPS, RF kill toggle, module unload, firmware-missing failure, and repeated hardware init/disable cycles. Runtime signals include firmware ready, MAC/BB/RF config success, interrupts masked/unmasked correctly, correct MAC address from EFUSE, valid channel power programming, association in station/AP/adhoc modes, hardware crypto for pairwise/group/WEP keys, rate table updates for B/G/N and RSSI changes, and no stuck `pwrdomain_protect` or `rfchange_inprogress`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/hw.h

## Purpose
This header declares RTL8192SE hardware-control entry points and media-status constants used by `sw.c`, the rtlwifi core, and sibling chip modules. It is the public interface for `hw.c`.

## Important APIs, Types, And Functions
The header defines media status encodings (`MSR_LINK_*`) and `enum WIRELESS_NETWORK_TYPE`. It declares hardware register access callbacks, EEPROM reading, interrupt recognition, init/disable/suspend/resume, network type and BSSID filtering, MAC address setting, QoS/beacon/interrupt-mask updates, rate table updates, channel access setting, RF kill checking, GPIO3 input mode, hardware security enabling, and CAM key programming.

## Control Flow
There is no direct control flow. `sw.c` places most declarations into `rtl8192se_hal_ops`, while `phy.c` calls GPIO/beacon helpers and other modules use security or rate callbacks through the ops table.

## State And Persistence
The functions declared here mutate hardware registers and shared rtlwifi state, but the header itself stores no state. The enum and macro values are compile-time constants matching MSR register encoding.

## Dependencies And Integration Points
It depends on `struct ieee80211_hw`, `struct ieee80211_sta`, `enum nl80211_iftype`, and rtlwifi structures from included parent headers. Its declarations must stay synchronized with `hw.c` definitions and `sw.c` HAL ops.

## Risks
Signature drift breaks HAL wiring. `rtl92se_set_mac_addr()` is declared as a real callback but implemented as a stub, so callers must not assume it writes hardware after init. Network type constants must match hardware MSR bit encoding.

## Test Signals
Build/link tests validate declaration consistency. Runtime tests should exercise each HAL callback through the generic rtlwifi core, especially init/disable, network type changes, beacon setup, rate updates, RF kill, and key programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/led.c

## Purpose
This file implements simple software LED control for RTL8192SE. It maps rtlwifi LED actions to LEDCFG register writes for LED0/LED1/GPIO0 pins while respecting RF-off power-save state.

## Important APIs, Types, And Functions
`rtl92se_sw_led_on()` clears LEDCFG nibbles for LED0 or LED1 to turn LEDs on. `rtl92se_sw_led_off()` sets LEDCFG bits for LED0/LED1 off state, with LED0 handling open-drain mode. `_rtl92se_sw_led_control()` maps `LED_CTL_POWER_ON`, `LED_CTL_LINK`, and `LED_CTL_NO_LINK` to on, and `LED_CTL_POWER_OFF` to off. `rtl92se_led_control()` is the HAL-facing entry point and filters actions when RF is off for reasons stronger than power save.

## Control Flow
The rtlwifi core or hardware code calls `rtl92se_led_control()` with an action. The function checks RF-off reason, logs, and dispatches to `_rtl92se_sw_led_control()`, which operates only on `ledctl.sw_led0`. The low-level functions read LEDCFG, mask/preserve unrelated bits, and write the new LED state.

## State And Persistence
The persistent state is the LEDCFG hardware register and `rtlpriv->ledctl` configuration, including `sw_led0` and `led_opendrain`. The off helper returns early if `rtlpriv` is null or `max_fw_size` is set, which effectively suppresses some off writes during firmware-buffer-valid states.

## Dependencies And Integration Points
It depends on rtlwifi LED action enums, PCI/register access helpers, RF power-save state, and LEDCFG register definitions. `hw.c` calls LED helpers during init, RF halt, RF kill, and card disable; `sw.c` wires `rtl92se_led_control()` into HAL ops.

## Risks
LED register bits are shared between pins and modes, so masks must preserve unrelated pin configuration. The `rtl92se_sw_led_off()` early return on `rtlpriv->max_fw_size` is surprising because `max_fw_size` is normally nonzero after firmware setup; this can prevent off transitions and should be preserved only if intentional. RF-off filtering means some user-visible LED actions are deliberately ignored in deeper radio-off states.

## Test Signals
Test LED behavior on module load, link/no-link, RF kill, IPS/LPS, card disable, and unload. Validate LED0 open-drain boards and LED1 boards if available, and confirm LEDCFG writes do not disturb GPIO configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/led.h

## Purpose
This header declares the RTL8192SE LED control API implemented by `led.c`.

## Important APIs, Types, And Functions
It exposes `rtl92se_sw_led_on()`, `rtl92se_sw_led_off()`, and `rtl92se_led_control()`. The functions operate on `struct ieee80211_hw`, `enum rtl_led_pin`, and `enum led_ctl_mode`.

## Control Flow
There is no executable control flow. Hardware and rtlwifi core paths include this header and call the declarations during power/link state changes.

## State And Persistence
The header has no state; the functions it declares mutate LEDCFG register state and `rtlpriv->ledctl`-selected pins.

## Dependencies And Integration Points
It depends on rtlwifi LED enums from parent includes. `sw.c` wires `rtl92se_led_control()` as the HAL `led_control` callback and `hw.c` directly calls the low-level LED functions for power/RF transitions.

## Risks
Declaration drift would break linking or HAL wiring. Since low-level LED functions are public within the module, callers can bypass RF-off filtering in `rtl92se_led_control()`, so direct calls should be limited to hardware power paths that intentionally need this.

## Test Signals
Build tests validate prototypes. Runtime tests should cover direct and HAL-mediated LED transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/led.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/phy.c

## Purpose
This file implements RTL8192SE PHY, baseband, RF, channel, bandwidth, RF-power, transmit-power, firmware-command, EPHY/ASPM, and beacon-timing control. It bridges table-driven BB/RF initialization, EFUSE-derived power data, dynamic-management firmware commands, and low-level RF serial register access.

## Important APIs, Types, And Functions
Public register APIs are `rtl92s_phy_query_bb_reg()`, `rtl92s_phy_set_bb_reg()`, `rtl92s_phy_query_rf_reg()`, and `rtl92s_phy_set_rf_reg()`. Configuration entry points are `rtl92s_phy_mac_config()`, `rtl92s_phy_bb_config()`, `rtl92s_phy_rf_config()`, `rtl92s_phy_config_rf()`, and `rtl92s_phy_get_hw_reg_originalvalue()`. Runtime control APIs include `rtl92s_phy_scan_operation_backup()`, `rtl92s_phy_set_bw_mode()`, `rtl92s_phy_sw_chnl()`, `rtl92s_phy_set_rf_power_state()`, `rtl92s_phy_set_txpower()`, `rtl92s_phy_set_fw_cmd()`, `rtl92s_phy_chk_fwcmd_iodone()`, `rtl92s_phy_switch_ephy_parameter()`, and `rtl92s_phy_set_beacon_hwreg()`.

Internal helpers implement RF 3-wire serial read/write, table command arrays for channel switching, RF sleep, PA bias current correction, power-group offset storage, register-definition initialization, BB/AGC/table programming, RF-path-specific tables, transmit-power index selection, and firmware command post-processing.

## Control Flow
During init, `rtl92s_phy_bb_config()` initializes register-definition mappings, programs PHY and AGC tables, applies RF-type-specific BB overrides, applies PG power tables when EFUSE autoload succeeded, reads path enable maps, and validates RF path count against RF type. `rtl92s_phy_rf_config()` sets total RF paths and delegates RF6052 configuration, while `rtl92s_phy_config_rf()` writes path A/B RF tables and adjusts PA bias for inferior ICs.

At runtime, bandwidth changes guard against concurrent channel/bandwidth work and stopped HAL state, update MAC/BB 20/40 MHz bits, set sideband fields, and call RF6052 bandwidth setup. Channel switching builds pre/RF/post command arrays, first reapplies transmit power, then writes RF channel bits for every active RF path. RF power state transitions bring the NIC out of halted IPS through `rtl_ps_enable_nic()`, wake from sleep by enabling TX/CCA, enter sleep after waiting for non-beacon TX queues to drain, or halt through PCI power-save helpers.

Firmware commands use `rtl92s_phy_set_fw_cmd()` to choose between newer command-map bits and older WFM5 post-processing depending on firmware version. `_rtl92s_phy_set_fwcmd_io()` handles legacy RA, IQK, scan pause/resume, high-power, LPS, A2 entry, and driver-controlled DM commands with completion polling.

## State And Persistence
State lives in `rtlphy` fields such as `phyreg_def[]`, `rf_pathmap`, `num_total_rfpath`, `rfreg_chnlval[]`, `current_channel`, `current_chan_bw`, channel/bandwidth in-progress flags, default initial gain, frame sync, MCS power offsets, current CCK/OFDM power indices, and CCK high-power flag. Power-save state lives in `ppsc`, including RF power state, halt level, sleep/awake jiffies, and RF-off reason. Firmware command state lives in `rtlhal->set_fwcmd_inprogress`, `current_fwcmd_io`, and command map/parameter registers.

## Dependencies And Integration Points
This file depends on Realtek register definitions, table arrays from `table.c`, RF6052 helpers in `rf.c`, firmware command macros from `fw.h`, dynamic-management state from `dm.h`, PCI queue state for RF sleep, power-save helpers in `../ps.h`, and hardware GPIO helpers from `hw.c`. It is called from `hw.c` during init and from rtlwifi HAL ops during scan, channel, bandwidth, RF power, and BB/RF register operations.

## Risks
RF serial access is protected by `rf_lock`, but BB writes are not similarly serialized; callers must avoid conflicting channel/bandwidth/DM operations. Channel switching validates channels 1-14 only with `WARN_ONCE` but still writes the provided channel bits, so invalid channel state can reach hardware. RF sleep waits on TX queues with a bounded loop and may sleep while frames remain. Firmware command paths have multiple version-dependent encodings; wrong firmware version assumptions can leave command bits uncleared or skip needed post-processing. Table programming uses raw vendor arrays and delays; ordering changes can break RF calibration. EPHY switching writes magic values for ASPM/backdoor clock-request behavior and is platform-sensitive.

## Test Signals
Test BB/RF read/write helpers, cold init table programming, RF type/path-map validation, channel 1-14 switching, 20/40 MHz changes with sideband selection, scan pause/restore, IPS/LPS enter/leave, RF kill, TX queue drain before sleep, firmware command completion, transmit-power updates across channels, and ASPM/EPHY behavior across suspend/resume. Hardware validation should include 1T1R, 1T2R, and 2T2R boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/phy.h

## Purpose
This header declares RTL8192SE PHY constants, channel-switch command structures, baseband configuration categories, firmware-version helper, and public PHY/RF control functions.

## Important APIs, Types, And Functions
Constants define maximum TX power index, RF sleep queue wait count, channel-switch command table sizes, and RF path limits. `enum version_8192s` identifies chip cuts. `enum swchnlcmd_id` and `struct swchnlcmd` define table-driven channel-switch commands. `enum baseband_config_type` selects PHY register or AGC table configuration. `hal_get_firmwareversion()` reads the firmware version from `rtlhal->pfirmware`. Prototypes expose BB/RF register access, scan backup/restore, bandwidth and channel switching, RF power state, MAC/BB/RF config, EPHY parameter switching, original register capture, TX power programming, firmware command handling, beacon hardware timing, and RF path configuration.

## Control Flow
The header has no executable flow. `hw.c` and `sw.c` call these APIs during HAL init and runtime operations. `phy.c` implements the staged flows and uses `struct swchnlcmd` for its channel-switch state machine.

## State And Persistence
The header stores no state. It defines the shape of channel-switch command records and exposes functions that mutate `rtlphy`, `rtlhal`, `ppsc`, hardware registers, and firmware command state.

## Dependencies And Integration Points
It depends on `enum radio_path`, `enum rf_pwrstate`, `enum nl80211_channel_type`, `enum fwcmd_iotype`, and `struct ieee80211_hw` from rtlwifi/mac80211 headers. `hal_get_firmwareversion()` assumes `rtlhal->pfirmware` points to `struct rt_firmware`, making it tightly coupled to `fw.h`.

## Risks
`hal_get_firmwareversion()` has no null check, so callers must only use it after firmware buffer allocation/parse. Channel-switch table sizes must be large enough for any future multi-step commands. Firmware/chip version enums must remain aligned with hardware detection in `hw.c`.

## Test Signals
Build/link coverage validates prototypes. Runtime tests should hit every HAL-wired function: BB/RF access, bandwidth/channel changes, RF power transitions, firmware command dispatch, and beacon interval updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/phy.h -->
