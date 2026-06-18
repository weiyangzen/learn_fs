# subset-b-005428 Research

Grouped source research for the RTL8723BS staging driver's HAL common layer, SDIO glue, power sequences, ODM dynamic-management core, PHY status parsing, register configuration, and firmware H2C command path. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_com.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_com.c

## Purpose

`hal_com.c` provides common HAL utilities shared by the RTL8723BS SDIO-specific layer: HAL data allocation, channel-plan selection, rate-code conversion, USB/SDIO queue-to-pipe mapping, C2H event reading, station rate-mask setup, generic hardware/ODM variable access, and RF gain-offset programming. The source was read as a complete 819-line file.

## Important APIs, Types, and Functions

Important entry points are `rtw_hal_data_init`, `rtw_hal_data_deinit`, `dump_chip_info`, `hal_com_config_channel_plan`, `HAL_IsLegalChannel`, `MRateToHwRate`, `HwRateToMRate`, `HalSetBrateCfg`, `Hal_MappingOutPipe`, `hal_init_macaddr`, `rtw_init_hal_com_default_value`, `c2h_evt_clear`, `c2h_evt_read_88xx`, `rtw_get_mgntframe_raid`, `rtw_hal_update_sta_rate_mask`, `SetHwReg`, `GetHwReg`, `GetHalDefVar`, `SetHalODMVar`, `GetU1ByteIntegerFromStringInDecimal`, `rtw_hal_check_rxfifo_full`, and `rtw_bb_rf_gain_offset`. The file manipulates `struct hal_com_data`, `struct dm_odm_t`, `struct sta_info`, `struct dvobj_priv`, `struct mlme_priv`, and `struct security_priv`.

## Control Flow

Initialization allocates `adapter->HalData`, seeds defaults, sets the MAC address through the chip-specific hardware register path, and later deallocates the same storage. Channel plan selection chooses default, EFUSE, or software configuration while honoring the EFUSE "disable software channel plan" bit. Rate helpers translate between driver `MGN_*` rates, descriptor `DESC_RATE*` values, and basic-rate bitmaps. Pipe mapping writes all WMM queues into `dvobj_priv->Queue2Pipe` according to one-, two-, or three-output-pipe layouts. C2H handling checks `REG_C2HEVT_CLEAR`, reads the C2H header and payload registers only when firmware owns a valid event, then clears the latch for the next event.

## State and Persistence Behavior

The main persistent state is adapter-scoped memory in `HalData`, including `BasicRateSet`, debug packet-dump flags, antenna detection, ODM support flags, and RF gain settings derived from EEPROM. `SetHwReg` mutates security hardware bits in `REG_SECCFG` and ODM ability masks. `SetHalODMVar` attaches or detaches station pointers from `dm_odm_t->pODM_StaInfo`, so station lifetime and MAC ID correctness matter. No file-backed persistence exists; hardware register state and adapter fields live for the device session.

## Dependencies and Integration Points

The file depends on the Realtek driver core (`drv_types.h`), H2C/C2H definitions, ODM precompiled headers, register accessors (`rtw_read*`, `rtw_write*`), rate helpers, EFUSE/channel-plan helpers, station lookup, and PHY RF access (`PHY_SetRFReg`). It is called by `hal_intf.c`, chip-specific `SetHwReg8723BS`/`GetHalDefVar8723BSDIO` wrappers, MLME code, security setup, and ODM station bookkeeping.

## Risks and Edge Cases

`dump_chip_info` builds a buffer but does not emit it in this snapshot, so it may be dead or incomplete diagnostic code. `SetHwReg(HW_VAR_SEC_DK_CFG)` treats `val` as a boolean pointer by testing pointer presence rather than dereferenced contents. `GetU1ByteIntegerFromStringInDecimal` can wrap a `u8` on large decimal strings. C2H payload length is trusted against a fixed 16-byte local layout. Queue mapping assumes `RtOutPipe` entries were populated correctly. `rtw_bb_rf_gain_offset` only programs path A and silently ignores unknown EEPROM gain codes.

## Test Signals

