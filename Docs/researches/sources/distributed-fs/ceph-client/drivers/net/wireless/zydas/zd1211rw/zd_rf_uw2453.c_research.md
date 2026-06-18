# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_uw2453.c

## Purpose
Implements Ubec UW2453/Maxim-new RF programming with documented synthesizer/VCO configuration, PLL lock probing, autocal fallback, per-channel tuning, and per-channel TX gain derived from EEPROM integration values.

## Important APIs, Types, And Functions
Exports `zd_rf_init_uw2453()`. Key helpers include `uw2453_synth_set_channel()`, `uw2453_write_vco_cfg()`, `uw2453_init_mode()`, `uw2453_set_tx_gain_level()`, `uw2453_init_hw()`, `uw2453_set_channel()`, `uw2453_switch_radio_on()`, `uw2453_switch_radio_off()`, and `uw2453_clear()`. Tables encode standard/autocal synth values, divide ratios, VCO configs, and TX gain values. `struct uw2453_priv` stores the selected VCO configuration index, with `-1` meaning autocal.

## Control Flow
Initialization writes BBP defaults, initial RF mode/filter/gain words, enters calibration modes, then iterates standard VCO configurations on channel 1. It clears and reads `UW2453_INTR_REG` to detect PLL lock, stores the next configuration after the one that locked, or falls back to autocal. Channel changes program synth/divide values, choose VCO config or autocal, enter RX/TX mode, write common CR values, update TX gain from EEPROM integration table, and set CR203. Radio on enters RX/TX mode and chooses CR251 value by chip generation; radio off enters idle and powers PLL down.

## State And Persistence
Allocates `rf->priv` as `struct uw2453_priv` and frees it through `uw2453_clear()`. Disables common chip channel-integration updates because it manages TX gain itself. Hardware state includes selected VCO, synth, TX gain, and RF mode registers.

## Dependencies And Integration Points
Uses locked chip IO, RF serial writes, EEPROM `pwr_int_values`, and `UW2453_INTR_REG` from the chip header. Selected for `MAXIM_NEW_RF` and `UW2453_RF`.

## Risks
PLL lock probing and use of the next VCO table entry are subtle vendor-compatible behavior. If no lock is detected, autocal behavior differs from standard tables. Out-of-range EEPROM integration values silently skip TX gain programming. Private allocation failure prevents RF init.

## Test Signals
Probe UW2453/MAXIM_NEW devices, confirm PLL lock or autocal debug path, switch all channels, validate TX gain from EEPROM values including high indices, run reset/disconnect to verify `uw2453_clear()`, and test radio off/on.
