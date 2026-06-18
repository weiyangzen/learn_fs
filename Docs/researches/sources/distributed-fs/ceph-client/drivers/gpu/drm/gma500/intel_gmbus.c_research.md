# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_gmbus.c

## Purpose
This file implements the GMA500 Intel GMBUS/DDC I2C adapters and a GPIO bit-banged fallback for display probing and control. It creates one Linux `i2c_adapter` per GMBUS pin group, maps those adapters onto either VDC or AUX register space depending on platform, and exposes helpers for speed selection, forced bit-banging, reset, and teardown.

## Important APIs, Types, and Functions
The exported entry points are `gma_intel_i2c_reset()`, `gma_intel_setup_gmbus()`, `gma_intel_gmbus_set_speed()`, `gma_intel_gmbus_force_bit()`, and `gma_intel_teardown_gmbus()`. The local `struct intel_gpio` wraps a bit-banged adapter, GPIO register offset, and `drm_psb_private`. `gmbus_xfer()` is the hardware transfer engine, while `intel_i2c_quirk_xfer()` drives transfers through the GPIO fallback. `intel_gpio_create()` maps GMBUS pins to GPIOA-F registers and registers an `i2c-algo-bit` bus.

## Control Flow
Setup allocates `dev_priv->gmbus`, chooses `dev_priv->gmbus_reg`, registers adapters named by port, programs `reg0` with the port number plus 100 kHz rate, and currently creates a forced bit-bang adapter for each port. Hardware transfer writes `GMBUS0`, emits `GMBUS1` cycles, shuttles data through `GMBUS3`, waits on `GMBUS2` ready/wait/error bits, and clears errors through `GMBUS_SW_CLR_INT`. On timeout it logs the failure, disables GMBUS, creates a GPIO fallback if needed, and retries through bit-banging.

## State and Persistence Behavior
Persistent driver state is in `dev_priv->gmbus`, each `intel_gmbus.reg0`, optional `force_bit` fallback adapters, and `dev_priv->gmbus_reg`. Transfers are synchronous and do not store message data after return. GPIO helpers preserve pull-up-disable bits across line toggles. Teardown unregisters both hardware and fallback adapters and leaves MMIO unmapping to driver unload.

## Dependencies and Integration Points
The code depends on Linux I2C core, `i2c-algo-bit`, DRM device private state, GMBUS/GPIO register definitions from `psb_intel_reg.h`, and register bases established in `psb_drv.c` and chip setup. LVDS, HDMI, SDVO, EDID probing, and BIOS/VBT display setup consume the adapters.

## Risks
The hardware path has short polling timeouts and falls back silently to GPIO, which can mask GMBUS regressions. `gmbus_func()` calls the fallback functionality callback without using its return value. The forced bit-bang default means hardware GMBUS is largely bypassed despite the code path existing. Adapter cleanup must match allocation; forced adapters are allocated separately from the main `dev_priv->gmbus` array.

## Test Signals
Useful signals are successful adapter registration for all GMBUS ports, EDID reads on LVDS/SDVO/HDMI DDC, timeout fallback logs only on unsupported pins, no I2C adapter leaks after unload, and successful suspend/resume display probing with `dev_priv->gmbus_reg` selecting AUX on MRST/Oaktrail and VDC on Poulsbo.
