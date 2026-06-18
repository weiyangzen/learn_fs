# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/led.c

## Purpose
`led.c` integrates ath5k GPIO LEDs with the Linux LED subsystem. It contains a PCI subsystem-device quirk table mapping known laptops/cards to LED GPIO pin and polarity, registers RX/TX LED class devices with mac80211 default triggers, and provides enable/disable/off helpers used during init, remove, suspend, and resume.

## Important APIs and Control Flow
The `ath5k_led_devices[]` table stores matches with encoded `driver_data`; `ATH_PIN()` and `ATH_POLARITY()` unpack it. `ath5k_init_leds()` exits if `CONFIG_MAC80211_LEDS` is disabled or no PCI device is present, matches quirks with `pci_match_id()`, sets `ATH_STAT_LEDSOFT`, configures `ah->led_pin` and `ah->led_on`, calls `ath5k_led_enable()`, then registers `ath5k-%s::rx` and `ath5k-%s::tx` LEDs.

`ath5k_led_enable()` sets the selected GPIO as output and turns it off. `ath5k_led_brightness_set()` maps LED core brightness to `ath5k_led_on()` or `ath5k_led_off()`. `ath5k_unregister_leds()` unregisters RX and TX devices and turns LEDs off. All LED operations check `CONFIG_MAC80211_LEDS` and/or `ATH_STAT_LEDSOFT`.

## State, Dependencies, and Integration
State is stored in `ah->status` bit `ATH_STAT_LEDSOFT`, `ah->led_pin`, `ah->led_on`, and `struct ath5k_led` instances for RX/TX. Dependencies include PCI IDs, the LED class API, mac80211 LED trigger names, GPIO helpers from `gpio.c`, and `wiphy_name()` for naming. Integration points are `ath5k_init_ah()`/deinit through base code and PCI suspend/resume through `ath5k_led_off()`/`ath5k_led_enable()`.

## Risks and Test Signals
Risks include incomplete quirk coverage, wrong polarity causing inverted LED behavior, partial registration failure leaving one LED active, and GPIO conflicts with RFKill or platform wiring. Test signals include correct LED class devices under sysfs, RX/TX triggers toggling the physical LED, off state on unregister/suspend, restored state on resume, and no LED registration attempts on non-PCI/AHB builds.
