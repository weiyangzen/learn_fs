# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_data.h

Purpose: this header defines the RTL8723B HAL private state stored behind `adapter->HalData`, including firmware, chip identity, PHY/channel, EFUSE/EEPROM, TX power, RF, beacon, antenna, SDIO, dynamic-management, ODM, and BT coexistence state.

Important APIs/types/macros: enums define multi-function support, polarity, regulator mode, and AMPDU burst mode. `struct dm_priv` stores dynamic-management and calibration state, including RSSI/PWDB smoothing, thermal values, IQK backups, Tx power tracking state, EDCA turbo history, and `INIDATA_RATE[32]`. `struct hal_com_data` is the main state object, with fields for version, firmware version/signature, current channel/bandwidth/side channel, basic rates, receive config, RF chip/path/package, EEPROM-derived customer/regulatory/BT/power/thermal/crystal data, TX power tables and limits, RF register definitions, channel register cache, beacon register shadows, antenna path/diversity, power-down, SDIO endpoint/free-page/OQT/RX FIFO state, ODM private state, BT coexistence, and interrupt masks. Macros include `GET_HAL_DATA` and RF path helpers.

Control flow and integration: almost every file in the subset reads or writes this structure. Firmware download fills firmware fields; chip-version and EFUSE parsing fill identity and calibration inputs; PHY config consumes RF/channel/TX power fields; SDIO init populates endpoint and FIFO state; TX/RX paths consume receive config, rate-control, and SDIO page state.

State and persistence: this is the central in-memory persistence object for one adapter. It persists from HAL data allocation through adapter teardown and mirrors selected hardware state so transitions can restore or update registers safely.

Dependencies: includes ODM precompilation headers, BT coexistence, and SDIO HAL declarations. Many fields depend on constants from RF, TX power, EFUSE, and SDIO headers.

Risks and test signals: field coupling is high; uninitialized fields can affect firmware commands, PHY power, SDIO resource accounting, and RX filters. Tests should include default-value initialization, EFUSE autoload success/failure, firmware download, channel/bandwidth switching, TX power calculations, free-page/OQT accounting, BT coexistence, and teardown/reinit cycles.
