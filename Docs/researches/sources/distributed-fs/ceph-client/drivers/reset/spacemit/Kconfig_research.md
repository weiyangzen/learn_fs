# sources/distributed-fs/ceph-client/drivers/reset/spacemit/Kconfig

Purpose: Kconfig menu for SpacemiT reset controller support, defining shared common infrastructure and K1/K3 SoC reset drivers.

Important APIs/types/functions: symbols are `RESET_SPACEMIT_COMMON`, `RESET_SPACEMIT_K1`, and `RESET_SPACEMIT_K3`. Common support selects `AUXILIARY_BUS`; K1 depends on `SPACEMIT_K1_CCU`, K3 depends on `SPACEMIT_K3_CCU`, and each selects the common reset code.

Control flow: no runtime flow. Build configuration exposes the menu when `ARCH_SPACEMIT || COMPILE_TEST`; enabling SoC CCU support defaults the matching reset driver to the CCU symbol value.

State and persistence: configuration state controls whether objects are built-in, modular, or absent.

Dependencies and integration: binds reset drivers to the SpacemiT CCU providers that create auxiliary devices and parent regmaps.

Risks and test signals: dependency drift with CCU symbols can produce missing auxiliary devices or link failures. Test allmodconfig, COMPILE_TEST without ARCH_SPACEMIT, built-in vs module combinations, and common symbol selection.
