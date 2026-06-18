<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_eeprom.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_eeprom.h` defines EEPROM/efuse constants, customer IDs, channel-plan defaults, and the `eeprom_priv` structure that stores parsed autoload and calibration information. The source was reviewed as a complete 118-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct eeprom_priv`, `EEPROM_*` offsets/sizes, `EEPROM_Default_*` values, `enum RT_CUSTOMER_ID`, and helpers/fields for MAC address, channel plan, thermal meter, TX power, regulatory, and Bluetooth coexistence data.

## Control Flow

HAL probe reads efuse/EEPROM shadow data, populates `eeprom_priv`, and later PHY, regulatory, MAC-address, and coexistence code consume the parsed fields.

## State and Persistence Behavior

`eeprom_priv` is persistent per adapter for the device lifetime and is the software copy of nonvolatile board configuration.

## Dependencies and Integration Points

Connected to `hal_pg.h`, `rtw_efuse.h`, `rtl8723b_hal.h`, PHY power configuration, and regulatory/cfg80211 setup. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Defaults on autoload failure must be conservative. Wrong power/channel/customer parsing can violate regulatory rules or break board-specific RF behavior.

## Test Signals

Efuse read with real hardware, autoload-failure fallback, MAC/channel/power table validation, and customer/channel-plan variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_eeprom.h -->
