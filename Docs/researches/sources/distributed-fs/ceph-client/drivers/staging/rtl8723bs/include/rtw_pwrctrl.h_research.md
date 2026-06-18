<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_pwrctrl.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_pwrctrl.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_pwrctrl.h` defines power-control state for IPS/LPS, RF power states, power-deny reasons, task-alive accounting, RPWM/CPWM firmware handshake, timers, and public power-management APIs. The source was reviewed as a complete 254-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct pwrctrl_priv`, `enum rt_rf_power_state`, `enum ps_deny_reason`, `rtw_init_pwrctrl_priv`, `rtw_register_task_alive`, `rtw_register_tx_alive`, `rtw_register_cmd_alive`, `cpwm_int_hdl`, `ips_enter`, `ips_leave`, `LPS_Enter`, `LPS_Leave`, `rtw_set_ps_mode`, `rtw_set_rpwm`, `_rtw_pwr_wakeup`, `rtw_pm_set_ips`, `rtw_pm_set_lps`, `rtw_ps_deny`, and `rtw_ps_deny_cancel`.

## Control Flow

Traffic, command, and power-management paths register active tasks, deny or allow power save, enter/leave IPS or LPS, and use RPWM/CPWM plus timers to synchronize host/firmware power states.

## State and Persistence Behavior

`pwrctrl_priv` persists locks, requested/current power modes, firmware power state, RPWM/CPWM values, timers/work items, IPS/LPS mode settings, RF power state, deny masks, and adapter backpointer.

## Dependencies and Integration Points

Integrated with HAL power sequences, firmware H2C power commands, command/transmit alive tracking, MLME link state, and Linux PM suspend/resume. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Power state races are high risk. Incorrect deny-mask handling or RPWM/CPWM timeout behavior can sleep while traffic is active or keep the device awake indefinitely.

## Test Signals

IPS/LPS enter-leave loops, traffic-triggered LPS leave, suspend/resume, command/xmit alive registration balance, and power-state timer timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_pwrctrl.h -->
