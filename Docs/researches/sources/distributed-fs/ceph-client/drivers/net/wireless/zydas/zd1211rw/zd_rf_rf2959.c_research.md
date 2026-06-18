# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_rf2959.c

## Purpose
Implements RF programming for RFMD RF2959 transceivers on original ZD1211 devices. It initializes BBP/RF registers, programs per-channel synthesizer values, and toggles radio power.

## Important APIs, Types, And Functions
Exports `zd_rf_init_rf2959()`. Internal functions include `rf2959_init_hw()`, `rf2959_set_channel()`, `rf2959_switch_radio_on()`, and `rf2959_switch_radio_off()`. `rf2959_table` maps channels to two RF words. A disabled debug block decodes RF2959 register-write bitfields for diagnostics.

## Control Flow
`zd_rf_init_rf2959()` rejects ZD1211B with `-ENODEV`, then installs callbacks. Hardware init writes a CR table and a default RF register vector. Channel switching writes the two per-channel RF words. Radio on/off writes CR10/CR11 combinations specific to RF2959.

## State And Persistence
No private heap state or special capability flags. Hardware RF/BBP register state persists until channel change, radio power change, or reset.

## Dependencies And Integration Points
Uses chip locked IO and RF serial write helpers. Selected from EEPROM RF ID `RF2959_RF` by the common RF layer.

## Risks
RF2959 is not supported for ZD1211B. Some register choices are documented as departures from vendor defaults to avoid CTS/TX continuation issues. The table includes comments about undocumented/bogus RF register references, which increases regression risk.

## Test Signals
Probe original ZD1211 RF2959 hardware, verify ZD1211B rejection, switch all channels including 14, run TX/RX stability tests, and check radio off/on recovery.
