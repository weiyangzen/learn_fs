# sources/distributed-fs/ceph-client/drivers/mfd/madera.h

Purpose: this private header connects the Madera bus frontends, shared MFD core, and codec-specific regmap/patch implementations.

Important APIs, types, and functions: it forward-declares `struct madera`, exports `madera_pm_ops`, `madera_of_match`, `madera_dev_init()`, `madera_dev_exit()`, and `madera_name_from_type()`. It declares 16-bit and 32-bit regmap configurations for SPI and I2C variants of CS47L15, CS47L35, CS47L85, CS47L90, and CS47L92 families. It also declares patch functions `cs47l15_patch()`, `cs47l35_patch()`, `cs47l85_patch()`, `cs47l90_patch()`, and `cs47l92_patch()`.

Control flow: this header has no runtime control flow, but it defines the compile-time contract: bus drivers pick regmap configs and call the shared init/exit functions; the core chooses patch functions after hardware ID verification.

State and persistence: no state is stored here. The declarations represent shared state in other translation units, especially the regmap definitions and device initialization functions.

Dependencies and integration points: includes OF and PM headers and relies on public `linux/mfd/madera/core.h` users to define `enum madera_type`. It is included by `madera-core.c`, `madera-i2c.c`, and `madera-spi.c`, and by codec-specific implementation files providing the declared symbols.

Risks: missing or mismatched declarations lead to link-time failures across Kconfig combinations. Any new codec family needs both transport regmap declarations and patch/core handling kept in sync. Test signals are build-matrix coverage for each `CONFIG_MFD_CS47L*` option, I2C/SPI frontend compilation, and symbol export/link validation.
