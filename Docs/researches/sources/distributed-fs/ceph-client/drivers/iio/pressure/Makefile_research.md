<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/Makefile

Purpose: kernel build mapping from pressure-driver Kconfig symbols to object files. It also composes multi-object core modules such as `bmp280.o` and `st_pressure.o`.

Important APIs, types, and functions: uses kbuild `obj-$(CONFIG_...) += ...` assignments and aggregate object variables. In this subset, `bmp280-objs := bmp280-core.o bmp280-regmap.o` links the core and regmap policy into one module, while `bmp280-i2c.o` and `bmp280-spi.o` are separate bus front ends. ABP2 and HSC have separate common and bus-specific objects.

Control flow: kbuild evaluates selected config symbols and builds the corresponding objects as built-in or modules. Object ordering here mostly follows driver names and config symbols.

State and persistence: this file affects compiled artifacts only. It has no runtime state, but it fixes module boundaries and symbol-resolution expectations.

Dependencies and integration points: integrates with Kconfig, module namespaces, exported common-probe symbols, and the IIO pressure directory. Any source file added to Kconfig must appear here to build.

Risks: mismatch between Kconfig symbols and object names causes silent missing drivers or unresolved exports. Multi-object modules must include all required implementation files, as with BMP280 core plus regmap. Hidden bus-helper symbols, such as `HSC030PA_I2C`, require object entries even when the source files are outside this work item.

Test signals: run targeted builds for the pressure directory, `make M=drivers/iio/pressure`, allmodconfig/modpost checks for unresolved symbols and namespace imports, and config matrix checks for I2C-only and SPI-only builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/Makefile -->
