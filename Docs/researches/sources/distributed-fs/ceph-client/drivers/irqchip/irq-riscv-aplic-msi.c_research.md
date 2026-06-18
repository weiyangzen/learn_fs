<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-msi.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-msi.c

## Purpose
`irq-riscv-aplic-msi.c` implements APLIC MSI-delivery mode, where wired interrupt sources are converted by APLIC into MSIs targeted at the RISC-V IMSIC.

## Important APIs, Types, and Functions
IRQ callbacks are `aplic_msi_irq_mask()`, `aplic_msi_irq_unmask()`, `aplic_msi_irq_eoi()`, `aplic_msi_irq_set_type()`, and `aplic_msi_write_msg()`. MSI-domain support comes from `aplic_msi_set_desc()`, `aplic_msi_translate()`, `aplic_msi_template`, and `aplic_msi_setup()`.

## Control Flow
Setup allocates common `aplic_priv`, reads IMSIC global configuration, derives APLIC MSI address field widths and base PPN, enables APLIC global MSI mode, ensures the platform device has an MSI domain, and creates an MSI device IRQ domain. When a parent MSI message is written, `aplic_msi_write_msg()` decodes the IMSIC address into group, hart, and guest indexes and writes the APLIC target register with hart, guest, and EIID data. Mask/unmask orders parent and APLIC operations to prevent unwanted delivery.

## State and Persistence
MSI mode state is in `priv->msicfg`, APLIC target registers, source configuration, and common saved registers. Level-triggered sources require EOI/set-type retrigger through `APLIC_SETIPNUM_LE` if the level is still asserted.

## Dependencies and Integration Points
The file depends on the IMSIC global config exported by `irq-riscv-imsic-state.c`, Linux MSI domain templates, OF MSI configuration, ACPI IMSIC fwnodes, and common APLIC helpers.

## Risks and Edge Cases
IMSIC address layout must fit APLIC field masks; otherwise setup fails. If the device MSI domain is not available yet, setup returns `-EPROBE_DEFER`. Zeroed MSI messages clear target registers by writing zero. Incorrect level retrigger behavior can lose level-sensitive interrupts after EOI.

## Test Signals
Validate MSI domain creation, IMSIC field-width bounds, DT `msi-parent` and ACPI domain discovery, target register composition from MSI messages, level interrupt retriggering, affinity pass-through, and zero-MSI target clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-msi.c -->
