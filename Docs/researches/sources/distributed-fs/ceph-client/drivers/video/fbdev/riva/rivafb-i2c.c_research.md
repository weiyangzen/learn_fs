# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/rivafb-i2c.c

## Purpose
`rivafb-i2c.c` provides bit-banged I2C/DDC support for the RIVA framebuffer driver. It exposes up to three DDC busses through Linux `i2c-algo-bit`, allowing `fbdev.c` to read monitor EDID blocks via `fb_ddc_read()`.

## Important APIs, types, and functions
- GPIO callbacks `riva_gpio_setscl()`, `riva_gpio_setsda()`, `riva_gpio_getscl()`, and `riva_gpio_getsda()` manipulate VGA CRTC-indexed DDC bits.
- `riva_setup_i2c_bus()` initializes one `struct riva_i2c_chan` adapter and registers it with `i2c_bit_add_bus()`.
- Exported helpers `riva_create_i2c_busses()`, `riva_delete_i2c_busses()`, and `riva_probe_i2c_connector()` are called from probe/remove/EDID discovery in `fbdev.c`.

## Control flow
`riva_create_i2c_busses()` attaches `par` to three channels, assigns DDC base indices `0x36`, `0x3e`, and `0x50`, and registers BUS1/BUS2/BUS3. Bus setup raises SDA/SCL, delays, and hands callbacks to the I2C bit-bang core. EDID probing checks whether the requested channel registered, reads EDID, returns it via `out_edid`, and reports success as `0` when an EDID buffer was returned.

## State and persistence behavior
Per-channel state lives in `struct riva_i2c_chan`: parent `par`, DDC base index, `i2c_adapter`, and bit algorithm data. Failed registration sets `chan->par = NULL`; deletion unregisters live adapters and clears the pointer. EDID buffers are allocated by `fb_ddc_read()` and freed by the caller path in `fbdev.c`.

## Dependencies and integration points
The file depends on `rivafb.h`, Linux I2C core, `i2c-algo-bit`, fbdev EDID helper `../edid.h`, VGA register access macros, and the active `par->riva.PCIO` CRTC window selected by `nv_driver.c`. It is compiled only when RIVA I2C support is enabled.

## Risks and test signals
Risks include no explicit locking around shared CRTC index/data registers, fixed DDC base guesses, inverted success convention in `riva_probe_i2c_connector()` relative to some kernel style, and possible bus leaks if partial creation is not deleted. Test signals include three adapter registrations, successful EDID read on expected connectors, clean deletion on remove and probe failure, and no interference with mode-setting CRTC accesses.
