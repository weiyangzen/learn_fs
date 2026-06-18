# subset-b-005427 Research

Grouped source research for the RTL8723BS HAL Bluetooth coexistence, 8723B hardware image loaders, RF calibration, and power-sequence parser. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b2Ant.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b2Ant.c

## Purpose

`HalBtc8723b2Ant.c` implements the RTL8723B two-antenna Bluetooth/Wi-Fi coexistence policy engine. It consumes BT C2H status reports, Wi-Fi state queried through `struct btc_coexist`, and board antenna metadata, then programs firmware H2C commands, PTA coexistence tables, antenna path registers, RF gain/filter tweaks, DAC swing, AGC table shifts, and Rx aggregation controls. The file was read as a complete 2630-line source.

## Important APIs, Types, and Functions

External entry points are `EXhalbtc8723b2ant_PowerOnSetting`, `EXhalbtc8723b2ant_InitHwConfig`, `EXhalbtc8723b2ant_InitCoexDm`, `EXhalbtc8723b2ant_IpsNotify`, `EXhalbtc8723b2ant_LpsNotify`, `EXhalbtc8723b2ant_ScanNotify`, `EXhalbtc8723b2ant_ConnectNotify`, `EXhalbtc8723b2ant_MediaStatusNotify`, `EXhalbtc8723b2ant_SpecialPacketNotify`, `EXhalbtc8723b2ant_BtInfoNotify`, `EXhalbtc8723b2ant_HaltNotify`, `EXhalbtc8723b2ant_PnpNotify`, and `EXhalbtc8723b2ant_Periodical`. Core internal helpers include RSSI hysteresis (`halbtc8723b2ant_BtRssiState`, `halbtc8723b2ant_WifiRssiState`), BT profile classification (`halbtc8723b2ant_UpdateBtLinkInfo`, `halbtc8723b2ant_ActionAlgorithm`), policy application (`halbtc8723b2ant_RunCoexistMechanism`), firmware controls (`halbtc8723b2ant_SetFwPstdma`, `halbtc8723b2ant_SetFwDacSwingLevel`, `halbtc8723b2ant_SetFwDecBtPwr`, `halbtc8723b2ant_SetFwIgnoreWlanAct`), and hardware controls (`halbtc8723b2ant_SetAntPath`, `halbtc8723b2ant_CoexTableWithType`, `halbtc8723b2ant_AgcTable`, `halbtc8723b2ant_RfShrink`, `halbtc8723b2ant_DacSwing`). Static singletons `GLCoexDm8723b2Ant` and `GLCoexSta8723b2Ant` hold current/preconfigured coexistence state.

## Control Flow

Initialization backs up RF register `0x1e`, configures antenna path and PTA registers, enables counters, and resets PS-TDMA and software mechanisms. Runtime begins when `EXhalbtc8723b2ant_BtInfoNotify` parses C2H bytes: source, retry count, RSSI, extended flags, inquiry/page bit, profile bits, TX/RX mask, and BT reset hints. It updates `pBtCoexist->btLinkInfo`, sets broad BT status, mirrors busy/DIG flags through `BTC_SET`, then calls `halbtc8723b2ant_RunCoexistMechanism`. The policy runner checks manual control and IPS, handles BT inquiry/page specially, performs common idle/disconnected handling when possible, otherwise dispatches by algorithm to SCO/HID/A2DP/PAN combinations. Each action chooses PTA table type, PS-TDMA pattern, BT power decrement, firmware DAC swing, RF path mask, Rx aggregation policy, and software mechanisms based on Wi-Fi bandwidth, Wi-Fi RSSI, BT RSSI, AP count, and BT retry history.

## State and Persistence Behavior

State is in static process-global structures, not file-backed persistence. `coex_dm_8723b_2ant` stores previous and current settings so duplicate register/H2C writes can be skipped, plus backup values for RF `0x1e` and register `0x948`. `coex_sta_8723b_2ant` stores BT link flags, LPS/IPS state, RSSI hysteresis state, C2H history, retry count, and inquiry/page state. Hardware-visible state persists in MAC/BB/RF registers and firmware coexistence settings until rewritten, reset, IPS/halt paths, or adapter teardown.

## Dependencies and Integration Points

The file includes `Mp_Precomp.h` and relies on `HalBtcOutSrc.h` callback pointers for register IO, BB/RF access, H2C sending, and Wi-Fi state queries. It integrates with the adapter-facing `hal_btcoex.c` layer, firmware H2C commands `0x60` through `0x66` and `0x69`/`0x6e`, Realtek PTA registers such as `0x6c0`, `0x6c4`, `0x6c8`, `0x6cc`, antenna path registers `0x948`, `0x92c`, `0x4c`, and RF registers including `0x1`, `0x1e`, `0x3b`, `0x40`, `0xed`, and `0xef`.

## Risks and Edge Cases

The policy is highly stateful and global, so multiple adapters or unexpected concurrent notifications can corrupt assumptions. H2C and register constants are magic values with no local validation. BT register access depends on a partial H2C implementation in `hal_btcoex.c`, and `fBtcGetBtReg` is a stub. `EXhalbtc8723b2ant_BtInfoNotify` writes `length` bytes into fixed `[10]` C2H storage without a local length clamp. Several notify hooks for scan/connect/special packet are empty, so temporary traffic states may only affect policy through adapter-layer globals. Incorrect antenna path or firmware version detection can route Wi-Fi/BT to the wrong switch path.