Useful signals include HAL allocation/deallocation smoke tests, channel-plan precedence tests for EFUSE/software/default/autoload-fail combinations, rate round-trip tests for all CCK/OFDM/MCS0-7 rates, C2H register emulation covering not-ready/invalid/valid events, security register bit tests, station attach/detach ODM pointer tests, and RF gain-offset tests with EEPROM values that map and do not map through `Array_kfreemap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_com.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_com_phycfg.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_com_phycfg.c

## Purpose

`hal_com_phycfg.c` owns common PHY transmit-power configuration for RTL8723BS. It parses power-by-rate register-page values, stores exact or relative per-rate offsets, derives base power by rate section, applies channel/bandwidth/rate/RF-path TX power indices, manages regulatory TX power limits, and maps channel plans into 2.4 GHz regulatory domains. The source was read as a complete 988-line file.

## Important APIs, Types, and Functions

Key APIs include `PHY_GetTxPowerByRateBase`, `PHY_InitTxPowerByRate`, `PHY_StoreTxPowerByRate`, `PHY_TxPowerByRateConfiguration`, `PHY_SetTxPowerIndexByRateSection`, `PHY_GetTxPowerIndexBase`, `PHY_GetTxPowerTrackingOffset`, `PHY_GetRateIndexOfTxPowerByRate`, `PHY_GetTxPowerByRate`, `PHY_SetTxPowerByRate`, `PHY_SetTxPowerLevelByPath`, `PHY_SetTxPowerIndexByRateArray`, `phy_get_tx_pwr_lmt`, `PHY_ConvertTxPowerLimitToPowerIndex`, `PHY_InitTxPowerLimit`, `PHY_SetTxPowerLimit`, and `Hal_ChannelPlanToRegulation`. It uses `struct hal_com_data` arrays such as `TxPwrByRateBase2_4G`, `TxPwrByRateOffset`, `MCSTxPowerLevelOriginalOffset`, and `TxPwrLimit_2_4G`.

## Control Flow

PHY register-page data enters through `PHY_StoreTxPowerByRate`. New-format pages (`PhyRegPgVersion > 0`) decode register/mask/value triples into per-rate offsets; old-format pages store raw section values. When the source table uses exact dBm values, `PHY_TxPowerByRateConfiguration` stores section bases and converts each rate to a relative offset. Runtime TX power setting asks for each rate section, calculates base power for the current channel/bandwidth, adds OFDM/BW diffs and thermal tracking offset, clips through regulatory limits, then writes the per-rate hardware TX index through chip-specific PHY helpers.

## State and Persistence Behavior

All state persists in `hal_com_data` for the active adapter: per-rate offsets, section bases, base channel power tables, regulatory limit tables, `Regulation2_4G`, and ODM PHY register-page metadata. Registry flags can disable power-by-rate or power-limit enforcement, and EEPROM regulatory values select default behavior. There is no disk persistence; values are rebuilt from EFUSE, registry options, and header-table configuration during device initialization.

## Dependencies and Integration Points

The file depends on rate constants, BB register addresses, channel width enums, regulatory domain constants, `HAL_IsLegalChannel`, `PHY_GetTxPowerIndex`, `PHY_SetTxPowerIndex`, ODM metadata, registry private fields, and the Realtek hardware image parser that calls `PHY_StoreTxPowerByRate` and `PHY_SetTxPowerLimit`. It is integrated by `odm_RegConfig8723B.c` for table-driven PHY configuration and by channel-change code when programming TX power for a channel.

## Risks and Edge Cases

Several paths assume valid 2.4 GHz channels and compute `Channel - 1`; invalid channel handling is inconsistent (`PHY_GetTxPowerIndexBase` resets to channel 1, while `phy_get_tx_pwr_lmt` assigns a converted channel into a variable named `channel` and leaves `idx_channel` initialized to `-1`, making the validity check suspect). String parsing for limits ignores conversion failures. Power-limit arrays are one-path oriented but loops include all `MAX_RF_PATH_NUM`. Regulatory aliases map several world/ETSI domains to FCC, which is intentional in this vendor driver but high risk if regulatory behavior is audited.

## Test Signals

Test coverage should include register-page decode tests for each TXAGC register/mask case, exact-dBm-to-relative conversion checks, channel 1/14 and invalid-channel cases, registry disable combinations, regulatory limit selection for FCC/ETSI/MKK/WW, power-limit string table parsing, and hardware-write traces confirming CCK/OFDM/HT rates receive expected TX indices for 20 MHz and 40 MHz operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_com_phycfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_intf.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_intf.c

## Purpose

`hal_intf.c` is the top-level HAL interface veneer used by the rest of the driver. It exposes generic `rtw_hal_*` entry points and delegates each operation to RTL8723BS-specific SDIO, PHY, DM, transmit, receive, interrupt, C2H, and firmware-command implementations. The source was read as a complete 324-line file.

## Important APIs, Types, and Functions

Important wrappers include chip setup/read/default/free functions, `rtw_hal_init`, `rtw_hal_deinit`, hardware register accessors, xmit/recv init and free functions, management transmit handling, rate-adaptation helpers, BB/RF register accessors, channel/bandwidth setters, DM watchdog paths, C2H helpers, MAC ID sleep/wakeup stubs, and `rtw_hal_fill_h2c_cmd`. The central types are `struct adapter`, `struct dvobj_priv`, `struct mlme_priv`, `struct sta_info`, and hardware/ODM enum values.

## Control Flow

Initialization calls `rtl8723bs_hal_init`, applies the current MLME opmode via `rtw_setopmode_cmd`, marks hardware initialized, optionally enables notch filtering, restores WEP keys, initializes MLME extension hardware state, and applies RF gain offset. Deinitialization calls the chip-specific HAL deinit and clears `hw_init_completed`. Most other calls are straight pass-through wrappers. Management TX adds BIP/AES software encryption handling for protected management frames before calling the chip-specific management transmit path.

## State and Persistence Behavior

This file mainly mutates adapter runtime state: `hw_init_completed`, opmode, restored security keys, management frame attributes, and dynamic-management state through watchdog calls. It does not own durable state; it coordinates adapter, dvobj, MLME, security, xmit, recv, PHY, and firmware state.

## Dependencies and Integration Points

It integrates the core `rtw_*` driver layers with RTL8723BS functions such as `rtl8723bs_hal_init`, `rtl8723bs_hal_xmit`, `rtl8723b_HalDmWatchDog`, `PHY_QueryBBReg_8723B`, `PHY_SetSwChnlBWMode8723B`, `FillH2CCmd8723B`, and C2H handlers. It is the dependency boundary for code that wants chip-agnostic HAL calls.

## Risks and Edge Cases

`rtw_hal_macid_sleep` and wakeup are effectively disabled because `GetHalDefVar` reports no support for `HAL_DEF_MACID_SLEEP`. Management transmit runs in interrupt context, so BIP/AES coalescing must remain nonblocking. `rtw_hal_init` uses `dvobj->padapters`, assuming a primary adapter layout. Many wrappers provide no validation and depend on chip-specific functions to reject invalid state.

## Test Signals

HAL init/deinit tests should verify `hw_init_completed` transitions and cleanup after chip init failure. Wrapper tests can use function-call tracing or fakes for PHY, SDIO, interrupt, and firmware command calls. Management TX tests should cover BIP multicast and AES unicast protected management frames. DM watchdog tests should confirm no chip DM is run before hardware initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_intf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_pwr_seq.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_pwr_seq.c

## Purpose

`hal_pwr_seq.c` defines RTL8723B power-transition scripts as `struct wlan_pwr_cfg` arrays. These arrays are parsed elsewhere to move the chip among card-emulation, active, radio-off, card-disable, suspend, resume, hardware power-down, firmware LPS, and software LPS states. The source was read as a complete 130-line file.

## Important APIs, Types, and Functions

The exported data objects are `rtl8723B_power_on_flow`, `rtl8723B_radio_off_flow`, `rtl8723B_card_disable_flow`, `rtl8723B_card_enable_flow`, `rtl8723B_suspend_flow`, `rtl8723B_resume_flow`, `rtl8723B_hwpdn_flow`, `rtl8723B_enter_lps_flow`, `rtl8723B_leave_lps_flow`, `rtl8723B_enter_swlps_flow`, and `rtl8723B_leave_swlps_flow`. The arrays are built from macros in `hal_pwr_seq.h`, such as `RTL8723B_TRANS_CARDEMU_TO_ACT` and `RTL8723B_TRANS_END`.

## Control Flow

There is no executable control flow in this file. Runtime power-control code selects the appropriate array and interprets each `wlan_pwr_cfg` entry in sequence until `RTL8723B_TRANS_END`, performing register writes, polling, delays, or command actions defined by the macro-expanded entries.

## State and Persistence Behavior

The file stores static transition tables only. Hardware power state changes persist in device registers and power domains after the parser executes the selected flow.

## Dependencies and Integration Points

It depends entirely on `hal_pwr_seq.h` for array lengths and transition macro contents. It integrates with RTL8723BS power-on, suspend/resume, IPS/LPS, card-disable, and radio-off code that consumes these arrays.

## Risks and Edge Cases

Array length expressions must match the number of macro-expanded entries; a macro/table drift can create truncation or extra uninitialized entries. The card-disable and card-enable arrays use lengths containing `RTL8723B_TRANS_CARDEMU_TO_PDN_STEPS` while one initializer uses `CARDEMU_TO_CARDDIS`, so the header definitions must stay consistent. Incorrect transition order can leave firmware or SDIO state inaccessible.

## Test Signals

Compile-time array sizing, parser dry-runs that count transitions to `END`, power-cycle smoke tests, suspend/resume tests, LPS enter/leave tests, and register-trace comparisons with Realtek reference sequences are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_pwr_seq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_sdio.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_sdio.c

## Purpose

`hal_sdio.c` provides small SDIO transmit-resource helpers for RTL8723BS. It tracks free TX FIFO pages, public-page borrowing, output-queue-token free space, and maximum transmit buffer length per queue. The source was read as a complete 105-line file.

## Important APIs, Types, and Functions

The exported functions are `rtw_hal_sdio_max_txoqt_free_space`, `rtw_hal_sdio_query_tx_freepage`, `rtw_hal_sdio_update_tx_freepage`, `rtw_hal_set_sdio_tx_max_length`, and `rtw_hal_get_sdio_tx_max_length`. They use `struct hal_com_data`, `struct dvobj_priv`, queue indices such as `HI_QUEUE_IDX`, `MID_QUEUE_IDX`, `LOW_QUEUE_IDX`, `PUBLIC_QUEUE_IDX`, and SDIO device IDs from `ffaddr2deviceId`.

## Control Flow

The query path checks whether dedicated free pages plus public free pages can satisfy a transmit request. The update path consumes dedicated pages first and falls back to the public queue. Maximum queue lengths are computed from queue-page counts plus half of the public queue, capped at `MAX_XMITBUF_SZ`, then selected by the output FIFO/device ID.

## State and Persistence Behavior

The state is entirely in `hal_com_data`: `SdioTxOQTMaxFreeSpace`, `SdioTxFIFOFreePage[]`, and `sdio_tx_max_len[]`. It persists only for the active adapter session and is updated as TX resources are consumed/refreshed.

## Dependencies and Integration Points

The file depends on the HAL default variable `HAL_DEF_TX_PAGE_SIZE`, SDIO queue indices, `ffaddr2deviceId`, and xmit scheduling code that queries and decrements pages before queuing frames. It is part of the SDIO HAL transmit path.

## Risks and Edge Cases

The free-page update lock is commented out, so concurrent TX scheduling could underflow or race if callers do not serialize access. `PageIdx` is not bounds-checked. Public page subtraction can underflow if query and update are not paired atomically. `rtw_hal_sdio_max_txoqt_free_space` imposes a minimum of 8, which can hide a lower hardware value.

## Test Signals

Unit tests should cover dedicated-only, public-borrowing, insufficient-page, queue-index mapping, and max-length capping. Concurrency tests or lockdep-style review should focus on page accounting under parallel transmit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm.c

## Purpose

`odm.c` is the central ODM dynamic-management coordinator for RTL8723BS. It contains OFDM/CCK swing tables, initializes common ODM state, computes rate-adaptation masks, monitors RSSI, initializes antenna and thermal tracking state, runs the periodic ODM watchdog, and exposes common-info init/hook/update APIs used by chip-specific DM setup. The source was read as a complete 1026-line file.

## Important APIs, Types, and Functions

Important objects and APIs include `OFDMSwingTable_New`, `CCKSwingTable_Ch1_Ch13_New`, `CCKSwingTable_Ch14_New`, `ODM_Get_Rate_Bitmap`, `ODM_RAStateCheck`, `odm_TXPowerTrackingInit`, `ODM_TXPowerTrackingCheck`, `ODM_DMInit`, `ODM_DMWatchdog`, `ODM_CmnInfoInit`, `ODM_CmnInfoHook`, `ODM_CmnInfoPtrArrayHook`, and `ODM_CmnInfoUpdate`. Internal helpers include common-info self init/update, rate-adaptive mask refresh, RSSI monitor, software antenna detect init, and swing-index discovery.

## Control Flow

`ODM_DMInit` initializes hardware-derived common fields, DIG, NHM, adaptivity, rate adaptation, CFO tracking, EDCA turbo, RSSI monitoring, TX power tracking, RF calibration state, BB power saving, dynamic TX power, and software antenna state. `ODM_DMWatchdog` updates current channel/control-channel and station-count state, reads false-alarm and NHM counters, updates RSSI, runs DIG or low-power DIG depending on firmware PS mode, applies adaptivity and CCK packet-detect thresholds, then, unless power saving is active, refreshes rate masks, EDCA, CFO tracking, and thermal TX power tracking.

## State and Persistence Behavior

The persistent runtime state is `struct dm_odm_t`, embedded in `hal_com_data`. It holds support-ability masks, fixed chip/interface/package metadata, pointers into driver state, linked/station/RSSI flags, station pointer array, DIG/FA/EDCA/CFO/RF-calibration substructures, swing indices, and thermal tracking values. Common-info hooks store live pointers rather than snapshots, so lifetime and update ordering are critical.

## Dependencies and Integration Points

The file depends on ODM submodules (`odm_DIG`, `odm_CfoTracking`, `odm_EdcaTurboCheck`, power-saving and TX-power modules), PHY register helpers, H2C RSSI reporting (`rtl8723b_set_rssi_cmd`), station rate update (`rtw_hal_update_ra_mask`), power-control state, MLME/station state, RF calibration (`ODM_TXPowerTrackingCallback_ThermalMeter`, `ODM_ClearTxPowerTrackingState`), and register definitions from ODM headers.

## Risks and Edge Cases

Common-info pointers can be NULL if `Update_ODM_ComInfo_8723b` did not hook them before `ODM_DMWatchdog`. `ODM_Get_Rate_Bitmap` trusts `macid` as an array index. The watchdog returns early when `pbPowerSaving` is true, skipping rate/EDCA/CFO/thermal work. Thermal tracking uses a two-phase trigger/callback sequence that depends on watchdog cadence. The swing tables and default indices must match RF calibration code expectations.

## Test Signals

Good signals include ODM init field snapshots, watchdog traces under linked/unlinked/LPS/power-saving states, rate-mask outputs for B/G/N modes and RSSI levels, RSSI monitor station aggregation tests, thermal tracking trigger/callback sequencing, and fault-injection for missing station pointers or disabled support abilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm.h

## Purpose

`odm.h` is the primary ODM contract header for the RTL8723BS dynamic-management subsystem. It defines support flags, wireless/interface/chip enums, rate-adaptive and PHY-info types, RF calibration state, antenna/diversity state, `struct dm_odm_t`, configuration type enums, external swing tables, and ODM public prototypes. The source was read as a complete 1122-line file.

## Important APIs, Types, and Functions

The most important type is `struct dm_odm_t`, which aggregates adapter pointer, fixed chip metadata, dynamic driver-state pointers, linked/RSSI/BT/adaptivity fields, station pointer array, `struct dig_t`, `struct ps_t`, `struct cfo_tracking`, `struct edca_t`, `struct odm_rf_cal_t`, antenna/path diversity state, and TX power tracking swing state. Other key types are `struct odm_phy_info`, `struct odm_packet_info`, `struct odm_rate_adaptive`, `struct swat_t`, `struct fat_t`, `struct pathdiv_t`, `struct ant_detected_info`, and `enum odm_cmninfo_e`. Prototypes expose `ODM_DMInit`, `ODM_DMWatchdog`, common-info APIs, rate-bitmap APIs, TX power tracking, and timer hooks.

## Control Flow

There is no executable flow in the header. It defines the state and function surface consumed by `odm.c`, `rtl8723b_dm.c`, PHY status parsing, register configuration, and ODM submodules.

## State and Persistence Behavior

The header defines adapter-session state rather than owning storage. `dm_odm_t` persists inside `hal_com_data` after `rtw_hal_data_init` and is reset by `rtl8723b_init_dm_priv`. Many fields are pointers into MLME, security, traffic, power, and station structures; those are live views of changing driver state.

## Dependencies and Integration Points

It includes smaller ODM submodule headers and is included through `odm_precomp.h`. It is the contract among HAL DM setup, watchdog, PHY status query, register table application, RF calibration, H2C RSSI reporting, and rate adaptation.

## Risks and Edge Cases

The structure is large and contains many legacy fields not used by this trimmed staging driver, increasing risk of stale assumptions. Duplicate macro definitions exist for traffic and SW antenna steps. Some prototypes are declared but implemented elsewhere or not present in this subset, so compile/link coverage is needed. Pointer-hook fields can be dereferenced by ODM code without local NULL checks.

## Test Signals

Compile coverage with all ODM consumers, structure initialization tests after `memset`, sparse/clang warnings for unused or mismatched declarations, and watchdog tests that exercise fields sourced through common-info hooks are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_CfoTracking.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_CfoTracking.c

## Purpose

`odm_CfoTracking.c` implements carrier-frequency-offset tracking for a linked RTL8723BS station. It adjusts crystal capacitance and automatic temperature compensation (ATC) based on per-packet CFO tail measurements. The source was read as a complete 210-line file.

## Important APIs, Types, and Functions

Public entry points are `ODM_CfoTrackingReset`, `ODM_CfoTrackingInit`, `ODM_CfoTracking`, and `odm_parsing_cfo`. Internal helpers are `odm_SetCrystalCap`, `odm_GetDefaultCrytaltalCap`, `odm_SetATCStatus`, and `odm_GetATCStatus`. The state is `struct cfo_tracking` inside `dm_odm_t`.

## Control Flow

PHY status parsing calls `odm_parsing_cfo` for OFDM packets, which stores path CFO tails and increments a packet counter. The watchdog calls `ODM_CfoTracking`; if support is disabled, not linked, or not exactly one station, it resets the crystal cap and ATC. Otherwise it waits for a new packet, converts CFO tail to kHz, filters an abnormal first large jump, enables or disables adjustment by high/low CFO thresholds, disables adjustment for BT coexistence, steps `CrystalCap` toward lower CFO, clamps it to six bits, writes `REG_MAC_PHY_CTRL`, and toggles ATC around the `CFO_TH_ATC` threshold.

## State and Persistence Behavior

Persistent adapter-session state includes default/current crystal cap, previous CFO average, packet counters, large-CFO filter flag, adjustment flag, and ATC status. Hardware state persists in `REG_MAC_PHY_CTRL` and `ODM_REG(BB_ATC)` until reset or rewritten.

## Dependencies and Integration Points

It depends on `dm_odm_t`, `hal_com_data->CrystalCap`, PHY BB register access, CFO fields from `struct phy_status_rpt_8192cd_t`, and the ODM watchdog. It integrates with `odm_HWConfig.c` through `odm_parsing_cfo`.

## Risks and Edge Cases

Only path A is averaged even though path B is stored. CFO adjustment is intentionally disabled when BT is enabled. Packet counter wrap is handled by resetting to zero. The default-cap accessor name has a typo but is static. Incorrect station ID handling can ignore CFO for station zero because parsing only updates when `station_id != 0`.

## Test Signals

Tests should cover no-link reset, multi-station reset, no-new-packet early return, positive and negative CFO cap adjustments, clamp at 0 and 0x3f, ATC threshold toggles, BT-enabled suppression, and packet counter wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_CfoTracking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_CfoTracking.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_CfoTracking.h

## Purpose

`odm_CfoTracking.h` declares CFO tracking thresholds, state, and public APIs. The source was read as a complete 39-line file.

## Important APIs, Types, and Functions

It defines `CFO_TH_XTAL_HIGH`, `CFO_TH_XTAL_LOW`, `CFO_TH_ATC`, `struct cfo_tracking`, and prototypes for `ODM_CfoTrackingReset`, `ODM_CfoTrackingInit`, `ODM_CfoTracking`, and `odm_parsing_cfo`.

## Control Flow

The header contains no runtime flow; it provides the declarations consumed by `odm.c`, `odm_CfoTracking.c`, and PHY status parsing.

## State and Persistence Behavior

`struct cfo_tracking` persists inside `dm_odm_t` and stores ATC status, crystal cap, CFO tails, previous average, packet counters, and reset/force flags.

## Dependencies and Integration Points

It depends on standard driver boolean and integer typedefs made available through ODM includes. It integrates with the ODM watchdog and PHY status parser.

## Risks and Edge Cases

The `ODM_CfoTrackingReset` prototype is split oddly over two lines but compiles as a normal declaration. Some fields (`bForceXtalCap`, `bReset`) are declared but not used in the visible implementation.

## Test Signals

Compile coverage and state initialization checks in `ODM_CfoTrackingInit`/reset are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_CfoTracking.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DIG.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DIG.c

## Purpose

`odm_DIG.c` implements dynamic initial gain (DIG), false-alarm statistics, NHM/adaptivity, EDCCA threshold control, low-power DIG, and CCK packet-detect threshold tuning for RTL8723BS. The source was read as a complete 813-line file.

## Important APIs, Types, and Functions

Important functions are `odm_NHMCounterStatisticsInit`, `odm_NHMCounterStatistics`, `odm_GetNHMCounterStatistics`, `odm_NHMCounterStatisticsReset`, `odm_NHMBBInit`, `odm_NHMBB`, `odm_SearchPwdBLowerBound`, `odm_AdaptivityInit`, `odm_Adaptivity`, `ODM_Write_DIG`, `odm_DigAbort`, `odm_DIGInit`, `odm_DIG`, `odm_DIGbyRSSI_LPS`, `odm_FalseAlarmCounterStatistics`, `odm_FAThresholdCheck`, `odm_ForbiddenIGICheck`, `odm_CCKPacketDetectionThresh`, and `ODM_Write_CCK_CCA_Thres`.

## Control Flow

Initialization configures NHM counters and adaptivity defaults, reads the current IGI from hardware, and sets DIG thresholds/bounds. Each watchdog pass reads false-alarm counters and NHM, then `odm_DIG` decides whether to abort due to disabled support, scanning, or disabled initial gain. It computes RSSI-based gain bounds, adjusts for BT and antenna diversity, updates forbidden IGI for excessive false alarms, selects false-alarm thresholds, moves current IGI up or down, clamps it, applies adaptivity limits, and writes IGI registers. Adaptivity can search for a lower EDCCA bound by polling report bits and then writes OFDM ECCA thresholds. CCK PD tuning writes `ODM_REG(CCK_CCA)` based on RSSI and CCK false alarms.

## State and Persistence Behavior

State is stored in `dm_odm_t->DM_DigTable`, `FalseAlmCnt`, NHM/adaptivity fields, RSSI fields, and hardware registers for IGI, NHM, false-alarm counters, EDCCA thresholds, and CCK CCA threshold. Values persist until the next watchdog, reset, or mode transition.

## Dependencies and Integration Points

It depends on register macros from `odm_RegDefine11N.h`/`Hal8723BReg.h`, PHY BB register access, traffic byte counters hooked into `dm_odm_t`, RSSI values from `odm_HWConfig.c`/RSSI monitor, support flags from `rtl8723b_dm.c`, and watchdog sequencing in `odm.c`.

## Risks and Edge Cases

`odm_NHMBB` dereferences traffic counter pointers and assumes common-info hooks are installed. False-alarm counters are held/read but not visibly reset for OFDM in this function, so reset behavior depends on hardware side effects or external code. `odm_SearchPwdBLowerBound` uses blocking delays and a loop that can affect watchdog latency. Several threshold constants are magic values tied to Realtek calibration. LPS DIG uses `RSSI_Min` and can underflow before clamping if state is bad.

## Test Signals

Signals include register-trace tests for DIG writes, false-alarm counter decoding tests, linked/unlinked first-connect/first-disconnect behavior, adaptivity threshold tests for BW20/BW40 and RSSI hysteresis, excessive false-alarm forbidden-IGI recovery, LPS DIG bounds, CCK PD threshold selection, and tests with disabled support flags or scan-in-progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DIG.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DIG.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DIG.h

## Purpose

`odm_DIG.h` declares the DIG and false-alarm data structures, DIG thresholds, low-power thresholds, and the public DIG/adaptivity/false-alarm APIs. The source was read as a complete 169-line file.

## Important APIs, Types, and Functions

The header defines `struct dig_t`, `struct false_ALARM_STATISTICS`, `enum ODM_Pause_DIG_TYPE`, threshold macros such as `DM_DIG_MAX_NIC`, `DM_DIG_MIN_NIC`, `DM_DIG_FA_TH*`, `DM_DIG_BACKOFF_*`, `DM_DIG_FA_TH*_LPS`, and prototypes for all functions implemented in `odm_DIG.c`.

## Control Flow

There is no executable flow; it defines the state and constants used by the ODM watchdog and DIG implementation.

## State and Persistence Behavior

`struct dig_t` stores current and previous IGI, thresholds, bounds, false-alarm recovery state, CCK CCA threshold state, BT IGI, and media-connect flags. `struct false_ALARM_STATISTICS` stores OFDM, CCK, and aggregate counter snapshots.

## Dependencies and Integration Points

It is included by `odm.h` and `odm_precomp.h`. It integrates with `dm_odm_t`, PHY register access, false alarm counter reads, RSSI processing, and low-power DM handling.

## Risks and Edge Cases

Many fields are legacy or unused in this trimmed driver, so initialization coverage matters. Threshold constants are hardware-specific and should not be changed without RF validation.

## Test Signals

Compile coverage, initialization snapshots, and tests that verify each threshold macro's use through `odm_DIG` and `odm_DIGbyRSSI_LPS` provide useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DIG.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DynamicBBPowerSaving.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DynamicBBPowerSaving.c

## Purpose

`odm_DynamicBBPowerSaving.c` implements a baseband RF-saving mode that rewrites selected BB registers when RSSI is high enough, and restores saved values when RSSI drops or normal mode is forced. The source was read as a complete 81-line file.

## Important APIs, Types, and Functions

The public functions are `odm_DynamicBBPowerSavingInit` and `ODM_RF_Saving`. The key state is `struct ps_t` inside `dm_odm_t`.

## Control Flow

Initialization sets previous/current CCA and RF states to sentinel maxima and clears saved register state. `ODM_RF_Saving` chooses RSSI thresholds, snapshots registers `0x874`, `0xc70`, `0x85c`, and `0xa74` on first use, selects RF save/normal state with hysteresis unless forced normal, and writes either the save-mode register values or the saved normal values when state changes.

## State and Persistence Behavior

`ps_t` persists saved register values, RSSI minimum, initialization flag, and previous/current RF state. Hardware register changes persist until the next state transition or adapter reset.

## Dependencies and Integration Points

It depends on `dm_odm_t->RSSI_Min`, `PatchID`, PHY BB register access, and the ODM support flag path that can call `dm_RF_Saving`. Initialization is invoked from `ODM_DMInit`.

## Risks and Edge Cases

The first snapshot occurs lazily at the first `ODM_RF_Saving` call, so if the hardware is already modified before that call, restore values may be wrong. RSSI `0xff` produces `RF_MAX` and no meaningful save/normal action. The function uses hard-coded registers and magic values.

## Test Signals

Tests should validate initialization, first-call register snapshots, high/low RSSI hysteresis, force-normal behavior, FUNAI patch thresholds, and exact register writes for save and restore transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DynamicBBPowerSaving.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DynamicBBPowerSaving.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DynamicBBPowerSaving.h

## Purpose

`odm_DynamicBBPowerSaving.h` declares dynamic BB power-saving state and APIs. The source was read as a complete 31-line file.

## Important APIs, Types, and Functions

It defines `struct ps_t`, the `dm_RF_Saving` alias, and prototypes for `ODM_RF_Saving` and `odm_DynamicBBPowerSavingInit`.

## Control Flow

There is no runtime flow; it is a declaration header for the BB RF-saving implementation.

## State and Persistence Behavior

`ps_t` stores previous/current CCA and RF states, RSSI minimum, initialization flag, and saved BB register values.

## Dependencies and Integration Points

It is included by `odm.h` and is initialized from `ODM_DMInit`.

## Risks and Edge Cases

Register backup fields must be initialized before restore. The header exposes raw register snapshots without guarding misuse.

## Test Signals

Compile coverage and state initialization tests in `odm_DynamicBBPowerSavingInit` are sufficient for the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DynamicBBPowerSaving.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DynamicTxPower.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DynamicTxPower.c

## Purpose

`odm_DynamicTxPower.c` initializes dynamic TX power state in the driver's DM private data. The source was read as a complete 22-line file.

## Important APIs, Types, and Functions

The only function is `odm_DynamicTxPowerInit`, which accesses `struct dm_odm_t`, `struct adapter`, `struct hal_com_data`, and `struct dm_priv`.

## Control Flow

The function resolves the adapter from ODM state, gets HAL and DM private data, disables dynamic TX power, and resets current and last high-power level to normal.

## State and Persistence Behavior

It mutates `dm_priv->bDynamicTxPowerEnable`, `LastDTPLvl`, and `DynamicTxHighPowerLvl`. No hardware register is written here; later code would consume these fields if dynamic TX power were enabled.

## Dependencies and Integration Points

It depends on `GET_HAL_DATA` and the TX power level constants from `odm_DynamicTxPower.h`. It is called by `ODM_DMInit`.

## Risks and Edge Cases

The feature is initialized disabled and no runtime algorithm exists in this file, so support flags may advertise dynamic TX power without active behavior.

## Test Signals

Initialization tests should confirm the three `dm_priv` fields are reset to disabled/normal after `ODM_DMInit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DynamicTxPower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DynamicTxPower.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DynamicTxPower.h

