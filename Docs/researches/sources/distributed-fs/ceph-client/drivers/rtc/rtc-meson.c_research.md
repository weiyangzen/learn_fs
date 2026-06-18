# sources/distributed-fs/ceph-client/drivers/rtc/rtc-meson.c

Purpose: supports the internal RTC block in Amlogic Meson6/Meson8/Meson8b/Meson8m2 SoCs, managing both the AHB front-end and a custom serial bus to RTC registers, plus battery-backed register memory exposed as NVMEM.

Important APIs and types: `struct meson_rtc` stores device, reset, regulator, peripheral regmap, and serial regmap. Low-level serial helpers include `meson_rtc_sclk_pulse()`, `meson_rtc_send_bit()`, `meson_rtc_get_bus()`, `meson_rtc_serial_bus_reg_read()`, and `meson_rtc_serial_bus_reg_write()`. RTC callbacks are `meson_rtc_gettime()` and `meson_rtc_settime()`. NVMEM callbacks are `meson_rtc_regmem_read()` and `meson_rtc_regmem_write()`.

Control flow: probe allocates RTC state and device, maps the AHB registers into a regmap, obtains reset and `vdd` regulator, enables the regulator, writes static analog values, initializes a custom regmap bus for serial registers, verifies the counter can be read, registers NVMEM over four 32-bit regmem registers, and registers the RTC. Serial reads acquire bus readiness, send address bits, switch direction, and shift in 32 data bits. Writes acquire the bus, send data and address bits, then set write direction.

State and persistence: the RTC counter and four regmem words are hardware-backed and may be battery-backed through the RTC supply. Software state only tracks resource handles. The regulator remains enabled after successful probe.

Dependencies and integration: platform MMIO, regmap MMIO and custom bus APIs, reset controller, regulator framework, RTC class, NVMEM provider, OF compatibles for Meson generations, and polling helpers.

Risks: remove path does not disable the regulator on driver unbind. `meson_rtc_write_static()` polls `RTC_REG4` but masks a bit defined for `RTC_ADDR0`, which should be checked against hardware behavior. NVMEM callbacks divide byte counts by four and ignore remainder, so unaligned/non-multiple accesses may be mishandled. Bus acquisition resets hardware up to three times on readiness timeout.

Test signals: regulator enable/failure cleanup, reset-on-bus-timeout, serial read/write bit order, counter read functional check, set/read epoch seconds, NVMEM offset/size alignment, static value programming, and probe failure unwinding.
