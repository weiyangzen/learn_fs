# sources/distributed-fs/ceph-client/drivers/peci/Kconfig

Purpose: Defines the top-level Kconfig menu for Linux PECI support and includes controller-driver options.

Important APIs and types: `menuconfig PECI` controls the PECI core as a tristate. `config PECI_CPU` enables the PECI CPU auxiliary-device driver and selects `AUXILIARY_BUS`. The file sources `drivers/peci/controller/Kconfig` under `if PECI`.

Control flow: Kconfig selection enables compilation of PECI core, optional CPU device support, and hardware controller menus. No runtime code.

State and persistence: Build configuration state determines which modules or built-in objects exist: `peci`, `peci-cpu`, and controller drivers.

Dependencies and integration points: Integrates with the kernel build system, auxiliary bus, and controller Kconfig files. Intended for Intel platform BMC kernels.

Risks: Controller options are invisible unless `PECI` is enabled. `PECI_CPU` creates auxiliary devices consumed by other drivers, so enabling it without functional controller support may not yield useful runtime behavior.

Test signals: Kconfig visibility, successful `CONFIG_PECI=m/y` builds, `peci.ko` and `peci-cpu.ko` generation when modular, and controller submenu inclusion.
