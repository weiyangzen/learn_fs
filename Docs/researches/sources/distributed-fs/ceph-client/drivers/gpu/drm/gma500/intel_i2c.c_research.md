# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_i2c.c

## Purpose
This is the older generic GPIO bit-banged I2C implementation used by GMA500 display code. It creates a single `gma_i2c_chan` from a GPIO register, exposes it as a Linux `i2c_adapter`, and provides low-level SCL/SDA callbacks for EDID and panel-control buses.

## Important APIs, Types, and Functions
The exported APIs are `gma_i2c_create()` and `gma_i2c_destroy()`. The callbacks `get_clock()`, `get_data()`, `set_clock()`, and `set_data()` implement `struct i2c_algo_bit_data` over the GPIO register in `chan->reg`. `struct gma_i2c_chan`, declared in `psb_intel_drv.h`, stores the adapter, algorithm data, target address, owning DRM device, and GPIO register.

## Control Flow
Creation allocates the channel, initializes the adapter name/owner/parent, wires `i2c-algo-bit` callbacks, registers the bus with `i2c_bit_add_bus()`, then idles SDA and SCL high. Set callbacks preserve pull-up-disable bits, choose input direction for logical high and output low for logical low, write the GPIO register, and delay for line settling.

## State and Persistence Behavior
The only persistent state is the allocated `gma_i2c_chan` and its registered adapter. The GPIO register is the live hardware state; no transfer data is cached. Destroy unregisters the adapter and frees the channel. Runtime access depends on the caller ensuring display register access is powered when required.

## Dependencies and Integration Points
The file integrates with LVDS DDC and backlight paths in `psb_intel_lvds.c`, with SDVO or other output probing via the shared `gma_i2c_chan` type, and with GPIO definitions and `REG_READ`/`REG_WRITE` macros from `psb_drv.h`/`psb_intel_reg.h`.

## Risks
There is no explicit `gma_power_begin()` around GPIO access here, so callers must avoid using it while MMIO is inaccessible. The function jumps to `out_free` even for allocation failure, which is harmless but makes the error flow less clear. Incorrect GPIO register selection can toggle unrelated pins, and a missing destroy path leaks an adapter.

## Test Signals
Signals include successful `i2c_bit_add_bus()` registration, EDID reads through LVDS DDC, I2C backlight writes on panels with I2C brightness control, stable SCL/SDA idle-high behavior, and clean adapter removal during connector or driver teardown.
