# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/rfkill.c

## Purpose
Implements hardware radio-enable detection and mac80211 rfkill polling for b43legacy. It reads the card-specific hardware switch state, updates cfg80211/mac80211 rfkill state, and turns the radio on or off to match the switch.

## Important APIs, Types, and Functions
`b43legacy_is_hw_radio_enabled()` reads high or low hardware-enable registers depending on core revision and handles early resume/not-started cases. `b43legacy_rfkill_poll()` powers up the SSB device temporarily if needed, reads the switch, updates `dev->radio_hw_enable`, calls `wiphy_rfkill_set_hw_state()`, and invokes `b43legacy_radio_turn_on()` or `b43legacy_radio_turn_off()`.

## Control Flow, State, and Persistence
Polling runs under `wl->mutex`. If the device is not initialized, it uses `ssb_bus_powerup()` and `ssb_device_enable()` for a temporary register read, then disables/powers down again. Persistent state is `dev->radio_hw_enable` and `dev->phy.radio_on`; rfkill state is held in the wiphy.

## Dependencies and Integration Points
Depends on SSB bus power management, b43legacy status checks, MMIO hardware-enable registers, radio on/off routines, and cfg80211 rfkill state. It is called through mac80211 rfkill polling.

## Risks and Test Signals
Risks include reading unavailable registers during early resume, leaving SSB powered, wrong active-low semantics between revision families, or desynchronizing rfkill and actual radio power. Test hardware switch toggles before start, while associated, during suspend/resume, and on both pre-rev3 and newer cores.
