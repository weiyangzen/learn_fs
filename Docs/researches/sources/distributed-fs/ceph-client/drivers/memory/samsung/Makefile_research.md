# sources/distributed-fs/ceph-client/drivers/memory/samsung/Makefile

Purpose: object mapping for Samsung memory-controller drivers.

Important APIs/types/functions: maps `CONFIG_EXYNOS5422_DMC` to `exynos5422-dmc.o` and `CONFIG_EXYNOS_SROM` to `exynos-srom.o`.

Control flow: kbuild includes these objects when their Kconfig symbols are enabled. There is no composite object or special ordering logic.

State and persistence: no runtime state. Build output depends only on selected Kconfig symbols.

Dependencies and integration: paired with `drivers/memory/samsung/Kconfig`. The selected objects integrate with platform-driver registration in their respective C files.

Risks: symbol/object name drift would leave drivers unbuilt. Because SROM is boolean and uses `builtin_platform_driver()`, changing this Makefile to modular behavior would require code changes.

Test signals: inspect `make M=drivers/memory/samsung` or full kernel build logs for `exynos5422-dmc.o` and `exynos-srom.o` under corresponding configs.
