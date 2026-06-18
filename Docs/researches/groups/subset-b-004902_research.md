# Research: subset-b-004902

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/reg.h

## Purpose
This header is the shared register map for the rtw88 Realtek wireless driver family. It gives the rest of the driver symbolic names for MAC, system, DMA, beacon, EDCA, RX/TX, baseband, RF, firmware mailbox, coexistence, USB, and LTE-coexistence registers, plus bit masks and field constructors used by chip-specific code such as `rtw8703b.c`, `rtw8723d.c`, common MAC/PHY helpers, firmware download, efuse access, coexistence, and bus glue.

## Important APIs, Types, And Functions
The file is macro-only; its API is the collection of `REG_*`, `BIT_*`, `BITS_*`, `MASK*`, and field helper definitions. Major areas include power and firmware boot registers (`REG_SYS_FUNC_EN`, `REG_SYS_PW_CTRL`, `REG_MCUFW_CTRL`, `FW_READY`, `FW_READY_LEGACY`), efuse access (`REG_EFUSE_CTRL`, `REG_EFUSE_ACCESS`, efuse address/data masks), DMA and queue layout (`REG_RQPN`, `REG_RQPN_NPQ`, `REG_AUTO_LLT`, `REG_TXDMA_PQ_MAP`, `REG_RXDMA_MODE`), MAC timing/filter registers (`REG_CR`, `REG_RCR`, `REG_BCN_CTRL`, `REG_TBTT_PROHIBIT`, `REG_EDCA_*`, `REG_RXFLTMAP*`), RF/baseband control (`REG_FPGA0_RFMOD`, `REG_OFDM*`, `REG_CCK*`, `REG_IQK_*`, `RF_*`), coexistence (`REG_BT_COEX_*`, `LTE_COEX_*`), and USB PHY controls.

Several field macros wrap common packed register fields, for example `BIT_RQPN_HLP()`, `BIT_TXDMA_*_MAP()`, `BIT_RXPSF_*`, `BIT_SET_RXPSF_*`, and RF channel masks. These are consumed by read/modify/write helpers throughout rtw88 rather than being invoked as functions.

## Control Flow
There is no runtime control flow in this header. The control-flow effect is indirect: chip code includes it to drive register programming sequences, calibration routines, firmware readiness polling, DMA queue setup, RX filter setup, and coexistence state changes. The same numeric register can have chip-generation aliases in this file, so call sites decide which definition applies based on the chip info and operation callbacks.

## State And Persistence
The macros name hardware state rather than storing driver state. Writes to these registers persist in device hardware until reset, power transition, firmware restart, or later driver reprogramming. The most sensitive persistent domains are power/clock enable bits, firmware download status bits, LLT/FIFO page allocation, RX/TX enable and filter bits, baseband/RF calibration state, and coexistence grants. Because the header is shared, incorrect masks or aliases can corrupt state across many chip families.

## Dependencies And Integration Points
The header depends on Linux bit helpers such as `BIT()`, `GENMASK()`, and common mask constants visible through included driver headers. It integrates with nearly every rtw88 subsystem: `mac.c` for MAC enable/filter/timing, `fw.c` for mailbox and firmware status, `phy.c` for BB/RF and calibration, `coex.c` for Bluetooth/LTE coexistence, bus backends for USB/SDIO/PCI power and interrupt details, and chip files that pass register constants into generic helper APIs.

## Risks
The main risks are silent hardware misprogramming from wrong offsets, duplicate aliases, masks that do not match a specific chip generation, or field helpers used with values outside the intended width. Many names cover undocumented vendor-derived registers, so maintainers rely on empirical behavior and neighboring chip support. Shared definitions also make refactors risky: a change intended for one chip can affect firmware download, power sequencing, RX filters, calibration, or coexistence on another.

## Test Signals
Useful signals are successful firmware download and `FW_READY` polling, stable power on/off and low-power transitions, correct efuse reads, working TX/RX after MAC enable, valid channel changes, calibration completion, RX PHY status reporting, beacon operation, coexistence debug output, and no register-access warnings across PCI/USB/SDIO variants. Regression tests should include devices from more than one rtw88 generation because this header is broad and shared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/regd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/regd.c

## Purpose
This file implements rtw88 regulatory-domain management. It maps ISO alpha-2 country codes to Realtek transmit-power regulatory groups for 2.4 GHz and 5 GHz, initializes cfg80211 regulatory behavior before hardware registration, handles later regulatory notifications, updates PHY adaptivity and transmit power when the regulatory domain changes, and exposes helpers for current regulatory selection and alternative power-limit groups.

## Important APIs, Types, And Functions
The large `rtw_reg_map[]` table maps countries to `struct rtw_regulatory` entries using `COUNTRY_REGD_ENT()`, with `rtw_reg_ww` as the worldwide fallback. `rtw_regd_init()` installs `wiphy->reg_notifier`, detects whether efuse contains a valid country, sets `REGULATORY_STRICT_REG` and `REGULATORY_COUNTRY_IE_IGNORE` for programmed domains, initializes `rtwdev->regd`, and applies channel capability limits. `rtw_regd_hint()` sends `regulatory_hint()` after `ieee80211_register_hw()` when efuse programmed a country.

