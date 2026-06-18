# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf85363.c

Purpose: supports NXP PCF85263 and PCF85363 I2C RTCs with BCD timekeeping, alarm 1 on INTA, oscillator load configuration, and one or two RTC-backed nvmem regions depending on the variant.

Important APIs/types/functions: `struct pcf85363` holds the RTC and regmap; `struct pcf85x63_config` selects max register and nvmem count. `pcf85363_rtc_read_time()` and `pcf85363_rtc_set_time()` bulk-read/write date registers, using STOP and CPR reset for writes. `pcf85363_rtc_read_alarm()`, `_pcf85363_rtc_alarm_irq_enable()`, `pcf85363_rtc_set_alarm()`, and `pcf85363_rtc_handle_irq()` implement full date alarm 1. `pcf85363_nvram_read/write()` expose the 64-byte RAM window and `pcf85x63_nvram_read/write()` expose the one-byte RAM register.

Control flow: probe chooses OF variant data or defaults to PCF85363, initializes regmap, allocates the RTC, programs crystal load, sets time range and ops, configures INTA output and clears flags when IRQ or wakeup is desired, requests a threaded low-trigger IRQ if present, sets alarm feature and wakeup capability based on IRQ/wakeup-source, registers the RTC, then registers each available nvmem region.

State and persistence: the hardware keeps time, alarm registers, alarm enable flags, interrupt flags, pin mode, oscillator setting, and battery-backed RAM. Driver state is only pointers to regmap/RTC. Alarm feature availability is dynamic: wakeup-source without a physical IRQ marks RTC alarm supported even though no interrupt handler is installed.

Dependencies and integration: uses I2C, OF match data, regmap, RTC core, devm nvmem registration via RTC, and IRQ threading. Device tree controls compatible variant, wakeup-source, IRQ flags, and quartz load.

Risks: the driver does not check oscillator-stop or validity flags on time reads, so stale time can appear valid after power loss. NVMEM registrations happen after `devm_rtc_register_device()` and their return values are ignored. The IRQ handler uses `i2c_get_clientdata(dev_id)` because it receives the client pointer, so changing the IRQ cookie would break it. Test signals include PCF85263 one-byte nvmem only, PCF85363 RAM window access, INTA alarm IRQ clear, wakeup-source without IRQ behavior, invalid oscillator cases, and STOP/CPR write timing.
