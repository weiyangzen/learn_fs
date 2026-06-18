<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-hlwd.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-hlwd.c

## Purpose
`gpio-hlwd.c` exposes Nintendo Wii Hollywood GPIO lines through gpiolib. It claims the hardware lines for Broadway CPU access, uses the always-accessible `HW_GPIOB_*` register window, and optionally presents the block as an interrupt controller.

## Important APIs, types, and functions
`struct hlwd_gpio` embeds a `gpio_generic_chip`, the big-endian MMIO base, parent IRQ, and software bitmaps for edge emulation. `hlwd_gpio_irqhandler()` handles cascaded interrupts. IRQ helpers provide ack, mask, unmask, enable, type selection, chip printing, and `hlwd_gpio_irq_setup_emulation()` for edge triggers. Probe is centered around `gpio_generic_chip_init()`.

## Control flow
Probe maps registers, writes all ones to `HW_GPIO_OWNER` before generic initialization, initializes the generic chip with big-endian register access, reads optional `ngpios`, masks and acknowledges all interrupts, and, if the node has `interrupt-controller`, wires a parent IRQ into the gpiochip irqchip. The parent handler reads pending and mask registers under the generic chip lock, emulates edge triggers by toggling inactive levels, acknowledges emulated edges, then dispatches selected child IRQs.

## State and persistence behavior
The hardware stores output, direction, interrupt mask, flags, level sense, and ownership. The driver stores only interrupt emulation state: `edge_emulation`, `rising_edge`, and `falling_edge`. Device-managed allocations cover lifetime; no persistent storage exists across driver unload or reboot.

## Dependencies and integration points
The driver binds to `nintendo,hollywood-gpio`, depends on MMIO big-endian accessors and `gpio-generic`, and integrates with DT `interrupt-controller` bindings. It relies on the Hollywood memory firewall allowing access to owner and GPIO registers.

## Risks and edge cases
Edge interrupts are emulated by changing level polarity, which is sensitive to races with changing input levels. Systems without AHBPROT/firewall access cannot safely claim ownership. The handler reads and modifies interrupt registers while holding the generic chip lock, so incorrect locking could cause lost edge-emulation transitions.

## Test signals
Use libgpiod for get/set/direction, boot tests with and without `interrupt-controller`, level-high/low and rising/falling/both-edge IRQ tests, and platform tests confirming all lines are owned by `HW_GPIOB_*` before generic state is read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-hlwd.c -->