## Test Signals

Useful signals are compile coverage for the staging driver, BT info C2H parsing tests with all profile bit combinations, regression tests for algorithm selection, H2C payload capture for PS-TDMA/DAC/channel-info commands, register trace checks for init/IPS/halt paths, concurrency or repeated-notification tests for previous/current state suppression, and real hardware coexistence validation for SCO, HID, A2DP, PAN(EDR), PAN(HS), inquiry/page, scan, LPS, and IPS scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b2Ant.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b2Ant.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b2Ant.h

## Purpose

`HalBtc8723b2Ant.h` declares the RTL8723B two-antenna coexistence status bits, algorithms, state structures, and notification entry points consumed by `HalBtc8723b2Ant.c` and dispatched through `hal_btcoex.c`. The file was read as a complete 146-line header.

## Important APIs, Types, and Functions

Important definitions include BT info bit masks such as `BT_INFO_8723B_2ANT_B_FTP`, `BT_INFO_8723B_2ANT_B_A2DP`, `BT_INFO_8723B_2ANT_B_HID`, `BT_INFO_8723B_2ANT_B_SCO_BUSY`, `BT_INFO_8723B_2ANT_B_ACL_BUSY`, `BT_INFO_8723B_2ANT_B_INQ_PAGE`, `BT_INFO_8723B_2ANT_B_SCO_ESCO`, and `BT_INFO_8723B_2ANT_B_CONNECTION`. It defines BT info sources, coarse BT statuses, coexistence algorithms, `struct coex_dm_8723b_2ant`, `struct coex_sta_8723b_2ant`, and all `EXhalbtc8723b2ant_*` prototypes.

## Control Flow

The header has no executable control flow. It defines the constants and state layout used by the implementation's event-driven control flow: power-on/init, IPS/LPS, media status, BT info, halt, PnP, and periodic notifications.

## State and Persistence Behavior

The state structs define in-memory persistence for previous/current coexistence decisions, PS-TDMA parameters, firmware/software mechanism states, last algorithm, BT status, Wi-Fi channel info, backup registers, profile flags, RSSI hysteresis, C2H history, retry count, and extended BT info. Actual instances are static in `HalBtc8723b2Ant.c`.

## Dependencies and Integration Points

The header assumes kernel/driver types and bit macros are already available via the precompiled include chain. It depends on `struct btc_coexist` from `HalBtcOutSrc.h`; inclusion ordering is provided by `Mp_Precomp.h`.

## Risks and Edge Cases

There is no include guard in this header, so repeated direct inclusion would rely on the current include pattern not to create conflicts. State array dimensions, especially `btInfoC2h[][10]`, must match parser behavior in the C file. Algorithm enum values are part of switch dispatch and debug interpretation, so reordering is risky.

## Test Signals

Compile coverage through `Mp_Precomp.h`, enum/switch exhaustiveness review against `HalBtc8723b2Ant.c`, static checks for include reuse, and tests that feed all BT info bit combinations through the parser are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b2Ant.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtcOutSrc.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtcOutSrc.h

## Purpose

`HalBtcOutSrc.h` is the shared Bluetooth coexistence abstraction header for the RTL8723BS HAL. It defines common coexistence constants, Wi-Fi/BT state query and set IDs, callback function pointer types, shared BT/coexistence state structures, and adapter-layer external APIs. The file was read as a complete 426-line header.

## Important APIs, Types, and Functions

Key macros include `NORMAL_EXEC`, `FORCE_EXEC`, RF path IDs, antenna-path IDs, Wi-Fi link-status bits, RSSI state helpers, and power/scan/media notification IDs. It defines `enum btc_chip_interface`, `struct btc_board_info`, `struct btc_bt_info`, `struct btc_stack_info`, `struct btc_bt_link_info`, `struct btc_statistics`, and central `struct btc_coexist`. The callback typedefs (`BFP_BTC_R1`, `BFP_BTC_W1`, `BFP_BTC_SET_BB_REG`, `BFP_BTC_GET_RF_REG`, `BFP_BTC_FILL_H2C`, `BFP_BTC_GET`, `BFP_BTC_SET`, and BT register callbacks) form the hardware/OS abstraction used by chip policy files. Exported APIs are `EXhalbtcoutsrc_*` functions and global `GLBtCoexist`.

## Control Flow

This header defines the dispatch contract but contains no runtime code. Runtime flow is implemented in `hal_btcoex.c`, which fills the function pointers, and in chip-specific modules, which call the callback table and receive translated notifications.

## State and Persistence Behavior

`struct btc_coexist` is the persistent in-memory context: it stores binding state, adapter pointer, board antenna data, BT metadata, profile/link info, interface type, lifecycle flags, statistics counters, last power-mode command bytes, and callback pointers. The header also defines smaller state containers for BT firmware/control state and stack profile state.

## Dependencies and Integration Points

