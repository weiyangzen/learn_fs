# Research: subset-b-004883

This grouped report covers the Realtek rtlwifi RTL8188EE PCI driver files and RTL8192C common support files listed in work item `subset-b-004883`. Each section is source-tree aligned and wrapped for reconciliation into the final per-file research artifacts.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/reg.h

## Purpose

`reg.h` is the RTL8188E/RTL92C-style hardware register and bit-field map used by the RTL8188EE driver. It contains no executable code, but it is the driver-wide ABI to MAC, PCIe, USB-named legacy registers, eFuse/EEPROM, CAM security, DMA queues, interrupts, baseband, OFDM/CCK PHY, RF, wake-on-WLAN, and descriptor-related constants. The surrounding driver uses these definitions through low-level helpers such as `rtl_read_*`, `rtl_write_*`, `rtl_get_bbreg`, `rtl_set_bbreg`, `rtl_get_rfreg`, and `rtl_set_rfreg`.

## Important APIs, Types, and Constants

The file exports register offsets such as `REG_SYS_FUNC_EN`, `REG_MCUFWDL`, `REG_HIMR`, `REG_RQPN`, `REG_PCIE_CTRL_REG`, `REG_EDCA_BE_PARAM`, `REG_RCR`, `REG_CAMCMD`, and `REG_TSFTR`. It also defines bit masks for power and clock gates (`FEN_*`, `APFM_*`, `SYS_CLK_EN`), interrupt bits (`IMR_*`, `HSIMR_*`, `HSISR_*`), receive filtering (`RCR_*`, `AAP`, `APM`, `AB`, `AM`), rate bitmaps (`RATR_*`, `RATE_*`), EEPROM/eFuse layout (`EEPROM_*`, `EFUSE_*`), security CAM encodings (`CAM_*`, `SCR_*`), and PHY/RF masks (`MASKDWORD`, `RFREG_OFFSET_MASK`, `BRFSI_RFENV`, `B3WIREDATALENGTH`, etc.). These constants are referenced heavily by `sw.c`, `rf.c`, `trx.c`, PHY code, DM code, and firmware code.

## Control Flow and State

There is no control flow, but the definitions encode hardware state transitions. For example, firmware download uses `MCUFWDL_EN`, `FWDL_CHKSUM_RPT`, `MCUFWDL_RDY`, and `WINTINI_RDY`; TX/RX activation uses `HCI_TXDMA_EN`, `RXDMA_EN`, `MACTXEN`, and `MACRXEN`; interrupt configuration uses `IMR_*`; RF path setup uses `BRFSI_RFENV` and 3-wire interface masks. Persistent hardware configuration is represented through EEPROM offsets, default power values, channel plans, VID/DID/SVID/SMID offsets, and eFuse size/protection constants.

## Dependencies and Integration Points

This header assumes common kernel bit helpers such as `BIT()` and is included by RTL8188EE implementation files. It is also aligned with shared rtlwifi abstractions that use indexed `rtl_hal_cfg.maps[]` entries, so chip-specific register names are mapped into common core names in `sw.c`. It includes duplicated legacy USB offsets even though RTL8188EE is PCIe, which reflects shared Realtek code heritage.

## Risks and Test Signals

The risks are bit-exactness and register drift: incorrect offsets or masks can silently break power sequencing, interrupts, DMA, security CAM programming, or RF calibration. Duplicated definitions such as `REG_USB_INFO` and repeated default constants should be treated cautiously during refactors. Useful test signals include successful probe, firmware readiness, working interrupts, TX/RX traffic, suspend/resume, hardware encryption, eFuse parsing, channel switching, RF calibration, and WoWLAN wake-reason handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/rf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/rf.c

## Purpose

`rf.c` implements RTL8188EE RF6052 radio configuration and transmit-power programming. It translates channel bandwidth, per-path power tables, EEPROM regulatory modes, thermal tracking adjustments, and dynamic high-power limits into RF and baseband register writes.

## Important APIs and Functions

