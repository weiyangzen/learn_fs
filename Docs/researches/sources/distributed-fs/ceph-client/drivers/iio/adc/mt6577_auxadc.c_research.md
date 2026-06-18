# sources/distributed-fs/ceph-client/drivers/iio/adc/mt6577_auxadc.c

Purpose: this platform driver supports MediaTek SoC AUXADC MMIO blocks. It exposes 16 voltage channels as processed millivolt readings and handles clock enable, power-down control, optional global-idle polling, and suspend/resume power management.

Important APIs, types, and functions: `struct mt6577_auxadc_device` stores MMIO base, main clock, mutex, and compatible quirks. `struct mtk_auxadc_compatible` controls whether sample calibration and global idle checks are used. `mt6577_auxadc_mod_reg()` performs read/modify/write on MMIO registers. `mt6577_auxadc_read()` clears a channel request, waits for the old ready bit to clear, sets the request bit, waits for sample timing, optionally polls global idle, then waits for ready and returns masked raw data. `mt6577_auxadc_read_raw()` converts raw 12-bit samples to millivolts using a 1500 mV full range.

Control flow: probe allocates the IIO device, maps registers, enables the `main` clock, checks the rate, stores match data, powers up the ADC by clearing PDN, registers a devm power-off action, and registers with IIO. Suspend sets PDN and disables the clock; resume enables the clock and powers up again.

State and persistence: software state is per-device and protected by a mutex during sampling. Hardware state includes request bits, ready bits, power-down bit, and clock state. There is no buffered mode or saved calibration table.

Dependencies and integration points: it depends on platform resources, clocks, MMIO polling helpers, device-property match data, OF compatibles for several MediaTek SoCs, and IIO direct mode.

Risks: calibration is currently a stub returning raw data, so compatibles with `sample_data_cali` do not apply real correction. The read path can return `-ETIMEDOUT` at three separate wait points. Clock-rate validation only rejects zero. Register offsets assume a fixed 0x04 stride across 16 channels.

Test signals: boot/probe for each compatible quirk, processed values on all channels, old-ready clear timeout, global-idle timeout on MT8173-style devices, suspend/resume reads, power-off devm action, and conversion scaling against known input voltages.
