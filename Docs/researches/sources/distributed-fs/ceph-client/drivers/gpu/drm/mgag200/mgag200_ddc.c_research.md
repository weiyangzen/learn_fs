# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_ddc.c

## Purpose
Creates a bit-banged I2C adapter over Matrox DAC GPIO lines for VGA DDC/EDID reads.

## Important APIs, types, and functions
- `struct mgag200_ddc` stores the `mga_device`, data/clock bit masks, `i2c_algo_bit_data`, and `i2c_adapter`.
- GPIO helpers `mga_i2c_read_gpio()`, `mga_i2c_set_gpio()`, and `mga_i2c_set()` manipulate DAC generic I/O registers.
- I2C algorithm callbacks implement setsda, setscl, getsda, getscl, pre_xfer, and post_xfer.
- `mgag200_ddc_create()` allocates, initializes, registers, and devm-manages the adapter.

## Control flow
Creation initializes DAC generic I/O registers, derives the data and clock masks from `mdev->info->i2c`, fills bit-bang callbacks and timings, names the adapter, registers it with `i2c_bit_add_bus()`, and installs a DRM-managed cleanup action. Each transfer locks `mdev->rmmio_lock`, bit-bangs GPIO, then unlocks.

## State and persistence
Adapter state persists for the DRM device lifetime through DRM-managed allocation. Hardware GPIO direction/data registers persist and are shared with DDC and BMC signaling paths.

## Dependencies and integration points
Depends on Linux I2C algobit, DRM managed resources, PCI/device parenting, and mgag200 register macros. Used by both plain VGA and BMC-aware VGA connector initialization.

## Risks
The GPIO semantics invert output state in `mga_i2c_set()`, so changes can easily break open-drain behavior. DDC transfers must remain serialized against modesetting because DAC indexed registers are shared. Wrong `i2c.data_bit` or `clock_bit` in device info causes EDID failure.

## Test signals
EDID read success, connector hotplug detection, fallback modes when EDID is absent, and absence of races with concurrent modesets are the main signals. I2C adapter registration failures should be visible in DRM error logs.
