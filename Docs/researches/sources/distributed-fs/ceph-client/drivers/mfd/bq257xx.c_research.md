<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bq257xx.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/bq257xx.c

Purpose: implements the MFD core for TI BQ25703A/BQ257xx buck-boost charger devices. It creates a 16-bit little-endian I2C regmap and registers regulator and charger child devices.

Important APIs and functions: `bq257xx_probe` allocates `struct bq257xx_device`, initializes regmap, stores client data, and calls `devm_mfd_add_devices`. The regmap config defines read-only manufacturer/status ranges, volatile control/status/ADC ranges, and MAPLE caching.

Control flow: probe allocates state, stores the I2C client, initializes the BQ25703 regmap with 8-bit register addresses and 16-bit little-endian values, attaches state to the client, and creates `"bq257xx-regulator"` and `"bq257xx-charger"` children.

State and persistence: parent state is `struct bq257xx_device` with client and regmap. Charger and regulator runtime state is owned by children; hardware register state persists in the charger IC.

Dependencies and integration points: depends on I2C, regmap, MFD core, and child drivers for charger and regulator functions. OF compatible is `"ti,bq25703a"` and I2C ID is `"bq25703a"`.

Risks: no device-ID check is performed even though manufacturer/device ID registers are defined read-only. No IRQ support or resources are provided. The writeable table is represented as "all except readonly range"; if future status registers appear outside that range, regmap may permit unintended writes.

Test signals: probe on BQ25703A hardware, 16-bit endian register reads/writes, child charger/regulator binding, rejection of writes to read-only manufacturer/status range, and error handling for regmap or child registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bq257xx.c -->
