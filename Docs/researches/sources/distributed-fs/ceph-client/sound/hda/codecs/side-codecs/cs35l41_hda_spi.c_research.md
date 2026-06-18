# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_spi.c

## Purpose
This file is the SPI bus binding for the CS35L41 HDA side codec. It validates the expected ACPI/device name, creates a SPI regmap, and delegates common amplifier initialization and teardown to the shared CS35L41 HDA core.

## Important APIs, types, and functions
`cs35l41_hda_spi_probe(struct spi_device *spi)` is the probe entry point. It accepts only devices whose name contains `CSC3551`, then calls `cs35l41_hda_probe(&spi->dev, "CSC3551", spi_get_chipselect(spi, 0), spi->irq, devm_regmap_init_spi(...), SPI)`. `cs35l41_hda_spi_remove()` calls the common remove function. `cs35l41_hda_spi_id[]`, `cs35l41_acpi_hda_match[]`, and `cs35l41_spi_driver` provide module matching and registration.

## Control flow
Probe rejects non-`CSC3551` names with `-ENODEV`. Otherwise the SPI chip select becomes the id passed to common code, which lets the core/property layer map bus instance to amp index. Remove has no local cleanup because state is owned by the common core and devm resources.

## State and persistence
The binding owns no durable per-device state. The regmap is devm-managed and the common core owns driver data, GPIO, firmware, PM, and playback state.

## Dependencies and integration points
It depends on Linux SPI, module, ACPI matching, regmap config from the CS35L41 core, and `cs35l41_hda_pm_ops`. It imports `SND_HDA_SCODEC_CS35L41`, integrating this bus module with the shared HDA smart-amp driver.

## Risks and edge cases
Only `CSC3551` is accepted for SPI. If platform naming changes while the ACPI id remains the same, probe will fail early. SPI chip-select mapping is delegated to common code and property overrides, so bus registration must preserve the intended chip-select value. As with I2C, direct passing of a regmap creation result relies on the common probe handling errors.

## Test signals
Probe on a `CSC3551` SPI platform should create a regmap, call the common probe with `SPI`, and bind into the HDA component framework. Unknown SPI devices should return `-ENODEV`. Remove and PM callback paths should be exercised through module unload and suspend/resume.
