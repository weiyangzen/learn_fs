# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pm.c

## Purpose
`pm.c` implements wil6210 runtime and system suspend/resume policy. It decides whether suspend is allowed, supports radio-off suspend by bringing hardware down, supports radio-on suspend when firmware/platform capabilities allow D3 suspend, manages queues, and wraps Linux runtime PM helpers.

## Important APIs, Types, And Functions
`wil_can_suspend()` validates global and VIF-level conditions. `wil_suspend()` and `wil_resume()` dispatch to radio-on or radio-off flows. `wil_suspend_keep_radio_on()` and `wil_resume_keep_radio_on()` coordinate WMI suspend/resume while preserving connected radio state. `wil_suspend_radio_off()` and `wil_resume_radio_off()` shut hardware down/up. Runtime helpers are `wil_pm_runtime_allow()`, `wil_pm_runtime_forbid()`, `wil_pm_runtime_get()`, and `wil_pm_runtime_put()`.

## Control Flow
Suspend eligibility rejects debug/WMI-only mode, runtime suspend without platform support, active monitor/AP-like interfaces, STA/P2P client runtime suspend, connecting VIFs, reset, and recovery. Radio-on suspend stops queues, checks TX/RX/WMI idle, sends `wmi_suspend()`, waits for RX drain, masks IRQs, disables reset-on-PERST, calls platform suspend, drops bus request, and sets suspended bits. Radio-off suspend calls `wil_down()` when active, disables PCIe IRQ, and calls platform suspend. Resume reverses the chosen mode and wakes connected queues.

## State And Persistence
The file updates `wil_status_suspending`, `wil_status_suspended`, and `wil_status_resuming`; `wil->bus_request_kbps_pre_suspend`; and suspend statistics counters. Runtime PM autosuspend delay is set to one second.

## Dependencies And Integration Points
It depends on active VIF accounting from `netdev.c`, queue control helpers, TX/RX idle checks, WMI suspend/resume and idle checks, reset/up/down in `main.c`, IRQ control, bus request/platform suspend/resume hooks, and PM callbacks in `pcie_bus.c`.

## Risks
The radio-on path is sensitive to races with TX, RX, WMI events, and NAPI. It uses `down_write_trylock(&mem_lock)` to block new memory/WMI work but releases it after marking suspending; status checks must remain consistent. Failure recovery after `wmi_suspend()` attempts `wmi_resume()` and queue wake, but no-fw-recovery mode changes behavior. Counters are diagnostic and not transactional.

## Test Signals
System suspend with connected STA, runtime idle rejection for STA, monitor/AP rejection, connecting-state rejection, pending TX/RX/WMI rejection, platform suspend/resume failures, WMI resume failure with recovery, repeated suspend while already suspended, and stats updates through debugfs.