It integrates the coexistence code with the broader rtl8723bs driver through adapter callbacks, firmware H2C sending, BB/RF accessors, raw register IO, LPS/IPS state, scan/media/connect notifications, and antenna configuration. It assumes Realtek driver enums such as `SINGLEMAC_SINGLEPHY`, `DUALMAC_DUALPHY`, `enum rt_media_status`, `BIT*`, `u8`, `u16`, and `u32`.

## Risks and Edge Cases

Many `BTC_GET_*` and `BTC_SET_*` values are untyped IDs whose payload type must match caller expectation. Incorrect callback initialization can turn chip policy actions into null dereferences. Global `GLBtCoexist` creates singleton behavior. The header contains a duplicate `enum {` line before scan notification constants, which is accepted only if the surrounding source as included remains syntactically valid in this tree; it is a fragile area for refactoring.

## Test Signals

Compile with all coexistence users enabled, callback initialization checks in `hal_btcoex_Initialize`, smoke tests for every `BTC_GET_*` and `BTC_SET_*` case, and notification routing tests for 1-antenna versus 2-antenna board settings provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtcOutSrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_BB.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_BB.c

## Purpose

`HalHWImg8723B_BB.c` embeds generated 8723B baseband hardware image data for AGC, PHY registers, and PHY power-group programming, then exposes loader functions that write those tables into the ODM/HAL configuration layer. The file was read as a complete 556-line source.

## Important APIs, Types, and Functions

The main functions are `ODM_ReadAndConfig_MP_8723B_AGC_TAB`, `ODM_ReadAndConfig_MP_8723B_PHY_REG`, `ODM_ReadAndConfig_MP_8723B_PHY_REG_PG`, and version getter `ODM_GetVersion_MP_8723B_PHY_REG_PG`. Static arrays are `Array_MP_8723B_AGC_TAB`, `Array_MP_8723B_PHY_REG`, and `Array_MP_8723B_PHY_REG_PG`. `CheckPositive` evaluates generated branch conditions against `struct dm_odm_t` cut, platform, package, interface, board type, and external PA/LNA type.

## Control Flow

The AGC and PHY loaders iterate table pairs. Values below `0x40000000` are direct `(offset, data)` writes through `odm_ConfigBB_AGC_8723B` or `odm_ConfigBB_PHY_8723B`. Values above that range start generated conditional blocks: the loader checks `COND_ELSE`/`COND_ENDIF`, calls `CheckPositive`, skips unmatched pairs, or writes matched branch pairs until the end marker. The PHY_REG_PG loader processes fixed groups of four values and writes them through `odm_ConfigBB_PHY_REG_PG_8723B` after setting version and value-type fields.

## State and Persistence Behavior

The source owns static read-only configuration arrays. Runtime persistence is hardware state programmed into BB/AGC registers and ODM metadata fields `PhyRegPgVersion` and `PhyRegPgValueType`; the arrays themselves are immutable.

## Dependencies and Integration Points

It includes `<linux/kernel.h>` and `odm_precomp.h`, uses macros such as `ARRAY_SIZE`, `READ_NEXT_PAIR`, `COND_ELSE`, `COND_ENDIF`, and ODM config hooks for BB AGC, PHY, and PHY_REG_PG. It is part of hardware initialization before RF calibration and normal radio operation.

## Risks and Edge Cases

Generated conditional parsing is index-sensitive; malformed arrays can skip incorrectly or read unintended pairs. `CheckPositive` duplicates logic also present in MAC/RF image files, so fixes can drift. Table constants are hardware/board specific and hard to validate without device traces. PHY_REG_PG writes regulatory/power values that can affect compliance and range.

## Test Signals

Build coverage, boot-time register-write trace comparison against vendor tables, board-variant tests for `CheckPositive`, validation that branch markers never overrun arrays, and RF/throughput smoke tests after AGC/PHY loading are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_BB.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_BB.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_BB.h

## Purpose

`HalHWImg8723B_BB.h` declares the RTL8723B baseband hardware image loader functions for AGC, PHY register, and PHY_REG_PG tables. The file was read as a complete 39-line header.

## Important APIs, Types, and Functions

It declares `ODM_ReadAndConfig_MP_8723B_AGC_TAB`, `ODM_ReadAndConfig_MP_8723B_PHY_REG`, `ODM_ReadAndConfig_MP_8723B_PHY_REG_PG`, and `ODM_GetVersion_MP_8723B_PHY_REG_PG`.

## Control Flow

There is no executable flow. The declared loaders are called by the HAL/ODM initialization sequence to program embedded hardware image tables.

## State and Persistence Behavior

The header owns no storage. It exposes functions that program persistent hardware register state and ODM PHY_REG_PG metadata in the corresponding C file.

## Dependencies and Integration Points

It depends on `struct dm_odm_t` from the ODM precompiled include chain. Integration is with the rtl8723bs PHY initialization path and any code that queries the generated PHY_REG_PG version.

## Risks and Edge Cases

Prototype drift from the implementation or missing ODM type declarations will break hardware initialization. Since these functions program hardware tables, accidental omission from init order can leave BB defaults incorrect.

## Test Signals

Compile coverage, include-order tests through `odm_precomp.h`, and initialization traces showing all declared loaders are invoked are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_BB.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_MAC.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_MAC.c

