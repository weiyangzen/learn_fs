<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/Makefile -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/Makefile

Purpose: kbuild manifest for all I2C hardware bus drivers. It maps Kconfig symbols to object files and records composite driver objects.

Important entries for this work item: ALi and AMD legacy SMBus drivers map one-to-one (`i2c-ali1535.o`, `i2c-ali1563.o`, `i2c-ali15x3.o`, `i2c-amd756.o`, `i2c-amd8111.o`); `CONFIG_I2C_AMD_MP2` builds both `i2c-amd-mp2-pci.o` and `i2c-amd-mp2-plat.o`; `CONFIG_I2C_AMD_ASF` builds `i2c-amd-asf-plat.o`; `I2C_ALTERA`, `I2C_ASPEED`, and `I2C_ACORN` map to their bus objects. The file also defines composite objects such as DesignWare, AT91, STM32F7, Octeon, and ThunderX.

Control flow and state: no runtime flow. It integrates Kconfig state with link/module composition and debug compilation via `ccflags-$(CONFIG_I2C_DEBUG_BUS) := -DDEBUG`.

Risks and tests: missing composite pairings cause link failures or half-present drivers, especially MP2 PCI/platform split. Test allmodconfig, per-symbol module builds, and `modpost` for shared exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/Makefile -->
