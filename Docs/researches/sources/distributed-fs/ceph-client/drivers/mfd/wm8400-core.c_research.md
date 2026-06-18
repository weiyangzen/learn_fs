# sources/distributed-fs/ceph-client/drivers/mfd/wm8400-core.c

`wm8400-core.c` is the WM8400 core and I2C frontend. It validates chip identity, configures regmap caching, registers the codec child, runs optional platform initialization, and exports a helper to reset the codec register cache.

Important APIs are `wm8400_volatile()`, `wm8400_register_codec()`, `wm8400_init()`, `wm8400_regmap_config`, `wm8400_reset_codec_reg_cache()`, `wm8400_i2c_probe()`, and `wm8400_driver_init()`. Init reads `WM8400_RESET_ID` and requires `0x6172`, reads revision from `WM8400_ID`, registers a devm MFD child named `wm8400-codec`, and calls `pdata->platform_init` if present. The regmap uses 8-bit registers, 16-bit values, Maple cache, max register `WM8400_REGISTER_COUNT - 1`, and marks interrupt status/levels and shutdown reason volatile.

State is the devres-managed `struct wm8400`, regmap cache, and registered codec child. Hardware identity/revision is read-only; platform initialization may program board-specific state. Dependencies include I2C, regmap, MFD core, WM8400 private/audio headers, and optional platform data.

Risks: missing platform initialization only warns and may leave board-required setup undone; no explicit remove path is present; only I2C is implemented here despite generic-init comments mentioning SPI; cache reset must keep using the same config. Test signals include rejecting wrong reset IDs, revision logging, `wm8400-codec` child creation, platform-init success/failure, and cache behavior after `wm8400_reset_codec_reg_cache()`.
