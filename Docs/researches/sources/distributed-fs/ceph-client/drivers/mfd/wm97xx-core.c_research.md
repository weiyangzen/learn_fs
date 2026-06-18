## sources/distributed-fs/ceph-client/drivers/mfd/wm97xx-core.c

Purpose: this is the AC97 MFD core for Wolfson WM9705, WM9712, and WM9713 devices. It identifies the AC97 codec by vendor ID, creates a regmap over the AC97 compatibility layer, and registers codec and touchscreen child devices with shared platform data.

Important APIs, types, and functions: `struct wm97xx_priv` holds the AC97 compatibility handle, regmap, device, and child platform data. `wm97xx_readable_reg()` and `wm97xx_writeable_reg()` define common AC97 register access policy. `wm9705_regmap_config`, `wm9712_regmap_config`, and `wm9713_regmap_config` define chip-specific defaults and volatility. `wm97xx_ac97_probe()` and `wm97xx_ac97_remove()` implement the AC97 codec driver, registered by `wm97xx_module_init()` and unregistered by module exit.

Control flow: probe allocates private state, obtains an `snd_ac97` compatibility object, stores driver data, fills `wm97xx_platform_data` with AC97 and optional battery platform data, selects regmap config and MFD cell list from vendor ID, attaches the same platform data to every child cell, initializes an AC97 regmap, then registers child devices (`wm9705-codec`, `wm9712-codec`, or `wm9713-codec`, plus `wm97xx-ts`). Remove releases the compatibility object.

State and persistence: persistent state lives in the AC97 codec device driver data and child platform data. Regcache defaults capture codec reset state for mixer volumes, powerdown, sample rates, GPIO, digitizer, and model-specific controls. Vendor ID registers are readable but not writable. WM9712 marks `AC97_REC_GAIN` volatile in addition to default AC97 volatility.

Dependencies and integration points: depends on AC97 codec core, AC97 compatibility helpers, regmap AC97 support, MFD core, and WM97xx public headers. Child codec/touchscreen drivers receive shared AC97/regmap access through platform data.

Risks and test signals: probe can fail on unsupported vendor IDs, compatibility allocation failure, regmap init failure, or MFD child registration failure. Because cell platform data is written into static cell arrays, repeated probe/remove paths should be checked for safe reuse. Test signals include AC97 ID match, child devices appearing, regmap reads/writes honoring stride 2 and vendor ID write protection, touchscreen child receiving digitizer registers, and compat release on failed probe/remove.
