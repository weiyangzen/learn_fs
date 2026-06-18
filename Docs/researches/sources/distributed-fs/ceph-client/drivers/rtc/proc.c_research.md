# sources/distributed-fs/ceph-client/drivers/rtc/proc.c

## Purpose

`proc.c` implements the legacy `/proc/driver/rtc` view for the RTC subsystem. It exposes the selected hardware clock-to-system device's current time, date, alarm, IRQ state, frequency limits, and optional driver-specific proc output.

## Important APIs, types, and functions

`rtc_proc_add_device()` creates `driver/rtc` with `proc_create_single_data()` for the RTC selected by `CONFIG_RTC_HCTOSYS_DEVICE` or, without that option, `rtc0`. `rtc_proc_del_device()` removes it. `rtc_proc_show()` formats values with `%ptRt` and `%ptRd`, calls `rtc_read_time()` and `rtc_read_alarm()`, and invokes `ops->proc()` when present. `is_rtc_hctosys()` maps `rtc->id` to `rtcN` and compares with the configured hctosys device.

## Control flow

At RTC registration, the core can call `rtc_proc_add_device()`. If the device is the hctosys RTC, a proc entry is created. A read of `/proc/driver/rtc` calls `rtc_proc_show()`, which first prints the current RTC time/date if readable, then alarm and IRQ metadata if `rtc_read_alarm()` succeeds, then always prints `24hr: yes`, followed by any low-level driver's `proc` hook.

## State and persistence behavior

No durable state is stored here. The proc entry is a transient view over the live `struct rtc_device`. It reports in-memory class state such as `uie_rtctimer.enabled`, `pie_enabled`, `irq_freq`, and `max_user_freq`.

## Dependencies and integration points

It depends on `linux/proc_fs.h`, `linux/seq_file.h`, `linux/rtc.h`, and local `rtc-core.h`. It integrates with the RTC core registration/removal paths and with drivers that implement the optional `proc` callback, such as the AT91SAM9 RTT driver.

## Risks and edge cases

Only one global `/proc/driver/rtc` exists, so systems with multiple RTCs expose only the selected hctosys RTC. `NAME_SIZE` limits `rtcN` string construction to ten bytes; overly large IDs are ignored. Proc output may omit sections if read callbacks fail. The local `const struct rtc_class_ops *ops = rtc->ops` is dereferenced for `ops->proc`, so this path assumes a registered device with valid ops.

## Test signals

Boot with different `CONFIG_RTC_HCTOSYS_DEVICE` values and multiple RTCs, confirm only the intended RTC creates `/proc/driver/rtc`, compare time/alarm fields with `/dev/rtc` ioctls, verify optional `proc` driver output, and ensure removal unregisters the proc entry.
