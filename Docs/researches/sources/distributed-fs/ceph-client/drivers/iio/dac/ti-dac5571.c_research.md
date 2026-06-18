# sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac5571.c

Purpose: I2C IIO output driver for TI single-channel and quad-channel DAC557x/DAC657x/DAC757x plus DAC081C081/DAC121C081 devices. It abstracts command formatting differences between one-channel and four-channel parts.

Important APIs/types/functions: `struct dac5571_spec` identifies channel count and resolution. `struct dac5571_data` stores I2C client, regulator, mutex, per-channel value cache, per-channel powerdown cache/mode, function pointers for data write and powerdown formatting, and a DMA-safe buffer. `dac5571_cmd_single()`, `dac5571_cmd_quad()`, `dac5571_pwrdwn_single()`, and `dac5571_pwrdwn_quad()` are the hardware protocol shims. `dac5571_ext_info` exposes per-channel powerdown state and mode.

Control flow: probe obtains match data from OF/I2C tables, enables `vref`, chooses single or quad command functions, initializes every channel to zero, and registers an IIO direct-mode device. Raw reads return cached values or Vref-derived scale. Raw writes reject out-of-range values and powered-down channels, then send the correct I2C frame and update cache on success. Powerdown toggles the target channel and restores the cached value when leaving powerdown.

State/persistence: all runtime state is volatile. `val[]`, `powerdown[]`, and `powerdown_mode[]` mirror user-visible sysfs state. Hardware channels are zeroed at probe, while remove unregisters the IIO device and disables the regulator.

Dependencies/integration: depends on I2C, regulator consumer API, device property match data, and IIO sysfs/ext-info. Device tables map many compatible strings to common specs.

Risks: probe assumes `i2c_get_match_data()` is non-null; board files without OF/fwnode match data could misbehave despite `i2c_device_id` carrying pointers. I2C helpers treat short writes as `-EIO`. Powerdown-mode available is shared by type while mode itself is separate. Test signals include all variant match entries, one- vs four-channel buffer layout, per-channel powerdown isolation, regulator errors, and cache consistency after failed I2C transfers.
