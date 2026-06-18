<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/axp20x-rsb.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/axp20x-rsb.c

Purpose: provides the sunxi RSB transport binding for X-Powers AXP PMICs. It supports Allwinner boards where the PMIC is accessed over the reduced serial bus and delegates common behavior to the AXP20x core.

Important APIs and functions: `axp20x_rsb_probe` and `axp20x_rsb_remove` mirror the I2C transport but use `devm_regmap_init_sunxi_rsb` and `sunxi_rsb_device_get_drvdata`. OF matches cover AXP223, AXP717, AXP803, AXP806, AXP809, and AXP813.

Control flow: probe allocates `struct axp20x_dev`, sets device and RSB IRQ, stores driver data, calls `axp20x_match_device`, initializes a sunxi RSB regmap using the selected config, and calls `axp20x_device_probe`. Remove calls the shared core removal path.

State and persistence: no transport-specific persistent state exists beyond the shared AXP20x state and bus regmap. PMIC register state and child devices are controlled by the core.

Dependencies and integration points: depends on `sunxi-rsb`, OF match data, regmap, and AXP20x core functions. It is the integration point for Allwinner PMICs on RSB rather than I2C.

Risks: only OF matching is supported. RSB addressing quirks such as AXP806 master/slave address-extension setup are handled later by the core, so incorrect firmware properties can leave the PMIC inaccessible after initial setup. No-IRQ child fallback follows the same core behavior as I2C.

Test signals: RSB probe on supported Allwinner boards, AXP806 master/self-working/slave configurations, IRQ and no-IRQ child registration, regmap read/write access over RSB, and remove/unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/axp20x-rsb.c -->
