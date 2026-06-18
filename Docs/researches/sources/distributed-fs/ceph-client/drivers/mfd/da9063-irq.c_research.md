# sources/distributed-fs/ceph-client/drivers/mfd/da9063-irq.c

## Purpose
`da9063-irq.c` maps DA9063 and DA9063L PMIC event registers into regmap IRQ domains.

## Important APIs, Types, and Functions
`da9063_irqs[]` maps full DA9063 events across EVENT_A through EVENT_D, including RTC alarm/tick. `da9063l_irqs[]` omits DA9063-only alarm/tick support while keeping common onkey, ADC, wake, thermal, regulator, DVC, warning, and GPIO events. `da9063_irq_chip` and `da9063l_irq_chip` define four status/mask/ack registers with `init_ack_masked = true`. `da9063_irq_init()` selects the correct chip and adds it with `devm_regmap_add_irq_chip()`.

## Control Flow
The core calls `da9063_irq_init()` after the regmap exists and before children are added. The function rejects missing parent IRQs, chooses DA9063 or DA9063L mapping by type, and installs a low-triggered shared oneshot regmap IRQ chip using the current IRQ base.

## State and Persistence
Regmap-irq owns virtual IRQ mappings and mask/cache state in `da9063->regmap_irq`. PMIC event and mask registers are volatile hardware state. `init_ack_masked` causes masked pending events to be acknowledged during initialization.

## Dependencies and Integration Points
The file depends on regmap-irq, MFD core, DA9063 core/type definitions, and Linux IRQ flags. Child devices registered by the core receive resources that refer to these logical IRQ IDs.

## Risks and Edge Cases
The function hard-fails when no parent IRQ is configured, so even non-interrupt child functionality cannot register through this core. Shared low-trigger assumptions must match board wiring. DA9063L lacks alarm/tick entries; child resources must not request those on DA9063L.

## Test Signals
Check full versus L IRQ map sizes, parent IRQ absence failure, masked-pending ACK at init, GPIO event delivery across EVENT_C/D, and named resource mapping for onkey/hwmon/RTC/regulator children.