Runtime handling is in `rtw_regd_notifier()`, driven by `rtw_regd_state_hdl()` and per-state handlers for worldwide, programmed, and user-setting modes. Public helpers are `rtw_regd_get()` for the active 2G/5G tx-power group, `rtw_regd_srrc()` for China/SRRC detection, and `rtw_regd_has_alt()` for mapping special groups such as IC, KCC, ACMA, CN, Qatar, Mexico, UK, and Ukraine to fallback groups.

## Control Flow
Before mac80211 registration, `rtw_regd_init()` checks efuse country code through `rtw_reg_find_by_name()`. A recognized code moves state to `RTW_REGD_STATE_PROGRAMMED`, configures strict regulatory flags, and later `rtw_regd_hint()` asks cfg80211 to apply that country. An unrecognized code stays worldwide.

When cfg80211 calls the notifier, the current state chooses the transition rule. Worldwide mode accepts user country requests and moves to setting mode when the requested domain is not worldwide. Programmed mode accepts only the driver-initiated request matching the efuse country. Setting mode accepts user requests and returns to worldwide if the requested alpha2 maps to the worldwide fallback. Accepted requests are applied under `rtwdev->mutex`, update `rtwdev->regd`, call `rtw_phy_adaptivity_set_mode()`, and recompute TX power for `hal->current_channel`.

## State And Persistence
The persistent software state is `rtwdev->regd`, containing the state enum, a pointer to the selected `struct rtw_regulatory`, and the DFS region from cfg80211. The file also mutates `wiphy->regulatory_flags` to ignore country IEs or clear that ignore flag when returning to worldwide. Hardware-observable state is applied indirectly through PHY adaptivity and TX power reprogramming. Channel flags can be permanently constrained for the lifetime of the registered wiphy when efuse hardware capability lacks 80 MHz support.

## Dependencies And Integration Points
This code depends on cfg80211/mac80211 regulatory APIs (`struct wiphy`, `struct regulatory_request`, `regulatory_hint()`), rtw88 core state in `main.h`, logging in `debug.h`, and PHY functions from `phy.h`. `rtw_regd_get()` feeds transmit-power-limit selection elsewhere in rtw88, and `rtw_regd_srrc()` lets PHY/coexistence code identify China-specific behavior. `rtw_regd_apply_hw_cap_flags()` integrates efuse hardware capability with `wiphy->bands`.

## Risks
Regulatory correctness is high impact. Wrong country mapping, fallback behavior, or state transitions can allow invalid channels or power levels, or unnecessarily restrict operation. The handler table indexes by `rtwdev->regd.state`, so invalid state values would be unsafe. `rtw_regd_has_alt()` indexes `rtw_regd_alt[regd]` without a local bounds check and relies on callers passing values below `RTW_REGD_MAX`. The country table is static and can drift from current regulatory requirements. Mutating wiphy flags in notifier paths must stay consistent with cfg80211 expectations.

## Test Signals
Test with efuse programmed to a valid country, efuse unset/invalid, user regulatory changes, worldwide fallback, and country changes while associated. Signals include expected cfg80211 regulatory events, correct `rtwdev->regd` state transitions, correct `REGULATORY_COUNTRY_IE_IGNORE` behavior, TX power table selection through `rtw_regd_get()`, adaptivity updates, and no 80 MHz channel exposure when efuse hardware capability lacks 80 MHz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/regd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/regd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/regd.h

## Purpose
This header declares the rtw88 regulatory interface and legacy channel-plan constants used by the regulatory and transmit-power code. It gives other rtw88 modules a compact API for regulatory initialization, regulatory hints, current TX-power regulatory group lookup, alternative-group lookup, and China/SRRC detection.

## Important APIs, Types, And Functions
The header aliases older mac80211 channel flags (`IEEE80211_CHAN_NO_IBSS`, `IEEE80211_CHAN_PASSIVE_SCAN`) to `IEEE80211_CHAN_NO_IR`. `enum rtw_chplan_id` lists Realtek channel-plan IDs seen in efuse/vendor data, including world, FCC, ETSI, MKK, IC, KCC, ACMA, CN-related, and Realtek-defined plans. `struct country_code_to_enum_rd` represents a country-code-to-domain mapping pair. `enum country_code_type` names legacy domain categories and terminates with `COUNTRY_CODE_MAX`.

The exported function declarations are `rtw_regd_init()`, `rtw_regd_hint()`, `rtw_regd_get()`, `rtw_regd_has_alt()`, and `rtw_regd_srrc()`.

## Control Flow
The header does not implement control flow. It defines call points used by probe and registration: initialize before `ieee80211_register_hw()`, send a hint after registration, then query current regulatory values during PHY/TX-power operation.

## State And Persistence
No state is stored here. The enums and constants must remain stable because efuse/channel-plan values and vendor-derived tables may encode these IDs persistently in hardware data. The API functions operate on `struct rtw_dev` state managed in `regd.c`.

## Dependencies And Integration Points
The declarations assume rtw88 core types such as `struct rtw_dev` and kernel wireless channel flags are visible through including context. `regd.c` implements the functions, while PHY and transmit-power code query the current regulatory group and alternate groups. The channel-plan IDs also document the efuse-facing vocabulary used by adjacent efuse parsing and power-limit code.

## Risks
Because this header mixes historical channel-plan constants with the current regulatory API, unused-looking values may still be hardware or vendor-data contracts. Removing or renumbering enum values would risk misinterpreting efuse/channel-plan data. The legacy channel flag aliases also hide API churn; call sites should not infer old IBSS/passive-scan semantics beyond `NO_IR`.

