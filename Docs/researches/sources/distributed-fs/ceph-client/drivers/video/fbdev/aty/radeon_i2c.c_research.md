# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_i2c.c

## Purpose

`radeon_i2c.c` provides the optional `CONFIG_FB_RADEON_I2C` DDC transport used by `radeon_monitor.c` to identify connected displays and obtain EDID. The hardware exposes DDC pins through Radeon GPIO-style registers, so this file wraps those registers in four Linux `i2c_adapter`s using `i2c-algo-bit`, then uses fbdev DDC helpers to classify connectors as CRT, LCD, DFP, or absent.

## Important APIs, Types, And Functions

The primary shared type is `struct radeon_i2c_chan`, defined in `radeonfb.h`, containing a back-pointer to `struct radeonfb_info`, the DDC GPIO register offset, an `i2c_adapter`, and an `i2c_algo_bit_data` object. The low-level bit callbacks are `radeon_gpio_setscl()`, `radeon_gpio_setsda()`, `radeon_gpio_getscl()`, and `radeon_gpio_getsda()`. They use `INREG()` and `OUTREG()` on `chan->ddc_reg`, setting output-enable bits low to drive the line low and clearing them to release the line high.

`radeon_setup_i2c_bus()` fills the adapter name, owner, parent device, bit algorithm callbacks, delay/timeout parameters, raises SCL/SDA, and registers with `i2c_bit_add_bus()`. `radeon_create_i2c_busses()` initializes four channels in fixed order: `ddc_monid` on `GPIO_MONID`, `ddc_dvi` on `GPIO_DVI_DDC`, `ddc_vga` on `GPIO_VGA_DDC`, and `ddc_crt2` on `GPIO_CRT2_DDC`. `radeon_delete_i2c_busses()` unregisters any initialized adapters. `radeon_probe_i2c_connector()` calls `fb_ddc_read()` and returns a Radeon monitor type based on the EDID digital-input bit and mobility/LVDS register state.

## Control Flow

Probe-time flow begins in `radeonfb_pci_register()` after PLL discovery. When I2C support is enabled, it calls `radeon_create_i2c_busses()`, which attempts all four adapter registrations regardless of previous failures. Later, `radeon_probe_screens()` probes specific logical DDC ports by passing enum values such as `ddc_dvi`, `ddc_vga`, or `ddc_crt2` into `radeon_probe_i2c_connector()`. That function converts the enum to the zero-based channel index with `conn - 1`, reads EDID, stores the allocated EDID pointer through `out_edid` if requested, and returns `MT_NONE` on read failure, `MT_LCD` for digital EDID when mobility LVDS is currently on, `MT_DFP` for other digital EDID, or `MT_CRT` for analog EDID.

Teardown flow is symmetric at device removal or failed probe cleanup: `radeon_delete_i2c_busses()` calls `i2c_del_adapter()` on each channel whose `rinfo` pointer remains set and then clears that pointer. EDID memory returned by `fb_ddc_read()` is not freed here; ownership is transferred to `rinfo->mon1_EDID` or `rinfo->mon2_EDID` and freed by the base driver.

## State And Persistence

The file keeps no static mutable state. All channel state lives in `rinfo->i2c[4]`. The Linux I2C core owns registered adapter state after `i2c_bit_add_bus()`, while EDID buffers are dynamically allocated by `fb_ddc_read()` and stored by callers. Electrical line state is maintained in hardware GPIO registers, with explicit readbacks after writes to flush posted MMIO.

## Dependencies And Integration Points

Dependencies are Linux I2C core, `i2c-algo-bit`, fbdev EDID/DDC support, Radeon register definitions, and the `INREG`/`OUTREG` MMIO helpers from `radeonfb.h`. The monitor probing file depends on the port numbering and return semantics here. The base driver depends on this file only under `CONFIG_FB_RADEON_I2C`; without it, monitor probing falls back to OF, BIOS scratch/register state, and DAC load detection.

## Risks

`radeon_create_i2c_busses()` ignores individual setup failures, leaving `rinfo` set even if an adapter was not registered; `radeon_delete_i2c_busses()` may call `i2c_del_adapter()` for a channel whose add failed. `radeon_probe_i2c_connector()` trusts `conn` to be 1 through 4, so incorrect callers would index outside `rinfo->i2c`. EDID classification uses only byte `0x14` and an LVDS-on heuristic, so unusual panels or stale LVDS state can be misclassified. Bit-banged timings are fixed at `udelay = 10` and `timeout = 20`, which may be marginal on some boards.

## Test Signals

Tests should exercise adapter registration/removal with all four ports, simulated `i2c_bit_add_bus()` failure, invalid or absent EDID, analog EDID classification, digital TMDS classification, and the mobility LVDS override. Integration signals include `radeonfb` debug logs for each port, monitor type chosen by `radeon_probe_screens()`, sysfs EDID content from the base driver, and absence of I2C adapter lifetime warnings during probe failure and module unload.