## Purpose

`odm_DynamicTxPower.h` defines near-field RSSI thresholds, dynamic TX high-power level constants, and the init prototype for dynamic TX power. The source was read as a complete 29-line file.

## Important APIs, Types, and Functions

It defines `TX_POWER_NEAR_FIELD_THRESH_*`, `TxHighPwrLevel_*` constants, and `odm_DynamicTxPowerInit`.

## Control Flow

There is no executable flow.

## State and Persistence Behavior

The constants describe state values stored in `dm_priv`; the header owns no storage.

## Dependencies and Integration Points

It is included by `odm.h` and consumed by `odm_DynamicTxPower.c`.

## Risks and Edge Cases

The header defines multiple levels that are not all used in the visible implementation, making stale or partial feature support likely.

## Test Signals

Compile coverage and initialization tests for `dm_priv` dynamic TX power fields are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DynamicTxPower.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_EdcaTurboCheck.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_EdcaTurboCheck.c

## Purpose

`odm_EdcaTurboCheck.c` implements EDCA turbo tuning for best-effort traffic. It selects uplink or downlink BE EDCA parameters based on traffic direction, wireless mode, and AP vendor interoperability quirks. The source was read as a complete 158-line file.

## Important APIs, Types, and Functions

The public functions are `ODM_EdcaTurboInit`, `odm_EdcaTurboCheck`, and `odm_EdcaTurboCheckCE`. Static tables `edca_setting_DL_GMode`, `edca_setting_UL`, and `edca_setting_DL` provide vendor-specific EDCA values indexed by `HT_IOT_PEER_*`.