## Test Signals
Build coverage is the primary signal for declarations. Runtime signals come from successful probe-time `rtw_regd_init()`/`rtw_regd_hint()` flow, correct power-limit lookup through `rtw_regd_get()`, and chip code using `rtw_regd_srrc()` or `rtw_regd_has_alt()` without out-of-range values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/regd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8703b.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8703b.c

## Purpose
This file is the chip implementation and hardware specification for Realtek RTL8703B in rtw88. It supplies power sequences, PHY/MAC initialization, efuse handling, channel programming, RX PHY status parsing, IQ calibration, thermal power tracking, Bluetooth coexistence parameters, and the exported `rtw8703b_hw_spec` consumed by SDIO module glue such as `rtw8723cs.c`.

## Important APIs, Types, And Functions
The central export is `const struct rtw_chip_info rtw8703b_hw_spec`. It references `rtw8703b_ops`, firmware names, descriptor sizes, efuse sizes, FIFO/page geometry, 2.4 GHz-only capabilities, HT support, no VHT, no LDPC/STBC, power sequences, queue/page tables, RF SIPI addresses, table exports from `rtw8703b_tables.c`, RFE definitions, power-track tables, and coexistence tables.

Important operation callbacks include `rtw8703b_read_efuse()`, `rtw8703b_phy_set_param()`, `rtw8703b_set_channel()`, `query_phy_status()`, `rtw8703b_phy_calibration()`, and `rtw8703b_pwr_track()`. Supporting code covers notch/spur calibration, `rtw8703b_iqk_*` calibration stages, OFDM/CCK swing programming, device-tree MAC fallback through `try_mac_from_devicetree()`, and coexistence setup functions such as `rtw8703b_coex_set_rfe_type()`.

## Control Flow
Probe code reaches this file through `rtw8703b_hw_spec.ops`. Power on/off uses static `struct rtw_pwr_seq_cmd` arrays for pre-enable, card-disabled to card-emulation, card-emulation to active, active to low-power, MCU reset, and card disable transitions. Efuse read delegates to `rtw8723x_read_efuse()` and, if the efuse MAC address is invalid, optionally fills it from device tree.

PHY setup powers the BB/RF domain, configures RF path A, loads generated MAC/AGC/BB/RF tables, sets RCR/HIQ/AFE/XTAL/EDCA/RX aggregation/beacon/AMPDU timing registers, initializes common PHY, checks CCK AGC report format from `REG_BB_AMP`, runs LCK, adjusts initial gain, and initializes power tracking. Channel changes program RF channel/bandwidth, call common MAC channel programming, write BB bandwidth/sideband/DFIR settings, and conditionally enable notch filters after PSD spur measurements on channels 5-8, 13, and 14.

RX PHY status dispatches by rate: CCK frames decode LNA/VGA fields from `struct phy_status_8703b`, including the long-report LNA high bit when enabled; OFDM frames decode AGC gain, signal power, EVM, SNR, and CFO. IQK runs up to three rounds, compares round similarity through shared rtw8723x helpers, chooses a final or hybrid candidate, and fills path A IQ matrices. Power tracking alternates between triggering the thermal meter and applying thermal deltas to OFDM/CCK swing tables, TXAGC remnants, XTAL tracking, and optional IQK.

## State And Persistence
The file mutates hardware registers extensively and persists runtime calibration state in `rtwdev->dm_info`: default swing indexes, thermal EWMA, delta power indexes, CCK AGC report type, RSSI/SNR/CFO/EVM values, IQK results, and power-track trigger state. Efuse-derived state includes crystal cap, thermal meter, RFE option, power-track type, and MAC address. Firmware and MAC/RF register state is not persistent across device reset and is reconstructed through chip ops and power sequences.

## Dependencies And Integration Points
The implementation depends on rtw88 core headers (`main.h`, `mac.h`, `phy.h`, `rx.h`, `coex.h`, `debug.h`, `reg.h`), shared RTL8723x helpers in `rtw8723x.h`, generated tables in `rtw8703b_tables.c`, and Linux device-tree MAC lookup from `<linux/of_net.h>`. It integrates with the generic rtw88 probe path through `struct rtw_chip_ops`, with SDIO module glue through `rtw8703b_hw_spec`, with firmware loading through `MODULE_FIRMWARE`, and with Bluetooth coexistence through common coex tables and callbacks.

## Risks
Most risk is hardware-sequencing risk. Power sequences and PHY init write many undocumented registers whose ordering matters. Channel notch filtering is empirically derived and can reduce sensitivity if enabled incorrectly. CCK RSSI depends on a sparse LNA gain table; invalid LNA indices return -120 dBm with a warning. IQK timeout/failure paths must restore backed-up path, LTE grant, and BB state or later TX quality and coexistence can break. Several comments mark uncertainty, including fixed power-track defaults, full-byte HIQ setting, unknown USB interface support, no 8703B WOWLAN implementation despite firmware, and incomplete WLAN TX power/RX gain coex controls.

