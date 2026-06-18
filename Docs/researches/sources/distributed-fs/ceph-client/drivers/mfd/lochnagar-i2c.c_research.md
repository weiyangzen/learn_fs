# sources/distributed-fs/ceph-client/drivers/mfd/lochnagar-i2c.c

Purpose: I2C core for Cirrus Logic Lochnagar audio accessory boards. It resets and identifies Lochnagar1/2, initializes board-specific regmaps and register patches, exports analogue-configuration synchronization, and populates child nodes from device tree.

Important APIs/types/functions: `lochnagar_i2c_probe()`, exported `lochnagar_update_config()`, `lochnagar_wait_for_boot()`, readable/volatile register callbacks, `lochnagar_configs`, and OF match data.

Control flow: probe obtains reset and optional present GPIOs, holds reset briefly, releases the board, creates the matched regmap, waits for boot by reading the reset/device-ID register, validates ID, reads firmware ID words, registers a regmap patch, and calls `devm_of_platform_populate()`. `lochnagar_update_config()` toggles Lochnagar2 analogue update and polls for acknowledgement while caller holds `analogue_config_lock`.

State and persistence: core state stores device, type, regmap, and analogue config mutex. Regmap cache is maple-backed; volatile callbacks prevent stale dynamic Lochnagar2 readings.

Dependencies and integration: depends on DT compatibles `cirrus,lochnagar1`/`2`, GPIOs, regmap, OF platform population, and `linux/mfd/lochnagar*.h` register maps used by child audio/GPIO/regulator components.

Risks: boot wait is fixed to 10 retries at 350 ms. Wrong OF match data or ID mismatch aborts probing. Analogue config update requires external lock discipline and only applies to Lochnagar2.

Test signals: reset/present GPIO behavior, ID and firmware logging, regmap patch application, OF child population, cache/volatile behavior, and analogue update polling.
