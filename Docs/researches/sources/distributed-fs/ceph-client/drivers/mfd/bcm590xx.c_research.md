<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bcm590xx.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/bcm590xx.c

Purpose: implements the Broadcom BCM59054/BCM59056 PMU MFD core. It creates primary and secondary I2C regmaps, verifies PMU identity and revision, and registers the voltage-regulator child.

Important APIs and functions: `bcm590xx_i2c_probe` performs allocation, regmap setup, dummy secondary I2C creation, identity parsing, and child creation. `bcm590xx_parse_version` reads `BCM590XX_REG_PMUID` and `BCM590XX_REG_PMUREV`, validating compatible match data and storing digital/analog revision nibbles.

Control flow: probe allocates `struct bcm590xx`, stores primary client, gets PMU ID from OF match data, initializes primary regmap, creates a secondary dummy I2C client at primary address OR BIT(2), initializes secondary regmap, validates PMU ID/revision, and adds `"bcm590xx-vregs"`. Error paths unregister the secondary dummy device after it has been created.

State and persistence: software state includes primary and secondary I2C clients, primary and secondary MAPLE regmaps, PMU ID, and revision fields. Device register state persists in the PMU; this core does not create IRQ state.

Dependencies and integration points: depends on I2C, OF matching for `"brcm,bcm59054"`/`"brcm,bcm59056"`, regmap, MFD core, and the regulator child driver. The secondary I2C client exposes registers at the PMU's second slave address.

Risks: there is no remove callback to unregister the secondary dummy I2C device on normal driver removal, which can leak the dummy client until device teardown. Non-OF I2C ID matching lacks PMU ID match data. No IRQ chip is provided. A mismatched compatible fails probe after secondary client creation but the error path handles that case.

Test signals: probe both PMU compatibles, primary/secondary regmap access, PMU ID mismatch handling, regulator child registration, module unload behavior for the dummy secondary client, and I2C error handling for ID/revision reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bcm590xx.c -->