## Purpose

`HalHWImg8723B_MAC.c` embeds and loads the generated RTL8723B MAC register initialization table. The file was read as a complete 237-line source.

## Important APIs, Types, and Functions

The main API is `ODM_ReadAndConfig_MP_8723B_MAC_REG`. Static state includes `Array_MP_8723B_MAC_REG`, and helper `CheckPositive` matches generated conditions against `struct dm_odm_t` board/cut/platform/package/interface fields.

## Control Flow

The loader walks `(offset, data)` pairs. Direct entries call `odm_ConfigMAC_8723B(pDM_Odm, offset, (u8)data)`. Conditional markers trigger the same generated IF/ELSE/ENDIF mini-parser used by the BB and RF image files: evaluate `CheckPositive`, skip unmatched entries, and configure matched entries until the branch ends.

## State and Persistence Behavior

The table is static and immutable. Runtime persistence is the programmed MAC register state, including coexistence-related defaults such as `0x765` and `0x76e` values near the end of the table.

## Dependencies and Integration Points

It includes `<linux/kernel.h>` and `odm_precomp.h`, uses `READ_NEXT_PAIR`, condition macros, and `odm_ConfigMAC_8723B`. It is part of chip initialization before normal firmware/HAL operation.

## Risks and Edge Cases

All writes are byte writes, so values must remain in the expected width. Conditional parser bugs or board metadata mistakes can silently skip critical MAC settings. The duplicated `CheckPositive` implementation can diverge from BB/RF image loaders.

## Test Signals

Compile coverage, register-write trace comparison, board-variant conditional tests, and device bring-up tests that verify MAC register defaults, beacon/control behavior, and coexistence baseline registers are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_MAC.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_MAC.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_MAC.h

## Purpose

`HalHWImg8723B_MAC.h` declares the RTL8723B MAC hardware image loader. The file was read as a complete 20-line header.

## Important APIs, Types, and Functions

It declares `ODM_ReadAndConfig_MP_8723B_MAC_REG(struct dm_odm_t *pDM_Odm)`.

## Control Flow

There is no executable control flow. The implementation is invoked by the HAL initialization sequence.

## State and Persistence Behavior

The header has no state. The declared function writes persistent MAC register state through the ODM/HAL layer.

## Dependencies and Integration Points

It depends on `struct dm_odm_t` from `odm_precomp.h` and integrates with the 8723B MAC initialization path.

## Risks and Edge Cases

The narrow header is low risk, but missing or mismatched inclusion prevents MAC image loading. Since the function is table-driven, init-order bugs are the main integration risk.

## Test Signals

Compile coverage and boot traces showing `ODM_ReadAndConfig_MP_8723B_MAC_REG` executes before later MAC/coexistence operations are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_MAC.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_RF.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_RF.c

## Purpose

`HalHWImg8723B_RF.c` embeds generated RTL8723B RF initialization data, SDIO thermal power-tracking delta swing tables, and TX power limit regulatory tables. The file was read as a complete 555-line source.

## Important APIs, Types, and Functions

Public functions are `ODM_ReadAndConfig_MP_8723B_RadioA`, `ODM_ReadAndConfig_MP_8723B_TxPowerTrack_SDIO`, `ODM_GetVersion_MP_8723B_TxPowerTrack_SDIO`, `ODM_ReadAndConfig_MP_8723B_TXPWR_LMT`, and `ODM_GetVersion_MP_8723B_TXPWR_LMT`. Static data includes `Array_MP_8723B_RadioA`, eight `gDeltaSwingTableIdx_MP_*_TxPowerTrack_SDIO_8723B` arrays, and string tuple table `Array_MP_8723B_TXPWR_LMT`. `CheckPositive` matches generated RF conditions.

## Control Flow

`ODM_ReadAndConfig_MP_8723B_RadioA` uses the generated pair interpreter to call `odm_ConfigRF_RadioA_8723B` for direct or conditionally selected entries. `ODM_ReadAndConfig_MP_8723B_TxPowerTrack_SDIO` copies embedded positive/negative delta swing tables for 2.4 GHz CCK/OFDM, path A/B, into `pDM_Odm->RFCalibrateInfo`. `ODM_ReadAndConfig_MP_8723B_TXPWR_LMT` iterates six-string tuples `(regulation, bandwidth, rate, rfPath, channel, value)` and passes them to `odm_ConfigBB_TXPWR_LMT_8723B`.

## State and Persistence Behavior

Static arrays are immutable. RadioA loading persists in RF registers. TxPowerTrack loading persists in `RFCalibrateInfo` arrays used later by `GetDeltaSwingTable_8723B` and thermal power tracking. TX power limits persist in ODM regulatory power-limit data structures populated by the config callback.

## Dependencies and Integration Points

It includes `<linux/kernel.h>` and `odm_precomp.h`; uses ODM RF/BB config callbacks, `DELTA_SWINGIDX_SIZE`, generated branch macros, and `memcpy`. It feeds `HalPhyRf.c`/`HalPhyRf_8723B.c` thermal tracking and the transmit power configuration path.

## Risks and Edge Cases

