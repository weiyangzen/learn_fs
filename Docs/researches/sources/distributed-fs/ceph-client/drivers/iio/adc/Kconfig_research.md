# sources/distributed-fs/ceph-client/drivers/iio/adc/Kconfig

Purpose: Kconfig menu for IIO analog-to-digital converter drivers under `drivers/iio/adc`.

Important APIs/types/functions: defines `menu "Analog to digital converters"` and one `config` symbol per ADC helper/core/driver. Relevant symbols for this subset include `IIO_ADC_HELPER`, `88PM886_GPADC`, `AB8500_GPADC`, and `AD4000`. Many entries express bus and subsystem dependencies (`SPI`, `I2C`, `MFD_*`, `REGULATOR`, `COMMON_CLK`, `GPIOLIB`, `THERMAL`, `HAS_IOMEM`) and select IIO buffer, DMA, trigger, regmap, backend, and SPI offload helpers.

Control flow: Kconfig has no runtime flow, but controls build inclusion and dependency propagation. `88PM886_GPADC` depends on and defaults to the 88PM886 PMIC MFD. `AB8500_GPADC` is a built-in boolean depending on AB8500 core and regulator support. `AD4000` depends on SPI and selects IIO buffer, DMAengine buffer, triggered buffer, and SPI offload infrastructure.

State and persistence behavior: no runtime state. The selected symbols persist in kernel `.config` and determine which objects the Makefile builds.

Dependencies and integration points: consumed by the kernel Kconfig system and paired with `drivers/iio/adc/Makefile`. It coordinates helper symbols shared by multiple drivers, such as `AD_SIGMA_DELTA`, `AD7091R`, `AD7606`, `QCOM_VADC_COMMON`, `STM32_DFSDM_CORE`, and `IIO_ADC_HELPER`.

Risks: dependency mistakes can expose drivers without required APIs or hide valid build combinations. `select` can force helper subsystems on, so selected symbols must not have unmet direct dependencies. The file relies on approximate alphabetical ordering; misplaced entries complicate maintenance. Help text module names must match Makefile object names and actual module output.

Test signals: run `make olddefconfig` and targeted `allyesconfig`/`allmodconfig` builds, verify `CONFIG_88PM886_GPADC`, `CONFIG_AB8500_GPADC`, and `CONFIG_AD4000` produce expected objects, check unmet dependency warnings, and compare new entries against alphabetical order and Makefile additions.
