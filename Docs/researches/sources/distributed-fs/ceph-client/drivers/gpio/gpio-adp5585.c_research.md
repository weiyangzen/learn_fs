# sources/distributed-fs/ceph-client/drivers/gpio/gpio-adp5585.c

## Purpose
This platform driver exposes GPIO support for ADP5585 and ADP5589 MFD devices. It handles variant-specific bank layouts, pin configuration, shared pin ownership, and optional GPIO IRQs sourced from the parent key/event notifier.

## Important APIs, types, and functions
`struct adp5585_gpio_chip` describes variant register bases, bank/bit mapping, event ranges, and bias layout. `struct adp5585_gpio_dev` stores the GPIO chip, notifier, regmap, and IRQ masks. GPIO callbacks include direction, get/set, `adp5585_gpio_set_config()`, `adp5585_gpio_request()`, and `adp5585_gpio_free()`. IRQ paths include `adp5585_gpio_key_event()`, `adp5585_irq_mask()`, `adp5585_irq_unmask()`, `adp5585_irq_set_type()`, and bus sync.

## Control flow
Probe gets the parent `struct adp5585_dev`, chooses ADP5585 or ADP5589 chip info from platform ID, inherits the parent's OF node, initializes GPIO callbacks, and optionally sets up an immutable irqchip when the parent advertises `interrupt-controller`. For IRQs it registers a blocking notifier on the parent event chain; key events in the GPIO event range are translated to child IRQs after active-high and edge-type checks.

## State and persistence behavior
Pin direction, output data, pull configuration, drive mode, debounce, and event enable state live in regmap registers. Runtime driver state includes parent `pin_usage`, `irq_mask`, `irq_en`, and `irq_active_high`. All IRQs start masked; bus sync writes changed enable and active-level bits.

## Dependencies and integration points
The driver depends on the ADP5585 MFD core, regmap, gpiolib, pinconf packed configs, and the parent event notifier. It integrates with shared keypad/GPIO pin muxing by claiming bits in `adp5585->pin_usage` and clearing parent pin config to GPIO mode.

## Risks and edge cases
Variant bank/bit math differs between ADP5585 and ADP5589, and ADP5585 has a pull-config bitfield hole after R5. GPIO IRQs are edge-only and rely on parent key-event delivery rather than a direct chained interrupt. Consumers must request pins to avoid conflicts with keypad or other parent functions.

## Test signals
Test pin request conflicts, reserved/missing pins, direction and output register writes by bank, bias/drive/debounce pinconf operations, notifier registration cleanup, edge-rising/falling IRQ delivery from parent events, and ADP5585 versus ADP5589 register offsets.