## Control Flow

Initialization clears current turbo state and non-BE packet tracking. The watchdog-facing `odm_EdcaTurboCheck` returns unless `ODM_MAC_EDCA_TURBO` is enabled, then calls the CE implementation. The CE implementation exits when unlinked, Wi-Fi spec mode is enabled, or AP vendor is invalid. If non-BE packets are absent, it compares current TX/RX byte counts to choose uplink or downlink, applies vendor/mode-specific EDCA overrides, writes `REG_EDCA_BE_PARAM`, and records turbo state. If conditions later require disabling turbo, it restores `hal_com_data->AcParam_BE`.

## State and Persistence Behavior

State lives in `dm_odm_t->DM_EDCA_Table`, `adapter->recvpriv.bIsAnyNonBEPkts`, `dvobj_priv->traffic_stat`, and the hardware EDCA BE register. The previous traffic index persists for diagnostics but is not heavily used in this snapshot.

## Dependencies and Integration Points

It depends on MLME association vendor detection, registry `wifi_spec`, traffic counters, recv non-BE tracking, `hal_com_data->AcParam_BE`, and MAC register writes. It is called from `ODM_DMWatchdog`.

## Risks and Edge Cases

`bbtchange` and `biasonrx` are local constants set false, reducing intended dynamic behavior. Turbo is skipped entirely in `wifi_spec` mode. Vendor table indices must match `HT_IOT_PEER_*`. If non-BE packet state is not maintained accurately elsewhere, BE EDCA may remain too aggressive or be restored too soon.

