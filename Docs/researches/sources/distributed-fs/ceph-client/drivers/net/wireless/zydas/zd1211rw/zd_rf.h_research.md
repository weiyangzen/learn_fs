# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf.h

## Purpose
Declares RF type IDs, RF write bit widths, `struct zd_rf`, RF callback contracts, common RF operations, and initializer entry points for each supported RF chip.

## Important APIs, Types, And Functions
Defines IDs such as `AL2230_RF`, `AL7230B_RF`, `UW2453_RF`, `AL2230S_RF`, and `RF2959_RF`; `RF_CHANNEL(ch)` table indexing; `RF_REG_BITS`, `RF_VALUE_BITS`, and `RF_RV_BITS`; callback members `init_hw`, `set_channel`, `switch_radio_on`, `switch_radio_off`, `patch_6m_band_edge`, and `clear`; and inline capability checks `zd_rf_should_update_pwr_int()` and `zd_rf_should_patch_cck_gain()`.

## Control Flow
No standalone flow. The header defines how RF implementation files register behavior and how chip code queries RF capabilities during channel calibration and optional patches.

## State And Persistence
`struct zd_rf` persists current channel, RF type, capability flags, private implementation data, and function pointers for the device lifetime.

## Dependencies And Integration Points
Included by chip, MAC, and RF implementation files. The chip object embeds `struct zd_rf` and converts back through `zd_rf_to_chip()`.

## Risks
The callback interface has no NULL checks in hot paths after init. RF private data ownership belongs to the RF implementation's `clear` callback. Incorrect capability flags can double-apply or skip EEPROM calibration.

## Test Signals
Build all RF implementation files, probe hardware with each EEPROM RF ID, and verify RF-specific `clear` paths under disconnect/reset.
