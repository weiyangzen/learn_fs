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
