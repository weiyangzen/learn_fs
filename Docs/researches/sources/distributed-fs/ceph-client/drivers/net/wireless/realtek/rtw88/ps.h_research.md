# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/ps.h

## Purpose
`ps.h` declares the power-save API for `rtw88` and defines the constants used for LPS thresholds, RPWM/CPWM power-mode bits, and leave-LPS timeout behavior. It is the narrow header through which core, transport, and mac80211-facing code coordinate IPS, LPS, and deep LPS transitions.

## Important APIs, Types, and Functions
- Policy/timing constants: `RTW_LPS_THRESHOLD`, `LEAVE_LPS_TRY_CNT`, and `LEAVE_LPS_TIMEOUT`.
- RPWM power bits: `POWER_MODE_ACK`, `POWER_MODE_PG`, `POWER_TX_WAKE`, and `POWER_MODE_LCLK`.
- IPS declarations: `rtw_enter_ips()` and `rtw_leave_ips()`.
- LPS/deep LPS declarations: `rtw_power_mode_change()`, `rtw_enter_lps()`, `rtw_leave_lps()`, `rtw_leave_lps_deep()`, `rtw_get_lps_deep_mode()`, and `rtw_recalc_lps()`.

## Control Flow
The header is consumed by `main.c` watchdog and scan/IPS paths, by `pci.c` deep/link power-save handling, and by any chip/backend code that needs to request or exit power-save states. Callers use `rtw_recalc_lps()` to update policy from vif state, `rtw_enter_lps()`/`rtw_leave_lps()` for runtime station power save, and `rtw_enter_ips()`/`rtw_leave_ips()` for full idle power-down/up.

## State and Persistence Behavior
The constants in this header shape runtime state stored in `struct rtw_dev`: traffic thresholds decide whether watchdog can enter LPS, power bits are written to HCI RPWM registers, and leave timeout constants bound firmware wait behavior. The header itself has no storage.

## Dependencies and Integration Points
`ps.h` assumes `struct rtw_dev`, `struct ieee80211_vif`, bit helpers, and `msecs_to_jiffies()` are available through including context. It integrates power-save code with firmware feature checks, HCI backends, coexistence notifications, and mac80211 vif power-save settings.

## Risks
- Timeout and retry constants are policy choices; too low can force false firmware failure handling, while too high can stall callbacks.
- Bit definitions must match firmware RPWM/CPWM protocol. Incorrect bits can prevent wake or deep-sleep entry.
- Public APIs require the locking discipline implemented in `ps.c`; the header does not encode that requirement.

## Test Signals
- Build inclusion from core and HCI backends.
- LPS entry threshold behavior under watchdog traffic counters.
- Firmware wake/ack behavior using both C2H and register-poll leave checks.
- Deep LPS with PG and TX wake firmware features.
