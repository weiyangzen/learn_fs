# sources/distributed-fs/ceph-client/arch/arm/plat-orion/Makefile

Purpose: Builds the legacy Marvell Orion ARM platform support objects and exposes the local `include` directory to those compilation units.

Important build rules: `ccflags-y := -I$(src)/include` makes `include/plat/*.h` visible. `obj-$(CONFIG_PLAT_ORION_LEGACY)` includes `irq.o`, `pcie.o`, `time.o`, `common.o`, and `mpp.o`. `gpio.o` is conditionally accumulated in `orion-gpio-$(CONFIG_GPIOLIB)` and then included only when legacy Orion support is enabled.

Control flow and integration: Kbuild selects this directory from the ARM platform tree. GPIO support depends on both `CONFIG_PLAT_ORION_LEGACY` and `CONFIG_GPIOLIB`; without GPIOLIB, callers must not rely on `orion_gpio_*` implementation symbols being built.

State and persistence: No runtime state. The file controls object presence and include path only.

Risks and test signals: Configuration matrix testing should cover `CONFIG_PLAT_ORION_LEGACY=y` with `CONFIG_GPIOLIB=y/n`, plus link checks for machine code that references GPIO helpers. Header path changes can break `#include <plat/...>` consumers.
