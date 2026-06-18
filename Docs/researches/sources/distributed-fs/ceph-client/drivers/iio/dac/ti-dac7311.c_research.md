# sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac7311.c

Purpose: SPI IIO output driver for single-channel TI DAC5311, DAC6311, and DAC7311 devices. It provides raw voltage output, scale from Vref, and shared powerdown controls.

Important APIs/types/functions: `struct ti_dac_spec` stores resolution; `struct ti_dac_chip` holds the SPI device, Vref regulator, cached raw value, powerdown flags, and a mutex-protected two-byte transfer buffer. `ti_dac_get_power()` converts the cached powerdown mode to command bits. `ti_dac_cmd()` packs the DAC value and power bits into the device wire format. IIO callbacks implement raw read/write, integer write format, and ext-info for powerdown.

Control flow: probe forces SPI mode 1 and 16 bits per word, sets up the IIO direct-mode channel, enables Vref, initializes the mutex, and registers the device. Writes validate the raw code against the selected resolution, reject writes while powered down, and send a two-byte SPI command under lock. Powerdown writes always send a command with value zero and update the cached boolean on success.

State/persistence: the only persisted driver state is volatile RAM: one raw output cache, selected powerdown mode, powerdown boolean, and resolution. The driver does not explicitly initialize the DAC output to zero during probe, unlike some neighboring TI DAC drivers.

Dependencies/integration: integrates with SPI, regulator, IIO, OF match, and SPI modalias tables. Scale reads the live regulator voltage in millivolts with a fractional-log2 denominator based on resolution.

Risks: `ti_dac_set_powerdown_mode()` only updates the cached mode and does not reprogram hardware if already powered down; contrast with related TI drivers that update active powerdown state. `ti_dac_write_powerdown()` sends zero rather than the cached DAC value when enabling powerdown and does not restore cached output on power-up. Test signals should cover SPI setup failure, regulator cleanup, resolution-specific bit shifts, mode changes while powered down, raw write `-EBUSY`, and readback from cache.
