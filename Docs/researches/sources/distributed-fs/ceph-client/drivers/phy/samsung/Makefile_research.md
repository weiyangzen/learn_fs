# sources/distributed-fs/ceph-client/drivers/phy/samsung/Makefile

Purpose: Maps Samsung PHY Kconfig symbols to object files and composes common multi-object drivers for Samsung UFS and USB2 PHY support.

Important APIs and functions: Object rules directly build `phy-exynos-dp-video.o`, `phy-exynos-mipi-video.o`, `phy-exynos-pcie.o`, `phy-exynos5-usbdrd.o`, and `phy-exynos5250-sata.o`. The `phy-exynos-ufs` composite includes `phy-samsung-ufs.o` plus GS101, Exynos7, ExynosAuto v9/v920, and FSD UFS data files. The `phy-exynos-usb2` composite includes `phy-samsung-usb2.o` plus selected Exynos4210, Exynos4x12, Exynos5250, and S5PV210 data files.

Control flow: Kbuild uses `obj-$(CONFIG_...)` and per-composite `-y` or `-$(CONFIG_...)` lines to decide which files are compiled and linked into each module or built-in object. UFS variant data is always linked when `PHY_SAMSUNG_UFS` is enabled; USB2 variant data is conditional on the hidden SoC support symbols.

State and persistence: The file persists build composition only. It determines which exported `const struct ..._drvdata` or `..._config` symbols are available to common probe code at link time.

Dependencies and integration points: Integrates with the Kconfig symbols in the same directory and with common C files that declare external SoC data structures, especially `phy-samsung-ufs.c`/`.h` and the common Samsung USB2 driver.

Risks: Missing a variant object causes unresolved externs or missing compatible support. Linking all UFS variants into one module increases compile coverage but can include tables for platforms not present at runtime. Conditional USB2 objects must remain synchronized with Kconfig defaults and extern declarations in shared headers.

Test signals: Kernel build for all relevant symbol combinations, `modinfo`/object inspection for module composition, and runtime matching of DT compatibles to data structures included by the selected objects.
