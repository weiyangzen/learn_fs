<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-main.h -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-main.h

## Purpose
`irq-riscv-aplic-main.h` is the internal contract between the RISC-V APLIC common code and its direct/MSI mode implementations.

## Important APIs, Types, and Functions
It defines `APLIC_DEFAULT_PRIORITY`, `struct aplic_msicfg`, `struct aplic_src_ctrl`, `struct aplic_saved_regs`, and `struct aplic_priv`. It declares common mask/unmask/type/translation/global-init/setup helpers, direct restore/setup helpers, and MSI setup. When `CONFIG_RISCV_APLIC_MSI` is disabled, `aplic_msi_setup()` is provided as an inline `-ENODEV` stub.

## Control Flow
The header has no executable flow, but it encodes how `aplic_probe()` hands a mapped register base to either `aplic_direct_setup()` or `aplic_msi_setup()`, while both modes use `aplic_setup_priv()` and shared irqchip callbacks.

## State and Persistence
The central state shape is `struct aplic_priv`, which carries firmware identity, interrupt counts, MMIO base, MSI address layout, saved PM registers, and optional GENPD notifier. `struct aplic_saved_regs` persists volatile hardware state across suspend or PM-domain off.

## Dependencies and Integration Points
It depends on Linux device, I/O, irqdomain, and fwnode types plus RISC-V APLIC register definitions included by implementation files. It is private to the irqchip directory.

## Risks and Edge Cases
The saved register array is indexed by hardware interrupt source IDs and also stores enable words at 32-source boundaries, so implementers must size it for `nr_irqs + 1`. `nr_idcs == 0` is used to distinguish MSI mode from direct mode in restore logic.

## Test Signals
Compile coverage across direct-only, MSI-enabled, DT, and ACPI configurations is the primary signal. Runtime validation comes from APLIC direct/MSI tests that exercise every declared helper contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-main.h -->
