# sources/distributed-fs/ceph-client/drivers/mfd/da9052-irq.c

## Purpose
`da9052-irq.c` exposes the DA9052 PMIC event registers as Linux virtual IRQs using regmap-irq and provides convenience wrappers for DA9052 child drivers.

## Important APIs, Types, and Functions
`da9052_irqs[]` maps 32 PMIC events across `EVENT_A` through `EVENT_D`. `da9052_regmap_irq_chip` defines status, mask, and ack bases. Exported wrappers `da9052_enable_irq()`, `da9052_disable_irq()`, `da9052_disable_irq_nosync()`, `da9052_request_irq()`, and `da9052_free_irq()` translate PMIC IRQ IDs through `regmap_irq_get_virq()`. `da9052_auxadc_irq()` completes the core ADC conversion. `da9052_irq_init()` and `da9052_irq_exit()` install and remove the IRQ chip.

## Control Flow
Initialization calls `regmap_add_irq_chip()` on the parent PMIC IRQ with low-triggered oneshot handling, enables wake on the parent IRQ, and registers a threaded ADC end-of-measurement handler. Child drivers call the exported wrappers with DA9052 logical IRQ IDs; the wrappers map to virtual IRQs and call generic IRQ APIs. Exit frees the ADC IRQ and deletes the regmap IRQ chip.

## State and Persistence
`da9052->irq_data` owns the regmap IRQ domain state. Event status and mask bits persist only in the PMIC register file. The ADC completion state is stored in the core object and signaled by the ADC event handler.

## Dependencies and Integration Points
The file depends on regmap-irq, Linux IRQ threading, and DA9052 register/IRQ enums. It integrates directly with `da9052_adc_manual_read()` and with child drivers that request PMIC-local interrupt lines.

## Risks and Edge Cases
All PMIC child IRQs depend on a valid parent `chip_irq`; absent or incorrectly triggered hardware IRQs will break ADC reads and child events. `enable_irq_wake()` is not unwound explicitly in exit. The helper uses low-triggered oneshot flags for child requests, so mismatched electrical configuration can cause repeated interrupts.

## Test Signals
Check creation of 32 virtual IRQs, status/mask/ack writes around event delivery, ADC completion behavior, child request/free paths, parent wake capability, and cleanup after failed ADC IRQ registration.
