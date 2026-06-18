# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ath79-misc.c

## Purpose
Implements the Atheros/QCA AR71xx/AR724x/AR913x MISC interrupt controller as a cascaded IRQ domain beneath a parent interrupt. The controller exposes 32 miscellaneous sources and publishes the CPU performance counter interrupt through `get_c0_perfcount_int()`.

## Important APIs, Types, and Functions
Key entry points are `ath79_misc_intc_of_init()`, `ar7100_misc_intc_of_init()`, and `ar7240_misc_intc_of_init()` through `IRQCHIP_DECLARE`. `ath79_misc_irq_handler()` is the chained handler, `misc_map()` installs `ath79_misc_irq_chip`, and mask/unmask/ack helpers manipulate the MISC enable/status registers. The exported `get_c0_perfcount_int()` integrates with MIPS timer/perf users.

## Control Flow
OF init parses the parent IRQ, maps the register block, creates a linear 32-entry domain, creates the perf-counter mapping for hwirq 5, disables and clears all sources, then attaches the chained handler. On parent IRQ entry, status is ANDed with enable, each set bit is dispatched via `generic_handle_domain_irq()`, and empty pending state is reported as spurious.

## State and Persistence
State is limited to MMIO enable/status bits, `domain->host_data`, and the global `ath79_perfcount_irq`. Chip callbacks flush writes with readbacks. AR7100 and AR7240 variants mutate the static chip callbacks to provide mask-ack or explicit ack behavior.

## Dependencies and Integration Points
Depends on OF address/IRQ parsing, Linux irqdomain, chained IRQ helpers, and raw MMIO access. It is a child of the SoC root interrupt path and feeds generic Linux IRQ handlers as level interrupts.

## Risks and Test Signals
Risks include variant-specific ack semantics, missing parent IRQ/registers, spurious parent interrupts, and global chip callback mutation if multiple incompatible instances were ever described. Test signals are boot logs without init errors, correct perf counter IRQ mapping, `/proc/interrupts` activity for MISC children, and no repeated spurious interrupt reports.
