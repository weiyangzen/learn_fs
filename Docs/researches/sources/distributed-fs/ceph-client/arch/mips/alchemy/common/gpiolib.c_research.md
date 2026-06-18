# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/gpiolib.c

## Purpose
`gpiolib.c` adapts Alchemy SoC GPIO controllers to the Linux gpiolib API. It registers one or two classic GPIO chips for Au1000/Au1100/Au15x0/Au12x0 variants, or a single GPIC-backed GPIO chip for Au1300.

## Important APIs, Types, And Functions
The classic GPIO callbacks are `gpio1_get()`, `gpio1_set()`, `gpio1_direction_input()`, `gpio1_direction_output()`, `gpio1_to_irq()`, and GPIO2 equivalents. `alchemy_gpio_chip[]` describes `"alchemy-gpio1"` and `"alchemy-gpio2"` with fixed global bases and counts. Au1300 callbacks are `alchemy_gpic_get()`, `alchemy_gpic_set()`, `alchemy_gpic_dir_input()`, `alchemy_gpic_dir_output()`, and `alchemy_gpic_gpio_to_irq()`, wrapped by `au1300_gpiochip` labeled `"alchemy-gpic"`. `alchemy_gpiochip_init()` is an `arch_initcall()`.

## Control Flow
At arch initcall, CPU type detection selects the correct GPIO registration path. Au1000 registers only GPIO1. Au1500 through Au1200 register GPIO1 and GPIO2. Au1300 registers the GPIC-backed GPIO chip. All callbacks translate gpiolib offsets into legacy global GPIO numbers by adding the chip base, then delegate to low-level Alchemy GPIO helpers.

## State And Persistence
The persistent state is the registered `gpio_chip` instances and the underlying hardware direction/value/IRQ mapping configured by low-level helpers. This file itself does not allocate dynamic memory or retain per-line state.

## Dependencies And Integration Points
It depends on `linux/gpio/driver.h`, `gpio-au1000.h`, `gpio-au1300.h`, and `alchemy_get_cputype()`. Board files use global GPIO numbers and, in MTX-1/GPR cases, software nodes or lookup tables that refer to `"alchemy-gpio2"`. IRQ integration relies on `to_irq` mapping to the interrupt setup in `irq.c`.

## Risks
The file uses fixed legacy global GPIO bases, which can conflict with newer dynamic GPIO numbering assumptions. The return value OR-ing when registering both GPIO1 and GPIO2 can lose exact failure causes and may leave one chip registered after the other fails. Board lookup tables depend on chip labels remaining stable. Au1300 shares GPIC GPIO and interrupt/pinmux state, so GPIO direction changes can affect device-function pins.

## Test Signals
Boot each CPU variant and confirm the expected GPIO chip labels and line counts appear. Board device probes should resolve `"alchemy-gpio2"` descriptors for MTX-1 and GPR. GPIO tests should read/write lines, switch direction, and map GPIO-to-IRQ for classic and Au1300 variants. Regression tests should verify Au1000 does not register GPIO2.
