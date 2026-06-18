<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-iwb.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-iwb.c

## Purpose
Implements the GICv5 Interrupt Wire Bridge, which exposes wired interrupt inputs as an MSI-style device domain so wired sources can be delivered through the GICv5 LPI/MSI hierarchy.

## Important APIs, Types, And Functions
`struct gicv5_iwb_chip_data` stores the IWB MMIO base and number of 32-bit wire-enable registers. `iwb_msi_template` defines the wired-to-MSI domain, chip callbacks, fixed message-data allocation, and OF/ACPI translation. Core functions are `gicv5_iwb_init_bases()`, `gicv5_iwb_create_device_domain()`, `gicv5_iwb_irq_domain_translate()`, `gicv5_iwb_set_type()`, `gicv5_iwb_irq_enable()`, and `gicv5_iwb_irq_disable()`.

## Control Flow
Platform probe maps the single IWB resource, reads IDR0 to derive the wire count, verifies firmware has already enabled IWB CR0, clears all WENABLER registers, waits for the enable operation to become idle, and creates a per-device MSI domain sized to the number of wires. IRQ enable first enables the physical wire and then the parent IRQ; disable reverses this by disabling the wire and then the parent. Type setting modifies WTMR bits to distinguish level and edge inputs.

## State And Persistence
The driver persists only the MMIO base, register count, and MSI device domain in memory. Hardware state is the WENABLER and WTMR bitmaps. It intentionally leaves CR0 enable ownership to firmware and does not provide a remove path or runtime power state handling.

## Dependencies And Integration Points
It depends on GICv5 shared register definitions, `gicv5_wait_for_op_atomic()`, Linux MSI domain templates, OF platform probing, ACPI device ID `ARMH0003`, and the parent MSI domain attached to the platform device. ACPI GSI translation extracts the IWB wire from encoded GICv5 GSI fields.

## Risks
The code assumes firmware enabled the IWB; systems that expect Linux to enable it will fail probe. Wire register bounds must match IDR0, or enable/type operations reject interrupts. Since the MSI write callback is intentionally empty, correctness depends on fixed message data and parent MSI plumbing rather than a normal generated MSI message.

## Test Signals
Test OF and ACPI enumeration, creation of a `DOMAIN_BUS_WIRED_TO_MSI` device domain, wired interrupt delivery for low/high and rising/falling sources, disable/enable cycles clearing WENABLER bits, and failure behavior when CR0 is disabled or wire numbers exceed IDR0 capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-iwb.c -->
