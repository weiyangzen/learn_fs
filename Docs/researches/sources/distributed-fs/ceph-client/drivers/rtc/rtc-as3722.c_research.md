# sources/distributed-fs/ceph-client/drivers/rtc/rtc-as3722.c

## Purpose

`rtc-as3722.c` is the RTC driver for AMS AS3722 PMICs. It provides BCD calendar read/set, alarm read/set, alarm IRQ enable/disable, and wakeup support through the AS3722 MFD.

## Important APIs, types, and functions

`struct as3722_rtc` stores the RTC device, device pointer, parent `struct as3722`, alarm IRQ, and software IRQ-enable flag. `as3722_time_to_reg()` and `as3722_reg_to_time()` convert six BCD registers relative to year 2000. RTC callbacks include `as3722_rtc_read_time()`, `as3722_rtc_set_time()`, `as3722_rtc_read_alarm()`, `as3722_rtc_set_alarm()`, and `as3722_rtc_alarm_irq_enable()`. `as3722_alarm_irq()` reports `RTC_AF`.

## Control flow

Probe allocates state, enables the RTC and alarm wakeup bits in `AS3722_RTC_CONTROL_REG`, marks the platform device wake-capable, registers the RTC with `devm_rtc_device_register()`, gets and requests the alarm IRQ, then disables the IRQ until an alarm is enabled. Setting an alarm first disables the IRQ, writes the six alarm BCD registers, and re-enables the IRQ if requested.

## State and persistence behavior

Hardware persists calendar, alarm, RTC enable, and alarm wakeup bits. Software `irq_enable` mirrors whether the IRQ line is enabled in Linux to avoid unbalanced `enable_irq()` and `disable_irq()` calls.

## Dependencies and integration points

The driver depends on the AS3722 MFD API (`as3722_block_read`, `as3722_block_write`, `as3722_update_bits`), platform IRQs, RTC class APIs, PM sleep wake IRQ operations, and the platform device name `"as3722-rtc"`.

## Risks and edge cases

The driver uses older `devm_rtc_device_register()` rather than allocate/register split. `read_alarm()` does not populate `enabled` or `pending`, so users may not see current enable state from readback. The IRQ handler reports alarms but does not acknowledge a PMIC status bit locally; that may be handled by the MFD IRQ layer and should be verified. Year values before 2000 are rejected.

## Test signals

Test enabling RTC control bits at probe, time set/read around 2000 boundary, alarm write/read and IRQ enable balancing, IRQ delivery through the MFD, suspend/resume wake IRQ, and userspace `RTC_ALM_READ` behavior for enabled/pending fields.
