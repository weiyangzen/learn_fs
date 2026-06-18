# sources/distributed-fs/ceph-client/net/mac80211/led.c

## Purpose
`led.c` implements optional `CONFIG_MAC80211_LEDS` trigger support for mac80211 devices. It provides RX, TX, association, radio, and throughput LED triggers; allocates trigger names; registers/unregisters LED triggers; exports trigger-name lookup helpers for drivers; and runs a timer-driven throughput blink policy based on driver-provided throughput thresholds.

## Important APIs, Types, And Functions
Public functions include `ieee80211_led_assoc()`, `ieee80211_led_radio()`, `ieee80211_alloc_led_names()`, `ieee80211_free_led_names()`, `ieee80211_led_init()`, `ieee80211_led_exit()`, and `ieee80211_mod_tpt_led_trig()`. Exported driver-facing helpers include `__ieee80211_get_radio_led_name()`, `__ieee80211_get_assoc_led_name()`, `__ieee80211_get_tx_led_name()`, `__ieee80211_get_rx_led_name()`, and `__ieee80211_create_tpt_led_trigger()`. Static activation/deactivation callbacks maintain atomic active counters, and `tpt_trig_timer()` computes blink timing from traffic deltas.

## Control Flow
Name allocation builds trigger names from `wiphy_name()` plus `rx`, `tx`, `assoc`, and `radio` suffixes. `ieee80211_led_init()` initializes active counters, assigns activation callbacks, and registers each named trigger, freeing failed names. If a throughput trigger was created by a driver, it registers that trigger too. Association/radio updates emit `LED_FULL` or `LED_OFF` only when the corresponding trigger has active users. TX/RX one-shot blinking is inlined in `led.h`. Throughput accounting accumulates bytes through inline helpers, samples once per second, converts deltas to Kbit/s, chooses a blink table entry, and calls `led_trigger_blink()`. `ieee80211_mod_tpt_led_trig()` starts or stops the timer based on radio/work/connected bits and the driver-requested mask.

## State And Persistence
LED state is stored in `struct ieee80211_local`: trigger objects, allocated names, atomic active counters, and optional `struct tpt_led_trigger`. Throughput trigger state persists in the allocated trigger object: name, blink table pointer/length, desired and active type masks, previous traffic count, running flag, timer, and back-pointer to `local`. No state persists beyond hardware unregister; `ieee80211_led_exit()` unregisters triggers and frees the throughput trigger, while `ieee80211_free_led_names()` frees name strings.

## Dependencies And Integration Points
The file depends on the kernel LED trigger subsystem, timers/jiffies, `wiphy_name()`, and mac80211 lifecycle hooks in `main.c` and `iface.c`. Interface idle/radio state calls `ieee80211_mod_tpt_led_trig()`, RX/TX paths call inline byte counters or blink helpers from `led.h`, and drivers can expose trigger names to platform LED configuration through the exported lookup functions.

## Risks And Edge Cases
LED support is optional; callers must tolerate NULL names when allocation or registration fails. Throughput trigger creation warns if called more than once. The blink table is driver-owned const data, so it must outlive the trigger. Byte counters are plain integer fields updated from TX/RX paths while sampled by a timer, so they are approximate rather than strongly synchronized. Timer shutdown uses `timer_delete_sync()` to avoid use-after-free, and throughput blinking is suppressed when the radio bit is inactive even if other wanted states are set.

## Test Signals
Useful checks include builds with and without `CONFIG_MAC80211_LEDS`, trigger registration failure injection, driver calls to exported name helpers, RX/TX blink activity only when active counters are nonzero, association/radio LED transitions, throughput blink table threshold selection, timer start/stop on connected/work/radio transitions, and unregister/free under device removal with timers enabled.
