<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/i2c/algos/Kconfig

Purpose: Kconfig menu for reusable software/hardware-assisted I2C algorithm modules. It is visible only when `I2C_HELPER_AUTO` is disabled, because normal bus drivers usually select needed helpers automatically.

Important symbols: `I2C_ALGOBIT` provides bit-banged I2C callbacks, `I2C_ALGOPCF` provides PCF8584 algorithm support, and `I2C_ALGOPCA` provides PCA9564/PCA9665 algorithm support. Each is tristate, allowing built-in or module builds.

Control flow and state: no runtime flow. Kconfig state controls whether kbuild includes the matching algorithm objects and whether downstream bus drivers can link exported helper functions such as `i2c_bit_add_bus`, `i2c_pcf_add_bus`, or `i2c_pca_add_bus`.

Dependencies and integration: this file is sourced under top-level `I2C`; selecting these symbols affects `drivers/i2c/algos/Makefile`. Bus drivers such as Acorn, Elektor, ICY, PCA platform/ISA, and GPIO-like adapters integrate through these algorithms.

Risks and tests: visibility or tristate mistakes can produce impossible module combinations. Test by building with helper auto on/off and by selecting each algorithm as `y` and `m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/Kconfig -->
