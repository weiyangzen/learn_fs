# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/Kconfig

Purpose: Kconfig menu for Marvell Berlin and Synaptics AS370 pinctrl support, active only when `ARCH_BERLIN` or `COMPILE_TEST` is enabled.

Important APIs/types/functions: defines hidden common `PINCTRL_BERLIN`, user/build selectable `PINCTRL_AS370`, `PINCTRL_BERLIN_BG4CT`, and SoC-default `PINCTRL_BERLIN_BG2`, `PINCTRL_BERLIN_BG2CD`, `PINCTRL_BERLIN_BG2Q`.

Control flow: selecting a SoC-specific symbol selects the common `PINCTRL_BERLIN` core. BG2/BG2CD/BG2Q use `def_bool MACH_*`; AS370 and BG4CT are explicit bool prompts. All public SoC entries depend on OF.

State and persistence: no runtime state; it controls compile-time inclusion and dependency closure.

Dependencies/integration: common core selects `PINMUX` and `REGMAP_MMIO`. The Makefile consumes these symbols to build `berlin.o` and the selected SoC table drivers.

Risks: because `PINCTRL_BERLIN` is `bool`, these drivers are built-in under the selected configs. Missing OF dependency would break DT-only probe paths, but all SoC symbols require OF.

Test signals: run Kconfig resolution for ARCH_BERLIN and COMPILE_TEST builds, confirm `berlin.o` is linked when any SoC symbol is enabled, and verify `MACH_BERLIN_*` defaults select expected drivers.
