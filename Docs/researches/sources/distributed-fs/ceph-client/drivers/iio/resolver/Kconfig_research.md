# sources/distributed-fs/ceph-client/drivers/iio/resolver/Kconfig

Purpose: Kconfig menu for resolver-to-digital converter drivers under IIO. It declares AD2S90, AD2S1200/AD2S1205, and AD2S1210 build options.

Important APIs/types/functions: this file has no C APIs, but it controls module availability. `AD2S90` depends on SPI. `AD2S1200` depends on SPI and GPIOLIB or COMPILE_TEST. `AD2S1210` depends on SPI, COMMON_CLK, GPIOLIB or COMPILE_TEST, and selects REGMAP, IIO_BUFFER, and IIO_TRIGGERED_BUFFER.

Control flow: build configuration enters `menu "Resolver to digital converters"` and exposes tristate choices. Help text describes sysfs/direct access and module names.

State and persistence: selected symbols persist in kernel configuration and drive Makefile object inclusion. There is no runtime state.

Dependencies/integration: integrates with kernel Kconfig dependency resolution and with the resolver Makefile. AD2S1210's selected buffer/regmap dependencies match its implementation requirements.

Risks and test signals: dependency drift can break compile coverage if driver code gains a new subsystem requirement. Test `allyesconfig`, `allmodconfig`, and COMPILE_TEST builds, especially AD2S1210 with and without GPIO support.
