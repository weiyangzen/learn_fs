# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1672.c

Purpose: implements a simple I2C RTC driver for the Dallas/Maxim DS1672, whose timekeeping is a 32-bit seconds counter plus control/trickle registers.

Important APIs/types/functions: `ds1672_read_time()` reads the control register, rejects a stopped oscillator via `DS1672_REG_CONTROL_EOSC`, reads the 4-byte little-endian counter, and converts it with `rtc_time64_to_tm()`. `ds1672_set_time()` writes the counter bytes and clears control to enable counting. `ds1672_probe()` checks raw I2C functionality, allocates the RTC, sets `range_max = U32_MAX`, registers the RTC, and stores client data.

Control flow: reads first perform a one-byte control register transaction to validate oscillator state, then perform a block-style I2C transfer from counter base. Writes send a six-byte buffer starting at counter base, containing four seconds bytes plus a zero control register byte. There is no alarm, IRQ, nvmem, or suspend/resume logic.

State and persistence: persistent state is the hardware seconds counter and control register. The driver has no private state beyond the registered `rtc_device` stored as I2C client data.

Dependencies and integration: depends on the I2C core, RTC core, and OF/I2C match tables (`dallas,ds1672`, `ds1672`). It requires `I2C_FUNC_I2C`.

Risks and test signals: the 32-bit counter limits representable time to the U32 seconds range. Setting time unconditionally clears the control register, so platform-specific trickle/control configuration is not preserved by this path. Test oscillator-stopped reads, full counter endian conversion, set/read round trips near `U32_MAX`, and adapter functionality rejection.