`rtl88e_phy_rf6052_set_bandwidth()` updates `rtlphy->rfreg_chnlval[0]` and writes `RF_CHNLBW` on path A for 20 MHz or 20/40 MHz operation. `rtl88e_phy_rf6052_set_cck_txpower()` builds CCK power words for RF paths A and B, handles scan-time power behavior, applies EEPROM regulatory offsets, clamps bytes to `RF6052_MAX_TX_PWR`, applies `rtl88e_dm_txpower_track_adjust()`, and writes CCK TX AGC registers. `rtl88e_phy_rf6052_set_ofdm_txpower()` builds OFDM/MCS power bases, calls `_rtl88e_get_txpower_writeval_by_regulatory()` for six rate groups, applies thermal tracking, and writes AGC registers through `_rtl88e_write_ofdm_power_reg()`. `rtl88e_phy_rf6052_config()` determines `num_total_rfpath` and delegates to `_rtl88e_phy_rf6052_config_parafile()`.

## Control Flow and State

RF configuration iterates over active RF paths, enables the RF environment through baseband interface registers, configures 3-wire address/data length, calls `rtl88e_phy_config_rf_with_headerfile()`, and restores previous RF environment bits. TX power paths consume mutable state from `rtlpriv->phy`, `rtlpriv->dm`, `rtlpriv->mac80211`, and `rtl_efuse`: channel bandwidth, channel number, original MCS offsets, power group counts, regulatory mode, scanning state, dynamic high power, and thermal tracking direction/value.

## Dependencies and Integration Points

The file depends on `reg.h` register/mask definitions, `phy.h` RF/BB accessors and RF table loader, `dm.h` thermal tracking adjustment, and rtlwifi private structs. It is called from channel/bandwidth switching, PHY initialization, and TX power update paths exposed through the HAL ops in `sw.c`.

## Risks and Test Signals

Power programming is regulatory-sensitive. Edge risks include off-by-one channel indexing into eFuse arrays, underflow when dynamic high-power subtraction is applied to packed byte fields, path B writes on nominal 1T devices, and mismatched regulatory mode interpretation. Test signals include valid channel switching, no RF path configuration failures, sane per-rate TX power on channels 1-14, thermal tracking behavior across temperature changes, scan stability, and compliance-oriented power table validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/rf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/rf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/rf.h

## Purpose

`rf.h` is the public RTL8188EE RF6052 interface for the chip-specific driver. It exposes the RF power ceiling and the functions that initialize RF paths, set bandwidth, and program CCK/OFDM transmit power.

## Important APIs

`RF6052_MAX_TX_PWR` caps per-byte transmit power values at `0x3f`. The prototypes are `rtl88e_phy_rf6052_set_bandwidth()`, `rtl88e_phy_rf6052_set_cck_txpower()`, `rtl88e_phy_rf6052_set_ofdm_txpower()`, and `rtl88e_phy_rf6052_config()`. These routines are implemented in `rf.c` and called by PHY/channel logic elsewhere in the RTL8188EE driver.

## Control Flow and State

The header itself has no control flow or persistent state. Its interface implies that callers must provide the active `ieee80211_hw`, current channel/bandwidth context in `rtl_priv`, and power arrays indexed by RF path.

## Dependencies and Integration Points

It depends on kernel/rtlwifi type visibility for `struct ieee80211_hw` and `u8`. It is included by `rf.c` and chip-specific PHY files. The functions bridge mac80211-driven channel state to low-level RF/baseband register writes.

## Risks and Test Signals

The main risk is API misuse: passing arrays that are not sized for path A/B or invoking power setup before eFuse/PHY state is initialized. Test signals are compile coverage, successful RF init, and working channel/power changes under normal association and scanning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/rf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/sw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/sw.c

## Purpose

`sw.c` is the RTL8188EE PCI driver glue. It initializes software state, requests firmware, defines module parameters, maps chip-specific register constants into rtlwifi common map slots, registers the HAL operation table, and binds PCI device ID `0x8179` to `rtl_pci_probe()`.

## Important APIs and Functions

