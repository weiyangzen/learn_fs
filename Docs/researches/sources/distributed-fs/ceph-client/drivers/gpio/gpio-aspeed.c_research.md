# sources/distributed-fs/ceph-client/drivers/gpio/gpio-aspeed.c

## Purpose
This is the main Aspeed parallel GPIO controller driver for AST2400, AST2500, AST2600, and AST2700 SoCs. It supports GPIO direction/value operations, IRQs, debounce timers, reset tolerance, pinctrl interaction, and optional coprocessor ownership handshaking.

## Important APIs, types, and functions
`struct aspeed_gpio` stores the gpiochip, MMIO base, lock, IRQ, SoC config, debounce timer accounting, optional clock, output data cache, and coprocessor bank map. `struct aspeed_gpio_llops` abstracts generation-specific register access and coprocessor privilege control. Exported coprocessor APIs are `aspeed_gpio_copro_set_ops()`, `aspeed_gpio_copro_grab_gpio()`, and `aspeed_gpio_copro_release_gpio()`.

## Control flow
Probe maps MMIO, obtains config and optional clock, sets line count from `ngpios` or config fallback, initializes GPIO callbacks and optional data cache, initializes coprocessor privilege to ARM where supported, wires a chained IRQ chip, allocates debounce accounting, and registers the chip. GPIO operations check bank capability masks, optionally request coprocessor access, update registers, and release access. IRQ handling reads status banks and dispatches child IRQs.

## State and persistence behavior
Hardware registers store value, direction, IRQ type/status/enable, debounce selector bits, reset tolerance, and command source. Runtime state includes debounce timer allocation (`offset_timer`, `timer_users`), optional `dcache` for output registers on G4-style hardware, global coprocessor callbacks, and per-bank coprocessor reference counts.

## Dependencies and integration points
The driver depends on OF platform resources, clocks, gpiolib, irqchip chaining, pinctrl GPIO request/free/config, packed pinconf, and internal Aspeed GPIO consumer APIs. AST2400/2500/2600 use banked G4-style ops; AST2700 uses G7 per-line control registers and no coprocessor callbacks.

## Risks and edge cases
Debounce has only three usable hardware timers; exhaustion disables the line's timer selection and returns an error. Coprocessor ownership is global and bank-counted, so imbalance returns errors and can leave command source ownership wrong. Bank property masks expose holes as unavailable lines. Missing clocks disable debounce. G4 output writes depend on a synchronized `dcache`.

## Test signals
Test line availability masks for each SoC, pinctrl request/free, direction and output cache behavior, all IRQ trigger types and valid masks, debounce timer reuse/exhaustion/disable, reset tolerance config, coprocessor grab/release balance, and AST2700 G7 register access.
