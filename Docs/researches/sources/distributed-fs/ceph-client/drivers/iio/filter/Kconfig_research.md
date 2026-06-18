# sources/distributed-fs/ceph-client/drivers/iio/filter/Kconfig

Purpose: Kconfig menu for IIO filter drivers, currently containing the Analog Devices ADMV8818 tunable high-pass/low-pass filter.

Important symbols: `ADMV8818` is a tristate user option depending on `SPI`, `COMMON_CLK`, and `64BIT`, and selecting `REGMAP_SPI`.

Control flow: enabling the option builds `admv8818.o` through the filter Makefile. The `COMMON_CLK` dependency matches the driver's optional `rf_in` clock and notifier integration; `64BIT` supports 64-bit frequency calculations exposed through IIO.

State/persistence: build-time only. Runtime state is in `admv8818.c`.

Dependencies/integration: integrates with SPI, regmap over SPI, common clock, and IIO. The help text identifies the device as a 2 GHz to 18 GHz digitally tunable high-pass/low-pass filter.

Risks: the help text contains a typo in "module"; not functional. If `COMMON_CLK` is unavailable, even manual non-clock filter mode cannot be built. Test signals include Kconfig dependency resolution and module build of `admv8818`.