## Test Signals
Test signals include successful firmware load for `rtw88/rtw8703b_fw.bin`, stable SDIO probe for 8723CS-class devices, valid device-tree MAC fallback when efuse MAC is invalid, correct 2.4 GHz association on 20/40 MHz channels, RX RSSI/SNR/EVM sanity for CCK and OFDM rates, spur/notch behavior on channels 5-8/13/14, IQK success logs and no persistent WARNs, thermal power tracking without TX power jumps, Bluetooth coexistence behavior on shared-antenna boards, suspend/power-off recovery, and absence of invalid register warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8703b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8703b.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8703b.h

## Purpose
This header declares RTL8703B-specific types, PHY status layout, register constants, and the exported chip descriptor. It is the public chip-local contract used by `rtw8703b.c`, generated table headers, and bus module glue such as `rtw8723cs.c`.

## Important APIs, Types, And Functions
The main symbol is `extern const struct rtw_chip_info rtw8703b_hw_spec`. `struct phy_rx_agc_info` and `struct phy_status_8703b` describe the packed RX PHY status report layout, with endian-aware bitfields for AGC gain/TRSW and final status bits such as SGI, RXSC, antenna selection, and antenna training. Macros define VGA/LNA extraction masks, the 8703B CCK long-report LNA bit handling, baseband registers (`REG_BB_PWR_SAV5_11N`, `REG_BB_AMP`, `REG_CCK_TXSF2`, `REG_CCK_DBG`, `REG_OFDM0_A_TX_AFE`, `REG_TXIQK_MATRIXB_LSB2_11N`, `REG_OFDM0_TX_PSD_NOISE`, `REG_IQK_RDY`), RF register `RF_RCK1`, and RX DMA aggregation burst constants.

## Control Flow
The header does not execute control flow. It shapes control flow in `rtw8703b.c`: RX PHY status parsing casts raw hardware bytes to `struct phy_status_8703b`, channel setup writes the baseband constants, IQK polling uses `REG_IQK_RDY`, and PHY init reads `BIT_MASK_RX_LNA` to select CCK AGC report format.

## State And Persistence
No software state is stored here. The packed PHY status struct represents transient per-packet hardware reports. Register definitions refer to persistent BB/RF state that remains until reset or reprogramming. The endian bitfields are part of the ABI between raw device reports and driver parsing.

## Dependencies And Integration Points
The header includes `rtw8723x.h`, so it shares calibration and common chip definitions with the RTL8723x family. It is included by `rtw8703b.c` and `rtw8723cs.c`. The exported chip info is passed as `driver_data` by the SDIO id table.

## Risks
Packed hardware-report definitions are fragile: field order, endian conditionals, and mask usage must match firmware/hardware output exactly. The comments note that the report may be shared with other chips but is currently local, and that some register bits are only partially understood. If `BIT_MASK_RX_LNA` interpretation is wrong, CCK RSSI can be significantly wrong.

## Test Signals
Build and sparse/endian coverage are useful for the packed bitfields. Runtime signals include sane RSSI for CCK and OFDM packets, correct detection of long CCK AGC report format, successful IQK polling through `REG_IQK_RDY`, and valid SDIO binding through `rtw8703b_hw_spec`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8703b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8703b_tables.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8703b_tables.c

## Purpose
This file contains generated/static hardware initialization and power-limit tables for RTL8703B. It packages BB power-by-rate, TX power limit, MAC register, AGC, baseband, and RF path A programming arrays into `struct rtw_table` exports consumed by `rtw8703b_hw_spec` and the generic rtw88 PHY table loader.

## Important APIs, Types, And Functions
The important exported table objects are produced by macros: `rtw8703b_bb_pg_tbl`, `rtw8703b_txpwr_lmt_tbl`, `rtw8703b_mac_tbl`, `rtw8703b_agc_tbl`, `rtw8703b_bb_tbl`, and `rtw8703b_rf_a_tbl`. The backing arrays are `rtw8703b_bb_pg[]`, `rtw8703b_txpwr_lmt[]`, `rtw8703b_mac[]`, `rtw8703b_agc[]`, `rtw8703b_bb[]`, and `rtw8703b_rf_a[]`.

The declaration macros select the table interpretation: `RTW_DECL_TABLE_BB_PG()` for power-by-rate page data, `RTW_DECL_TABLE_TXPWR_LMT()` for regulatory/channel/rate-section power limits, `RTW_DECL_TABLE_PHY_COND(..., rtw_phy_cfg_mac/agc/bb)` for conditional register programming, and `RTW_DECL_TABLE_RF_RADIO(..., A)` for RF path A.

## Control Flow
There is no procedural control flow in this file. During `rtw8703b_phy_set_param()`, `rtw_phy_load_tables()` walks the exported table objects from the chip info and applies each register/value pair through the appropriate MAC, AGC, BB, or RF loader. TX power-limit data is consulted later when transmit power is calculated for the active regulatory group, channel, bandwidth, and rate section.

## State And Persistence
The arrays are read-only driver data. Applying them creates persistent hardware state in MAC, AGC, BB, RF, TX-power, and power-by-rate registers until later updates or reset. Regulatory TX power limits are data state used repeatedly by power calculation rather than one-time register state.

## Dependencies And Integration Points
The file depends on `main.h`, `phy.h`, and `rtw8703b_tables.h` for table types and declarations. It integrates directly with `rtw8703b.c` through `rtw8703b_hw_spec.mac_tbl`, `.agc_tbl`, `.bb_tbl`, `.rf_tbl`, RFE definitions, and power-limit references. The values are vendor-derived hardware programming data and must match the silicon and firmware assumptions.

