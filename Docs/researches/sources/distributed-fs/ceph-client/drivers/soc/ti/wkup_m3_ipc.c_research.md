# sources/distributed-fs/ceph-client/drivers/soc/ti/wkup_m3_ipc.c

## Purpose
This file implements IPC between the ARM MPU and AM33xx/AM43xx Wakeup M3 remote processor. It exposes PM operations used by `pm33xx.c`, boots the M3 remoteproc asynchronously, exchanges low-power commands through control IPC registers plus mailbox kicks, handles M3 TX events, and reports wake/status information.

## Important APIs, Types, And Functions
Exported APIs are `wkup_m3_ipc_get` and `wkup_m3_ipc_put`. The exposed operation table contains `set_mem_type`, `set_resume_address`, `prepare_low_power`, `finish_low_power`, `request_pm_status`, `request_wake_src`, and `set_rtc_only`. Important helpers include `wkup_m3_copy_aux_data`, `wkup_m3_scale_data_fw_cb`, `wkup_m3_txev_handler`, `wkup_m3_ping`, `wkup_m3_ping_noirq`, IPC register read/write helpers, and probe/remove/PM callbacks.

## Control Flow
Probe maps IPC registers, requests the TXEV IRQ, obtains a mailbox channel, resolves a remoteproc phandle, initializes IPC state and optional VTT/io-isolation/scale-data firmware settings, then starts a kernel thread that boots the remoteproc. The TXEV handler acknowledges the event, transitions state from reset or message states, records firmware version, initializes optional scale data, completes synchronous waits, and reenables TXEV. Low-power preparation writes resume address, command, memory/VTT/isolation/halt flags, optional scale offsets, sets state, and pings the M3. Finish sends reset and waits for completion.

## State And Persistence
Global singleton `m3_ipc_state` provides the shared handle. Per-device state stores mapped IPC memory, mailbox, remoteproc, completion, state enum, firmware options, wake flags, VTT/isolation/halt bits, resume address, memory type, and debugfs path. IPC registers and M3 DMEM hold command and auxiliary data across low-power handshakes.

## Dependencies And Integration Points
It depends on remoteproc, mailbox, firmware loading, debugfs, suspend PM, and OF compatibles `ti,am3352-wkup-m3-ipc` and `ti,am4372-wkup-m3-ipc`. It is consumed directly by AM33xx PM code.

## Risks And Test Signals
Risks include singleton lifetime assumptions, 500 ms sync timeout, missing mailbox/rproc deferral, auxiliary data size not explicitly bounded against firmware size, state-machine desynchronization, and remove paths assuming `m3_ipc_state`. Test signals include CM3 firmware version logs, PM status 0, wake source strings, successful standby/deepsleep/idle pings, debugfs halt control, and RTC-only reboot of remoteproc on resume.
