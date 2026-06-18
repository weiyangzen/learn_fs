<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-sys-off-wakeup.c -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-sys-off-wakeup.c

## Purpose

This optional feature registers Turris Omnia MCU restart, true poweroff, and wake-from-poweroff support. It exposes the wakeup feature as an RTC alarm even though the MCU provides uptime-relative wake scheduling rather than a real wall clock.

## Important APIs, Types, And Functions

`omnia_get_uptime_wakeup()` reads current MCU uptime and wakeup time. RTC ops implement `read_time`, `read_alarm`, `set_alarm`, and `alarm_irq_enable`. `omnia_power_off()` sends the poweroff command with magic, optional front-button wake flag, and big-endian CRC32. `omnia_restart()` sends light or hard reset control bits. `front_button_poweron` sysfs controls whether front-button power-on is requested. `omnia_mcu_register_sys_off_and_wakeup()` registers sys-off handlers and the RTC device.

## Control Flow

Registration always installs a restart handler. If `OMNIA_FEAT_POWEROFF_WAKEUP` is absent, it stops there. Otherwise it installs a poweroff handler, allocates/registers an RTC wakeup-only device, and defaults front-button power-on to true. RTC alarm operations translate between `rtc_time` and MCU seconds since reset.

## State And Persistence

Kernel state stores the last requested `rtc_alarm` and `front_button_poweron` flag. The MCU stores wakeup scheduling and performs reset/poweroff actions. The RTC time base is not persistent wall time; it is MCU uptime.

## Dependencies And Integration Points

It depends on sys-off handlers, reboot mode, RTC class, CRC32, I2C MCU commands, sysfs visibility, and feature bits.

## Risks

Users may mistake the RTC for a real clock; it is wakeup-only and uptime-relative. `front_button_poweron` is mutable kernel state and not persisted unless userspace reapplies it. Poweroff CRC byte order is intentionally unusual and must match MCU firmware. Restart returns `NOTIFY_DONE` after sending reset and delaying 1 ms.

## Test Signals

Test restart handler for normal and hard reboot modes, poweroff command bytes/CRC, RTC read/set/alarm-enable, feature-gated sysfs visibility, front-button power-on toggling, and behavior across MCU reset or driver reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-sys-off-wakeup.c -->
