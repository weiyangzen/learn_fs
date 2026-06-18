# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ath79.c

## Purpose
This platform driver supports GPIO controllers in Atheros/QCA AR71xx, AR724x, AR913x, and related ath79 SoCs. It uses `gpio-generic` for basic MMIO GPIO operations and implements optional interrupt-controller support.

## Important APIs, types, and functions
`struct ath79_gpio_ctrl` wraps a `gpio_generic_chip`, MMIO base, and `both_edges` bitmap. IRQ functions include mask/unmask, enable/disable, set type, and `ath79_gpio_irq_handler()`. Probe reads `ngpios`, detects AR9340 output-enable polarity, initializes generic GPIO registers, and optionally fills `gpio_irq_chip`.

## Control flow
Probe validates `ngpios < 32`, maps MMIO, configures generic GPIO data/set/clear/direction registers, and registers the chip. If `interrupt-controller` is present, it allocates a parent IRQ array and uses a chained handler. Edge-both interrupts are emulated by flipping polarity based on the current input state whenever pending status is handled.

## State and persistence behavior
GPIO and IRQ state is hardware register state. The driver keeps only the `both_edges` bitmap to remember which lines need polarity toggling. Generic GPIO locking protects register read-modify-write sequences.

## Dependencies and integration points
Dependencies are OF platform binding, `gpio-generic`, gpiolib irqchip helpers, and chained interrupt handling. Compatible strings include `qca,ar7100-gpio` and `qca,ar9340-gpio`.

## Risks and edge cases
Both-edge emulation can miss very fast toggles if polarity cannot be updated between edges. Direction register polarity differs for AR9340. The driver rejects 32 or more GPIOs because bit operations assume a sub-32-bit controller. Parent IRQ retrieval is stored directly without checking for negative values in the optional branch.

## Test signals
Test both compatible variants, `ngpios` validation, generic get/set/direction operations, interrupt-controller presence/absence, rising/falling/level trigger programming, both-edge polarity updates, and child IRQ dispatch.
