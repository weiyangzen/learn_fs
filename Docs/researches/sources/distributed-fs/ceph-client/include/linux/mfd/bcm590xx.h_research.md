## sources/distributed-fs/ceph-client/include/linux/mfd/bcm590xx.h

Purpose: This header defines the shared Broadcom BCM590xx PMU MFD device structure, chip IDs, revision IDs, and dual-regmap layout.

Important APIs, types, and constants: PMU ID constants identify BCM59054 and BCM59056. Revision constants encode known digital and analog revision values for those chips. `enum bcm590xx_regmap_type` distinguishes primary and secondary register maps. Max-register constants bound the primary (`0xe7`) and secondary (`0xf0`) regmaps. `struct bcm590xx` stores the parent device, primary and secondary I2C clients, primary and secondary regmaps, PMU ID, and digital/analog revisions.

Control flow: No functions are declared. Parent probe reads ID/revision registers over I2C, initializes both regmaps, stores them in `struct bcm590xx`, and registers child devices that choose the required register map.

State and persistence: Hardware state lives in PMU registers across two I2C address spaces. Kernel state tracks the two bus clients and regmaps plus chip identity.

Dependencies and integration points: Includes device, I2C, and regmap headers; integrates with MFD children that require PMU regulator, power, or auxiliary functions and must address the correct regmap.

Risks: Primary/secondary register-map selection is a common failure point; a correct offset on the wrong I2C client is still wrong hardware. Revision constants are limited to known variants and may need extension for new silicon.

Test signals: Probe should verify both I2C clients/regmaps initialize, PMU ID matches supported IDs, revision reads match expected values, and child accesses route through the correct `BCM590XX_REGMAP_*` map.
