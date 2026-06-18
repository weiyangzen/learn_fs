# sources/distributed-fs/ceph-client/drivers/gpio/gpio-aspeed-sgpio.c

## Purpose
This platform driver supports Aspeed serial GPIO masters on AST2400/2500, AST2600 SGPIOM, and AST2700 SGPIOM. It exposes paired input/output logical lines for serial GPIO pins and provides IRQ support on input lines.

## Important APIs, types, and functions
`struct aspeed_sgpio` stores the gpiochip, device, clock, raw spinlock, MMIO base, parent IRQ, and SoC pdata. `struct aspeed_sgpio_llops` abstracts generation-specific register access. GPIO callbacks include `aspeed_sgpio_get()`, `aspeed_sgpio_set()`, direction helpers, and `aspeed_sgpio_set_config()`. IRQ callbacks include ack, mask/unmask, type setup, handler, and valid-mask initialization.

## Control flow
Probe reads `ngpios` and `bus-frequency`, calculates the SGPIO clock divider from APB clock, writes the enable/config register, initializes callbacks, calls `aspeed_sgpio_setup_irqs()`, and registers the chip with `ngpio = nr_gpios * 2`. Even offsets are inputs and odd offsets are outputs. IRQ setup disables and clears all input IRQs, configures default falling/level-low style bits, and attaches a chained parent handler.

## State and persistence behavior
State is MMIO hardware state: data, output latch, IRQ enable/type/status, reset tolerance, and generation-specific control registers. The raw spinlock serializes register bit operations. Persistent-state pinconf toggles reset tolerance bits.

## Dependencies and integration points
The driver depends on platform MMIO resources, OF match data, a clock provider, gpiolib, pinconf packed configs, and chained IRQ handling. Generation-specific integration is through `aspeed_sgpio_g4_llops` for AST2400/2600 and `aspeed_sgpio_g7_llops` for AST2700.

## Risks and edge cases
The logical offset model is unusual: input GPIOs are even, output GPIOs are odd, and IRQs are valid only on inputs. `ngpios` must be a multiple of 8 and the divider must fit 16 bits. AST2700 uses per-pin control registers unlike earlier banked registers, so low-level ops must match the compatible.

## Test signals
Test invalid `ngpios` and zero/too-low bus frequencies, divider programming, input/output direction rejection on wrong parity, IRQ valid mask, IRQ type programming, status dispatch to even offsets, and reset-tolerance pinconf on each supported compatible.
