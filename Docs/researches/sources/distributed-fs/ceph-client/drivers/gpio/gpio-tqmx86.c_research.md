<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tqmx86.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tqmx86.c

Purpose: implements GPIO for the TQ-Systems TQMx86 PLD, exposing four output lines and four input lines, with optional chained edge interrupts on input lines.

Important APIs, types, and functions: `struct tqmx86_gpio_data` stores gpiochip, I/O port mapping, parent IRQ, raw spinlock, output shadow bitmap, and per-line IRQ type state. GPIO callbacks are get, set, direction_input, direction_output, and get_direction. IRQ callbacks are mask, unmask, set_type, chained `tqmx86_gpio_irq_handler()`, valid-mask initialization, and chip printing.

Control flow: probe maps an I/O resource, initializes outputs as outputs and inputs as inputs, clears output shadow to zero because hardware cannot read previous output state, enables runtime PM, optionally masks/clears interrupts and wires a one-parent gpio IRQ chip, then registers the gpiochip. Both-edge interrupt mode is emulated by flipping the configured edge after each interrupt based on current input level.

State and persistence behavior: output shadow is authoritative for output register writes. `irq_type[]` stores trigger and unmasked state. Runtime PM callbacks are no-ops but provide a PM device for IRQ-domain use.

Dependencies and integration points: depends on platform I/O resources, optional parent IRQ, gpiolib irqchip helpers, raw port I/O, runtime PM, and fixed PLD register layout.

Risks and test signals: output lines can technically be reconfigured by callbacks even though hardware naming implies fixed outputs/inputs; interrupt valid mask clears only outputs. Probe zeroes all outputs, which may alter board state. Test input/output directions, output shadow consistency, optional no-IRQ probe, IRQ valid-mask, both-edge emulation, runtime PM domain attachment, and cleanup after registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tqmx86.c -->
