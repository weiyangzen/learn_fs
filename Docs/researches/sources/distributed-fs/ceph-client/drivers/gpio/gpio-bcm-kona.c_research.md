# sources/distributed-fs/ceph-client/drivers/gpio/gpio-bcm-kona.c

## Purpose
This built-in platform driver supports Broadcom Kona GPIO controllers. It exposes banked GPIO lines, per-bank parent IRQs, GPIO lock/unlock protection registers, debounce configuration, and an irqdomain for GPIO interrupts.

## Important APIs, types, and functions
`struct bcm_kona_gpio` stores MMIO base, bank count, raw spinlock, gpiochip, irqdomain, and flexible bank array. `struct bcm_kona_gpio_bank` stores bank ID, parent IRQ, unlock counts, and back pointer. GPIO callbacks cover request/free, direction, get/set, debounce config, and `to_irq`. IRQ support uses `bcm_gpio_irq_chip`, custom irqdomain ops, chained bank handlers, and request/release resource hooks.

## Control flow
Probe counts platform IRQs to determine bank count, allocates state, creates a linear IRQ domain, maps MMIO, records each bank parent IRQ, resets hardware by unlocking banks, masking/clearing interrupts, and relocking, registers the gpiochip, installs chained handlers for each bank, and initializes the lock. GPIO and IRQ resource requests unlock per-pin registers; releases relock them when both GPIO and IRQ users are gone.

## State and persistence behavior
Hardware stores direction, output/input status, interrupt mask/status, debounce, and lock state. The driver maintains per-pin `gpio_unlock_count[]` to handle overlapping GPIO and IRQ ownership safely. IRQ mappings live in the irqdomain until removal.

## Dependencies and integration points
The driver depends on platform IRQ resources, OF compatible `brcm,kona-gpio`, irqdomain APIs, chained IRQs, gpiolib, and pinconf debounce. It uses lockdep classes for child IRQs to avoid false recursion reports.

## Risks and edge cases
Balanced lock/unlock accounting is critical; unbalanced locks log errors and can leave pins writable or locked unexpectedly. Level IRQs are unsupported. The driver manually removes the irqdomain on probe failure but is built-in, so teardown paths are minimal. Debounce accepts only 0 or 1-128 ms.

## Test signals
Test bank-count detection, max-bank rejection, reset masking/clearing, GPIO request/free lock counts, direction/value operations, debounce rounding, `to_irq` mapping, edge IRQ types, bank chained handlers, and simultaneous GPIO plus IRQ consumers on one line.
