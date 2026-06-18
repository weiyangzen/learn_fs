# sources/distributed-fs/ceph-client/drivers/gpio/gpio-xlp.c

## Purpose
Provides GPIO and chained interrupt support for Broadcom/Netlogic XLP GPIO controllers, exposing 70 GPIOs out of a register layout capable of up to 96 lines.

## Important APIs, Types, And Functions
- `struct xlp_gpio_priv` stores the gpiochip, enabled IRQ bitmap, pointers to interrupt/output/pad-drive register groups, and spinlock.
- `xlp_gpio_get_reg` and `xlp_gpio_set_reg` access bit positions across 32-bit register banks.
- IRQ callbacks `xlp_gpio_irq_enable`, `xlp_gpio_irq_disable`, `xlp_gpio_irq_mask_ack`, `xlp_gpio_irq_unmask`, and `xlp_gpio_set_irq_type` control interrupt enable, status ack, type, and polarity.
- `xlp_gpio_generic_handler` walks enabled GPIOs, reads status registers by bank, and dispatches pending child IRQs.
- GPIO callbacks `xlp_gpio_dir_output`, `xlp_gpio_dir_input`, `xlp_gpio_get`, and `xlp_gpio_set` manage output-enable and pad-drive bits.

## Control Flow
Probe maps the controller, gets the parent IRQ, sets register pointers from the base, initializes a 70-line gpiochip, attaches a chained irqchip to the parent, and registers the chip. Direction output enables output drive but ignores the requested initial state; value changes are handled separately through the pad-drive register. IRQ unmask enables the hardware bit and records it in `gpio_enabled_mask`; the chained handler only scans enabled GPIOs and dispatches those with status set.

## State And Persistence
Hardware registers retain output-enable, pad-drive, interrupt enable, type, polarity, and status. Software tracks enabled child IRQs in `gpio_enabled_mask` so the chained handler can avoid scanning disabled lines.

## Dependencies And Integration Points
Depends on platform MMIO and IRQ resources, gpiolib chained irqchip APIs, ACPI IDs `BRCM9006` and `CAV9006`, and fixed XLP register layout constants.

## Risks And Edge Cases
`direction_output` does not apply the requested initial output value, which may surprise consumers expecting gpiolib semantics. `gpio_chip.base` is fixed at 0. IRQ enable only calls `gpiochip_enable_irq`; hardware enabling happens in unmask, so handler setup must follow the expected core order. Only 70 GPIOs are exposed although the register layout supports 96.

## Test Signals
Check output direction plus initial value behavior, get/set on pad-drive bits, direction input/output register bits, IRQ type/polarity for all four trigger modes, mask-ack status clearing, enabled-mask scanning across 32-bit register boundaries, ACPI binding, and parent chained handler dispatch.
