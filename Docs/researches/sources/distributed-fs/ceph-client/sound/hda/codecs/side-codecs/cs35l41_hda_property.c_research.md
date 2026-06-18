# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_property.c

## Purpose
This file supplies board-specific property overrides for CS35L41 HDA amplifiers on systems whose ACPI `_DSD` data is missing, incomplete, or wrong. It maps ACPI HID and subsystem id combinations to amplifier count, channel placement, boost topology, reset GPIO, speaker-id GPIO, and SPI chip-select handling so the shared CS35L41 HDA core can run on affected laptops.

## Important APIs, types, and functions
`struct cs35l41_config` is the main static board table row: it records subsystem id, number of amps, boost type, channel assignments, GPIO resource indices, and internal boost component values. `cs35l41_config_table[]` contains the large list of known subsystem ids. `struct cs35l41_prop_model` maps HID/SSID pairs to an `add_prop` implementation. The exported API is `cs35l41_add_dsd_properties()`, which selects the first matching model row and calls one of the override helpers.

Key helpers are `cs35l41_add_gpios()`, `generic_dsd_config()`, `hp_i2c_int_2amp_dual_spkid()`, `lenovo_legion_no_acpi()`, and `missing_speaker_id_gpio2()`. `cs35l41_add_gpios()` builds ACPI GPIO mapping arrays for `reset-gpios`, `spk-id-gpios`, and, for limited two-amp SPI cases, `cs-gpios`.

## Control flow
The public call scans `cs35l41_prop_model_table[]` for matching HID and optional SSID. Generic systems then look up `cs35l41_config_table[]`, verify that the driver's ACPI companion matches the physical ACPI device, optionally install GPIO mappings when `_DSD` is absent, derive amp index from SPI chip select or I2C address, fetch reset and speaker-id GPIOs, set speaker position and channel index, and fill `cs35l41_hw_cfg`. Special HP and Lenovo helpers bypass the generic table where the hardware layout needs custom speaker-id or ACPI-less reset handling. `missing_speaker_id_gpio2()` injects a missing speaker-id mapping and then falls back to the normal ACPI parser.

## State and persistence
The file mutates the caller-owned `struct cs35l41_hda`: `index`, `channel_index`, `reset_gpio`, `speaker_id`, `cs_gpio`, and `hw_cfg`. It may also install device-managed ACPI GPIO mappings on the physical ACPI device. No state persists beyond device lifetime, but the static subsystem tables are effectively policy data baked into the driver.

## Dependencies and integration points
It depends on ACPI property APIs, GPIO consumer APIs, SPI chip-select APIs, and CS35L41 core structures. Integration points include `cs35l41_hda_parse_acpi()`, `cs35l41_get_speaker_id()`, `fwnode_gpiod_get_index()`, `devm_acpi_dev_add_driver_gpios()`, `gpiod_get_index()`, `spi_set_csgpiod()`, and `spi_setup()`. It is tightly coupled to real laptop subsystem ids from Dell, HP, Asus, Lenovo, and others.

## Risks and edge cases
The largest risk is table drift: wrong subsystem data can swap left/right channels, select the wrong boost mode, or request wrong GPIO indices. The generic SPI CS workaround only supports two-amp systems and refuses to extend chip selects without `_DSD`. If `_DSD` already exists, reset/speaker-id GPIO mappings cannot be safely added, so the driver warns and may rely on firmware data. Shared GPIO ownership and manual `gpiod_put()` paths must stay balanced.

## Test signals
Test by probing each modeled HID/SSID path, validating amp index and channel placement for two- and four-amp designs, checking internal boost values in `hw_cfg`, confirming speaker-id reads, verifying SPI dual-chip-select behavior, and ensuring unsupported systems return `-ENOENT` so the caller can use ordinary ACPI parsing or fail cleanly.
