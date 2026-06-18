# sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb-i2c.c

Purpose: optional DDC2/I2C support for the S3 Savage fbdev driver. It creates a bit-banged I2C adapter over chip-specific GPIO/DDC registers and reads monitor EDID for mode selection.

Important APIs/types/functions: exported-to-driver helpers are `savagefb_create_i2c_busses`, `savagefb_delete_i2c_busses`, and `savagefb_probe_i2c_connector`. GPIO algorithms are split between `savage4_gpio_setscl/setsda/getscl/getsda` for MMIO-style registers and `prosavage_gpio_setscl/setsda/getscl/getsda` for VGA CRTC-register style DDC. `savage_setup_i2c_bus` fills `struct i2c_adapter` and `struct i2c_algo_bit_data`.

Control flow: bus creation stores `par` in `par->chan`, selects a DDC register and bit callbacks by chipset, raises SCL/SDA, and registers the bit-bang adapter. Savage4 may choose `CR_SERIAL2` instead of `CR_SERIAL1` based on revision and CR A6. EDID probing first uses `fb_ddc_read` if the adapter exists, then falls back to firmware EDID via `fb_firmware_edid`. Delete unregisters the adapter if it was registered and clears `chan.par`.

State and persistence: adapter state persists in `struct savagefb_par.chan` for the lifetime of the framebuffer. The I2C callbacks mutate hardware DDC output bits and read input bits from either MMIO or VGA register space; no EDID is cached in this file.

Dependencies and integration: depends on `CONFIG_FB_SAVAGE_I2C`, I2C bit algorithm support, fbdev DDC helpers, PCI device parentage, MMIO established by the main driver, and register helpers/macros from `savagefb.h`.

Risks: `strcpy` copies the adapter name without a local bounds check, relying on the passed string size. Bit operations are not protected by a bus-specific hardware lock beyond I2C core serialization. Unsupported chips silently leave `chan.par = NULL`, so callers must tolerate no EDID. Chip register selection is hardware-specific and easy to regress.

Test signals: builds with I2C enabled, adapter registration logs for Savage4/ProSavage/Twister/Savage2000, EDID read success and firmware fallback, clean adapter deletion on probe failure/remove, and mode selection changes in the main driver based on EDID.
