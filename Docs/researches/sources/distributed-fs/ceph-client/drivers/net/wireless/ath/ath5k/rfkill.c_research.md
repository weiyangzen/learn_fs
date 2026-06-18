# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/rfkill.c

Purpose: Implements ath5k hardware rfkill GPIO setup, interrupt toggling, and mac80211/cfg80211 hardware-rfkill state reporting.

Important APIs and functions: `ath5k_rfkill_hw_start()` reads EEPROM rfkill GPIO and polarity, initializes a tasklet, drives the rfkill output to the unblocked state, and enables GPIO interrupt if the EEPROM header advertises rfkill. `ath5k_rfkill_hw_stop()` disables the interrupt, kills the tasklet, and drives the GPIO to the blocked state so the Wi-Fi LED turns off. Static helpers drive GPIO output high/low according to polarity, configure GPIO interrupt edge, read blocked state, and report changes through `wiphy_rfkill_set_hw_state()`.

Control flow: Start copies EEPROM config into `ah->rf_kill`, sets up `toggleq`, disables rfkill by writing the inverse polarity, then arms GPIO interrupt edge detection. On GPIO interrupt, the tasklet reads current GPIO state and reports blocked/unblocked state to the wiphy. Stop disables interrupt edge handling, synchronously kills the tasklet, and asserts rfkill.

State and persistence: Mutates `ah->rf_kill.gpio`, `ah->rf_kill.polarity`, and the tasklet lifecycle. It changes hardware GPIO direction, output value, and interrupt polarity. The EEPROM configuration is persistent but only read here; runtime rfkill state is reflected to cfg80211/rfkill core.

Dependencies and integration points: Depends on ath5k GPIO helpers, EEPROM capability macros, tasklet infrastructure, `struct ieee80211_hw`/wiphy rfkill integration, and driver interrupt handling that schedules `toggleq`.

Risks: The code comments that configuring GPIO input can disable rfkill on some hardware, so state reads avoid reconfiguring direction in `ath5k_is_rfkill_set()`. Wrong polarity can invert regulatory/user-visible block state. Interrupt edge selection uses current GPIO state and must be updated when enabling/disabling to catch toggles reliably.

Test signals: Toggle the physical rfkill switch, verify cfg80211/rfkill state changes, confirm no toggles after stop, test EEPROM absent/present rfkill headers, validate polarity on devices with active-high and active-low switches, and confirm LED/off behavior on shutdown.
