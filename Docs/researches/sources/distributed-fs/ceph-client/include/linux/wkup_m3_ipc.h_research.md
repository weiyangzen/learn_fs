# sources/distributed-fs/ceph-client/include/linux/wkup_m3_ipc.h

## Purpose
`wkup_m3_ipc.h` declares the platform IPC interface to the TI Wakeup M3 remote processor used for AMx3 low-power state management. It models firmware, mailbox, SRAM/shared-memory, debugfs, and power-state operations.

## Important APIs, Types, and Functions
Power-state constants are `WKUP_M3_DEEPSLEEP`, `WKUP_M3_STANDBY`, and `WKUP_M3_IDLE`. `struct wkup_m3_ipc` stores the remoteproc pointer, IPC memory base, device, memory type, resume address, voltage/isolation configuration, state, halt flag, voltage-scaling offsets, firmware name, completion, mailbox client/channel, ops table, RTC-only flag, and debugfs path. `struct wkup_m3_wakeup_src` describes wake IRQ/source text. `struct wkup_m3_scale_data_header` describes packed firmware offset data. `struct wkup_m3_ipc_ops` provides callbacks for memory type, resume address, low-power prepare/finish, PM status, wake source query, and RTC-only mode. Public APIs are `wkup_m3_ipc_get()`, `wkup_m3_ipc_put()`, and `wkup_m3_set_rtc_only_mode()`.

## Control Flow
Platform PM code obtains the singleton IPC object, configures memory type and resume address, asks the M3 firmware to prepare a low-power state through mailbox/shared memory, waits for `sync_complete`, then finishes low-power handling and queries status or wake source after resume. RTC-only mode is set through the ops hook.

## State and Persistence
State is runtime platform power-management state and firmware communication context. Some fields describe resume behavior across suspend, but the kernel-side object itself is not durable. Remote firmware state persists while the M3 is running.

## Dependencies and Integration Points
Dependencies include mailbox client APIs, remoteproc, completions, iomem, devices, debugfs, and TI AMx3 PM code. Integration points include SoC suspend/resume, wake-source reporting, firmware loading, voltage scaling, and RTC-only low-power paths.

## Risks
Mailbox completion and firmware state must be synchronized or suspend can hang. Resume address and memory type must match platform memory layout. Packed scale-data offsets are firmware ABI. Singleton get/put users must avoid use-after-free. RTC-only mode changes power behavior and must be platform-gated.

## Test Signals
Signals include suspend/resume through deep sleep, standby, and idle; wake-source reporting; mailbox timeout handling; firmware load failures; RTC-only mode; debugfs status; and repeated PM cycles under lockdep.
