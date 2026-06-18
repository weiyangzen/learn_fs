# sources/distributed-fs/ceph-client/drivers/rtc/rtc-jz4740.c

Purpose: implements the Ingenic JZ4740/JZ4760/JZ4770/JZ4780 SoC RTC as a platform MMIO RTC, including timekeeping, alarm IRQs, hibernate-based poweroff, wakeup timing parameters, and an optional exported 32 kHz clock.

Important APIs and functions: the `jz4740_rtc_ops` callbacks are `jz4740_rtc_read_time()`, `jz4740_rtc_set_time()`, `jz4740_rtc_read_alarm()`, `jz4740_rtc_set_alarm()`, and `jz4740_rtc_alarm_irq_enable()`. Register access is centralized in `jz4740_rtc_reg_read()`, `jz4740_rtc_reg_write()`, `jz4740_rtc_wait_write_ready()`, `jz4780_rtc_enable_write()`, and `jz4740_rtc_ctrl_set_bits()`. Probe wires resources, wake IRQ, optional `pm_power_off`, and optional `clk_hw` provider.

Control flow: probe maps registers, enables the `rtc` clock, marks the device wake-capable, registers the RTC, and requests the alarm/update IRQ. Reads reject uninitialized hardware by checking the scratchpad magic, then read the seconds register until two consecutive values match. Setting time writes seconds and then stores the scratchpad marker. Alarm setup writes `SEC_ALARM` and toggles alarm enable and interrupt bits. The IRQ handler translates 1 Hz and alarm flags into `rtc_update_irq()` events and clears hardware flags through the protected control update helper.

State and persistence: the hardware stores seconds, alarm seconds, regulator and wake timing registers, hibernate state, and a scratchpad initialization marker. Driver state is `struct jz4740_rtc`, including mapped base, SoC type, RTC device, optional clock hardware, and spinlock. `dev_for_power_off` is a static singleton for system-power-controller use. The RTC persists if the SoC backup domain remains powered.

Dependencies and integration: depends on platform resources, device tree compatibles, `devm_clk_get_enabled()`, PM wake IRQ helpers, RTC class APIs, optional OF clock provider, and the kernel global `pm_power_off` hook. The SoC type controls whether the JZ4780 write-enable sequence is required before writes.

Risks: all writes depend on `WRDY` polling and, on newer chips, the magic `WENR` sequence; timeout handling is critical. The wakeup/reset tick calculations mask values with the field mask and may deserve hardware validation. Alarm times are stored as lower 32-bit seconds, matching the advertised `U32_MAX` range. The global poweroff hook can only support one device.

Test signals: boot on each compatible, read before/after scratchpad initialization, write-ready timeout injection, JZ4780 write-enable failure, alarm enable/disable and IRQ clearing, wake-from-suspend, hibernate poweroff, and optional 32 kHz clock registration and enable state.
