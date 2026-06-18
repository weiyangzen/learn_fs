# sources/distributed-fs/ceph-client/drivers/irqchip/Makefile

Purpose: Maps IRQ chip Kconfig symbols to build objects.

Important APIs/types/functions: Object entries for core `irqchip.o`, AL FIC, Alpine MSI, ATH79, Exynos combiner, Armada MPIC, Aspeed controllers, RISC-V ACLINT, Apple AIC, GIC variants, Loongson, Qualcomm, STM32, TI, and many other controllers.

Control flow: Kbuild includes each object according to its `CONFIG_*` symbol. Some symbols build multiple objects, such as ARM GIC common/variant files and ARM GIC v5 components.

State and persistence: No runtime state; it controls build artifact inclusion and module linkage.

Dependencies/integration: Couples the Kconfig menu to implementation files and architecture-specific early init registration via `IRQCHIP_DECLARE`.

Risks and test signals: Build-test important symbol combinations, especially entries with line continuations and MSI library dependencies; ensure object names match source files and removed/renamed drivers are not left referenced.
