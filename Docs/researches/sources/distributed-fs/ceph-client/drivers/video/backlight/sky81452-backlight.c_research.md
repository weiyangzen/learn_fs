# sources/distributed-fs/ceph-client/drivers/video/backlight/sky81452-backlight.c

Purpose: Skyworks SKY81452 backlight driver. It configures LED current-sink channels, dimming mode, short-detection threshold, boost-current limit, and exposes diagnostic sysfs attributes.

Important APIs/types/functions: `struct sky81452_bl_platform_data` holds parsed DT configuration. `sky81452_bl_update_status()` writes brightness minus one to `SKY81452_REG0` and enables configured sinks in `SKY81452_REG1`. Sysfs handlers expose writable `enable` and read-only `open`, `short`, and `fault`. `sky81452_bl_parse_dt()` parses `led-sources` and Skyworks properties; `sky81452_bl_init_device()` writes mode/current/threshold configuration to `SKY81452_REG2`.

Control flow: probe parses DT, initializes hardware, registers a backlight with regmap as private data, stores drvdata, and creates the sysfs group. Runtime update enables sinks only for positive brightness and clears all sinks on zero. Remove removes sysfs, sets brightness zero, updates status, and lowers the optional enable GPIO.

State and persistence: configuration is local during probe and hardware registers persist. The backlight device stores brightness. Diagnostic attributes read live fault registers.

Dependencies and integration: parent supplies a regmap via `dev_get_drvdata(dev->parent)`, optional GPIO, OF properties, Linux backlight, sysfs.

Risks: parsed `pdata` is not attached as platform data, but update/remove retrieve platform data from the device, so DT-only operation can dereference NULL unless the parent prepopulates platform data. The `while (--num_entry)` loop skips source index 0 when building `enable`. Sysfs string assembly uses small fixed fragments but no `sysfs_emit`. Tests should cover DT led-source masks including first element, brightness updates, sysfs fault formatting, invalid current/threshold, and DT-only remove/update.
