# sources/distributed-fs/ceph-client/drivers/rtc/rtc-cros-ec.c

## Purpose
ChromeOS Embedded Controller RTC driver. It translates RTC class operations into EC host commands for current time and relative alarm management, and listens for EC host events to report RTC alarm interrupts.

## Important APIs, types, and functions
- `struct cros_ec_rtc` stores the EC pointer, RTC device, EC event notifier, and a saved absolute alarm value used across IRQ enable/disable.
- `cros_ec_rtc_get()` and `cros_ec_rtc_set()` wrap `cros_ec_cmd_xfer_status()` for `EC_CMD_RTC_*` commands.
- `cros_ec_rtc_read_time()` and `set_time()` map EC 32-bit seconds to/from `rtc_time`.
- Alarm read/set convert between RTC absolute alarm time and EC relative alarm offsets; disabled alarms send `EC_RTC_ALARM_CLEAR`.
- `cros_ec_rtc_alarm_irq_enable()` saves the current alarm when disabling and restores it if still in the future when enabling.
- `cros_ec_rtc_event()` checks `EC_HOST_EVENT_RTC` and calls `rtc_update_irq()`.
- Probe validates initial EC time read, initializes wakeup, registers RTC with `range_max = U32_MAX`, probes old EC 24-hour alarm limit, clears test alarm, registers RTC, and subscribes to EC notifier.

## Control flow
All hardware communication is synchronous host-command traffic to the parent EC. Alarm operations always read current EC time first because EC alarm commands are relative. The notifier path is asynchronous and translates EC host events into RTC alarm interrupts.

## State and persistence behavior
Time and active alarm live in EC firmware. Software stores `saved_alarm` only when RTC core disables alarm IRQs, so it can restore a future alarm later. Range is limited to 32-bit seconds.

## Dependencies and integration points
Depends on ChromeOS EC protocol/data structures, platform child device model, blocking notifier chain, PM wake IRQ via parent EC IRQ, and RTC class. Binds to platform ID `"cros-ec-rtc"`.

## Risks
- EC alarms are relative; races between reading current time and setting an offset can shift the alarm by command latency.
- Old EC firmware may reject offsets beyond 24 hours; probe detects this by attempting a two-day alarm.
- `saved_alarm` logic must handle wrap and past alarms correctly.
- Alarm read does not set `enabled` or `pending`, only computes the time.

## Test signals
Host-command mocks for get/set/read alarm, old firmware 24-hour alarm detection, EC host event delivery, suspend/resume wake via parent EC IRQ, alarm disable/restore behavior, and U32 range validation.
