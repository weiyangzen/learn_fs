# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-agn-hw.h

## Purpose
Defines legacy AGN hardware constants: RTC instruction/data memory bounds, RSSI offset, retry defaults, transmit-power range, EEPROM/OTP image sizing, and queue count.

## Important APIs, Types, and Functions
Important macros include `IWLAGN_RTC_INST_*`, `IWLAGN_RTC_DATA_*`, `IWL60_RTC_*`, `IWLAGN_RSSI_OFFSET`, retry limits, `IWLAGN_TX_POWER_TARGET_POWER_MIN/MAX`, OTP high/low limits, and `IWLAGN_NUM_QUEUES`.

## Control Flow
No executable flow. Firmware loading and legacy DVM code use these constants to place and size firmware sections and configure old-device retry/power defaults.

## State and Persistence Behavior
All values are compile-time hardware ABI constants. They influence firmware image placement and hardware queue sizing but do not store runtime state.

## Dependencies and Integration Points
Included by `iwl-drv.c` for legacy firmware section offsets and by older AGN/DVM code.

## Risks
Changing addresses or sizes can make firmware uploads land outside RTC memory on legacy devices. Retry/power constants affect behavior across old hardware families.

## Test Signals
DVM firmware load on 5000/6000-era devices, section-size validation, EEPROM/OTP reads, queue setup, and RSSI/power calculations are the relevant signals.
