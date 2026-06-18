<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson-64bit.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson-64bit.c

## Purpose
`gpio-loongson-64bit.c` is the modern Loongson GPIO platform driver for multiple 64-bit Loongson SoCs and chipsets. It supports bit-control and byte-control register layouts, optional reset deassertion, simple `to_irq` mapping, and a full irqchip for LS2K0300.

## Important APIs, types, and functions
`struct loongson_gpio_chip_data` describes label, mode, register offsets, interrupt count, parent handler, and irqchip. `struct loongson_gpio_chip` stores the generic chip wrapper, spinlock, base, and chip data. Byte-control callbacks implement direction/get/set. `loongson_gpio_to_irq()` enables per-line interrupts for simple mapping. LS2K0300 IRQ support uses ack/mask/unmask/set_type and `loongson_gpio_ls2k0300_irq_handler()`.

## Control flow
Probe gets match data, maps the register resource, deasserts optional reset, then initializes either gpio-generic for bit-control mode or custom byte-control callbacks. If chip data provides a real irqchip, parent IRQs are gathered and disabled/cleared before gpiochip registration; otherwise an `inten_offset` installs `to_irq`.

## State and persistence behavior
GPIO state is in MMIO registers. Byte-control mode uses a spinlock around direction and output writes; bit-control mode delegates locking to gpio-generic. Interrupt type is programmed in per-line polarity/edge/dual registers for LS2K0300.

## Dependencies and integration points
The driver binds to many Loongson OF compatibles and ACPI IDs, uses `gpio-generic`, platform IRQs, optional reset controls, and postcore init to make GPIOs available early.

## Risks and edge cases
The same driver name overlaps with older `gpio-loongson.c` on some builds. In simple `to_irq` mode, calling `to_irq` has the side effect of enabling hardware interrupt bits. LS2K0300 status bits may be set spuriously, so the handler must check enable bits too.

## Test signals
Test each OF/ACPI match-data variant, bit vs byte register mode, optional reset failure, simple `to_irq` enable side effects, LS2K0300 all trigger types including edge-both dual register, and spurious status filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson-64bit.c -->