## Test Signals

Tests should cover unlinked and `wifi_spec` exits, invalid vendor exit, uplink/downlink traffic selection, Cisco/Airgo/Marvell/Atheros overrides, restore of `AcParam_BE`, and non-BE packet suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_EdcaTurboCheck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_EdcaTurboCheck.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_EdcaTurboCheck.h

## Purpose

`odm_EdcaTurboCheck.h` declares EDCA turbo state and APIs. The source was read as a complete 23-line file.

## Important APIs, Types, and Functions

It defines `struct edca_t` with current turbo state, current RDL state, and previous traffic index. It declares `odm_EdcaTurboCheck`, `ODM_EdcaTurboInit`, and `odm_EdcaTurboCheckCE`.

## Control Flow

There is no runtime flow.

## State and Persistence Behavior

The state persists inside `dm_odm_t->DM_EDCA_Table` and controls whether EDCA settings need to be restored.

## Dependencies and Integration Points

It is included by `odm.h` and used by the ODM watchdog.

## Risks and Edge Cases

Only a small subset of intended EDCA state is represented here; correctness depends on external traffic/non-BE tracking.

## Test Signals

Compile coverage and initialization checks after `ODM_EdcaTurboInit` are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_EdcaTurboCheck.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_HWConfig.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_HWConfig.c

