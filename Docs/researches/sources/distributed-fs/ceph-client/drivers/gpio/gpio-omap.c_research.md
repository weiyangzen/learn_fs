<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-omap.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-omap.c

## Purpose
Main OMAP2/3/4 and MPUIO GPIO bank driver. It handles GPIO direction/value operations, debounce, IRQ type/mask/wake, runtime PM, CPU cluster PM, register context save/restore, and missed non-wakeup edge IRQ workarounds.

## Important APIs, types, and functions
`struct gpio_bank` stores MMIO base, register layout, IRQ, non-wakeup masks, saved context, locks, chip, debounce clock, PM flags, usage masks, and context-loss state. Core functions cover direction/dataout, debounce, trigger programming, IRQ enable, bank IRQ handling, request/free, idle/unidle, CPU PM notifier, probe/remove, and runtime/system PM.

## Control flow
Probe selects OF or legacy platform data, maps the bank, gets debounce clock, enables runtime PM, initializes hardware, registers the chip/irqchip, requests the parent IRQ, registers CPU PM notifier, and drops the PM reference. Request/free maintain `mod_usage`; IRQ startup/shutdown maintain `irq_usage`. The IRQ handler repeatedly reads enabled pending bits, clears edge bits before child dispatch, toggles both-edge emulation where required, and dispatches child IRQs.

## State and persistence behavior
Context includes direction, dataout, IRQ enables, wake, detect registers, debounce registers, saved datain, non-wakeup GPIO masks, and context-loss count. Suspend/CPU-idle save state, disable debounce clocks, apply errata workarounds, and resume restores context or synthesizes missed non-wakeup edge IRQs.

## Dependencies and integration points
Depends on OMAP platform register definitions, OF compatibles, runtime PM, CPU PM notifiers, MPUIO support, pinctrl generic bias config, gpiolib, IRQ domains, and optional debounce clocks.

## Risks and edge cases
Register layouts and inverted IRQ-enable semantics vary by SoC. Debounce clock ordering is critical. Non-wakeup edge synthesis is inherently racy. Incorrect usage-mask accounting can idle live banks. Level and edge IRQ clear ordering differs.

## Test signals
Request/free PM balance, direction/value/multiple operations, debounce conversion, trigger validation, wake enable, nested IRQ delivery, context-loss restore, and synthetic IRQ generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-omap.c -->
