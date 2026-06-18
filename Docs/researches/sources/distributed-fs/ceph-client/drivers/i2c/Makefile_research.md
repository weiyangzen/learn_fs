<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/Makefile -->
## sources/distributed-fs/ceph-client/drivers/i2c/Makefile

Purpose: kbuild object manifest for the I2C core and top-level helper modules. It wires selected Kconfig symbols to object files and always descends into `algos/`, `busses/`, and `muxes/`.

Important build APIs: `obj-$(CONFIG_I2C)` builds `i2c-core.o`, composed from `i2c-core-base.o` and `i2c-core-smbus.o`, with conditional additions for ACPI, slave support, OF, and OF dynamic probing. Other entries build `i2c-boardinfo.o`, `i2c-smbus.o`, `i2c-dev.o`, `i2c-mux.o`, `i2c-atr.o`, `i2c-stub.o`, and slave backends.

Control flow and state: no runtime control flow. Its state is build composition derived from Kconfig. Integration points are the core I2C subsystem, bus/algorithm subdirectories, and `ccflags-$(CONFIG_I2C_DEBUG_CORE) := -DDEBUG`, which changes compiled debug behavior.

Risks and tests: object omissions or wrong conditional composition can cause unresolved symbols or missing runtime features. Test with `make M=drivers/i2c`, allmodconfig fragments around I2C, and link checks for ACPI/OF/slave variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/Makefile -->
