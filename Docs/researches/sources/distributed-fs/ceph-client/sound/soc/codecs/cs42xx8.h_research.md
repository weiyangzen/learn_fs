# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42xx8.h

Purpose: Declares the shared CS42xx8 bus/core contract and defines the CS42448/CS42888 register map and bit fields.

Important APIs, types, and functions: `struct cs42xx8_driver_data` carries variant name and ADC count. Extern declarations expose `cs42xx8_pm`, `cs42448_data`, `cs42888_data`, `cs42xx8_regmap_config`, and `cs42xx8_probe()`. Register macros cover chip ID, power, functional mode, interface format, ADC control, transition control, DAC mute, volume, invert, status, mask, and MUTEC registers. Helper macros build functional-mode masks and values for DAC/ADC directions.

Control flow: Bus drivers call `cs42xx8_probe()` and attach `cs42xx8_pm`. The core uses register and bitfield macros for DAI format setup, functional mode selection, power/mute controls, volatile/writeable regmap behavior, and variant-specific capture support.

State and persistence: The header stores no state. Its exported declarations define module boundaries, while macros define the hardware state that regmap caches and restores.

Dependencies and integration points: Consumers must include it in a Linux device/regmap/ASoC context. It supports I2C transport today and could support another transport by reusing the exported regmap config/probe/PM symbols.

Risks: `struct cs42xx8_driver_data` uses a fixed-size mutable `char name[32]` even though variant names are constant; accidental mutation would affect DAI naming. Many field macros are open-coded rather than using `GENMASK`, increasing maintenance risk when changing widths. Header macros do not enforce valid variant-specific ADC3 usage.

Test signals: Build coverage for transport/core linkage, regmap tests for writeable/volatile boundaries, and runtime tests confirming functional-mode helper macros produce correct DAC vs ADC fields.