Regulatory string tables are compliance-sensitive. A tuple ordering or width mistake can misconfigure channel limits. Delta swing table sizes must match destination arrays. Conditional RF register programming is board-specific and hard to validate without hardware. Fallback behavior in calibration uses 8188E tables if channel is outside 2.4 GHz, so missing load can change thermal response.

## Test Signals

Compile coverage, RF register traces against vendor images, checksum or count checks for delta swing copies, regulatory power-limit table validation by channel/rate/bandwidth/regulation, and thermal tracking tests that confirm copied tables are selected at runtime are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_RF.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_RF.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_RF.h

## Purpose

`HalHWImg8723B_RF.h` declares the RTL8723B RF hardware image, SDIO power-tracking table, and TX power limit loaders. The file was read as a complete 41-line header.

## Important APIs, Types, and Functions

It declares `ODM_ReadAndConfig_MP_8723B_RadioA`, `ODM_ReadAndConfig_MP_8723B_TxPowerTrack_SDIO`, `ODM_GetVersion_MP_8723B_TxPowerTrack_SDIO`, `ODM_ReadAndConfig_MP_8723B_TXPWR_LMT`, and `ODM_GetVersion_MP_8723B_TXPWR_LMT`.

## Control Flow

The header has no runtime flow. It exposes table loaders used during RF/PHY initialization and calibration setup.

## State and Persistence Behavior

No storage is owned here. The declared functions program RF registers, RF calibration delta swing state, and ODM TX power-limit data.

## Dependencies and Integration Points

It depends on `struct dm_odm_t` and integrates with ODM initialization and 8723B RF calibration/power tracking.

## Risks and Edge Cases

Prototype drift or missing calls can leave RF, power tracking, or regulatory limits uninitialized. Version getters are useful for validating generated table revisions; if callers ignore them, table drift may be invisible.

## Test Signals

Compile coverage, init-sequence tests that call all declared loaders, and version getter checks are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_RF.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf.c

## Purpose

`HalPhyRf.c` provides generic ODM RF power-tracking glue for rtl8723bs and delegates chip-specific behavior to the 8723B calibration implementation. The file was read as a complete 273-line source.

## Important APIs, Types, and Functions

Public functions are `ConfigureTxpowerTrack`, `ODM_ClearTxPowerTrackingState`, and `ODM_TXPowerTrackingCallback_ThermalMeter`. `ConfigureTxpowerTrack` delegates to `ConfigureTxpowerTrack_8723B`. `ODM_ClearTxPowerTrackingState` resets swing indexes, delta/remnant power indexes, modify flags, and thermal baselines. `ODM_TXPowerTrackingCallback_ThermalMeter` is the main thermal watchdog callback.

## Control Flow

The thermal callback obtains the 8723B `txpwrtrack_cfg`, gets delta swing table pointers, reads RF thermal meter register `c.ThermalRegAddr`, exits if tracking is disabled or EEPROM thermal meter is invalid, updates a rolling average, computes deltas against previous thermal/LCK values, triggers LC calibration if threshold is crossed, maps thermal delta to path-specific positive/negative power index changes, clamps OFDM/CCK indexes, calls the chip-specific set-power function in `MIX_MODE`, updates base swing indexes, records the new thermal value, and resets `TXPowercount`.

## State and Persistence Behavior

The file mutates `pDM_Odm->RFCalibrateInfo`, including thermal history, average buffer/index, callback counters, delta power indexes, power offsets, OFDM/CCK indexes, Tx power changed flags, and LCK/IQK baselines. It also updates `BbSwingIdx*`, remnant swing indexes, and TxAGC modify flags. Persistent effects occur through chip-specific callbacks that write BB/RF/Tx power state.

## Dependencies and Integration Points

It includes `odm_precomp.h` and depends on `hal_com_data`, `struct dm_odm_t`, `struct txpwrtrack_cfg`, `PHY_QueryRFReg`, `PHY_SetTxPowerIndexByRateSection`, 8723B config callbacks, swing table constants, and ODM RF calibration state. It is usually driven by periodic dynamic mechanism/watchdog logic.

## Risks and Edge Cases

Several values are unsigned while negative offsets are represented through assignments to `u8`-like state in surrounding structures, so boundary behavior depends on struct field types. The callback assumes delta swing tables were populated by RF image loading. Invalid EEPROM thermal values disable tracking entirely. Only path A and optional path B are considered through `RfPathCount`; wrong path count or table size can miscalibrate power.

## Test Signals

Unit-style thermal delta tests, hardware traces for Tx power index updates, LCK trigger tests at threshold, checks that `ODM_ClearTxPowerTrackingState` is called after TxAGC changes, and watchdog tests with invalid EEPROM thermal values are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf.h

## Purpose

`HalPhyRf.h` defines the generic RF power-tracking method enum, callback signatures, configuration structure, and public ODM RF tracking APIs. The file was read as a complete 40-line header.

## Important APIs, Types, and Functions

It defines `enum pwrtrack_method` with `BBSWING`, `TXAGC`, and `MIX_MODE`; callback typedefs `FuncSetPwr`, `FuncLCK`, and `FuncSwing`; `struct txpwrtrack_cfg`; and prototypes for `ConfigureTxpowerTrack`, `ODM_ClearTxPowerTrackingState`, and `ODM_TXPowerTrackingCallback_ThermalMeter`.