`rtl88e_init_aspm_vars()` configures PCIe ASPM policy defaults and module-controlled ASPM support. `rtl88e_init_sw_vars()` initializes DM flags, RX/TX configuration masks, interrupt masks, power-save knobs, firmware buffer allocation, asynchronous firmware request for `rtlwifi/rtl8188efw.bin`, early-mode defaults, skb wait queues, and timers. `rtl88e_deinit_sw_vars()` frees firmware memory and deletes timers. `rtl8188ee_hal_ops` binds all major chip callbacks: EEPROM read, interrupt handling, hardware init/disable/suspend/resume, network type, BSSID filtering, QoS/beacon setup, rate table update, TX/RX descriptor operations, channel/bandwidth control, watchdog DM, RF power state, LED, security, BB/RF access, and BT coexist status. `rtl88ee_hal_cfg` supplies register maps and rate maps for common code. The bottom of the file declares module metadata, module parameters, PM ops, `pci_driver`, and `module_pci_driver()`.

## Control Flow and State

Probe enters the common PCI layer, which consumes `rtl88ee_hal_cfg` from the device ID table. Software init prepares `rtl_priv`, `rtl_pci`, `rtl_hal`, power-save, and dynamic-management state before firmware loading completes through `rtl_fw_cb`. Runtime state persists in `rtlpriv->dm`, `rtlpriv->psc`, `rtlpci`, `rtlhal`, timer structures, and module parameter storage.

## Dependencies and Integration Points

This file integrates `core`, `pci`, `hw`, `phy`, `dm`, `trx`, `led`, and `table` components into the rtlwifi common framework and mac80211. It depends on Linux firmware loading, PCI driver registration, module parameters, timers, and PM helpers.

## Risks and Test Signals

Risks include firmware request failure cleanup, inconsistent module parameter defaults versus descriptions, interrupt mask omissions, timer lifetime during probe failure/remove, and map entries that do not match `reg.h`. Test signals include module load/unload, firmware request callback success/failure, PCI probe/remove, suspend/resume, MSI/aspm toggles, interrupts, association, TX/RX, hardware security, and timer cleanup without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/table.c

## Purpose

`table.c` contains static RTL8188EE hardware initialization tables. It is data-only: PHY register/value pairs, PHY power-group triples, RF path A register/value pairs, MAC byte register/value pairs, and AGC table entries consumed by PHY initialization routines.

## Important Data

`RTL8188EEPHY_REG_1TARRAY` programs the 1T baseband/PHY register set, including FPGA, CCK, OFDM, IQK, AGC, and TX gain defaults. `RTL8188EEPHY_REG_ARRAY_PG` stores power group programming as address/mask/value triples for TX power offsets. `RTL8188EE_RADIOA_1TARRAY` stores RF path A radio values and includes delay sentinel entries such as `0xFFE`. `RTL8188EEMAC_1T_ARRAY` stores MAC/EDCA/SIFS/filter/register defaults as byte-oriented address/value pairs. `RTL8188EEAGCTAB_1TARRAY` writes AGC gain table entries through repeated `0xC78` writes.

## Control Flow and State

The file has no code-level control flow. Runtime control is in PHY code that iterates these arrays according to the lengths declared in `table.h`, interprets pairs or triples, handles delay markers, and writes values into hardware. Once applied, the data becomes hardware state in MAC, BB, AGC, and RF blocks.

## Dependencies and Integration Points

`table.c` includes `table.h`, which exports arrays and lengths. PHY initialization functions such as config-with-headerfile routines load these arrays during hardware init and RF setup. Register addresses correspond to definitions in `reg.h`.

## Risks and Test Signals

The table format is positional and length-sensitive. Incorrect declared lengths, pair/triple interpretation errors, or accidental value edits can break radio bring-up, calibration, sensitivity, or regulatory power behavior. Test signals include successful PHY/MAC/RF init, stable association, expected RSSI/sensitivity, TX power across channels, AGC behavior, and comparison against vendor/reference initialization tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/table.h

## Purpose

`table.h` declares the RTL8188EE initialization arrays defined in `table.c` and publishes their element counts to PHY initialization code.

## Important APIs and Data

The header defines `RTL8188EEPHY_REG_1TARRAYLEN`, `RTL8188EEPHY_REG_ARRAY_PGLEN`, `RTL8188EE_RADIOA_1TARRAYLEN`, `RTL8188EEMAC_1T_ARRAYLEN`, and `RTL8188EEAGCTAB_1TARRAYLEN`, plus extern declarations for the corresponding `u32` arrays. The lengths are raw element counts, not row counts, so pair tables and triple tables require different iteration strides.

