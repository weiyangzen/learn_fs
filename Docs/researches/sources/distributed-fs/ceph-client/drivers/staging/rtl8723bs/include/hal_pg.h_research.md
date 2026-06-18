<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pg.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pg.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pg.h` declares efuse/EEPROM programming helpers and constants for parsing RTL8723B package data, MAC address, regulatory values, thermal meter, transmit power indexes, and Bluetooth coexistence efuse sections. The source was reviewed as a complete 69-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `EFUSE_ShadowMapUpdate`, `EFUSE_ShadowRead`, `EFUSE_ShadowWrite`, `Hal_EfuseParseIDCode`, `Hal_ReadPROMVersion`, `Hal_ReadPowerSavingMode`, `Hal_ReadTxPowerInfo8723B`, `Hal_ReadBoardType8723B`, `Hal_EfuseParseBTCoexistInfo`, and related `Hal_EfuseParse*` routines.

## Control Flow

During adapter bring-up, efuse content is loaded into a shadow map and parser helpers extract board and RF calibration values before PHY, MAC, power, and coexistence configuration use them.

## State and Persistence Behavior

The parsed values populate `eeprompriv`, HAL data, MAC address fields, per-rate power tables, channel plan, customer ID, and BT coexistence flags. The header itself does not persist data.

## Dependencies and Integration Points

Integrates with efuse access in `rtw_efuse.h`, chip configuration in `rtl8723b_hal.h`, and PHY power code in `hal_phy_cfg.h`. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Autoload failure paths must use sane defaults. Bad offset parsing corrupts transmit power limits, regulatory behavior, or MAC identity. BT coexistence fields can change RF scheduling behavior.

## Test Signals

Probe with valid and simulated autoload-fail efuse maps, verify MAC/channel plan/power table parsing, and run RF calibration plus BT coexistence smoke checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pg.h -->
