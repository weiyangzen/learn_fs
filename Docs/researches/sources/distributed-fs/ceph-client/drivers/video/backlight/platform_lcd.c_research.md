# sources/distributed-fs/ceph-client/drivers/video/backlight/platform_lcd.c

Purpose: generic platform LCD power wrapper. It registers an `lcd_device` and delegates actual panel power changes to board-supplied `struct plat_lcd_data` callbacks.

Important APIs/types/functions: `struct platform_lcd` stores the `lcd_device`, platform data, current power value, and suspend flag. `platform_lcd_get_power()`, `platform_lcd_set_power()`, and `platform_lcd_controls_device()` implement `struct lcd_ops`. Probe consumes `dev_get_platdata()`, optionally calls `pdata->probe()`, and registers with `devm_lcd_device_register()`.

Control flow: probe validates platform data, performs optional board probing, creates the LCD device, stores drvdata, and sets initial power to `LCD_POWER_REDUCED`. `set_power()` maps `LCD_POWER_OFF` or suspended state to callback value `0`; all other LCD power states map to callback value `1`. Suspend sets `suspended`, reapplies remembered power as off, and resume clears `suspended` and reapplies it.

State and persistence: `power` and `suspended` are in-memory only. The board callback owns any persistent hardware state.

Dependencies and integration: platform bus, LCD class, `video/platform_lcd.h`, board platform data. `controls_device()` links the LCD to the parent display device by comparing `plcd->us->parent`.

Risks: no NULL check for `pdata->set_power`, so platform data is mandatory beyond mere structure presence. Callback failures cannot be surfaced because `set_power` returns success unconditionally. Test signals include probe without pdata, suspend/resume callback arguments, initial reduced-power call, and display-device ownership matching.