## Control Flow and State

There is no control flow or persistent state. The declared lengths control runtime table walking in PHY configuration paths and therefore directly determine how much initialization data is written to hardware.

## Dependencies and Integration Points

It includes `<linux/types.h>` for `u32` and is included by `table.c`, `sw.c`, and PHY configuration code. It is tightly coupled to the array layout in `table.c`.

## Risks and Test Signals

The main risk is length drift: if an array changes without its length constant changing, initialization can truncate data or read beyond array boundaries. Test signals include build coverage, table-size sanity checks, and successful hardware init with no malformed register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/trx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/trx.c

## Purpose

`trx.c` implements RTL8188EE transmit and receive descriptor handling. It maps mac80211 frames to firmware queues, fills PCI TX descriptors, decodes RX descriptors into `rtl_stats` and `ieee80211_rx_status`, translates PHY status to RSSI/EVM/signal quality, maintains antenna-diversity statistics, and exposes generic descriptor get/set callbacks for rtlwifi PCI rings.

## Important APIs and Functions

`rtl88ee_rx_query_desc()` parses RX descriptor fields with `trx.h` helpers, handles normal RX versus TX report packets, sets CRC/decryption/rate/bandwidth/mactime status for mac80211, and invokes `_rtl88ee_translate_rx_signal_stuff()` when PHY status is present. `_rtl88ee_query_rxphystatus()` handles separate CCK and OFDM/HT signal calculations, including CCK AGC report conversion, OFDM RSSI/SNR/EVM, signal strength scaling, and antenna selection retention. `_rtl88ee_smart_antenna()` updates fast antenna training statistics. `rtl88ee_tx_fill_desc()` maps a skb for DMA, clears descriptor content, sets first/last segment, rate, AMPDU, RTS/CTS, bandwidth, sequence, security type, queue selection, rate fallback, buffer size/address, MAC ID/rate ID, QoS, multicast/broadcast, and antenna selection. `rtl88ee_tx_fill_cmddesc()` prepares firmware command/beacon descriptors. `rtl88ee_set_desc()`, `rtl88ee_get_desc()`, `rtl88ee_is_tx_desc_closed()`, and `rtl88ee_tx_polling()` adapt chip descriptors to rtlwifi PCI ring management.

## Control Flow and State

RX flow starts from a descriptor and skb, computes offset to the 802.11 header after driver-info and shift bytes, validates BSSID/self/beacon status, updates statistics, then passes normalized RX metadata to mac80211. TX flow starts with mac80211 TX info and station state, derives rate-control metadata through `rtl_get_tcb_desc()`, optionally pushes early-mode bytes, DMA maps the skb, and programs the descriptor consumed by hardware. Persistent state is updated in `rtlpriv->stats`, `rtlpriv->dm.fat_table`, PCI ring descriptors, DMA mappings, and mac80211 RX status.

## Dependencies and Integration Points

The file depends on descriptor bit helpers and structs from `trx.h`, register constants from `reg.h`, rate constants from `def.h`, DMA APIs, mac80211 frame helpers, rtlwifi base/stats helpers, dynamic management, LED/PHY support, and PCI queue structures. It is wired into `rtl8188ee_hal_ops` in `sw.c`.

## Risks and Test Signals

Descriptor packing is high risk because bit positions, endian handling, and DMA ownership must match hardware exactly. The code returns on DMA mapping failure without setting an error back to the caller, so TX error accounting depends on outer layers. RX decryption handling has special robust-management-frame logic that must stay aligned with mac80211 expectations. Test signals include RX status correctness, FCS failure reporting, hardware crypto with protected and robust management frames, AMPDU throughput, beacon/management queues, TX descriptor ownership turnover, DMA mapping/unmapping behavior, antenna diversity training, and 20/40 MHz RX/TX behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/trx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/trx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/trx.h

## Purpose

`trx.h` defines the RTL8188EE TX/RX descriptor ABI. It provides descriptor sizes, early-mode helpers, little-endian bitfield accessors, packed documentation structs for TX/RX/PHY status layouts, CCK-rate detection, and exported descriptor function prototypes.

