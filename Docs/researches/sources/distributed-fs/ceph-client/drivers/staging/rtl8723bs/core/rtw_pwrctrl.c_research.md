# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_pwrctrl.c

## Purpose

`rtw_pwrctrl.c` implements runtime power management for the RTL8723BS driver. It controls inactive power save (IPS), leisure power save (LPS), firmware RPWM/CPWM state transitions, task-alive accounting for command and transmit paths, power-save deny masks, and public configuration setters for LPS/IPS modes.

The file keeps the adapter and firmware in a state where the NIC can sleep when idle but wake reliably before IO, transmit, command processing, scan, join, AP mode, or system suspend constraints require full power. Its state is volatile and stored in `struct pwrctrl_priv`, with side effects in firmware registers, timers, work items, and Bluetooth coexistence notifications.

## Important APIs, types, and functions

Important entry points include `ips_enter()`, `ips_leave()`, `rtw_ps_processor()`, `traffic_check_for_leave_lps()`, `rtw_set_rpwm()`, `rtw_set_ps_mode()`, `LPS_Enter()`, `LPS_Leave()`, `LeaveAllPowerSaveModeDirect()`, `LeaveAllPowerSaveMode()`, `LPS_Leave_check()`, `cpwm_int_hdl()`, task-alive functions (`rtw_register_task_alive()`, `rtw_unregister_task_alive()`, `rtw_register_tx_alive()`, `rtw_register_cmd_alive()`, `rtw_unregister_tx_alive()`, `rtw_unregister_cmd_alive()`), `rtw_init_pwrctrl_priv()`, `_rtw_pwr_wakeup()`, `rtw_pm_set_lps()`, `rtw_pm_set_ips()`, and the power-save deny helpers.

The core state object is `struct pwrctrl_priv`, reached through `adapter_to_pwrctl()` or `dvobj_to_pwrctl()`. Critical fields are `rf_pwrstate`, `change_rfpwrstate`, `ips_mode`, `ips_mode_req`, `bips_processing`, `bpower_saving`, `bkeepfwalive`, `ps_processing`, `pwr_mode`, `power_mgnt`, `bLeisurePs`, `fw_current_in_ps_mode`, `rpwm`, `cpwm`, `tog`, `cpwm_tog`, `brpwmtimeout`, `alives`, `ps_deny`, `ips_deny_time`, suspend flags, timers, and work items.

## Control flow

IPS entry is driven by `rtw_ps_processor()`, normally reached through the power-state check timer and command path. It first checks the `ps_deny` mask, suspend status, requested IPS mode, and `rtw_pwr_unassociated_idle()`. The idle check rejects power-down if the interface or buddy is associated, linking, scanning, AP/IBSS, under WPS, already saving power, within the IPS deny window, or holding non-free transmit buffers. Every fourth check while RF is on, the processor sets `change_rfpwrstate = rf_off` and calls `ips_enter()`, which notifies Bluetooth coexistence, takes the power lock, and calls `_ips_enter()` to power down hardware through `rtw_ips_pwr_down()`.

IPS leave uses `ips_leave()` and `_ips_leave()`. If RF is off and no IPS transition is active, it marks processing, requests `rf_on`, calls `rtw_ips_pwr_up()`, updates `rf_pwrstate`, clears firmware-alive and power-saving flags, unlocks, and notifies coexistence with `IPS_NONE`.

LPS entry uses `LPS_Enter()`. It rejects Bluetooth-controlled LPS, requires exactly one associated interface, reuses `PS_RDY_CHECK()`, waits through an idle counter, and calls `rtw_set_ps_mode()` with the configured `power_mgnt` mode. LPS leave uses `LPS_Leave()` or `LeaveAllPowerSaveMode*()`, sets active mode, raises RPWM to awake state, optionally waits for firmware RF-on with `LPS_RF_ON_check()`, and clears `bpower_saving`.

`rtw_set_ps_mode()` is the main firmware power-mode setter. For active mode, it raises RPWM to `PS_STATE_S4`, sends `HW_VAR_H2C_FW_PWRMODE`, clears `fw_current_in_ps_mode`, and notifies coexistence unless BT owns LPS. For sleep modes, it requires `PS_RDY_CHECK()` or BT-owned LPS, stores smart-PS and antenna mode, sends firmware power mode, picks a target RPWM level (`S0` if no tasks alive, `S2` otherwise or per BT constraint), and calls `rtw_set_rpwm()`.

