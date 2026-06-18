# sources/distributed-fs/ceph-client/net/mac80211/led.h

## Purpose
`led.h` is the internal abstraction layer for mac80211 LED support. It exposes lightweight TX/RX and throughput accounting helpers to hot paths while compiling them to no-ops when LED support is disabled, and it declares the lifecycle and state-change functions implemented in `led.c`.

## Important APIs, Types, And Functions
The always-visible inline helpers are `ieee80211_led_rx()`, `ieee80211_led_tx()`, `ieee80211_tpt_led_trig_tx()`, and `ieee80211_tpt_led_trig_rx()`. Under `CONFIG_MAC80211_LEDS`, the header declares `ieee80211_led_assoc()`, `ieee80211_led_radio()`, `ieee80211_alloc_led_names()`, `ieee80211_free_led_names()`, `ieee80211_led_init()`, `ieee80211_led_exit()`, and `ieee80211_mod_tpt_led_trig()`. Without LED support, those functions become empty inlines.

## Control Flow
TX/RX blink helpers check the corresponding atomic active counter before calling `led_trigger_blink_oneshot()` with `MAC80211_BLINK_DELAY`. Throughput helpers check `tpt_led_active` and add byte counts to the throughput trigger counters. The rest of the lifecycle control flow is delegated to `led.c`; this header ensures callers do not need conditional compilation around each LED update site.

## State And Persistence
The header does not own storage, but it directly accesses `ieee80211_local` LED trigger fields and atomic active counters. Throughput byte counters accumulate in `local->tpt_led_trigger` until sampled by the timer in `led.c`. When LED support is disabled, no LED state is read or updated.

## Dependencies And Integration Points
The header includes list, spinlock, LED subsystem headers, and `ieee80211_i.h` for `struct ieee80211_local`. It is used by RX/TX paths, interface/radio state logic, and hardware allocation/registration cleanup. It hides `CONFIG_MAC80211_LEDS` from most callers and keeps hot-path overhead to atomic reads plus simple counter updates when enabled.

## Risks And Edge Cases
Because inline helpers are used from hot paths, they must remain cheap and must not sleep. Throughput helpers assume `local->tpt_led_trigger` exists when `tpt_led_active` is nonzero, which is established by registration ordering in `led.c`. Any future change to activation ordering must preserve that invariant. Disabled LED builds should be tested because many functions become no-ops and unused fields may otherwise hide build issues.

## Test Signals
Compile coverage with `CONFIG_MAC80211_LEDS=y` and `n` is the primary signal. Runtime tests should confirm TX/RX paths do not crash before trigger activation, throughput byte counters increment only while active, and callers can invoke lifecycle/state helpers unconditionally in both configurations.