## Purpose

`odm_HWConfig.c` parses receive PHY status reports into signal/RSSI/EVM/CFO metrics, updates per-station smoothed RSSI for dynamic management, and dispatches table-driven RF/BB configuration header readers for RTL8723B. The source was read as a complete 446-line file.

## Important APIs, Types, and Functions

Important functions include `odm_signal_scale_mapping`, `odm_phy_status_query`, `ODM_ConfigRFWithHeaderFile`, `ODM_ConfigRFWithTxPwrTrackHeaderFile`, and `ODM_ConfigBBWithHeaderFile`. Internal helpers include `odm_query_rx_pwr_percentage`, `odm_evm_db_to_percentage`, `odm_cck_rssi`, `odm_rx_phy_status_parsing`, and `odm_Process_RSSIForDM`. It uses `struct phy_status_rpt_8192cd_t`, `struct odm_phy_info`, `struct odm_packet_info`, and station RSSI statistics.

## Control Flow

`odm_phy_status_query` first parses raw PHY status. CCK packets derive RSSI from LNA/VGA AGC report and signal quality from CCK SQ; OFDM packets derive per-path RSSI/SNR, all-path PWDB, EVM, and CFO tail. It then updates driver RSSI state unless RSSI test mode is active. RSSI smoothing tracks CCK and OFDM averages separately, maintains a packet map to weight mixed CCK/OFDM history, updates per-station undecorated smoothed RSSI, and counts beacon PHY queries. Configuration APIs select generated Realtek header-table readers according to RF/BB config type and SDIO interface.

## State and Persistence Behavior

The function mutates caller-supplied `odm_phy_info`, `dm_odm_t->PhyDbgInfo`, `RSSI_A`, `RSSI_B`, `RxRate`, CFO tracking state, and `sta_info->rssi_stat` smoothed fields. These values persist across packets and feed the ODM watchdog, rate adaptation, DIG, and firmware RSSI reports.

## Dependencies and Integration Points

It depends on raw PHY report layout from `odm_HWConfig.h`, descriptor rate constants, station pointer hooks in `dm_odm_t`, CFO parsing, generated hardware image functions such as `ODM_ReadAndConfig_MP_8723B_PHY_REG`, and register configuration wrappers.

## Risks and Edge Cases

`station_id == 0xFF`, invalid station pointers, or BSSID mismatch suppress RSSI updates. CCK RSSI conversion supports only specific LNA indices. The packet-map smoothing uses 64-bit history and must avoid stale initial values. The signal-scale mapping is SDIO-specific and returns zero for unsupported interfaces. CFO parsing only occurs on OFDM paths.

## Test Signals

Tests should cover CCK LNA/VGA conversions, OFDM per-path RSSI/SNR/EVM conversion, signal scaling boundaries, station RSSI smoothing for CCK-only/OFDM-only/mixed packet histories, beacon count increments, BSSID mismatch suppression, CFO parsing calls, and config dispatcher selection for RF radio, TX power limit, TX power tracking, PHY register, AGC, and PHY register page tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_HWConfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_HWConfig.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_HWConfig.h

## Purpose

`odm_HWConfig.h` declares the raw RTL8723B PHY status report layout and ODM hardware configuration APIs. The source was read as a complete 86-line file.

## Important APIs, Types, and Functions

It defines bitfield `struct phy_rx_agc_info_t`, raw report `struct phy_status_rpt_8192cd_t`, and prototypes for `odm_phy_status_query`, RF/BB/FW config dispatchers, and `odm_signal_scale_mapping`.

## Control Flow

There is no executable flow; it provides ABI-like layout and function declarations.

## State and Persistence Behavior

The report structs describe transient RX descriptor/PHY-status bytes. Parsed results are stored elsewhere in `odm_phy_info`, station RSSI stats, and `dm_odm_t`.

## Dependencies and Integration Points

It depends on ODM endian macros and `dm_odm_t` definitions. It integrates raw receive status from the hardware RX path with ODM parsing.

## Risks and Edge Cases

The bitfield layout depends on `ODM_ENDIAN_TYPE`; incorrect endian detection corrupts AGC and antenna fields. Struct layout must match firmware/hardware RX status bytes exactly.

## Test Signals

Build checks on little-endian and layout/offset tests against known PHY status samples are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_HWConfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_RegConfig8723B.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_RegConfig8723B.c

## Purpose

`odm_RegConfig8723B.c` applies generated RTL8723B MAC, BB, RF, PHY register-page, and TX power-limit table entries. It is the low-level bridge between Realtek header tables and hardware register writes or HAL power-table storage. The source was read as a complete 177-line file.

## Important APIs, Types, and Functions

Public functions are `odm_ConfigRFReg_8723B`, `odm_ConfigRF_RadioA_8723B`, `odm_ConfigMAC_8723B`, `odm_ConfigBB_AGC_8723B`, `odm_ConfigBB_PHY_REG_PG_8723B`, `odm_ConfigBB_PHY_8723B`, and `odm_ConfigBB_TXPWR_LMT_8723B`.

## Control Flow

RF config handles special delay pseudo-addresses, writes RF registers, delays between writes, and retries problematic RF registers `0xb6` and `0xb2` with readback verification; the `0xb2` retry also retriggers LCK through RF register `0x18`. MAC config writes one byte. BB AGC/PHY config writes BB registers or interprets delay pseudo-addresses. PHY register-page entries are stored into TX power-by-rate tables instead of immediately written. TX power-limit entries are passed to `PHY_SetTxPowerLimit`.

## State and Persistence Behavior

Hardware register writes persist until reset or later table/application writes. PHY register-page and TX power-limit entries persist in `hal_com_data` arrays and are consumed when setting channel/rate power.

## Dependencies and Integration Points