`rtw_set_rpwm()` writes requested power state to firmware through `HW_VAR_SET_RPWM`. It avoids redundant transitions, handles surprise removal and driver-stopped constraints, toggles the RPWM toggle bit, adds `PS_ACK` when waking from low states to S2 or higher, arms a timeout timer, and polls CPWM for a matching toggle until `LPS_RPWM_WAIT_MS` expires. Timeout work either synthesizes CPWM S2 for a non-0xEA register condition or retries RPWM with `brpwmtimeout` set.

Task-alive registration is used by command and transmit paths before touching firmware in LPS. Register functions set `CMD_ALIVE`, `XMIT_ALIVE`, or a caller tag, request RPWM S2 when firmware is asleep, and can return `_FAIL` until CPWM rises. Unregister functions clear the bit and lower RPWM toward S0 only when no alive tasks remain or BT requires S2.

Wakeup flow in `_rtw_pwr_wakeup()` leaves all power-save modes, updates the IPS deny window, waits up to about 3 seconds for power processing or autosuspend to clear, rejects system suspend or net-closed autosuspend, leaves IPS if RF is off, and finally validates driver-up and hardware-init state.

## State and persistence behavior

All persisted information is in memory for the adapter lifetime. Initialization sets RF on, IPS/LPS modes from registry settings, CPWM S4, RPWM 0, active power mode, smart-PS parameters, timers, work items, suspend flags, counters, and wake-on-WLAN flags. No file or NVRAM state is written.

The firmware-visible state is updated with HAL register calls: `HW_VAR_SET_RPWM`, `HW_VAR_CPWM`, `HW_VAR_H2C_FW_PWRMODE`, and `HW_VAR_FWLPS_RF_ON`. The power lock protects most `pwrctrl_priv` transitions. The timer and work item split is important: timer handlers avoid IO and schedule work when a register retry is needed.

## Dependencies and integration points

This module depends on `drv_types.h`, `hal_data.h`, jiffies/timers, HAL power-up/down hooks (`rtw_ips_pwr_down()`, `rtw_ips_pwr_up()`), Bluetooth coexistence (`hal_btcoex_*`), MLME state checks, cfg80211 power-management policy, transmit and command completions, and `rtw_lps_ctrl_wk_cmd()` for queued LPS control. `rtw_recv.c` calls `traffic_check_for_leave_lps()` after RX traffic, and transmit paths call the same helper for TX bursts. MLME connection callbacks call LPS controls when connecting or disconnecting.

## Risks and edge cases

`traffic_check_for_leave_lps()` uses static `start_time` and `xmit_cnt`, so TX traffic accounting is shared across adapters instead of per adapter. In multi-interface scenarios this can leave LPS too early or too late.

Several paths busy wait with `mdelay()` or one-millisecond polling. `_rtw_pwr_wakeup()` can spin for up to roughly 3 seconds while waiting for suspend or power processing, and `rtw_set_rpwm()` polls CPWM. These paths must remain out of atomic context and can affect resume or command latency.

Task-alive registration can initially return `_FAIL` then recheck CPWM after unlocking. Callers must be prepared for transient failure during wake. Missed unregister calls would pin firmware at a higher power state, while premature unregister could lower RPWM while command or transmit work still needs IO.

Power mode transitions are coordinated with Bluetooth coexistence policy. Tests need to cover both BT-controlled and Wi-Fi-controlled LPS because branches can suppress or override normal state changes.

IPS decisions assume transmit buffer counts are fully free before powering down. Any accounting leak in xmit buffers can block IPS indefinitely; any false free count can power down while work remains.

## Test signals

Important test signals include IPS entering only while unassociated and idle, IPS leave restoring RF and clearing `bpower_saving`, LPS entering after the idle threshold, LPS leave on RX/TX bursts, `LeaveAllPowerSaveMode()` behavior when linked and unlinked, RPWM/CPWM timeout recovery, command/transmit alive registration under LPS, suspend/autosuspend wake rejection, `rtw_pm_set_lps()` and `rtw_pm_set_ips()` return values for invalid modes, PS deny mask behavior, and Bluetooth coexistence ownership of LPS. Instrumenting `rf_pwrstate`, `pwr_mode`, `fw_current_in_ps_mode`, `rpwm`, `cpwm`, `alives`, and HAL power-mode writes gives the clearest regression signal.
