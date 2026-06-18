# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ps.c

## Purpose
`ps.c` implements rtw89 runtime power-save behavior. It coordinates leisure power save (LPS), low-power MAC/HCI modes, idle power save (IPS), Bluetooth coexistence notifications, firmware H2C/C2H acknowledgement checks, P2P Notice of Absence programming, and one-shot NoA duration tracking. The file bridges mac80211 power-save policy and VIF state with Realtek firmware commands and hardware power-mode transitions.

## Important APIs and functions
- `__rtw89_enter_ps_mode()` and `__rtw89_leave_ps_mode()` set or clear `RTW89_FLAG_LOW_POWER_MODE` and call the chip/MAC/HCI power-mode transition path when `rtwdev->ps_mode` is enabled.
- `rtw89_enter_lps()` enters firmware LPS for each link of a VIF, sends RF PS and multi-link/channel information, notifies BTC that radio control is firmware-owned, and optionally enters low-power mode.
- `rtw89_leave_lps()` exits LPS globally, leaves low-power mode first, reinitializes PHY dynamic mechanisms, sends active LPS parameters to station/P2P-client links, restores BTC radio state, applies digital power compensation, and reinitializes TRX protection.
- `rtw89_enter_ips()` and `rtw89_leave_ips()` implement idle power save by deinitializing/reinitializing VIF MAC state around `rtw89_core_stop()` and `rtw89_core_start()`.
- `rtw89_recalc_lps()` enables LPS only for a single station VIF with mac80211 PS enabled and disables it for MCC or non-station/multiple-VIF combinations.
- Firmware check helpers `rtw89_fw_receive_lps_h2c_check()` and `rtw89_fw_leave_lps_check()` validate LPS leave acknowledgement through C2H register features and MAC PS status polling, incrementing `ps_hang_cnt` and notifying SER after repeated hangs.
- P2P functions `rtw89_process_p2p_ps()`, `rtw89_p2p_disable_all_noa()`, `rtw89_p2p_noa_renew()`, `rtw89_p2p_noa_append()`, and `rtw89_p2p_noa_fetch()` maintain firmware NoA state and construct P2P NoA IEs.
- `rtw89_p2p_noa_once_init()`, `_deinit()`, and `_recalc()` manage delayed work that tracks finite NoA windows and restores beacon-filter configuration when the duration ends.

## Control flow and state behavior
LPS entry starts by atomically setting `RTW89_FLAG_LEISURE_PS`; a second entry attempt returns immediately. Each VIF link receives a legacy PS H2C parameter with its MAC ID and `RTW89_LAST_RPWM_PS`. P2P client links suppress the additional low-power MAC/HCI mode because the code keeps `can_ps_mode` false for that role. After link-level commands, the driver sends RF PS info plus one of the firmware-supported LPS channel or multi-link info formats. If requested and allowed, the driver enters low-power mode, which may switch HCI mode on chips whose `low_power_hci_modes` include the current `ps_mode` and when WoWLAN is not active.

LPS leave clears `RTW89_FLAG_LEISURE_PS`; if it was not set, leave is a no-op. The function exits low-power mode first, then calls `rtw89_phy_dm_reinit()` before sending active LPS parameters per station or P2P-client link. The firmware checks persist hang state in `rtwdev->ps_hang_cnt`; successful leave resets it to zero, while repeated timeout or bad-ack paths can trigger SER assertion recovery. Runtime state is kept in device flags, `ps_mode`, `lps_enabled`, per-link MAC IDs, per-link NoA state, and firmware feature flags.

IPS is deeper than LPS. Entry sets `RTW89_FLAG_INACTIVE_PS`, skips shutdown if already powered off, deinitializes all VIF links at the MAC layer, then stops the core. Leave refuses to run if already powered on, starts the core, sets the channel, initializes VIF links again, and clears inactive PS. P2P NoA state is separate: recurring NoA descriptors are pushed to firmware, while finite one-shot windows are calculated against hardware TSF, merged with any still-active previous window, and scheduled as wiphy delayed work to toggle `noa_once->in_duration` and beacon filtering.

## Dependencies and integration points
`ps.c` includes `chan.h`, `coex.h`, `core.h`, `debug.h`, `fw.h`, `mac.h`, `phy.h`, `ps.h`, `reg.h`, `ser.h`, and `util.h`. It integrates with mac80211 queues and NAPI during HCI mode switches, firmware H2C commands for LPS/P2P/beacon filters, MAC power and VIF lifecycle functions, PHY dynamic-mechanism reinitialization, Bluetooth coexistence radio-state notifications, SER recovery, RCU-protected BSS configuration access, TSF reads, and wiphy delayed work. Locking expectations are explicit on public paths that require the wiphy lock.

## Risks and edge cases
- Firmware feature negotiation controls acknowledgement and LPS-info formats. A mismatch can skip necessary checks or send an unsupported command format.
- Leave-LPS polling uses per-MACID bit slicing of `mac->ps_status`; incorrect MAC ID or register definitions can produce false hangs.
- `rtw89_ps_power_mode_change_with_hci()` briefly stops queues, flushes TX work, pauses HCI, switches MAC/HCI mode, and schedules NAPI on leave; ordering regressions can lose or stall packets.
- `rtw89_recalc_lps()` deliberately disables LPS for MCC, multiple VIFs, or non-station roles. New interface combinations need careful policy review.
- IPS leave logs `rtw89_core_start()` failure but still proceeds to channel and VIF initialization, which may rely on lower layers tolerating a failed start.
- One-shot NoA timing truncates delays to `UINT_MAX` microseconds and warns on unhandled far-future begin times; long or wrapped schedules may be approximated.

## Test signals
Signals include successful association with mac80211 PS causing `lps_enabled`, clean LPS enter/leave H2C traces, `ps_hang_cnt` staying at zero, no SER assertion during repeated suspend/resume or PS toggles, queues resuming after HCI low-power mode leave, IPS entry powering down the core only while idle, IPS leave restoring channel and VIF MAC state, BTC radio-state notifications matching LPS transitions, P2P NoA firmware commands matching BSS config, and beacon filtering restored after finite NoA windows.
