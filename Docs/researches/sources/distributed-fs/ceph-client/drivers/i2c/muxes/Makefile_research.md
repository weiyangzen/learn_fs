# sources/distributed-fs/ceph-client/drivers/i2c/muxes/Makefile

Purpose: object list for I2C mux drivers. It maps each mux Kconfig symbol to its object file and enables debug bus logging flags.

Important entries: object mappings include `i2c-arb-gpio-challenge.o`, `i2c-demux-pinctrl.o`, `i2c-mux-gpio.o`, `i2c-mux-gpmux.o`, `i2c-mux-ltc4306.o`, `i2c-mux-mlxcpld.o`, `i2c-mux-mule.o`, `i2c-mux-pca9541.o`, `i2c-mux-pca954x.o`, `i2c-mux-pinctrl.o`, and `i2c-mux-reg.o`.

Control flow: Kbuild includes objects when the corresponding `CONFIG_` value is `y` or `m`. `ccflags-$(CONFIG_I2C_DEBUG_BUS) := -DDEBUG` enables driver debug prints when configured.

State and persistence: no runtime state.

Dependencies and integration: pairs directly with `Kconfig` and the parent I2C build system.

Risks: a missing object mapping would silently omit a selected driver. Debug flag scope applies to this directory's compilation units.

Test signals: kernel builds for each mux symbol as module and built-in, plus debug config builds.