## Risks
The risk profile is data correctness. A single wrong register/value pair can break initialization, calibration, RF sensitivity, output power, coexistence, or regulatory compliance. The TX power-limit table contains permissive sentinel-like `63` values for some channel/rate combinations; consumers must interpret those correctly. Because table loaders hide control flow behind data, failures can be hard to localize without register traces.

## Test Signals
Signals include successful table loading during probe, working association after PHY init, sane RX sensitivity and TX throughput, correct channel 1-14 behavior, regulatory power-limit selection for FCC/ETSI/MKK mappings, RF path A operation, and no unexpected register-loader warnings. Comparing register dumps against known-good vendor-driver initialization is useful for table regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8703b_tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8703b_tables.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8703b_tables.h

## Purpose
This header declares the RTL8703B table exports generated in `rtw8703b_tables.c`. It gives the chip implementation a stable list of table objects to attach to `struct rtw_chip_info`.

## Important APIs, Types, And Functions
The declarations are `rtw8703b_bb_pg_tbl`, `rtw8703b_txpwr_lmt_tbl`, `rtw8703b_mac_tbl`, `rtw8703b_agc_tbl`, `rtw8703b_bb_tbl`, and `rtw8703b_rf_a_tbl`, all as `const struct rtw_table`.

## Control Flow
No control flow is implemented. The header enables `rtw8703b.c` to reference table objects that are later traversed by generic rtw88 PHY and power-limit loaders.

## State And Persistence
The header owns no state. The declared tables are read-only data; when loaded, they program persistent hardware register state and provide power-limit policy data.

## Dependencies And Integration Points
It depends on the including code having `struct rtw_table` visible, normally through rtw88 core headers. It is included by `rtw8703b.c` and `rtw8703b_tables.c`.

## Risks
Mismatched declarations and definitions would break builds or bind the chip descriptor to the wrong table. Adding new table objects in the C file without updating this header prevents the chip implementation from using them.

## Test Signals
Build/link success and successful PHY table loading through `rtw8703b_hw_spec` are the main signals. Runtime proof comes from stable 8703B initialization and correct TX power-limit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8703b_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723cs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723cs.c

## Purpose
This is the SDIO module glue for Realtek RTL8723CS-class devices in rtw88. In this tree, RTL8723CS binds to the RTL8703B chip implementation by passing `rtw8703b_hw_spec` as SDIO driver data.

## Important APIs, Types, And Functions
The `rtw_8723cs_id_table[]` matches `SDIO_VENDOR_ID_REALTEK` and `SDIO_DEVICE_ID_REALTEK_RTW8723CS`, with `.driver_data = &rtw8703b_hw_spec`. `rtw_8723cs_driver` wires the Linux SDIO driver callbacks to common rtw88 SDIO helpers: `rtw_sdio_probe`, `rtw_sdio_remove`, `rtw_sdio_shutdown`, and `rtw_sdio_pm_ops`. `module_sdio_driver()` registers the module.

## Control Flow
When the SDIO core matches the device ID, it invokes `rtw_sdio_probe()`. The common probe extracts the chip info from driver data and uses the 8703B operations and tables for firmware loading, power sequencing, MAC/PHY setup, and runtime operation. Removal, shutdown, and power management are delegated completely to common SDIO code.

## State And Persistence
This file stores only static module metadata and device ID data. Runtime device state is owned by the SDIO core and common rtw88 structures allocated by `rtw_sdio_probe()`. Persistent hardware behavior is defined by the referenced `rtw8703b_hw_spec`, not by this glue file.

## Dependencies And Integration Points
The file depends on Linux MMC/SDIO IDs and module APIs, `main.h`, `sdio.h`, and `rtw8703b.h`. It is an integration point between the kernel SDIO bus match table and the rtw88 RTL8703B chip implementation.

## Risks
The key risk is identity mismatch: this module labels the device as 8723CS while using 8703B hardware data, so the assumption that the SDIO 8723CS target is compatible with `rtw8703b_hw_spec` must remain valid. Missing or wrong SDIO IDs prevent autoload. Any common SDIO PM or shutdown bug affects this module because it has no local recovery logic.

## Test Signals
Signals include module autoload via the SDIO modalias, successful `rtw_sdio_probe()`, firmware load for the 8703B spec, interface creation, suspend/resume through `rtw_sdio_pm_ops`, and clean remove/shutdown on 8723CS hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723d.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723d.c

## Purpose
This file is the chip implementation and hardware specification for Realtek RTL8723D in rtw88. It supports PCI, SDIO, and USB module wrappers by exporting `rtw8723d_hw_spec`, and implements RTL8723D-specific PHY initialization, RX PHY status parsing, channel programming, shutdown, IQ calibration for S1/S0 paths, CCK packet-detect tuning, thermal power tracking, Bluetooth coexistence, power sequences, and interface PHY parameters.

## Important APIs, Types, And Functions
The exported object is `const struct rtw_chip_info rtw8723d_hw_spec`. It attaches `rtw8723d_ops`, firmware `rtw88/rtw8723d_fw.bin`, descriptor/efuse/FIFO/page geometry, 2.4 GHz HT-only capability, power sequences, page/RQPN tables, PCIe interface PHY parameters, generated tables from `rtw8723d_table.c`, RFE definitions, power-track tables, and coexistence metadata.