## Important APIs, Types, and Macros

Constants include `TX_DESC_SIZE`, `RX_DESC_SIZE`, `RX_DRV_INFO_SIZE_UNIT`, `USB_HWDESC_HEADER_LEN`, and descriptor offsets. `set_tx_desc_*()` helpers write packet size, offset, ownership, MAC ID, queue, security, aggregation, sequence, RTS/CTS, bandwidth, rate, fallback, antenna selection, buffer size/address, and next descriptor address. `get_rx_desc_*()` helpers read packet length, CRC/ICV, driver-info size, shift, PHY status, software decrypt, ownership, MAC ID, aggregation, sequence, rate, HT, bandwidth, report selection, wake matches, TSF, and buffer address. `struct phy_status_rpt`, `struct rx_fwinfo_88e`, `struct tx_desc_88e`, and `struct rx_desc_88e` document packed hardware layouts.

## Control Flow and State

The inline helpers are direct bit operations over `__le32` descriptor words using `le32p_replace_bits()` and `le32_get_bits()`. They do not allocate or persist state, but the descriptor words they mutate are shared with DMA hardware and PCI ring management.

## Dependencies and Integration Points

The header depends on Linux endian/bit helpers and rate constants such as `DESC92C_RATE1M`. It is consumed by `trx.c`, PCI ring code, and HAL callbacks registered in `sw.c`. It is the contract between software descriptor construction and hardware DMA interpretation.

## Risks and Test Signals

Risks include bit-position mistakes, endian regressions, packed C bitfield portability assumptions, 32-bit DMA address limitations in helpers that accept `u32`, and confusion from `USB_HWDESC_HEADER_LEN` naming in PCI code. Test signals include descriptor dumps, successful TX/RX DMA, ownership bit transitions, RX report parsing, WoWLAN wake pattern fields, early-mode aggregation, and builds on endian-sensitive configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/trx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/Makefile

## Purpose

The `rtl8192c/Makefile` defines the shared `rtl8192c-common` kernel object used by RTL8192C/8188C family drivers.

## Important Build Rules

`rtl8192c-common-objs` is composed from `main.o`, `dm_common.o`, `fw_common.o`, and `phy_common.o`. `obj-$(CONFIG_RTL8192C_COMMON) += rtl8192c-common.o` gates compilation on the Kconfig symbol `CONFIG_RTL8192C_COMMON`.

## Control Flow and State

There is no runtime control flow. Build-time state is the object list and Kconfig selection. Enabling the symbol links common module metadata, dynamic-management code, firmware helpers, and PHY helpers into one common object.

## Dependencies and Integration Points

This integrates with the Linux kernel Kbuild system and chip-specific rtlwifi drivers that select or depend on `CONFIG_RTL8192C_COMMON`.

## Risks and Test Signals

Risks are build omissions when common files gain new dependencies or when chip-specific modules expect symbols not linked into `rtl8192c-common.o`. Test signals are `make M=...` builds with `CONFIG_RTL8192C_COMMON=m/y`, module dependency checks, and successful symbol resolution for RTL8192C-family drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/dm_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/dm_common.c

## Purpose

`dm_common.c` implements shared dynamic-management logic for RTL8192C-family devices: digital initial gain, false alarm accounting, EDCA turbo, dynamic TX power, thermal TX power tracking, RF saving, rate adaptive mask initialization, and Bluetooth coexistence decisions.

## Important APIs and Functions

Exported entry points include `rtl92c_dm_init()`, `rtl92c_dm_watchdog()`, `rtl92c_dm_write_dig()`, `rtl92c_dm_init_edca_turbo()`, `rtl92c_dm_check_txpower_tracking()`, `rtl92c_dm_init_rate_adaptive_mask()`, `rtl92c_dm_rf_saving()`, `rtl92c_dm_dynamic_txpower()`, `rtl92c_dm_bt_coexist()`, and the power-index helpers `dm_savepowerindex()`, `dm_writepowerindex()`, and `dm_restorepowerindex()`. Static helpers collect false alarm counters, adjust initial gain by RSSI/false alarms, manage multi-station/ad hoc behavior, tune CCK packet detection, monitor PWDB, select EDCA BE parameters based on TX/RX byte deltas and BT coexistence, run thermal-meter based OFDM/CCK swing adjustments, trigger LC/IQ calibration, and classify BT service state.

