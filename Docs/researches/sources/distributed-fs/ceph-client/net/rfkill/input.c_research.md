# sources/distributed-fs/ceph-client/net/rfkill/input.c

## Purpose
Bridges input-layer rfkill keys and switches to rfkill global operations, including type-specific toggles, master switch EPO/restore/unblock behavior, and rate limiting of repeated operations.

## Important APIs, Types, and Functions
Defines `enum rfkill_input_master_mode`, `enum rfkill_sched_op`, module parameter `master_switch_mode`, delayed work `rfkill_op_work`, and input handler `rfkill_handler`. Exported init/exit for the core are `rfkill_handler_init()` and `rfkill_handler_exit()`. Internal scheduling helpers include `rfkill_schedule_global_op()`, `rfkill_schedule_toggle()`, `rfkill_schedule_evsw_rfkillall()`, and `rfkill_op_handler()`.

## Control Flow
Input events for `KEY_WLAN`, `KEY_BLUETOOTH`, `KEY_UWB`, `KEY_WIMAX`, and `KEY_RFKILL` schedule toggles. `SW_RFKILL_ALL` schedules either EPO on switch-off or a configurable master operation on switch-on. The delayed work first drains pending global operations, bypassing rate limiting for new EPO, then applies type-specific toggles unless the EPO lock is active. `rfkill_connect()` registers and opens matching input devices, while `rfkill_start()` samples initial switch state under the input device event lock.

## State and Persistence
State is in pending bitmaps `rfkill_sw_pending` and `rfkill_sw_state`, pending global op fields, `rfkill_last_scheduled`, and the configured master switch mode. It is runtime-only.

## Dependencies and Integration
Depends on the input layer, delayed work, rfkill core global functions in `rfkill.h`, and key/switch event codes. Built into the rfkill object when `CONFIG_RFKILL_INPUT` is enabled.

## Risks and Test Signals
Risks include lost toggles while a global op is pending, rate-limit latency, EPO lock preventing normal toggles, and changing semantics through the master switch mode parameter. Test signals are key press toggles for each type, master switch off causing immediate EPO, switch on performing unlock/restore/unblock according to mode, initial switch-state handling on device start, and handler unregister cancelling delayed work.