It depends on `PHY_SetRFReg`, `PHY_QueryRFReg`, `PHY_SetBBReg`, `PHY_StoreTxPowerByRate`, `PHY_SetTxPowerLimit`, delay APIs, and generated header readers from `HalHWImg8723B_*`. It is called by `odm_HWConfig.c` dispatchers.

## Risks and Edge Cases

Retry loops are bounded but silent on failure. Delay pseudo-addresses must match generated table conventions. RF path support is effectively path A for this chipset. Incorrect table values can directly program bad RF/BB hardware state or bad power limits.

## Test Signals

Register-write trace tests for normal entries, delay entries, `0xb6` retry, `0xb2` retry/LCK, PHY_REG_PG storage, and TX power-limit forwarding are useful. Hardware bring-up logs should match Realtek reference table order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_RegConfig8723B.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_RegConfig8723B.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_RegConfig8723B.h

## Purpose

`odm_RegConfig8723B.h` declares RTL8723B register-configuration helpers used by generated hardware image tables. The source was read as a complete 45-line file.

## Important APIs, Types, and Functions

It declares RF, MAC, BB AGC, BB PHY register-page, BB PHY, and TX power-limit config functions implemented in `odm_RegConfig8723B.c`.

## Control Flow

There is no runtime flow.

## State and Persistence Behavior

The header owns no state; implementations mutate hardware registers and HAL power tables.

## Dependencies and Integration Points

It requires `struct dm_odm_t`, `enum rf_path`, and integer typedefs from ODM includes. It is included by `odm_precomp.h` and generated table readers.

## Risks and Edge Cases

Prototype drift would break generated hardware image application. TX power-limit string pointer arguments depend on table data staying NUL-terminated and valid.

## Test Signals

Compile coverage with all generated hardware image readers is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_RegConfig8723B.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_RegDefine11N.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_RegDefine11N.h

## Purpose

`odm_RegDefine11N.h` defines ODM register addresses and bit masks for 802.11n-generation Realtek PHY/RF/MAC blocks used by RTL8723BS dynamic-management code. The source was read as a complete 162-line file.

## Important APIs, Types, and Functions

The header defines RF registers (`ODM_REG_RF_MODE_11N`, `ODM_REG_CHNBW_11N`, thermal meter registers), BB page 8/A/B/C/D/E registers for DIG, false alarms, CCK CCA, ATC, IQK, TXAGC, and MAC registers for EDCA, TX pause, RSSI monitor, and antenna training. It also defines bit masks such as `ODM_BIT_IGI_11N`, `ODM_BIT_CCK_RPT_FORMAT_11N`, `ODM_BIT_BB_RX_PATH_11N`, and `ODM_BIT_BB_ATC_11N`.

## Control Flow

There is no executable flow; macros are resolved through `ODM_REG()` and `ODM_BIT()` in ODM implementation files.

## State and Persistence Behavior

The macros name hardware state locations. State is held in hardware registers when read/written by ODM code.

## Dependencies and Integration Points

It is included by `odm_precomp.h` and used by DIG, CFO tracking, NHM/adaptivity, PHY parsing, EDCA, and register configuration paths.

## Risks and Edge Cases

Address or bit-mask mistakes cause silent hardware misconfiguration. `ODM_REG_PSD_DATA_11N` is defined twice with the same value. The header is specific to 11n register naming and must match `odm_interface.h` macro expansion.

## Test Signals

Register trace comparison, compile coverage for every `ODM_REG/ODM_BIT` use, and hardware smoke tests for DIG/FA/CFO/EDCA behavior are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_RegDefine11N.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_interface.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_interface.h

## Purpose

`odm_interface.h` provides macro indirection for resolving generic ODM register and bit names to 11n-specific macro names. The source was read as a complete 40-line file.

## Important APIs, Types, and Functions

Important macros are `_reg_11N`, `_bit_11N`, `_cat`, `ODM_REG(_name)`, and `ODM_BIT(_name)`.

## Control Flow

There is no runtime flow. At preprocessing time, `ODM_REG(IGI_A)` becomes `ODM_REG_IGI_A_11N`, and `ODM_BIT(IGI)` becomes `ODM_BIT_IGI_11N`.

## State and Persistence Behavior

The header owns no state; it maps symbolic references to hardware register macros.

## Dependencies and Integration Points

It depends on `odm_RegDefine11N.h` providing the target macros. It is included by `odm_precomp.h` and used throughout ODM code.

## Risks and Edge Cases

Only 11n expansion is supported in this snapshot, so adding 11ac or chip-specific variants requires changing macro dispatch. Missing target macros fail at compile time.

## Test Signals

Compile coverage of all `ODM_REG`/`ODM_BIT` call sites is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_precomp.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_precomp.h

## Purpose

`odm_precomp.h` is the consolidated include header for RTL8723BS ODM implementation files. It pulls in ODM types, common ODM state, submodules, PHY/RF calibration headers, chip HAL headers, register definitions, generated hardware images, and register configuration prototypes. The source was read as a complete 47-line file.

## Important APIs, Types, and Functions

It defines `BEAMFORMING_SUPPORT 0` and includes `odm_types.h`, `odm.h`, `odm_HWConfig.h`, `odm_RegDefine11N.h`, `odm_EdcaTurboCheck.h`, `odm_DIG.h`, `odm_DynamicBBPowerSaving.h`, `odm_DynamicTxPower.h`, `odm_CfoTracking.h`, `HalPhyRf.h`, `HalPhyRf_8723B.h`, `rtl8723b_hal.h`, `odm_interface.h`, `odm_reg.h`, generated `HalHWImg8723B_*` headers, `Hal8723BReg.h`, and `odm_RegConfig8723B.h`.

## Control Flow

There is no runtime flow.

## State and Persistence Behavior

The header owns no storage but controls the declaration environment for most ODM `.c` files.

## Dependencies and Integration Points

It is included by ODM implementation files and centralizes dependencies on generated hardware image tables and RF calibration code.

## Risks and Edge Cases

Large include aggregation can hide dependency cycles and makes compile order sensitive. `TEST_FALG___` appears to be a misspelled legacy define. Beamforming is hard-disabled.

## Test Signals

Full driver compile coverage and include-order checks are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_precomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_reg.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_reg.h

## Purpose

`odm_reg.h` defines a secondary set of ODM MAC/BB/RF register addresses and one bitmap used by legacy or shared ODM code. The source was read as a complete 91-line file.

## Important APIs, Types, and Functions

Macros include `ODM_BB_RESET`, `RF_T_METER_OLD`, `RF_T_METER_NEW`, EDCA registers, TX pause, BB page 8/A/C/D/E addresses, RF gain/channel registers, PSD/path-diversity registers, and `BIT_FA_RESET`.

## Control Flow

There is no executable flow.

## State and Persistence Behavior

The macros name hardware state; actual persistence is in device registers.

## Dependencies and Integration Points

It is included by `odm_precomp.h` and used by ODM/RF calibration code that references legacy macro names rather than the `ODM_REG(..._11N)` indirection.

## Risks and Edge Cases

Duplication with `odm_RegDefine11N.h` can drift. Some registers refer to features only partially present in this driver, such as path diversity and PSD.

## Test Signals

Compile coverage and hardware register trace comparisons for callers using these legacy names are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_types.h

## Purpose

`odm_types.h` provides foundational ODM type aliases, endian selection, status enum, adapter-to-ODM accessor, and table-reader helper macros. The source was read as a complete 47-line file.

## Important APIs, Types, and Functions

