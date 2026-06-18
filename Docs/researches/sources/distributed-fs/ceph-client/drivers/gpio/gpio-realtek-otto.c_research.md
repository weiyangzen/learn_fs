# sources/distributed-fs/ceph-client/drivers/gpio/gpio-realtek-otto.c

## Purpose
This driver supports Realtek Otto-family GPIO controllers with up to 32 GPIOs, optional edge interrupts, port-order quirks, and optional per-CPU IRQ mask registers. It uses `gpio_generic_chip` for normal GPIO operations and custom IRQ state because the interrupt mask register encodes both type and enable state.

## Important APIs, Types, and Functions
`struct realtek_gpio_ctrl` stores generic GPIO state, MMIO bases, CPU mask data, raw spinlock, per-line `intr_mask` and `intr_type` arrays, and function pointers for port-order-specific reads/writes and IMR bit positions. `realtek_gpio_update_line_imr()` is central: it writes the AND of selected type and enable mask into the 2-bit IMR field. IRQ operations include ack, mask/unmask, set_type, parent handler, optional affinity, and `realtek_gpio_irq_init()`.

## Control Flow
Probe reads match flags, validates `ngpios`, maps the base resource, chooses normal or reversed port ordering, initializes the generic chip, and conditionally wires a parent IRQ unless interrupts are disabled by compatibility data. For per-CPU-capable variants, it maps a second resource, derives present CPUs from resource size, and uses that mask in affinity programming. The chained IRQ handler reads ISR and dispatches set bits through the GPIO IRQ domain.

## State and Persistence
GPIO values and directions are hardware-backed through generic helpers. Interrupt type and mask state are persisted in the driver arrays, then materialized to IMR under the raw spinlock. Hardware ISR is cleared by writing a mask to the ISR register. There are no suspend/resume callbacks.

## Dependencies and Integration Points
The driver integrates with DT match data for Realtek variants, generic GPIO MMIO helpers, chained IRQs, cpumask/affinity APIs, and optional per-CPU MMIO ranges. Endianness and port layout are selected by compatibility flags.

## Risks
Incorrect port-order flags can map GPIO lines to the wrong ISR/IMR bits, causing lost or misdelivered interrupts. The hardware supports edge trigger modes only in this driver. Affinity updates assume the secondary resource width exactly represents per-CPU masks. IMR read-modify-write uses raw `ioread32()` regardless of bank read endian helpers, which must match the IMR register layout.

## Test Signals
Test each compatible's port ordering, all edge trigger modes, IRQ mask/type combinations, ISR clear behavior, optional interrupt-disabled compatible, per-CPU affinity programming on rtl9300-style devices, and `ngpios` boundary handling.
