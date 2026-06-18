# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rfkill.c

## Purpose
This file implements hardware radio-switch polling for RTL8187 devices and reports state to cfg80211/wiphy rfkill.

## Important APIs, Types, And Functions
The public functions are `rtl8187_rfkill_init()`, `rtl8187_rfkill_poll()`, and `rtl8187_rfkill_exit()`. `rtl8187_is_radio_enabled()` reads GPIO state using `priv->rfkill_mask` and is the low-level switch sampler.

## Control Flow
Initialization samples GPIO, logs whether the switch is on or off, sets the wiphy hardware rfkill state to the inverse of enabled, and starts wiphy rfkill polling. mac80211 calls `rtl8187_rfkill_poll()` through `rtl8187_ops.rfkill_poll`; the poll locks `conf_mutex`, resamples the switch, logs transitions, and updates wiphy rfkill state. Exit stops polling.

## State And Persistence
`priv->rfkill_mask` is selected during probe from product ID and EEPROM GPIO selection. `priv->rfkill_off` stores the last sampled enabled state. Hardware state lives in GPIO0/GPIO1 bits.

## Dependencies And Integration Points
It depends on `rtl8187.h` for private state and register I/O, and on mac80211/cfg80211 wiphy rfkill APIs. `dev.c` initializes the mask, calls init/exit, and exposes the poll callback in `ieee80211_ops`.

## Risks
The field name `rfkill_off` stores enabled/on state, which is easy to misread. Sampling writes GPIO0 with the mask cleared before reading GPIO1, so GPIO side effects must match the hardware design. Wrong mask selection for 8197/8198 variants will invert or miss the hardware switch. Polling is serialized with `conf_mutex`, but long register I/O delays could still interact with stop/disconnect timing.

## Test Signals
Test physical switch transitions on RTL8187/8189/8197/8198-style devices, verify `rfkill list` state, check logs for on/off transitions, confirm blocked devices stop association/TX via mac80211, and ensure polling stops before disconnect frees the hardware.
