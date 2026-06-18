# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/wow.c

## Purpose
`wow.c` connects cfg80211/mac80211 Wake-on-Wireless support to ath9k hardware. It advertises supported triggers, programs default deauth/disassoc and user packet patterns, enters low-power WoW mode on suspend, restores interrupts/work on resume, and configures device wakeup capability.

## Important APIs, types, and functions
`ath9k_init_wow()` publishes `wiphy->wowlan` capabilities when PCI WoW or `force_wow` is enabled, selecting legacy or newer pattern count by chip revision. `ath9k_suspend()` is the main suspend entry point. `ath9k_resume()` restores interrupts and calls `ath9k_hw_wow_wakeup()`. `ath9k_set_wakeup()` toggles device wakeup. Helpers include `ath9k_wow_map_triggers()`, `ath9k_wow_add_disassoc_deauth_pattern()`, and `ath9k_wow_add_pattern()`.

## Control flow and integration
Suspend deinitializes channel context, locks `sc->mutex`, rejects invalid devices, missing triggers, multi-vif, multi-channel, or unassociated STA state, maps triggers, cancels work/ANI, wakes hardware, stops BT coexistence, programs mandatory deauth/disassoc patterns in slots 0 and 1, programs user patterns starting at slot 2, saves the old interrupt mask, enables only beacon-miss/global interrupts for sleep, synchronizes IRQ/tasklet shutdown, enables hardware WoW, restores power-save, and sets `ATH_OP_WOW_ENABLED`. Resume wakes hardware, restores `wow_intr_before_sleep`, obtains wake status, restarts work and BT coexistence, clears the WoW flag, and restores power-save.

## State and persistence behavior
Software state includes `sc->wow_intr_before_sleep`, `ATH_OP_WOW_ENABLED`, device wakeup enablement, and wiphy WoW capability pointers. Hardware state includes pattern slots, trigger enables, interrupt masks, and wake status across suspend.

## Dependencies
The file depends on cfg80211 WoW structs, mac80211 suspend/resume hooks, ath9k HAL WoW functions, interrupt/tasklet synchronization, power-save helpers, BT coexistence start/stop, and current BSSID state in `ath_common`.

## Risks
Risks include false wakes from broad masks, missed wakes if pattern/mask construction is wrong, failure paths after work/BT coexistence have been stopped, suspend returning `1` for unsupported runtime conditions, and lack of multi-vif/multi-channel WoW support. Pattern slots 0 and 1 are reserved for disconnect detection, so user pattern accounting must stay aligned with advertised capabilities.

## Test signals
Signals include cfg80211 WoW capability visibility, suspend rejection for unsupported states, magic packet wake, user pattern wake, deauth/disassoc wake, beacon miss wake, restored interrupt masks after resume, and no lost network work/BT coexistence after repeated cycles.