It defines `GET_ODM`, `enum hal_status`, `ODM_ENDIAN_BIG`, `ODM_ENDIAN_LITTLE`, `ODM_ENDIAN_TYPE`, `STA_INFO_T`, `PSTA_INFO_T`, `USE_WORKITEM`, `FPGA_TWO_MAC_VERIFICATION`, `READ_NEXT_PAIR`, `COND_ELSE`, and `COND_ENDIF`.

## Control Flow

There is no runtime flow except macro expansion. `READ_NEXT_PAIR` advances generated table parsing indices safely enough to avoid reading past `ArrayLen`.

## State and Persistence Behavior

The header owns no state. `GET_ODM` locates adapter-scoped `hal_com_data.odmpriv`.

## Dependencies and Integration Points

It includes `drv_types.h` and is the first ODM include in `odm_precomp.h`.

## Risks and Edge Cases

Endian detection depends on `__LITTLE_ENDIAN`. `GET_ODM` assumes `HalData` is allocated and typed as `struct hal_com_data`. `READ_NEXT_PAIR` requires callers to maintain `ArrayLen` and `i` semantics consistently.

## Test Signals

Compile coverage, endian-layout checks for PHY status structs, and generated table parser tests that hit `READ_NEXT_PAIR` boundary behavior are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_cmd.c

## Purpose

`rtl8723b_cmd.c` constructs and sends RTL8723B firmware H2C commands, builds reserved-page management frames used by firmware power save and BT coexistence, downloads those pages into TX packet buffer, and configures rate adaptation, RSSI reporting, media status, and power modes. The source was read as a complete 963-line file.

## Important APIs, Types, and Functions

Important functions include `FillH2CCmd8723B`, `rtl8723b_set_FwMediaStatusRpt_cmd`, `rtl8723b_set_FwMacIdConfig_cmd`, `rtl8723b_set_rssi_cmd`, `rtl8723b_set_FwPwrMode_cmd`, `rtl8723b_set_FwPsTuneParam_cmd`, `rtl8723b_set_FwPwrModeInIPS_cmd`, `rtl8723b_download_rsvd_page`, `rtl8723b_set_FwJoinBssRpt_cmd`, `rtl8723b_Add_RateATid`, and `rtl8723b_download_BTCoex_AP_mode_rsvd_page`. Internal builders include `_is_fw_read_cmd_down`, `ConstructBeacon`, `ConstructPSPoll`, `ConstructNullFunctionData`, `rtl8723b_set_FwRsvdPage_cmd`, `rtl8723b_set_FwRsvdPagePkt`, `ConstructBtNullFunctionData`, and `SetFwRsvdPagePkt_BTCoex`.

## Control Flow

`FillH2CCmd8723B` serializes H2C mailbox access with `h2c_fwcmd_mutex`, waits for firmware to clear the selected mailbox bit, writes up to three payload bytes plus ID into the main mailbox, writes extension bytes for longer commands, and advances the mailbox index. Power-mode commands derive awake interval, RLBM, power state, BT coexistence values, and adaptive TSF beacon timing before sending H2C. Reserved-page download builds beacon, PS-Poll, null data, QoS null, and BT QoS null frames into a command xmit frame, inserts fake TX descriptors, sends the combined buffer, polls beacon-valid state, informs firmware of page locations, and restores beacon-related hardware bits.

## State and Persistence Behavior

State persists in `hal_com_data->LastHMEBoxNum`, `RegFwHwTxQCtrl`, MLME extension beacon timing counters, power-control `fw_psmode_iface_id`, firmware mailbox registers, reserved-page TX buffer contents, and firmware command state. The command buffers are stack-local or xmit-frame local.

## Dependencies and Integration Points

The file depends on H2C packing macros from `hal_com_h2c.h`, hardware registers (`REG_HMEBOX_*`, `REG_BCN_*`, `REG_FWHW_TXQ_CTRL`, `REG_CR`), xmit frame allocation/free/send helpers, MLME and security state, BT coexistence callbacks, fake TX descriptor generation, ODM rate bitmap selection, and HAL beacon-valid register helpers.

## Risks and Edge Cases

`_is_fw_read_cmd_down` busy-spins without delay. H2C payloads longer than seven bytes fail. Reserved-page construction must fit within reserved page size; overflow frees the frame but does not report error. Beacon construction in AP mode copies `pktlen` bytes after adding IE length, which is easy to misread and should be regression-tested. Poll loops can iterate up to 100 downloads and rely on `yield`. Many hardware bits are temporarily changed and must be restored even on failure paths.

## Test Signals

Tests should cover H2C mailbox selection, extension payloads, command length rejection, surprise removal, media status packing, MACID config packing, RSSI command packing, power-mode packing with and without BT control, reserved-page layout/page locations/overflow, beacon-valid retry loops, AP-mode BT coexist reserved-page download, and rate bitmap filtering before MACID config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_dm.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_dm.c

## Purpose

`rtl8723b_dm.c` wires the RTL8723BS adapter state into the common ODM engine and drives the normal and low-power dynamic-management watchdog paths. The source was read as a complete 264-line file.

## Important APIs, Types, and Functions

Important functions are `rtl8723b_InitHalDm`, `rtl8723b_HalDmWatchDog`, `rtl8723b_hal_dm_in_lps`, `rtl8723b_HalDmWatchDog_in_LPS`, and `rtl8723b_init_dm_priv`. Internal setup helpers are `Init_ODM_ComInfo_8723b` and `Update_ODM_ComInfo_8723b`.

## Control Flow

`rtl8723b_init_dm_priv` clears `dm_priv` and initializes fixed ODM common info. `rtl8723b_InitHalDm` sets DM flags, hooks live driver pointers into ODM, and calls `ODM_DMInit`. The normal watchdog exits if hardware init is incomplete, checks firmware PS awake state, optionally checks RX FIFO, updates linked/station/BT common info, and calls `ODM_DMWatchdog`. The LPS path updates link state, gets the associated station RSSI, updates `RSSI_Min`, and schedules an LPS work command if current IGI differs from RSSI by more than five. `rtl8723b_hal_dm_in_lps` writes DIG directly and reports RSSI to firmware.

## State and Persistence Behavior

This file initializes and updates `hal_com_data->dmpriv` and `odmpriv`, including support ability flags, pointer hooks to MLME/traffic/channel/security/power fields, station pointer array, link state, station state, BT enabled state, and RSSI minimum. It also affects hardware through ODM watchdog and LPS DIG writes.

## Dependencies and Integration Points

It integrates adapter/MLME/power/station state with `ODM_CmnInfo*` APIs, `ODM_DMInit`, `ODM_DMWatchdog`, `ODM_Write_DIG`, `rtl8723b_set_rssi_cmd`, BT coexistence status, `rtw_hal_get_hwreg`, `rtw_hal_check_rxfifo_full`, and LPS work command scheduling.

## Risks and Edge Cases

`Update_ODM_ComInfo_8723b` hooks `ODM_CMNINFO_MP_MODE` to a local stack variable `zero`, leaving `pDM_Odm->mp_mode` dangling after return; subsequent `odm_TXPowerTrackingInit` dereferences it during the same init sequence, but later use would be unsafe. ODM ability flags are first set to RF-only in fixed init and later expanded in update. Low-power watchdog depends on a valid station for the current BSSID and skips if RSSI is nonpositive. Normal watchdog suppresses some work when firmware is in PS mode.

## Test Signals

Tests should verify ODM fixed fields, support ability masks, all pointer hooks after update, station array clearing, normal watchdog behavior before/after hardware init, BT enabled updates, LPS watchdog RSSI/IGI thresholds, and the lifetime issue around the MP-mode hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_dm.c -->
