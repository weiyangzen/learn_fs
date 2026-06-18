# sources/distributed-fs/ceph-client/kernel/power/suspend_test.c

## Purpose
Provides a boot-time suspend self-test facility driven by RTC wake alarms. It can automatically enter a requested suspend state shortly after boot and rely on a wakealarm-capable RTC to resume the system.

## Important APIs, Types, and Functions
`TEST_SUSPEND_SECONDS` defines the alarm delay. State includes `suspend_test_start_time`, `test_repeat_count_max`, `test_repeat_count_current`, and initdata `test_state_label`. Runtime timing helpers `suspend_test_start()` and `suspend_test_finish()` are called by `suspend.c` around device suspend/resume phases. Boot setup is handled by `setup_test_suspend()` registered through `__setup("test_suspend", ...)`. The late initcall `test_suspend()` locates an RTC and calls `test_wakealarm()`.

## Control Flow
`setup_test_suspend()` parses `test_suspend=<state>[,<repeat>]`, where state is one of the PM labels and repeat is an optional count. `test_suspend()` runs after PM and RTC initialization, validates that the requested state is currently exposed in `pm_states`, finds an RTC device with `RTC_FEATURE_ALARM` whose parent may wake the system, opens it, and calls `test_wakealarm()`.

`test_wakealarm()` reads current RTC time, sets a wake alarm `TEST_SUSPEND_SECONDS` in the future, then attempts the requested suspend state. If `mem` returns `-ENODEV`, it falls back to standby; if standby fails, it falls back to suspend-to-idle. It repeats until the configured count is reached, then disables the alarm.

`suspend_test_start()` records `jiffies`; `suspend_test_finish()` prints elapsed time for a labeled phase and warns if it exceeded the alarm window, because the wake alarm may have fired before the system fully entered sleep.

## State and Persistence Behavior
All state is boot-time or per-test runtime state. The RTC alarm is programmed in hardware and explicitly disabled after testing. The repeat counter persists only for the initcall execution.

## Dependencies and Integration Points
Depends on RTC class devices, wakealarm capability, PM state labels from `suspend.c`, `pm_suspend()`, and suspend device timing hooks in `suspend_devices_and_enter()`. It is controlled solely by the kernel command line.

## Risks
Risks include false failures on systems with uninitialized RTCs, RTCs that cannot wake the platform despite advertising alarms, races with long suspend entry taking longer than the alarm delay, fallback masking failures in the originally requested state, and reliance on `jiffies` instead of a suspend-resilient clock for timing diagnostics.

## Test Signals
Boot with `test_suspend=mem`, `test_suspend=standby`, `test_suspend=freeze`, and repeat forms such as `test_suspend=mem,3`. Validate behavior with and without wakealarm-capable RTCs, with RTC wake disabled, and on platforms where `mem` is unsupported. Watch logs for phase timing warnings and suspend failure codes.
