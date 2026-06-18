# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41-spi.c

Purpose: SPI transport binding for CS35L40/41/51/53-compatible devices using the shared CS35L41 ASoC core.

Important APIs and data: `cs35l41_id_spi` exposes SPI modaliases. `cs35l41_spi_probe()` allocates `struct cs35l41_private`, sets `spi->max_speed_hz` to `CS35L41_SPI_MAX_FREQ`, creates the SPI regmap from `cs35l41_regmap_spi`, stores `dev` and `irq`, and calls `cs35l41_probe()`. `cs35l41_spi_remove()` calls `cs35l41_remove()`. OF compatibles include `cirrus,cs35l40` and `cirrus,cs35l41`; ACPI IDs include `CSC3541` and `CLSA3541`. The driver binds PM through exported `cs35l41_pm_ops`.

Control flow: kernel SPI matching enters probe, allocates device-private state with devres, applies SPI setup, initializes regmap, then delegates all hardware bring-up to the common codec probe. Removal only recovers drvdata and delegates teardown. Module registration uses `module_spi_driver()`.

State and persistence: this file owns no persistent hardware state beyond storing the common private pointer in SPI drvdata. Any platform data returned by `dev_get_platdata()` is passed through as optional `cs35l41_hw_cfg`; otherwise the core parses firmware properties.

Dependencies and integration: depends on SPI, ACPI/OF matching, regmap SPI support, and `cs35l41.h`. It imports the shared regmap config and core probe/remove exported by the library/core files.

Risks: `dev_err_probe(cs35l41->dev, ...)` is used before `cs35l41->dev` is assigned if `devm_regmap_init_spi()` fails, which depends on a null-safe device pointer path and is suspicious compared with using `&spi->dev`. `spi_setup()` failure aborts early, but max-speed forcing can override board settings. The ID table lists multiple related part names while the common probe still validates chip IDs.

Test signals: probe/remove can be tested by SPI modalias or OF/ACPI enumeration, regmap initialization failure injection, and validation that runtime/system PM callbacks from the shared core are wired through the bus driver.
