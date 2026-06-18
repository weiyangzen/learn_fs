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
