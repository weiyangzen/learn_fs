# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf.c

## Purpose
Provides the common RF transceiver abstraction for ZD1211RW. It maps EEPROM RF type IDs to names and RF-specific initializer modules, installs per-RF callbacks, and wraps channel/radio operations with chip PHY-register locking.

## Important APIs, Types, And Functions
Exports `zd_rf_name()`, `zd_rf_init()`, `zd_rf_clear()`, `zd_rf_init_hw()`, `zd_rf_scnprint_id()`, `zd_rf_set_channel()`, `zd_switch_radio_on()`, `zd_switch_radio_off()`, `zd_rf_patch_6m_band_edge()`, and `zd_rf_generic_patch_6m()`. It dispatches to `zd_rf_init_rf2959()`, `zd_rf_init_al2230()`, `zd_rf_init_al7230b()`, and `zd_rf_init_uw2453()`.

## Control Flow
`zd_rf_init()` defaults `update_channel_int` on. During chip init, `zd_rf_init_hw()` selects an RF implementation by type, stores the type, locks PHY registers, calls the RF `init_hw` callback, then unlocks. Later channel and radio state calls validate channel range and invoke installed callbacks under the chip mutex and, for radio on/off, PHY lock/unlock.

## State And Persistence
`struct zd_rf` stores RF type, current channel, capability bits, optional private data, and callback pointers. The RF-specific register programming persists in hardware until channel changes, radio state changes, or device reset.

## Dependencies And Integration Points
Depends on `zd_chip` for lock/register helpers and `zd_mac.h` for channel bounds. Integrated from `zd_chip_init_hw()` after EEPROM POD parsing.

## Risks
Unsupported RF IDs fail probe. Callback pointers must be installed correctly before `zd_rf_init_hw()` calls `rf->init_hw`. Channel validation only enforces 1..14, not regulatory permissions. The RF abstraction assumes callers already hold `chip->mutex`.

## Test Signals
Probe each supported RF, verify unsupported IDs return `-ENODEV`, switch channels 1..14, toggle radio on/off, and inspect debug identity strings for correct RF names.