## Control Flow and State

`rtl92c_dm_init()` initializes DM flags and baseline state. `rtl92c_dm_watchdog()` is the runtime coordinator: when RF is on, firmware is not in PS mode, firmware is awake, and RF change is idle, it runs PWDB monitoring, DIG, false alarm stats, BB power saving, dynamic TX power, thermal tracking, BT coexistence, and EDCA turbo. State persists in `rtlpriv->dm`, `dm_digtable`, `dm_pstable`, `falsealm_cnt`, `ra`, `stats`, `btcoexist`, `phy`, and cached backup registers such as `reg_874`, `reg_c70`, `reg_85c`, and `reg_a74`.

## Dependencies and Integration Points

The file depends on `dm_common.h`, common PHY calibration functions, rtlwifi PCI/base/core helpers, register definitions from rtl8192ce, and firmware command helpers for RSSI/power-save integration. It is shared across chip-specific modules and assumes the caller supplies chip-specific register access through `rtlpriv->cfg->ops`.

## Risks and Test Signals

Risks include global static state shared across devices (`initialized`, EDCA counters, media connect), temperature compensation arithmetic and table bounds, hard-coded magic registers, BT coexistence heuristics, and watchdog gating that can skip needed updates while firmware power-save state is wrong. Test signals include watchdog traces, false alarm counters, stable RSSI and rate adaptation, EDCA parameter changes under uplink/downlink load, thermal TX power tracking across temperature changes, BT coexistence traffic, RF saving transitions, and multi-adapter testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/dm_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/dm_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/dm_common.h

## Purpose

`dm_common.h` declares shared RTL8192C dynamic-management thresholds, flags, enums, state helpers, and exported function prototypes.

## Important APIs, Types, and Constants

Important constants include DIG/false-alarm thresholds (`DM_DIG_FA_*`), OFDM/CCK swing table lengths, TX high-power levels (`TXHIGHPWRLEVEL_*`), near-field thresholds, dynamic function flags (`DYNAMIC_FUNC_*`), DM type flags, and RSSI source selectors. It defines `struct swat_t` for software antenna switching state, enums for DIG operation type, 1R/2R CCA, RF saving state, and antenna switch state. Prototypes expose DM init/watchdog, DIG write, EDCA turbo init, TX power tracking, rate adaptive mask init, RF saving, PHY calibration callbacks, dynamic TX power, BT coexistence, and power-index backup/restore.

## Control Flow and State

The header has no runtime control flow. It defines the constants and prototypes that shape `dm_common.c` state transitions and the chip-specific PHY/DM call graph.

## Dependencies and Integration Points

It includes rtlwifi common `wifi.h`, rtl8192ce `def.h` and `reg.h`, and `fw_common.h`. This coupling means the common DM layer uses RTL8192CE register naming even when shared by related chips.

## Risks and Test Signals

Risks include threshold changes affecting radio sensitivity or compliance, enum/flag drift relative to common `rtl_priv` fields, and accidental dependency expansion from included chip-specific headers. Test signals include build coverage for all consumers and runtime validation of DIG, dynamic TX power, BT coexistence, and calibration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/dm_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/fw_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/fw_common.c

## Purpose

`fw_common.c` implements shared RTL8192C-family firmware download and host-to-controller command handling. It loads firmware into device memory, waits for firmware readiness, serializes H2C mailbox writes, sends power-save commands, prepares reserved pages, reports join state, and configures P2P power-save offload.

## Important APIs and Functions

`rtl92c_download_fw()` parses an optional firmware header, enables firmware download, writes pages or blocks through `rtl_fw_page_write()`/`rtl_fw_block_write()`, disables download mode, and waits for checksum/ready bits. `_rtl92c_fill_h2c_command()` serializes access with `h2c_lock`, chooses one of four HME boxes, waits for firmware to clear the previous command, writes normal and extended mailbox bytes for command lengths 1-5, and rotates `last_hmeboxnum`. `rtl92c_fill_h2c_cmd()` checks `fw_ready`, copies the command payload, and delegates to the mailbox writer. Other exported helpers include `rtl92c_firmware_selfreset()`, `rtl92c_set_fw_pwrmode_cmd()`, `rtl92c_set_fw_rsvdpagepkt()`, `rtl92c_set_fw_joinbss_report_cmd()`, and `rtl92c_set_p2p_ps_offload_cmd()`.