## Control Flow

There is no executable flow. The structure is filled by chip-specific code and consumed by the generic thermal callback to invoke set-power, LC calibration, and delta swing table selection.

## State and Persistence Behavior

The header owns no storage. It defines a transient configuration object whose function pointers bridge generic tracking to chip-specific implementations.

## Dependencies and Integration Points

It depends on `struct dm_odm_t`, `struct adapter`, and Realtek integer types from the include chain. It integrates `HalPhyRf.c` with `HalPhyRf_8723B.c`.

## Risks and Edge Cases

Function pointer contracts are not type-safe beyond the typedefs; wrong `RfPathCount`, table sizes, or callback assignment can corrupt thermal tracking. Additions to `enum pwrtrack_method` require switch updates in chip-specific handlers.

## Test Signals

Compile coverage, tests that `ConfigureTxpowerTrack_8723B` fills every callback/size field, and thermal callback tests exercising all three power tracking methods are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf_8723B.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf_8723B.c

## Purpose

`HalPhyRf_8723B.c` implements RTL8723B-specific Tx power tracking, IQ calibration (IQK), LC calibration (LCK), and IQC restore/application logic. The file was read as a complete 1796-line source.

## Important APIs, Types, and Functions

Public APIs are `ODM_TxPwrTrackSetPwr_8723B`, `ConfigureTxpowerTrack_8723B`, `ODM_SetIQCbyRFpath`, `PHY_IQCalibrate_8723B`, and `PHY_LCCalibrate_8723B`. Important internals include `setIqkMatrix_8723B`, `setCCKFilterCoefficient`, `GetDeltaSwingTable_8723B`, path calibration helpers `phy_PathA_IQK_8723B`, `phy_PathA_RxIQK8723B`, `phy_PathB_IQK_8723B`, `phy_PathB_RxIQK8723B`, matrix fillers `_PHY_PathAFillIQKMatrix8723B` and `_PHY_PathBFillIQKMatrix8723B`, save/reload helpers for ADDA/MAC/BB registers, `phy_SimularityCompare_8723B`, `phy_IQCalibrate_8723B`, and `phy_LCCalibrate_8723B`.

## Control Flow

Power tracking chooses limits based on current or forced data rate, then applies TXAGC, BBSWING, or MIX_MODE. MIX_MODE uses BB swing until limits are exceeded, then records remnant OFDM/CCK indexes and refreshes Tx power index sections. IQK checks calibration ability and in-progress flags, optionally restores saved IQC/LOK data, otherwise performs up to three calibration candidates, each saving/restoring MAC/BB/ADDA state, programming IQK tones and RF modes, switching antenna paths/GNT_BT, running one-shot TX/RX IQK for path A and optionally path B, validating result registers, comparing candidate similarity, filling IQC matrices, saving recoverable backup registers, restoring GNT_BT and RF mode, and applying IQC for the selected RF path in 2-antenna mode. LCK waits for scans to finish, marks LCK in progress, pauses traffic or continuous TX, toggles RF LC calibration bit, handles an SDIO/package-specific channel 10 workaround, and restores traffic/RF state.

## State and Persistence Behavior

The code mutates `pDM_Odm->RFCalibrateInfo`: IQK in-progress flags, LCK in-progress flags, LOK values, IQC register/value arrays, IQK result registers, backup/recover arrays, thermal power tracking indexes, remnant swing indexes, and TxAGC modify flags. It writes persistent BB/RF/MAC hardware state for IQ imbalance, CCK coefficients, RF modes, PA/LNA calibration modes, TX power indexes, queue pause state, and LC calibration state.

## Dependencies and Integration Points

It includes `<drv_types.h>` and `odm_precomp.h`, and depends on `HalPhyRf.h`, generated RF power tracking tables from `HalHWImg8723B_RF.c`, ODM register constants, `PHY_SetBBReg`, `PHY_QueryBBReg`, `PHY_SetRFReg`, `PHY_QueryRFReg`, `PHY_SetTxPowerIndexByRateSection`, `rtw_read8`, `rtw_write8`, `rtw_write32`, `mdelay`, rate macros, and swing tables.

## Risks and Edge Cases

Calibration is timing- and hardware-state-sensitive. Early returns in `PHY_IQCalibrate_8723B` after successful restore leave `bIQKInProgress` set because the flag is set before the restore block and not cleared on that return path. `ODM_CheckPowerStatus` always returns true, so callers do not get real power-state protection. Many register constants assume 8723B path mapping and can disrupt BT coexistence if interrupted. Candidate selection uses register similarity heuristics; failed candidates fall back to defaults and may degrade RF quality. LCK blocks in 50 ms increments up to 2 seconds while scan is in progress.

## Test Signals

Hardware IQK/LCK result traces, tests for restore/recovery paths, checks that in-progress flags clear after every exit path, Tx power tracking tests for CCK/OFDM/HT rates, scan/LCK interaction tests, and RF throughput/EVM/regulatory validation after calibration are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf_8723B.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf_8723B.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf_8723B.h

## Purpose

