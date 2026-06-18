# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/rfkill.c

`rfkill.c` implements b43 hardware radio-kill polling. It checks the hardware radio enable bit and synchronizes that state with cfg80211/mac80211 rfkill state and b43 software radio state.

`b43_is_hw_radio_enabled()` reads `B43_MMIO_RADIO_HWENABLED_HI` and returns true when `B43_MMIO_RADIO_HWENABLED_HI_MASK` is clear. `b43_rfkill_poll()` is the mac80211 rfkill poll callback. It converts `ieee80211_hw` to `b43_wl`, locks `wl->mutex`, temporarily powers/enables the device if it is below `B43_STAT_INITIALIZED`, reads the hardware bit, and updates `dev->radio_hw_enable` when changed. It logs the transition, calls `wiphy_rfkill_set_hw_state(hw->wiphy, !enabled)`, and invokes `b43_software_rfkill()` when hardware and software radio state differ.

State persists in `dev->radio_hw_enable`, `dev->phy.radio_on`, rfkill core state, and possibly hardware state changed by software rfkill. Dependencies include b43 bus power management, device enable/disable, status helpers, and mac80211 rfkill registration in `main.c`.

Risks include leaving a down device powered after polling, incorrect lock ordering, and rfkill state drift. Tests should toggle hardware rfkill while the interface is down and started, and cover suspend/resume/powerdown paths.