## Control Flow and State

Firmware download is a staged sequence: enable MCU download registers, write firmware body, disable download mode, poll `FWDL_CHKSUM_RPT`, set `MCUFWDL_RDY`, clear `WINTINI_RDY`, and poll for `WINTINI_RDY`. H2C command flow is guarded by `rtlhal->h2c_setinprogress` under spinlock, then waits for firmware-read status, writes payload bytes, updates the mailbox index, and clears the in-progress flag. Reserved-page setup mutates a static 768-byte packet template with current MAC/BSSID/AID, sends it as a command packet, then tells firmware page locations. P2P offload writes NoA descriptors and sends a compact offload command.

## Dependencies and Integration Points

The file depends on rtlwifi firmware write helpers, PCI/base/core helpers, eFuse/common types, rtl8192ce register/definition headers, `fw_common.h`, skb allocation, and H2C command IDs from common definitions. It is linked by `rtl8192c-common` and called from chip-specific init, power-save, join, and P2P paths.

## Risks and Test Signals

Risks include returning success from `rtl92c_download_fw()` even after `_rtl92c_fw_free_to_go()` reports an error, static reserved-page packet mutation across devices, mailbox timeout behavior under firmware hangs, command length handling limited to five bytes, and P2P NoA start-time loops. Test signals include firmware load success/failure logs, checksum/ready polling, H2C mailbox traces, LPS entry/exit, reserved page download, join report behavior, P2P CTWindow/NoA offload, and concurrent command stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/fw_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/fw_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/fw_common.h

## Purpose

`fw_common.h` declares firmware-size/page constants, chip-version helper macros, H2C payload setters, and exported firmware command APIs for RTL8192C-family common code.

## Important APIs and Constants

Firmware constants include `FW_8192C_SIZE`, start/end address, `FW_8192C_PAGE_SIZE`, polling delay, and timeout count. Header detection is handled by `IS_FW_HEADER_EXIST()`. Version helpers classify normal chips, RF type, 92C serial, UMC vendor, and UMC B-cut devices. H2C setter macros fill power-mode, join report, and reserved-page location fields. Prototypes cover firmware download, H2C command fill, firmware self-reset, power-mode command, reserved-page packet setup, join-BSS report, async USB write hook, and P2P power-save offload.

## Control Flow and State

The header contains no runtime control flow. Its macros are used by `fw_common.c` to decide firmware layout, command payload content, and chip behavior branches.

## Dependencies and Integration Points

It relies on kernel bit and endian helpers being available from includers. It is included by `dm_common.h` and `fw_common.c`, making firmware command declarations visible to dynamic-management and chip-specific code.

## Risks and Test Signals

Risks include signature-mask mistakes, version-helper drift relative to hardware definitions, payload setter macros without bounds checking, and the orphan-looking `usb_writeN_async()` declaration needing a matching consumer/provider. Test signals include builds for PCI/USB variants, firmware header parsing, chip-version branch coverage, and H2C command byte validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/fw_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/main.c

## Purpose

`main.c` supplies module metadata for the shared `rtl8192c-common` component.

## Important APIs and Metadata

The file includes `wifi.h` and `<linux/module.h>`, then declares authors, GPL license, and module description: "Realtek 8192C/8188C 802.11n PCI wireless". It does not register a bus driver; registration is handled by chip-specific PCI/USB modules that link against this common object.

## Control Flow and State

There is no runtime control flow, no persistent state, and no init/exit function in this file. Its effect is build/module metadata only.

## Dependencies and Integration Points

It is part of `rtl8192c-common-objs` in the Makefile. It integrates with Linux module metadata tooling and modinfo output.

## Risks and Test Signals

The main risk is metadata mismatch: the description says PCI even though the common component is shared by family drivers. Test signals are successful module build/link and expected `modinfo` metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/main.c -->
