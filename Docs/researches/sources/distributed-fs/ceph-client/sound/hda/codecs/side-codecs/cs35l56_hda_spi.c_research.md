# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda_spi.c

## Purpose
This file is the SPI transport binding for CS35L54/56/57 HDA smart amplifiers. It performs SPI-specific configuration, creates a SPI regmap, and delegates common smart-amp behavior to the shared CS35L56 HDA core.

## Important APIs, types, and functions
`cs35l56_hda_spi_probe()` allocates `struct cs35l56_hda`, sets `base.dev`, calls `cs35l56_init_config_for_spi()`, optionally enables hibernate capability, initializes `base.regmap` with `cs35l56_regmap_spi`, calls `cs35l56_hda_common_probe(cs35l56, id->driver_data, spi_get_chipselect(spi, 0))`, and requests IRQ handling with `cs35l56_irq_request()`. The SPI id table covers `cs35l54-hda`, `cs35l56-hda`, and `cs35l57-hda`; ACPI matches `CSC3554`, `CSC3556`, and `CSC3557`.

## Control flow
The SPI-specific setup runs before common probe so the shared core sees a fully configured control port. If common probe fails, probe returns the error. If IRQ setup fails, common remove is called to unwind. Remove forwards to `cs35l56_hda_remove()`.

## State and persistence
No independent long-lived state exists outside the allocated shared object and devm SPI regmap. The SPI chip select is the amp id consumed by common ACPI parsing.

## Dependencies and integration points
Dependencies include Linux SPI, regmap, module infrastructure, CS35L56 shared SPI configuration helpers, common HDA PM ops, and shared IRQ handling. The module imports both `SND_HDA_SCODEC_CS35L56` and `SND_SOC_CS35L56_SHARED`.

## Risks and edge cases
`cs35l56_init_config_for_spi()` must run successfully before regmap use; misconfigured SPI mode/timing would break all later register traffic. Probe unwind after IRQ failure mirrors the I2C binding and is important because common probe already registered components and runtime PM. Chip-select values must match ACPI `cirrus,dev-index` or platform fixups.

## Test signals
Validate SPI mode/config setup, chip-select to amp-index mapping, regmap register access, IRQ request failure unwind, component binding, shared playback/firmware behavior, and system/runtime PM through the common ops.
