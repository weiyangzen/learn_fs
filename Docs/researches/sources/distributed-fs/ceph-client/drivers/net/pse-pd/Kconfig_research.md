# sources/distributed-fs/ceph-client/drivers/net/pse-pd/Kconfig

Purpose: defines Kconfig options for Ethernet Power Sourcing Equipment support and its controller drivers.

Important options: `PSE_CONTROLLER` is a bool menu option gated by `REGULATOR` and enables the core PSE framework. `PSE_REGULATOR` builds the simple regulator-backed PoDL PSE provider. `PSE_PD692X0` enables the Microchip PD692x0 I2C PSE driver and selects `FW_LOADER` plus `FW_UPLOAD` for firmware update support. `PSE_SI3474` enables the Skyworks Si3474 I2C driver. `PSE_TPS23881` enables the TI TPS23881 I2C driver.

Control flow: the menu is visible only after `PSE_CONTROLLER`; child tristates control which objects the Makefile includes. Selecting chip drivers brings in only the subsystem dependencies listed here, while detailed runtime requirements such as regulators, firmware blobs, IRQs, and device-tree topology are enforced by the individual drivers.

State and persistence: no runtime state is stored here. The selected symbols determine whether code is built-in, modular, or omitted, and therefore whether PSE ethtool/regulator integration exists in a kernel image.

Dependencies and integration: this file connects net PSE code to the regulator, I2C, firmware loader, and firmware upload subsystems through Kconfig symbols. Driver module names are documented for modular builds.

Risks and test signals: risks are missing dependency declarations, especially firmware upload for PD692x0 or I2C for chip drivers, and user confusion from the core being bool while providers are tristate. Test signals include allmodconfig/allyesconfig coverage, `PSE_CONTROLLER=n` hiding child symbols, modular builds for each provider, and dependency checks when REGULATOR or I2C is disabled.
