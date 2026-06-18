# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_al2230.c

## Purpose
Implements RF programming for Airoha AL2230 and AL2230S transceivers on ZD1211 and ZD1211B devices. It contains per-channel RF register tables, initialization sequences, channel switching, radio power control, and AL2230S-specific adjustments.

## Important APIs, Types, And Functions
Exports `zd_rf_init_al2230()`. Internal functions include `zd1211_al2230_init_hw()`, `zd1211b_al2230_init_hw()`, `zd1211_al2230_set_channel()`, `zd1211b_al2230_set_channel()`, `zd1211_al2230_switch_radio_on()`, `zd1211b_al2230_switch_radio_on()`, `al2230_switch_radio_off()`, and `zd1211b_al2230_finalize_rf()`. Tables `zd1211_al2230_table` and `zd1211b_al2230_table` hold per-channel RF words; `ioreqs_init_al2230s` patches AL2230S register values.

## Control Flow
Initialization chooses ZD1211 or ZD1211B sequences based on `zd_chip_is_zd1211b()`. Each sequence writes BBP CR tables, optional AL2230S overrides, RF channel/default words, PLL enable/disable sequences, phase-noise/yield fixes, and final CR203/CR240 state. Channel changes write the per-channel RF words and finalize the RF. Radio on/off toggles CR11 and CR251 values appropriate to chip generation.

## State And Persistence
No private heap state. Behavior depends on `chip->al2230s_bit`, `rf.type`, and `chip->new_phy_layout`. `rf->patch_cck_gain` is enabled and `rf->patch_6m_band_edge` points to the generic chip patch.

## Dependencies And Integration Points
Uses chip locked write helpers, RF serial writes, CR register definitions, and RF type from EEPROM POD. Installed through `zd_rf_init_hw()` in the common RF layer.

## Risks
Magic register sequences are vendor-derived and order-sensitive. AL2230S detection combines EEPROM bit and RF type; wrong detection changes band-edge and init values. ZD1211B uses faster CR-based RF writes for many values while original ZD1211 uses USB RF writes; mixing paths would break programming.

## Test Signals
Probe AL2230 and AL2230S devices on both ZD1211 and ZD1211B, switch all channels, test channels 1/11 for band-edge patching, toggle radio, and compare TX power/receive sensitivity against vendor-driver behavior.
