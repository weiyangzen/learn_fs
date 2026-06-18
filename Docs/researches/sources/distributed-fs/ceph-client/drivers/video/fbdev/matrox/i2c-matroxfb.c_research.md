## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/i2c-matroxfb.c

Purpose: `i2c-matroxfb.c` is an extension module that provides bit-banged I2C adapters for Matrox framebuffer devices. It exposes primary DDC, optional secondary DDC, and optional MAVEN TV-out buses over GPIO bits in the DAC general I/O registers.

Important APIs and functions: it implements a private `matroxfb_driver` named `i2c-matroxfb` with `i2c_matroxfb_probe()` and `i2c_matroxfb_remove()`, registered via exported `matroxfb_register_driver()`. GPIO/I2C callbacks are `matroxfb_gpio_setsda()`, `matroxfb_gpio_setscl()`, `matroxfb_gpio_getsda()`, and `matroxfb_gpio_getscl()` through an `i2c_algo_bit_data` template. `i2c_bus_reg()` initializes each `i2c_bit_adapter`.

Control flow: module init registers the extension driver. For each existing or future Matrox fbdev instance, probe allocates `matroxfb_dh_maven_info`, initializes DAC GPIO registers under DAC lock, registers the primary DDC adapter with Millennium-specific or generic bit masks, and on dual-head devices attempts secondary DDC and MAVEN adapters. If the MAVEN bus registers, it scans address `0x1b` for a `maven` client. Remove unregisters any initialized adapters and frees state.

State and persistence: per-device state is `matroxfb_dh_maven_info`, containing three `i2c_bit_adapter` structures. Hardware GPIO direction/data registers are reset during probe. Adapter registration persists in the kernel I2C core until remove.

Dependencies and integration points: depends on Matrox DAC I/O helpers/locks, `matroxfb_maven.h` for `i2c_bit_adapter`, Linux I2C bit-banging core, and the Matrox private extension-driver list. Consumers include EDID/DDC code and the MAVEN encoder driver.

Risks: GPIO register access shares DAC registers with other code and XFree/Xorg-era users, so `matroxfb_set_gpio()` repeatedly resets `GENIODATA`. Secondary DDC failure is partially tolerated, but primary failure aborts probe. The bit-banged bus has fixed delay/timeout values and may be fragile on unusual cards or cable states. The code treats `-ENODEV` on secondary DDC as a VGA-to-TV plug hint.

Test signals: load with `CONFIG_FB_MATROX_I2C` on Millennium, G200/G400, and dual-head cards; verify `/sys` I2C adapters named `DDC:fb%u #0`, `DDC:fb%u #1`, and `MAVEN:fb%u`; read EDID on primary/secondary connectors; and confirm module unload removes adapters cleanly. Watch dmesg for tolerated secondary/MAVEN registration failures.
