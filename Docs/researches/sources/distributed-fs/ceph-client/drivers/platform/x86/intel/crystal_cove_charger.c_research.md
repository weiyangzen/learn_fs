<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/crystal_cove_charger.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/crystal_cove_charger.c

## Purpose
Implements the Crystal Cove PMIC external-charger IRQ pass-through. It is not a charger power_supply driver; it creates a nested IRQ domain so an external charger driver can consume the PMIC's single charger IRQ after the PMIC-specific level-2 acknowledgement is handled.

## Important APIs, Types, And Functions
`struct crystal_cove_charger_data` stores regmap, IRQ domain, nested charger IRQ, and mask state. The irqchip implements mask/unmask with bus lock and sync to `MCHGRIRQ_REG`. `crystal_cove_charger_irq()` handles the parent IRQ, dispatches the nested IRQ, then writes `CHGRIRQ_REG` bit 0 to acknowledge.

## Control Flow
Probe creates a one-entry irq_domain on the parent fwnode, marks it `DOMAIN_BUS_WAKEUP`, maps hwirq 0, installs a simple nested irqchip, masks the second-level interrupt, then requests the parent threaded IRQ. Consumers obtain the nested IRQ through the shared firmware node/domain.

## State And Persistence
State includes mask and new_mask software copies and the PMIC mask register. The IRQ domain is removed by a devm action.

## Dependencies And Integration Points
Depends on the Crystal Cove PMIC MFD regmap, IRQ domain APIs, nested threaded IRQs, and external charger child drivers.

## Risks And Test Signals
Risks are domain collision on shared MFD fwnodes, unbalanced masking, and failing to ack the PMIC level-2 source. Test by binding the external charger, verifying nested IRQ delivery, checking charger insertion events, and confirming no interrupt storm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/crystal_cove_charger.c -->
