# sources/distributed-fs/ceph-client/drivers/video/backlight/pandora_bl.c

Purpose: Pandora handheld-specific backlight driver. It exposes a Linux backlight device named `pandora-backlight` and translates brightness into TWL4030 PWM0 writes for a TWL4030 PWM0 plus TPS61161 LED-driver arrangement.

Important APIs/types/functions: `struct pandora_private` tracks whether the PWM was off; `pandora_backlight_update_status()` implements `struct backlight_ops`; `pandora_backlight_probe()` allocates state, registers the backlight, configures PWM period, initializes max brightness, and enables the PWM pin mux. Hardware access uses `twl_i2c_read_u8()` and `twl_i2c_write_u8()` against `TWL_MODULE_PWM` and `TWL4030_MODULE_INTBR`.

Control flow: backlight core calls `update_status`; power, fb blank, and suspend states force brightness to zero. On first transition from off, the driver writes maximum PWM duty for TPS61161 calibration, enables clock before PWM output, waits for the 1-wire detection window, then writes the requested duty. On zero brightness it disables PWM output before the clock and skips redundant off writes.

State and persistence: only runtime state is `old_state`; hardware registers persist until later driver or PM events. There is no NVM or file persistence.

Dependencies and integration: platform driver, TWL MFD register access, Linux backlight core, suspend/resume through `BL_CORE_SUSPENDRESUME`.

Risks: TWL I2C return values are ignored, so probe/status updates report success even if register programming fails. The device is highly board-specific and assumes exact PWM/TPS61161 behavior and timing. Tests should exercise brightness clamp, off-to-on calibration path, suspend blanking, and register sequence ordering on TWL-backed hardware or mocks.
