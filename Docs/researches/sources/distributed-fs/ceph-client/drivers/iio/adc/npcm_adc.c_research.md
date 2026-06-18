# sources/distributed-fs/ceph-client/drivers/iio/adc/npcm_adc.c

Purpose: this platform driver exposes the ADC controller in Nuvoton NPCM7xx and NPCM8xx SoCs. It provides eight voltage channels, interrupt-driven single conversions, selectable internal/external reference voltage, and sample-frequency reporting.

Important APIs, types, and functions: `struct npcm_adc_info` describes data mask, internal reference, and resolution. `struct npcm_adc` stores MMIO registers, clock, wait queue, optional VREF regulator, reset control, lock, and interrupt status. `npcm_adc_isr()` acknowledges ADC interrupt status and wakes waiters. `npcm_adc_read()` selects a channel, starts conversion, waits up to 10 ms, resets the ADC block on stuck conversion, and returns masked data. `npcm_adc_read_raw()` serializes raw reads and returns scale from regulator voltage or internal VREF.

Control flow: probe allocates IIO state, maps MMIO, obtains reset and clock handles, computes sample rate from the existing divider, requests the IRQ, configures reference selection based on optional `vref`, initializes the wait queue, enables ADC and interrupt bits, starts conversion, and registers the IIO device. Remove unregisters IIO, clears ADC enable, disables the regulator, and disables the clock.

State and persistence: `int_status` is the wait condition for one conversion. Hardware state includes channel select, conversion bit, interrupt enable/status, reference select, reset line, and regulator state. No buffered data or persisted calibration exists.

Dependencies and integration points: it depends on platform MMIO resources, reset controller, clocks, optional regulator, IRQs, OF compatibles `nuvoton,npcm750-adc` and `nuvoton,npcm845-adc`, and IIO direct mode.

Risks: probe never calls `clk_prepare_enable()` before using or later disabling the clock, so clock-provider expectations should be checked against the wider tree. Timeout recovery resets the ADC and starts conversion but still returns `-ETIMEDOUT`. Optional regulator errors other than `-ENODEV` fail probe. Sample rate is read from boot-time divider state, not programmed by this driver.

Test signals: probe on both SoC data variants, external and internal reference modes, raw conversion completion IRQ, timeout/reset path, scale calculation with regulator voltage, sample-frequency reporting, concurrent user reads serialized by the mutex, and remove disabling ADC/regulator/clock.
