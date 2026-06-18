# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_lvds_i2c.c

## Purpose
This file implements an LPC GPIO bit-banged I2C bus for LVDS DDC on Atom E6xx/Oaktrail systems. It is used when normal GMBUS/DDC probing is unavailable but an LPC GPIO base was discovered.

## Important APIs, Types, and Functions
The exported function is `oaktrail_lvds_i2c_init()`. Local callbacks `get_clock()`, `get_data()`, `set_clock()`, and `set_data()` implement `i2c-algo-bit` using LPC GPIO registers. Register offsets include `RGIO` and `RGLVL`; line masks are `GPIO_CLOCK` and `GPIO_DATA`.

## Control Flow
Initialization allocates a `gma_i2c_chan`, points `chan->reg` at `dev_priv->lpc_gpio_base`, sets adapter metadata and bit-bang callbacks, idles SDA/SCL high, delays, and registers the bus. Get callbacks set the corresponding GPIO to input in `RGIO` and read `RGLVL`. Set callbacks choose input/high or output/low by modifying `RGIO` and `RGLVL`.

## State and Persistence Behavior
The created `gma_i2c_chan` and Linux adapter persist until the caller destroys them with `gma_i2c_destroy()`. The file does not keep global state. Hardware state is the LPC GPIO direction and level registers.

## Dependencies and Integration Points
It is called from `oaktrail_lvds_init()` as a fallback DDC bus. It depends on `dev_priv->lpc_gpio_base` being discovered in `psb_driver_load()` from PCI device 31:0 and on Linux I2C bit-banging.

## Risks
The bus directly performs `inl`/`outl` on LPC I/O ports; a wrong base can touch unrelated hardware. The adapter has a slower 100 usec bit delay, which may affect probing time. Cleanup responsibility sits with the LVDS caller, so early returns must destroy the bus.

## Test Signals
Signals include EDID reads succeeding on systems with LPC GPIO DDC, correct SCL/SDA idle-high behavior, no I/O port faults, and bus cleanup when LVDS probe fails or the connector is destroyed.
