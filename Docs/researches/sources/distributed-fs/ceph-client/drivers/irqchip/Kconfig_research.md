# sources/distributed-fs/ceph-client/drivers/irqchip/Kconfig

Purpose: Provides the central IRQ chip configuration menu for many architecture and SoC interrupt controllers.

Important APIs/types/functions: `config IRQCHIP`, GIC/ITS/MSI options, Armada/Alpine/AL FIC/Aspeed/ACLINT/Apple/Exynos symbols, dependency and `select` relationships for `IRQ_DOMAIN`, `IRQ_DOMAIN_HIERARCHY`, `GENERIC_MSI_IRQ`, `IRQ_MSI_LIB`, `GENERIC_IRQ_CHIP`, and architecture gates.

Control flow: Kconfig symbol selection determines which irqchip drivers are built and which generic IRQ/MSI capabilities are enabled. Several options are hidden bools selected by architecture code; others are user-visible for compile-test or module-capable drivers.

State and persistence: No runtime state. The file persists build-time capability decisions in `.config`, which directly affect early boot interrupt-controller availability.

Dependencies/integration: Integrates irqchip drivers with architecture support, OF/ACPI interrupt discovery, PCI MSI, SMP IPI, mailbox/MFD/regmap helpers, and virtualization-related GIC features.

Risks and test signals: Run Kconfig dependency checks for cross-architecture compile tests, ensure selected drivers pull required generic IRQ/MSI libraries, and verify user-visible tristate entries do not select unavailable architecture-only APIs.
