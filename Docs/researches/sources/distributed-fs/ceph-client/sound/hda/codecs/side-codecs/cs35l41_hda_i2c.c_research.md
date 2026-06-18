# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_i2c.c

## Purpose
This is the I2C bus binding for the Cirrus CS35L41 HD-audio side codec driver. It does not implement amplifier policy itself; it identifies supported ACPI-instantiated devices, builds an I2C regmap, and delegates all real initialization, runtime PM, component binding, firmware, and audio behavior to `cs35l41_hda_probe()` and `cs35l41_hda_remove()` from the shared CS35L41 HDA core.

## Important APIs, types, and functions
The key entry point is `cs35l41_hda_i2c_probe(struct i2c_client *clt)`. It derives a `device_name` by scanning `dev_name(&clt->dev)` for `CLSA0100`, `CLSA0101`, or `CSC3551`, then calls `cs35l41_hda_probe(&clt->dev, device_name, clt->addr, clt->irq, devm_regmap_init_i2c(...), I2C)`. `cs35l41_hda_i2c_remove()` forwards removal to the shared core. The `i2c_device_id`, `acpi_device_id`, and `i2c_driver` tables expose the module to I2C and ACPI matching. The driver imports the `SND_HDA_SCODEC_CS35L41` namespace and uses `cs35l41_hda_pm_ops` for PM callbacks supplied by the core.

## Control flow
Probe performs only HID/name validation and regmap construction. Unsupported names return `-ENODEV` before any regmap or core state is created. Supported devices pass the physical I2C address as the amplifier id and the I2C IRQ into the core. Remove is symmetric and intentionally thin.

## State and persistence
This file owns no persistent state beyond driver registration tables. Per-device state is allocated and attached by the common CS35L41 HDA core. The I2C regmap is device-managed, so its lifetime follows the client device. Firmware, calibration, GPIO, and playback state live outside this file.

## Dependencies and integration points
It depends on the Linux I2C, module, ACPI/mod_devicetable, and regmap infrastructure, plus `cs35l41_hda.h`. It integrates with ACPI names used both by direct ACPI enumeration and serial-multi-instantiate style devices, which is why it checks `dev_name()` rather than only table data.

## Risks and edge cases
The string matching is deliberately narrow. A supported ACPI id presented under an unexpected device name will be rejected. Because `devm_regmap_init_i2c()` is passed directly into the core call, error handling for an `ERR_PTR` regmap must be robust in `cs35l41_hda_probe()`. Device-name matching must remain aligned with ACPI tables and with serial-multi-instantiate naming conventions.

## Test signals
Useful signals are successful binding for `CLSA0100`, `CLSA0101`, and `CSC3551`; rejection of unknown names; a valid regmap visible to the common probe; interrupt handoff to the core; module autoload from ACPI; and clean remove with no device-managed resource leaks.
