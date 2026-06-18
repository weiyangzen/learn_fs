# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42xx8-i2c.c

Purpose: Provides the I2C bus binding for the shared CS42448/CS42888 (`cs42xx8`) ASoC codec core.

Important APIs, types, and functions: `cs42xx8_i2c_probe()` retrieves chip-specific `struct cs42xx8_driver_data` from the I2C/OF match, initializes an I2C regmap using exported `cs42xx8_regmap_config`, calls shared `cs42xx8_probe()`, enables runtime PM, and requests idle. `cs42xx8_i2c_remove()` disables runtime PM. Match tables bind `cirrus,cs42448` to `cs42448_data` and `cirrus,cs42888` to `cs42888_data`.

Control flow: This file is intentionally thin. All chip validation, regulator/clock/reset handling, ASoC registration, and PM callbacks live in `cs42xx8.c`; the I2C layer only supplies regmap and driver data. The driver's PM pointer is `cs42xx8_pm`, so runtime and system sleep behavior dispatches into the core.

State and persistence: No codec state is owned here. Runtime PM enablement affects the device's power lifecycle after successful shared probe.

Dependencies and integration points: Depends on I2C, OF/module match data, PM runtime, ASoC headers, and exported symbols from `cs42xx8.c`. It is the integration point for device tree and I2C device IDs.

Risks: If match data is missing, probe fails early; this is correct but makes table coverage essential. Runtime PM is enabled only after `cs42xx8_probe()` has already powered up, registered, and powered down/cache-only state, so PM ordering relies on the core's final state. The remove path only disables PM because devm resources and core-managed suspend paths handle the rest.

Test signals: Test OF and legacy I2C matching for both chip variants, missing match-data failure, runtime PM idle after probe, and remove while suspended/active.
