# sources/distributed-fs/ceph-client/drivers/iio/filter/Makefile

Purpose: Kbuild glue for IIO filter drivers.

Important targets: `obj-$(CONFIG_ADMV8818) += admv8818.o` compiles the ADMV8818 driver when selected.

Control flow: one-to-one symbol-to-object mapping. Alphabetical ordering is documented for future additions.

State/persistence: no runtime behavior.

Dependencies/integration: consumes the `ADMV8818` Kconfig symbol and feeds the kernel build system. The object depends on regmap/SPI/common-clock configuration selected in Kconfig.

Risks: minimal. Additions should preserve ordering and ensure Kconfig selects any required bus helpers. Test signals are build coverage when `CONFIG_ADMV8818=m` and `=y`.
