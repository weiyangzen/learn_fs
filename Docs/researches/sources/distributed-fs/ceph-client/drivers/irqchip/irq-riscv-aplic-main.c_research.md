<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-main.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-main.c

## Purpose
`irq-riscv-aplic-main.c` provides common RISC-V APLIC setup, register initialization, IRQ type programming, firmware parsing, and power-management state save/restore shared by direct and MSI delivery modes.

## Important APIs, Types, and Functions
Global list `aplics` tracks active controllers. PM helpers are `aplic_save_states()`, `aplic_restore_states()`, syscore callbacks, GENPD notifier, `aplic_pm_add()`, and `aplic_pm_remove()`. Shared IRQ helpers are `aplic_irq_mask()`, `aplic_irq_unmask()`, `aplic_irq_set_type()`, `aplic_irqdomain_translate()`, `aplic_init_hw_global()`, `aplic_setup_priv()`, and platform `aplic_probe()`.

## Control Flow
Probe maps MMIO and selects MSI mode when `msi-parent` exists in DT or IMSIC ACPI fwnode exists; otherwise it selects direct mode. Common setup reads interrupt source count and IDC count from DT or ACPI, resets APLIC source/target/domain registers, allocates saved-register arrays, registers PM hooks, and lets the selected mode build domains. Global init enables domain interrupts and optionally MSI delivery mode. Suspend/GENPD pre-off saves target and enable state; resume restores domain config, MSI address config when applicable, source config before target/enable, and replays pending interrupts for MSI mode.

## State and Persistence
State is MMIO-backed plus `struct aplic_saved_regs`: domain config, optional MSI address config, per-source sourcecfg/target, and per-32-source enable words. It persists only in RAM during PM transitions. The driver supports multiple APLIC instances via the global list.

## Dependencies and Integration Points
It integrates with OF and ACPI RISC-V interrupt descriptions, IMSIC global configuration, platform devices, generic PM domains, runtime PM, syscore PM, and the direct/MSI setup files.

## Risks and Edge Cases
Restore ordering matters because inactive sources make target and enable state read-only zero. The save loop stores enable words in sparse `srcs[i]` entries at 32-source boundaries, including the exact `nr_irqs` boundary when divisible by 32. Mode selection depends on firmware properties and IMSIC availability.

## Test Signals
Validate DT and ACPI source/IDC parsing, direct versus MSI mode selection, PM save/restore with enabled and pending interrupts, source type programming, invalid zero hwirq rejection, and warning paths when `DOMAINCFG` writes do not stick.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-main.c -->
