# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_i2c.c

Purpose: implements a GPIO-backed bit-banged I2C adapter for HIBMC VGA DDC/EDID.

Important APIs/functions: `hibmc_ddc_create()` initializes `struct i2c_adapter` and `struct i2c_algo_bit_data`, sets 20 us delay and 2000 us timeout, and registers the bus. `hibmc_ddc_del()` removes it. Internal `setsda/setscl/getsda/getscl` callbacks manipulate MMIO GPIO data and direction bits.

Control flow: VDAC init creates the DDC adapter before registering the VGA connector. EDID reads in `hibmc_drm_vdac.c` use the adapter. Destroy paths call `hibmc_ddc_del()`.

State and persistence: the I2C adapter state is embedded in `struct hibmc_vdac`. SDA/SCL electrical state is represented by GPIO data and direction registers. There is no persistent state.

Dependencies and integration points: depends on I2C bit-bang core, PCI/DRM device parent pointers, and HIBMC MMIO from `struct hibmc_drm_private`.

Risks: GPIO open-drain semantics are encoded through direction changes: high means input/released, low means drive low. Incorrect direction handling can break EDID or hold the bus. No explicit locking is done around GPIO register updates beyond the I2C algorithm's sequencing.

Test signals: VGA EDID read, DDC detect, connector hotplug polling, adapter registration/removal, and bus recovery after NACK/timeouts.
