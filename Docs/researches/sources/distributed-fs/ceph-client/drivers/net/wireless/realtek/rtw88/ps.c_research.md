# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/ps.c

## Purpose
`ps.c` implements idle power save (IPS), leisure power save (LPS), deep LPS coordination, firmware power-mode acknowledgement, and LPS recalculation for the `rtw88` core. It bridges core lifecycle (`rtw_core_start/stop()`), HCI link/deep power-save hooks, firmware H2C power-mode commands, coexistence notifications, port restoration, and mac80211 vif power-save state.

## Important APIs, Types, and Functions
- IPS APIs: `rtw_enter_ips()` and `rtw_leave_ips()`, with helper `rtw_ips_pwr_up()`.
- Firmware/HCI power toggle: `rtw_power_mode_change()`.
- LPS helpers: `rtw_enter_lps()`, `rtw_leave_lps()`, `rtw_leave_lps_deep()`, `rtw_get_lps_deep_mode()`, `rtw_enter_lps_core()`, `rtw_leave_lps_core()`, and deep LPS helpers.
- Firmware leave-LPS validation: register polling fallback and C2H completion path through `rtw_fw_leave_lps_check()`.
- LPS policy recomputation: `rtw_recalc_lps()` and vif iterator helpers.

## Control Flow
IPS entry checks `RTW_FLAG_POWERON`; if powered, it notifies coexistence, stops core, and allows HCI link power save. IPS leave disables HCI link power save, powers the device back up through `rtw_core_start()`, notifies coexistence, restores the operating channel, and rewrites all vif port configuration registers.

LPS entry is called with `rtwdev->mutex` held. It ignores requests when coexistence forces LPS control, sets `lps_conf.mode` and port, programs LPS state (`RTW_RF_OFF`, awake interval, RLBM, smart PS), notifies coexistence, sends firmware power mode, enters HCI link PS, sets `RTW_FLAG_LEISURE_PS`, and then optionally enters deep PS. Deep PS is allowed only after LPS and only when the selected firmware/chip deep mode is not `NONE`; PG mode sends page information before HCI deep PS.

LPS leave first leaves deep PS, then if LPS is active switches mode to active, sets all-on state and active firmware parameters, disables HCI link PS, prepares C2H completion if supported, sends firmware power mode, waits for firmware to complete leave-LPS either by C2H or by polling `REG_TCR`, clears `RTW_FLAG_LEISURE_PS`, and notifies coexistence. On timeout, it clears the firmware power-management bit directly and dumps firmware debug info.

`rtw_recalc_lps()` counts vifs, treating any non-station interface or more than one station as disqualifying. Only exactly one station vif with `cfg.ps` enables LPS; otherwise it disables PS and forces LPS leave.

## State and Persistence Behavior
`ps.c` mutates `rtwdev->lps_conf`, `rtwdev->ps_enabled`, `RTW_FLAG_LEISURE_PS`, `RTW_FLAG_LEISURE_PS_DEEP`, and HCI link/deep power-save state. IPS and LPS are runtime hardware/firmware states only. `lps_leave_check` is a completion reused across leave-LPS operations when firmware advertises C2H support. Port register configuration is restored from persistent `rtw_vif` fields after IPS leave.

## Dependencies and Integration Points
This file depends on core lifecycle (`main.c`), HCI power hooks, firmware H2C power-mode/page-info commands, register definitions, MAC port configuration, coexistence notifications, debug logging, and mac80211 vif iteration. PCI implements `deep_ps` and `link_ps`; USB/SDIO backends provide equivalent HCI hooks.

## Risks
- `rtw_power_mode_change()` uses RPWM/CPWM toggle semantics and atomic polling. A missed firmware ack indicates severe hardware/firmware lockup and currently triggers warnings plus debug dumps.
- Entering deep PS before LPS or with active TX/DMA is unsafe; transport backends must enforce their side of the contract.
- IPS leave restores port configuration after full core restart; missing vif fields or ordering bugs can leave MAC/BSSID/net type stale.
- `rtw_recalc_lps()` is conservative: AP or multiple station interfaces disable LPS. Changes to multi-vif support must revisit firmware constraints.
- Several public functions assert `rtwdev->mutex` is held. Calling them unlocked can race watchdog, scan, mac80211 callbacks, or transport IRQ paths.

## Test Signals
- Idle transition into IPS and wake from scan/association with channel and port config restored.
- Single station with PS enabled entering and leaving LPS under watchdog traffic thresholds.
- Multi-vif, AP, and non-station cases disabling LPS and forcing leave.
- Firmware variants with `FW_FEATURE_LPS_C2H` and without it, validating both completion and register-poll leave checks.
- Deep LPS modes `NONE`, `LCLK`, and `PG`, including WoWLAN firmware mode selection.
- Forced firmware ack timeout path producing warnings and debug dump without deadlocking.
