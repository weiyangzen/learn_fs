<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-rc5t583.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-rc5t583.c

## Purpose
GPIO child driver for Ricoh RC5T583 PMIC. It provides sleeping direction/value operations, maps GPIOs to parent PMIC IRQs, and returns pins to PG/alternate mode on free.

## Important APIs, types, and functions
`struct rc5t583_gpio` stores chip and parent PMIC. GPIO callbacks are get, set, direction input/output, `to_irq()`, and free. Probe obtains parent data and optional legacy base, then registers `RC5T583_MAX_GPIO` lines.

## Control flow
Input reads `GPIO_MON_IOIN`; set/clear writes `GPIO_IOOUT`. Direction input clears `GPIO_IOSEL` and `GPIO_PGSEL`; direction output writes value, sets `GPIO_IOSEL`, and clears `GPIO_PGSEL`. Free sets `GPIO_PGSEL`. IRQs are parent `irq_base + RC5T583_IRQ_GPIO0 + offset`.

## State and persistence behavior
No local shadow state. PMIC registers hold mode, direction, output, and monitor values. No local PM handling.

## Dependencies and integration points
Depends on RC5T583 MFD helpers, parent platform data and IRQ base, platform child creation, and gpiolib.

## Risks and edge cases
Chip field assignments use comma operators, which is valid but unusual. `to_irq()` assumes a valid parent IRQ base. Freeing a line changes pin mode away from GPIO.

## Test signals
Direction/mode register sequences, output-before-direction, monitor reads, IRQ mapping, free-to-PG-mode behavior, and legacy GPIO base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-rc5t583.c -->