Important callbacks are `rtw8723d_phy_set_param()`, `query_phy_status()`, `rtw8723d_set_channel()`, `rtw8723d_shutdown()`, `rtw8723d_phy_calibration()`, `rtw8723d_phy_cck_pd_set()`, and `rtw8723d_pwr_track()`. IQK is organized around `struct rtw_8723d_iqk_cfg` and path configs for `PATH_S1` and `PATH_S0`; helper families perform one-shot calibration, TX/RX failure checks, matrix fills, RF standby, path preconfiguration, and final result selection.

## Control Flow
Probe enters through bus-specific wrappers and common rtw88 code using `rtw8723d_hw_spec`. Power sequencing uses card-disabled to card-emulation, card-emulation to active, active to LPS, pre-card-disable, card-emulation, card-disabled, and post-card-disable arrays. PHY setup enables BB/RF power, loads hardware tables, configures RCR/HIQ/AFE/XTAL, handles an AFE variant, sets timing, beacon, AMPDU, LTR, TXDMA, LCK, initial gain, and power tracking.

RX PHY parsing switches on the low nibble page field. Page 0 handles simple CCK-like power/rssi/bandwidth. Page 1 decodes OFDM/HT power, RF mode, RXSC-derived bandwidth, EVM, SNR, and CFO into `rtw_rx_pkt_stat` and `dm_info`. Channel changes program RF path A/B channel and bandwidth, run spur calibration on channels 13/14, call common MAC channel setup, and write BB DFIR/RF mode/CCK sideband state. Shutdown disables USB suspend through `REG_HCI_OPT_CTRL`.

IQK runs three rounds across S1 and S0, with TX then RX calibration per path and retry loops. It backs up path control, LTE grants, and registers using shared rtw8723x helpers, compares result similarity, falls back to a hybrid candidate when possible, fills S1 and S0 TX/RX IQ matrices, stores selected IQK results in `dm_info`, and logs register state. Power tracking alternates thermal-meter trigger and correction application; it adjusts OFDM/CCK swing, TXAGC remnants, XTAL, TX power level, and triggers IQK when needed.

## State And Persistence
The file persists chip runtime state in hardware registers and `rtwdev->dm_info`: thermal averages, default swing indexes, TXAGC remnants, current RSSI/SNR/CFO/EVM values, CCK packet-detect level, IQK results, and power-track trigger state. Efuse fields drive crystal cap, AFE variant, thermal meter, share-antenna/RFE selection, and power-track behavior. `rtwdev->coex` stores current coexistence power/rx-gain levels and RFE metadata. Hardware state is rebuilt on reset through power sequences, table load, PHY init, channel setup, and calibration.

## Dependencies And Integration Points
The implementation depends on rtw88 core, firmware, TX/RX, PHY, MAC, debug, coexistence, and shared RTL8723x helpers. It integrates with PCI (`rtw8723de.c`), SDIO (`rtw8723ds.c`), and USB (`rtw8723du.c`) wrappers through the exported chip info. It also integrates with generated tables, generic TX power calculation, common `rtw8723x_mac_init/postinit`, RF SIPI read/write helpers, cfg80211/mac80211 HT capabilities through the chip descriptor, and coex debugfs through `coex_info_hw_regs_8723d`.

## Risks
The file is register-sequence heavy and hardware-sensitive. IQK has many path-specific RF writes, LTE grant changes, and backup/restore points; failures can leave calibration or coexistence state wrong. `rtw8723d_set_channel_rf()` reads and writes both RF paths even though the chip is configured as 2.4 GHz HT-only and may be in 1x1 variants. CCK PD updates depend on false-alarm state and current association. Coex TX power and RX gain callbacks cache levels and rewrite AGC tables; stale cache state could skip needed reprogramming. Regulatory and power-limit compliance depends on generated tables and `rtw_phy_set_tx_power_level()` being called after swing/TXAGC changes.

## Test Signals
Signals include successful probe over PCI/SDIO/USB, firmware load, stable 20/40 MHz operation on all 2.4 GHz channels, correct shutdown on USB variants, PHY status page 0/page 1 parsing with plausible RSSI/SNR/EVM, spur/notch behavior on channels 13/14, IQK completion without fallback WARNs, thermal power tracking with correct TX power recalculation, CCK packet-detect level changes under false-alarm load, Bluetooth coexistence table/TDMA behavior for shared and non-shared antenna boards, and clean suspend/resume/power-off recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723d.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723d.h

## Purpose
This header declares RTL8723D chip identity and RX PHY status extraction helpers. It is included by the main chip implementation and bus-specific module wrappers.

## Important APIs, Types, And Functions
The main external symbol is `rtw8723d_hw_spec`. PHY status macros use `le32_get_bits()` on raw PHY status memory: page 0 exposes `GET_PHY_STAT_P0_PWDB()`, while page 1 exposes per-path power (`GET_PHY_STAT_P1_PWDB_A/B()`), RF mode, legacy/HT RXSC, RXEVM, CFO tail, and RXSNR. It also defines default OFDM/CCK swing indexes and `CCK_DFIR_NR` for channel BB DFIR table sizing.

## Control Flow
The header has no executable control flow. `rtw8723d.c` uses the PHY status macros inside page-specific parsers and uses the swing/DFIR constants during power-track initialization and channel programming.