`HalPhyRf_8723B.h` declares RTL8723B-specific RF calibration and Tx power tracking APIs and calibration constants. The file was read as a complete 68-line header.

## Important APIs, Types, and Functions

Constants include `IQK_DELAY_TIME_8723B`, `IQK_DEFERRED_TIME_8723B`, `index_mapping_NUM_8723B`, `AVG_THERMAL_NUM_8723B`, and `RF_T_METER_8723B`. It declares `ConfigureTxpowerTrack_8723B`, `ODM_TxPwrTrackSetPwr_8723B`, `PHY_IQCalibrate_8723B`, `ODM_SetIQCbyRFpath`, `PHY_LCCalibrate_8723B`, `PHY_DigitalPredistortion_8723B`, and several underscored calibration helper prototypes.

## Control Flow

No executable flow is present. The declarations are consumed by the generic RF tracking file and the wider PHY/HAL code to trigger 8723B-specific tracking and calibration flows.

## State and Persistence Behavior

The header owns no state. Declared functions mutate ODM RF calibration state and hardware registers in the implementation.

## Dependencies and Integration Points

It depends on `struct txpwrtrack_cfg`, `struct dm_odm_t`, and `struct adapter` from surrounding headers. It integrates `HalPhyRf.c` with the 8723B implementation and exposes calibration hooks to other HAL code.

## Risks and Edge Cases

Several underscored helper prototypes do not match the static helper names/visibility in the implementation (`_8723B` suffix differences and static definitions), indicating stale declarations or unused legacy API surface. `PHY_DigitalPredistortion_8723B` is declared here but not implemented in the researched C file, so link coverage depends on other build exclusions or dead declarations.

## Test Signals

Compile/link coverage, symbol reachability checks for declared calibration helpers, and direct tests for public calibration functions are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf_8723B.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPwrSeqCmd.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPwrSeqCmd.c

## Purpose

`HalPwrSeqCmd.c` implements the Realtek hardware power-sequence command parser for RTL8723/RTL8188E-series devices. It interprets `struct wlan_pwr_cfg` arrays and performs register reads/writes, polling, delays, and termination. The file was read as a complete 145-line source.

## Important APIs, Types, and Functions

The only public function is `HalPwrSeqCmdParsing(struct adapter *padapter, u8 CutVersion, u8 FabVersion, u8 InterfaceType, struct wlan_pwr_cfg PwrSeqCmd[])`. It uses macros from `HalPwrSeqCmd.h`, including `GET_PWR_CFG_FAB_MASK`, `GET_PWR_CFG_CUT_MASK`, `GET_PWR_CFG_INTF_MASK`, `GET_PWR_CFG_CMD`, `GET_PWR_CFG_BASE`, `GET_PWR_CFG_OFFSET`, `GET_PWR_CFG_MASK`, and `GET_PWR_CFG_VALUE`.

## Control Flow

The parser loops over commands until `PWR_CMD_END`. It first filters each command by FAB, CUT, and interface masks. `PWR_CMD_WRITE` reads a byte from SDIO local or system register space, applies a mask/value update, and writes it back. `PWR_CMD_POLLING` repeatedly reads until the masked value matches the expected value or `pollingCount` exceeds 5000, delaying 10 microseconds between failed checks. `PWR_CMD_DELAY` delays in microseconds or milliseconds depending on the command value. `PWR_CMD_READ` is a no-op.

## State and Persistence Behavior

No file-local state is retained. Persistent effects are direct writes to SDIO local registers or system registers, and time spent polling/delaying during power transitions.

## Dependencies and Integration Points

It includes `<drv_types.h>` and `<HalPwrSeqCmd.h>`, and integrates with adapter register IO through `SdioLocalCmd52Read1Byte`, `SdioLocalCmd52Write1Byte`, `rtw_read8`, `rtw_write8`, `udelay`, and generated power sequence arrays.

## Risks and Edge Cases

The loop trusts the command array to contain `PWR_CMD_END`; malformed arrays can run indefinitely through memory. `pollingCount` is not reset per polling command, so multiple polling commands share the 5000 count budget. Millisecond delays are implemented as `udelay(offset * 1000)`, which can busy-wait for long delays. `PWR_CMD_READ` does nothing, so read commands only serve as placeholders unless callers expect side effects elsewhere.

## Test Signals

Unit tests with synthetic power arrays, timeout tests for polling mismatch, SDIO versus normal register write tests, command-filter tests for cut/fab/interface masks, and suspend/resume or power-on hardware traces are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPwrSeqCmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/Mp_Precomp.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/Mp_Precomp.h

## Purpose

`Mp_Precomp.h` is the small include aggregator used by Bluetooth coexistence implementation files in the rtl8723bs HAL. The file was read as a complete 23-line header.

## Important APIs, Types, and Functions

It includes `<drv_types.h>`, `<hal_data.h>`, defines `BT_TMP_BUF_SIZE` as `100`, undefines `bEnable` if already defined, and includes `HalBtcOutSrc.h`, `HalBtc8723b1Ant.h`, and `HalBtc8723b2Ant.h`.

## Control Flow

There is no runtime flow. It controls compile-time include ordering for coexistence modules.

## State and Persistence Behavior

