# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/leds.c

## Purpose
Implements optional LED class integration for b43legacy. It maps SPROM GPIO LED behavior values to Linux LED class devices and mac80211 LED triggers for TX, RX, association, and radio state.

## Important APIs, Types, and Functions
Public functions are `b43legacy_leds_init` and `b43legacy_leds_exit`. Internal helpers are `b43legacy_led_turn_on`, `b43legacy_led_turn_off`, `b43legacy_led_brightness_set`, `b43legacy_register_led`, `b43legacy_unregister_led`, and `b43legacy_map_led`.

## Control Flow
Initialization reads four GPIO behavior bytes from SPROM. If an entry is `0xFF`, board-specific defaults are supplied for common Compaq and Asus cases. Each behavior is mapped to direct GPIO on/off or to one or more LED class devices with mac80211 default triggers. Brightness callbacks check software radio and hardware RF switch state, then update the GPIO control bit with active-low handling under `wl->leds_lock`. Exit unregisters all registered LEDs and turns them off.

## State and Persistence
Runtime state lives in `dev->led_tx`, `dev->led_rx`, `dev->led_assoc`, and `dev->led_radio`, each holding LED classdev registration data, GPIO index, active-low flag, device pointer, and name. Hardware GPIO output state persists until changed, reset, or cleanup.

## Dependencies and Integration Points
Depends on LED class, mac80211 LED trigger names, SSB SPROM GPIO fields, PCI vendor IDs for fallback mappings, RF-kill helper `b43legacy_is_hw_radio_enabled`, and b43legacy MMIO GPIO accessors.

## Risks
The brightness callback intentionally accepts a small race reading radio state to avoid heavy locking. Multiple behaviors can map one GPIO to both TX and RX LED devices, so registration failures or duplicate state must be handled gracefully. Incorrect SPROM defaults can invert or mislabel LEDs.

## Test Signals
With `CONFIG_B43LEGACY_LEDS`, validate `/sys/class/leds` entries, TX/RX trigger blinking, association/radio triggers, active-low boards, RF-kill radio LED synchronization, and cleanup on module unload. Disabled LED builds should compile via stubs.