## State And Persistence
No state is stored here. The macros interpret transient per-packet status bytes. The default swing constants influence initialization of persistent dynamic-management state in `rtwdev->dm_info`.

## Dependencies And Integration Points
It includes `rtw8723x.h` and depends on little-endian bit extraction helpers. It is included by `rtw8723d.c`, `rtw8723de.c`, `rtw8723ds.c`, and `rtw8723du.c`; bus wrappers use only the exported chip descriptor declaration.

## Risks
The PHY status macros cast byte pointers to `__le32 *` and use fixed word offsets, so hardware report layout assumptions must remain exact and aligned enough for supported architectures. Wrong masks or offsets would corrupt RSSI, bandwidth, EVM, SNR, and CFO reporting, which feeds dynamic mechanisms and user-visible signal metrics.

## Test Signals
Signals include sane RSSI and bandwidth reporting for page 0 and page 1 PHY status, no alignment warnings on supported platforms, correct power-track defaults, and successful module linking against `rtw8723d_hw_spec`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723d_table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723d_table.c

## Purpose
This file contains static/generated hardware tables for RTL8723D. It packages MAC, AGC, BB, power-by-rate, RF path A, and TX power-limit data into rtw88 table objects consumed by `rtw8723d_hw_spec` and generic table loaders.

## Important APIs, Types, And Functions
The exported tables are declared through macros as `rtw8723d_mac_tbl`, `rtw8723d_agc_tbl`, `rtw8723d_bb_tbl`, `rtw8723d_bb_pg_tbl`, `rtw8723d_rf_a_tbl`, and `rtw8723d_txpwr_lmt_tbl`. Backing arrays include `rtw8723d_mac[]`, `rtw8723d_agc[]`, `rtw8723d_bb[]`, `rtw8723d_bb_pg[]`, `rtw8723d_rf_a[]`, and `rtw8723d_txpwr_lmt[]`.

The table macros indicate interpretation: conditional MAC/AGC/BB register loading with `rtw_phy_cfg_mac`, `rtw_phy_cfg_agc`, and `rtw_phy_cfg_bb`; RF radio programming for path A; BB power-group programming; and regulatory TX power-limit lookup.

## Control Flow
This file is data-only. During PHY setup, `rtw_phy_load_tables()` applies MAC/AGC/BB/RF tables referenced from `rtw8723d_hw_spec`. TX power-limit entries are consulted later by power calculation code using regulatory group, 2.4 GHz band, bandwidth, rate section, and channel.

## State And Persistence
The arrays are read-only kernel data. Loading the tables produces persistent hardware register state until reset/reprogramming. The TX power-limit table is persistent policy data used across channel and regulatory changes.

## Dependencies And Integration Points
The file depends on `main.h`, `phy.h`, and `rtw8723d_table.h`. It integrates with `rtw8723d.c` through the chip descriptor and RFE definitions. It also depends on the generic rtw88 table declaration macros and loader functions interpreting the pair arrays correctly.

## Risks
Incorrect table data can cause probe failures, broken RX/TX sensitivity, calibration failures, invalid output power, or regulatory violations. The RF table is path-A only, so assumptions about path mapping must match `rtw8723d.c`. The TX power-limit table is dense and hard to audit manually; off-by-one channel, bandwidth, or rate-section entries are plausible regression points.

## Test Signals
Test signals include clean table load, stable association and throughput, expected RSSI/false-alarm behavior, successful IQK and power tracking after table load, correct TX power across FCC/ETSI/MKK-style regulatory groups, and register dumps matching known-good initialization data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723d_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723d_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723d_table.h

## Purpose
This header declares the RTL8723D generated table objects used by the chip implementation.

## Important APIs, Types, And Functions
It declares `rtw8723d_mac_tbl`, `rtw8723d_agc_tbl`, `rtw8723d_bb_tbl`, `rtw8723d_bb_pg_tbl`, `rtw8723d_rf_a_tbl`, and `rtw8723d_txpwr_lmt_tbl` as `const struct rtw_table`.

## Control Flow
No control flow is implemented. The declarations allow `rtw8723d.c` to bind table objects into `rtw8723d_hw_spec`, after which generic rtw88 table loaders handle traversal and programming.

## State And Persistence
The header stores no state. The declared objects are read-only table data; their application programs persistent hardware registers and provides TX power-limit policy.

## Dependencies And Integration Points
The header depends on `struct rtw_table` being visible to includers. It is included by `rtw8723d.c` and `rtw8723d_table.c`.

## Risks
The risk is interface drift between table definitions and declarations. Missing declarations prevent the chip descriptor from referencing required tables, while wrong names/types fail the build.

## Test Signals
Build/link success and successful RTL8723D PHY initialization are the primary signals. Runtime behavior should show table-driven MAC/BB/RF setup and power-limit selection working through `rtw8723d_hw_spec`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723d_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723de.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723de.c

## Purpose
This is the PCI module glue for Realtek RTL8723DE devices in rtw88. It binds the PCI vendor/device ID to the shared RTL8723D chip implementation.

## Important APIs, Types, And Functions
`rtw_8723de_id_table[]` matches `PCI_VENDOR_ID_REALTEK` device `0xD723` and stores `&rtw8723d_hw_spec` in `.driver_data`. `rtw_8723de_driver` delegates probe/remove/shutdown/error handling to common PCI rtw88 helpers: `rtw_pci_probe`, `rtw_pci_remove`, `rtw_pci_shutdown`, `rtw_pci_err_handler`, and `rtw_pm_ops`. `module_pci_driver()` registers the driver.