The header owns no runtime state. It makes shared coexistence types and chip-specific declarations available to C files.

## Dependencies and Integration Points

It sits between general driver/HAL headers and BT coexistence headers. `HalBtc8723b2Ant.c` includes it directly, and `hal_btcoex.c` includes it via angle brackets.

## Risks and Edge Cases

The `bEnable` undef is a broad preprocessor side effect. Include aggregation can hide missing direct dependencies in chip-specific headers. Changes here affect both 1-antenna and 2-antenna coexistence compilation.

## Test Signals

Compile coverage for all coexistence files, preprocessor/include-order checks, and ensuring both `HalBtc8723b1Ant.h` and `HalBtc8723b2Ant.h` remain compatible through this aggregator are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/Mp_Precomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_btcoex.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_btcoex.c

## Purpose

`hal_btcoex.c` is the adapter-facing Bluetooth coexistence glue for rtl8723bs. It owns the global coexistence context, binds it to an adapter, implements the callback table expected by chip-specific coexistence code, translates driver notifications into coexistence events, and exposes wrapper APIs used by the wider HAL. The file was read as a complete 1333-line source.

## Important APIs, Types, and Functions

Global state is `struct btc_coexist GLBtCoexist`, plus scan/IQK globals `GLBtcWiFiInScanState` and `GLBtcWiFiInIQKState`. Initialization and binding are handled by `hal_btcoex_Initialize` and `EXhalbtcoutsrc_BindBtCoexWithAdapter`. Callback implementations include `halbtcoutsrc_Get`, `halbtcoutsrc_Set`, raw register accessors, BB/RF accessors, BT register H2C write, and H2C fill. External dispatchers include `EXhalbtcoutsrc_PowerOnSetting`, `EXhalbtcoutsrc_InitHwConfig`, `EXhalbtcoutsrc_InitCoexDm`, IPS/LPS/scan/connect/media/special-packet/BT-info/halt/PnP/periodical notification functions, antenna setters, and public `hal_btcoex_*` wrappers.

## Control Flow

`hal_btcoex_Initialize` clears the global context, sets SDIO interface type, binds the adapter, and installs callback pointers. Public `hal_btcoex_*` wrappers call `EXhalbtcoutsrc_*`, which validate binding/manual-control state, update statistics and global scan state, translate driver enums into BTC enums, and dispatch to either 2-antenna or 1-antenna chip-specific handlers based on `boardInfo.btdmAntNum`. `halbtcoutsrc_Get` answers chip policy queries from mlme, security, firmware version, bandwidth, traffic counters, RSSI, channel, AP count, and power mode. `halbtcoutsrc_Set` updates BT/coex flags or triggers actions such as LPS enter/leave, low-power disable, aggregation control, or RA mask refresh. IO callbacks perform register, BB/RF, local SDIO, and H2C accesses.

## State and Persistence Behavior

The file uses singleton global state for adapter binding, board antenna info, BT flags, statistics counters, power mode command bytes, callback table, scan state, and IQK state. Hardware-visible persistence comes from register writes, BB/RF writes, H2C commands, LPS/low-power control calls, aggregation rejection toggles, and RA mask updates. `hal_btcoex_HaltNotify` unbinds the global context via the chip-specific halt path.

## Dependencies and Integration Points

It includes `<hal_data.h>`, `<hal_btcoex.h>`, and `<Mp_Precomp.h>`. It integrates with mlme state (`check_fwstate`, `WIFI_ASOC_STATE`, `WIFI_AP_STATE`, `WIFI_UNDER_LINKING`), power management (`rtw_btcoex_LPS_Enter`, `rtw_btcoex_LPS_Leave`, `rtw_register_task_alive`, `rtw_unregister_task_alive`), register IO (`rtw_read8/16/32`, `rtw_write8/16/32`), PHY helpers (`PHY_SetBBReg`, `PHY_QueryBBReg`, `PHY_SetRFReg`, `PHY_QueryRFReg`), firmware H2C (`rtw_hal_fill_h2c_cmd`), station/RA mask helpers, and chip-specific `EXhalbtc8723b1ant_*`/`EXhalbtc8723b2ant_*` modules.

## Risks and Edge Cases

Global singleton state prevents safe multi-adapter coexistence. Many callbacks assume `pBtcContext`, adapter, and output pointers are valid. Several get/set cases return false or are stubs, including HS operation/RSSI, MP mode, MIMO PS, BT info control, BT coexist control, antenna control, and `halbtcoutsrc_GetBtReg`. `halbtcoutsrc_SetBtReg` writes only low bytes through two H2C commands with a 200 ms sleep and ignores `RegType`. `hal_btcoex_RecordPwrMode` copies `cmdLen` bytes into a 10-byte array without a local clamp. Scan state is tracked by a global rather than firmware state to avoid stale flags, but this still depends on balanced notifications.

## Test Signals

Callback table initialization tests, wrapper dispatch tests for one-antenna/two-antenna board settings, `BTC_GET`/`BTC_SET` payload tests, register/H2C trace tests, LPS/low-power interaction tests, scan/IQK gating tests for BT info notification, bounds tests for power mode recording, and multi-adapter negative tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_btcoex.c -->
