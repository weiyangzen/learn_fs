<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-rpmi-sysmsi.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-rpmi-sysmsi.c

## Purpose
`irq-riscv-rpmi-sysmsi.c` implements an RPMI System MSI controller for RISC-V. It exposes firmware-managed system MSI indexes as a wired-to-MSI domain backed by mailbox calls to RPMI firmware and a parent IMSIC MSI domain.

## Important APIs, Types, and Functions
Message payload structs model GET_ATTRIBUTES, SET_MSI_STATE, and SET_MSI_TARGET transactions. `struct rpmi_sysmsi_priv` stores the device, mailbox client/channel, number of MSIs, and ACPI GSI base. Firmware helpers are `rpmi_sysmsi_get_num_msi()`, `rpmi_sysmsi_set_msi_state()`, and `rpmi_sysmsi_set_msi_target()`. IRQ callbacks mask/unmask through firmware and parent chip, write MSI target messages, translate firmware specs, and create an MSI device domain through `rpmi_sysmsi_template`.

## Control Flow
Probe allocates state, configures a mailbox client, requests a channel, queries firmware for MSI count, optionally reads ACPI GSI mapping and updates the GSI range, ensures the device has a platform MSI parent domain through OF or ACPI IMSIC lookup, and creates a device MSI domain. Mask disables the system MSI in firmware then masks the parent; unmask unmasks parent first then enables firmware state. `irq_write_msi_msg` sends target address/data to firmware.

## State and Persistence
State lives in RPMI firmware and the mailbox-backed system MSI table. The Linux driver keeps only the count and GSI base. Zeroed MSI messages are ignored rather than clearing firmware target state.

## Dependencies and Integration Points
It depends on RPMI mailbox message APIs, IMSIC MSI domains, OF `riscv,rpmi-system-msi`, ACPI ID `RSCV0006`, RISC-V ACPI GSI helpers, and Linux MSI domain templates.

## Risks and Edge Cases
Mailbox failures during mask/unmask/write only warn after probe, so firmware desynchronization can persist. No remove path frees the mailbox channel after successful builtin probe. The translation subtracts `gsi_base`; invalid firmware specs below that base can underflow into large hwirqs.

## Test Signals
Validate firmware attribute count, no-MSI rejection, mailbox error conversion, OF and ACPI MSI parent discovery, ACPI GSI range update, mask/unmask ordering, MSI target programming, and behavior when parent MSI domain probes late.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-rpmi-sysmsi.c -->
