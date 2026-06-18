# sources/distributed-fs/ceph-client/drivers/iio/dac/vf610_dac.c

Purpose: platform IIO output driver for the Freescale/NXP Vybrid VF610 on-chip DAC. It programs memory-mapped registers, exposes one voltage output channel, and supports runtime conversion-mode selection.

Important APIs/types/functions: `struct vf610_dac` contains clock, device pointer, conversion mode, MMIO base, and mutex. `vf610_dac_init()` enables DAC, selects reference, and starts in low-power mode. `vf610_dac_exit()` clears DAC enable. `vf610_set_conversion_mode()` toggles `VF610_DAC_LPEN`; `vf610_read_raw()` and `vf610_write_raw()` expose raw value and scale.

Control flow: probe allocates an IIO device, maps the MMIO resource, gets and enables the `dac` clock, sets direct-mode channel metadata, initializes the mutex, calls `vf610_dac_init()`, and registers the IIO device. Raw writes store `VF610_DAC_DAT0(val)` to the data register under lock. Suspend disables the DAC and clock; resume reenables the clock and reinitializes control bits.

State/persistence: hardware data register is read directly for raw value; conversion mode is cached in RAM and reset to low-power by `vf610_dac_init()`. Suspend/resume does not preserve the previous conversion mode or output value explicitly. Scale is hard-coded to 3300 mV / 2^12 based on datasheet assumptions.

Dependencies/integration: uses platform resources, device tree compatible `fsl,vf610-dac`, clock framework, MMIO helpers, PM ops, and IIO sysfs enum ext-info. It includes regulator headers but does not use a regulator.

Risks: raw writes mask to 12 bits instead of rejecting out-of-range or negative values. Resume may surprise users by resetting low-power mode and possibly output state depending on hardware retention. Test signals include MMIO register writes, PM suspend/resume, conversion-mode sysfs, clock failure paths, and validation of 12-bit raw write semantics.
