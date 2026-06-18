# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8925.c

Purpose: provides RTC support for the MAX8925 PMIC, including time, alarm0, IRQ wake flags, and custom BCD-like digit conversion.

Important APIs and types: `struct max8925_rtc_info` holds RTC device, parent chip, RTC I2C client, device, and IRQ. `tm_calc()` decodes register digits into `rtc_time`; `data_calc()` encodes them. RTC callbacks include read/set time and alarm. `rtc_update_handler()` handles alarm IRQ and disables alarm0 match bits.

Control flow: probe obtains parent chip and RTC client, requests platform IRQ, enables wakeup, and registers the RTC. Time and alarm paths bulk-read/write eight registers via MAX8925 helpers. Alarm read combines IRQ mask, alarm control, and RTC status to populate enabled and pending. Suspend/resume set or clear the parent's wakeup flag bit.

State and persistence: PMIC RTC registers store time, alarm, masks, status, and control. Software state is volatile; wakeup intent is reflected in parent `wakeup_flag` during suspend.

Dependencies and integration: MAX8925 MFD helpers, platform IRQ, RTC class, PM sleep hooks, and parent wakeup flag contract.

Risks: conversion helpers encode `tm_mon` directly rather than `tm_mon + 1`, which should be checked against hardware conventions and other drivers. Probe uses `platform_get_irq()` without checking before request. Alarm IRQ enable is not exposed separately in `rtc_class_ops`; alarm enable comes through `set_alarm()`.

Test signals: digit conversion around month/year boundaries, IRQ mask/status pending behavior, alarm0 control `0x77`, platform IRQ failure, suspend/resume wakeup flag, and invalid buffer length handling.
