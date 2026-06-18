# sources/distributed-fs/ceph-client/drivers/iio/frequency/Kconfig

Purpose: Kconfig menu for IIO frequency devices including DDS/clock distribution and PLL/frequency synthesizer drivers.

Important symbols: `AD9523`, `ADF4350`, `ADF4371`, `ADF4377`, `ADMFM2000`, `ADMV1013`, `ADMV1014`, `ADMV4420`, and `ADRF6780`. Dependencies select SPI, GPIOLIB, COMMON_CLK, REGMAP_SPI, and 64BIT as needed by each implementation.

Control flow: choices are grouped under clock generator/distribution and PLL frequency synthesizers. Each symbol maps to a same-named object in the Makefile.

State/persistence: build-time only. Runtime configuration is through device tree/platform data and IIO sysfs/debugfs.

Dependencies/integration: captures bus and framework needs for the frequency directory. `ADF4377` and converter drivers depend on common clock where they consume or provide clocks; regmap-based SPI drivers select `REGMAP_SPI`.

Risks: dependency changes can break compile-time assumptions, particularly 64-bit arithmetic for ADMV1014 and SPI/regmap availability for ADF437x/ADMV4420. Test signals include allmodconfig-style builds and ensuring `select REGMAP_SPI` matches source use.