## Control Flow
When PCI core matches the ID, `rtw_pci_probe()` receives the chip info through the id table and initializes the generic rtw88 device using RTL8723D ops and tables. Removal, PCI shutdown, runtime/system PM, and PCI error recovery are handled by common rtw88 PCI code.

## State And Persistence
This file contains only static ID and driver-registration data. Runtime state is allocated and managed by common rtw88 PCI code. Hardware persistence is governed by `rtw8723d_hw_spec` and common PCI power/error handling.

## Dependencies And Integration Points
It depends on Linux PCI/module APIs, `pci.h`, and `rtw8723d.h`. It is the integration point between PCI modalias autoloading and the shared RTL8723D chip implementation.

## Risks
Wrong PCI IDs or driver data break autoload/probe. Because all behavior is delegated, any mismatch between PCI-specific capabilities and `rtw8723d_hw_spec` must be handled in common PCI or chip code. PCI error recovery depends entirely on `rtw_pci_err_handler`.

## Test Signals
Signals include module autoload on RTL8723DE PCI hardware, successful `rtw_pci_probe()`, firmware load, normal interface creation, suspend/resume via `rtw_pm_ops`, clean shutdown, and correct behavior through PCI error recovery paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723de.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723ds.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723ds.c

## Purpose
This is the SDIO module glue for Realtek RTL8723DS devices in rtw88. It matches both 1-antenna and 2-antenna SDIO IDs and delegates all behavior to common SDIO code using `rtw8723d_hw_spec`.

## Important APIs, Types, And Functions
`rtw_8723ds_id_table[]` has entries for `SDIO_DEVICE_ID_REALTEK_RTW8723DS_1ANT` and `SDIO_DEVICE_ID_REALTEK_RTW8723DS_2ANT`, both with `.driver_data = &rtw8723d_hw_spec`. `rtw_8723ds_driver` uses `rtw_sdio_probe`, `rtw_sdio_remove`, `rtw_sdio_shutdown`, and `rtw_sdio_pm_ops`, and is registered by `module_sdio_driver()`.

## Control Flow
On SDIO match, common `rtw_sdio_probe()` initializes the rtw88 device using the shared RTL8723D chip descriptor. Remove, shutdown, and PM callbacks are delegated to common SDIO helpers.

## State And Persistence
The file owns static ID/driver metadata only. Runtime device state, bus state, firmware state, and hardware programming are all owned by common rtw88 SDIO and RTL8723D chip code.

## Dependencies And Integration Points
It depends on Linux MMC/SDIO IDs, module support, `main.h`, `sdio.h`, and `rtw8723d.h`. It connects SDIO hardware IDs to the common rtw88 SDIO stack and RTL8723D chip implementation.

## Risks
The two antenna variants share the same chip descriptor, so antenna/RFE differences must be represented by efuse data and chip/coex code rather than this ID table. Missing IDs prevent autoload. SDIO PM and shutdown failures cannot be locally mitigated here.

## Test Signals
Signals include autoload for both 1ANT and 2ANT SDIO IDs, successful probe and firmware load, correct antenna/RFE behavior from efuse, suspend/resume via `rtw_sdio_pm_ops`, and clean removal/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723du.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723du.c

## Purpose
This is the USB module glue for Realtek RTL8723DU devices in rtw88. It matches Realtek and Edimax USB IDs and delegates common USB initialization to rtw88 using `rtw8723d_hw_spec`.

## Important APIs, Types, And Functions
`rtw_8723du_id_table[]` includes a Realtek 0xd723 8723DU 1x1 entry and an Edimax EW-7611ULB V2 entry (`0x7392:0xd611`), both using `rtw8723d_hw_spec` as driver info. `rtw8723du_probe()` is a thin wrapper around `rtw_usb_probe()`. `rtw_8723du_driver` registers USB callbacks for probe and disconnect through `module_usb_driver()`.

## Control Flow
USB core matching invokes `rtw8723du_probe()`, which immediately calls `rtw_usb_probe(intf, id)`. The common USB probe retrieves `rtw8723d_hw_spec` from the device ID and initializes firmware, power, MAC/PHY, TX/RX, and mac80211 integration. Disconnect uses `rtw_usb_disconnect()`.

## State And Persistence
This file owns only static ID and driver structures. Runtime state is created by common USB and rtw88 core code. Hardware programming and firmware persistence are defined by the RTL8723D chip descriptor.

## Dependencies And Integration Points
It depends on Linux USB/module APIs, `main.h`, `usb.h`, and `rtw8723d.h`. It is the USB bus integration point for RTL8723D-family hardware and selected third-party adapters.

## Risks
Wrong USB interface matching could bind non-compatible vendor-specific devices because the table uses class/subclass/protocol `0xff`. The wrapper has no PM callbacks beyond common USB behavior visible through `rtw_usb_probe()`/disconnect, so suspend behavior depends on shared USB code. Device-specific quirks for the Edimax adapter would need to be handled elsewhere.

## Test Signals
Signals include USB modalias autoload for both IDs, successful `rtw_usb_probe()`, firmware load, interface creation, traffic over USB, clean disconnect, and no unintended binding to unrelated vendor-specific Realtek interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723du.c -->
