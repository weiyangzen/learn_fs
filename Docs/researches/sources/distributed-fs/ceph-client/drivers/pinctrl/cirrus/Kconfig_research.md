# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/Kconfig

Purpose: Kconfig entries for Cirrus Logic CS42L43, Lochnagar, and Madera-family pinctrl drivers.

Important APIs/types/functions: defines visible tristate `PINCTRL_CS42L43` and `PINCTRL_LOCHNAGAR`, hidden tristate `PINCTRL_MADERA`, and hidden bool chip-table selectors `PINCTRL_CS47L15`, `PINCTRL_CS47L35`, `PINCTRL_CS47L85`, `PINCTRL_CS47L90`, `PINCTRL_CS47L92`.

Control flow: CS42L43 depends on `MFD_CS42L43` and selects GPIOLIB, PINMUX, PINCONF, and GENERIC_PINCONF. Lochnagar depends on `MFD_LOCHNAGAR && !MIPS`, avoiding a symbol clash. Madera is selected by MFD options and selects PINMUX/GENERIC_PINCONF.

State and persistence: compile-time only.

Dependencies/integration: paired with the Cirrus Makefile, MFD parent drivers, gpiolib, pinctrl, and generic pinconf infrastructure.

Risks: hidden chip selectors must be selected by Madera MFD Kconfig; otherwise the common Madera driver probes but no chip table is available and returns `-ENODEV`. The `!MIPS` guard is necessary due to `RST` naming conflicts.

Test signals: Kconfig dependency resolution for MFD-enabled builds, module/built-in combinations for CS42L43 and Lochnagar, and compile coverage for each hidden Madera chip selector.
