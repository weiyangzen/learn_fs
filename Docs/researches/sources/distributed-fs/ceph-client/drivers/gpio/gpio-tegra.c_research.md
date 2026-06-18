<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tegra.c

Purpose: implements legacy NVIDIA Tegra20/Tegra30/Tegra210 GPIO controllers with banked MMIO GPIO, optional debounce, chained bank IRQs, hierarchical parent IRQ support, debugfs visibility, and noirq suspend/resume.

Important APIs, types, and functions: `struct tegra_gpio_bank` stores per-bank locks, debounce counts, and PM snapshots. `struct tegra_gpio_soc_config` describes register layout and debounce support. `struct tegra_gpio_info` holds device, MMIO, bank data, gpiochip, bank count, and parent IRQs. GPIO callbacks cover request/free, direction, get/set, get_direction, and debounce `set_config`. IRQ callbacks include ack, mask, unmask, set_type, shutdown, wake, affinity, resource request/release, and chained `tegra_gpio_irq_handler()`.

Control flow: probe counts platform IRQs as banks, allocates bank/IRQ arrays, initializes locks, optionally finds the Tegra210 PMC parent domain, maps registers, disables all GPIO interrupts, registers the gpiochip, and creates debugfs. IRQ set_type programs `GPIO_INT_LVL`, makes the line input, locks it as IRQ, and optionally forwards type to a parent domain. The chained handler scans ports in the bank associated with the parent IRQ and dispatches pending enabled bits.

State and persistence behavior: hardware registers hold line configuration. Debounce count is cached per port because the register is shared. PM saves CNF, OUT, OE, INT_ENB, INT_LVL, debounce, and wake masks and restores them on resume.

Dependencies and integration points: integrates with pinctrl GPIO request/direction, irqdomain hierarchy, optional PMC wake parent, debugfs, and OF compatibles for Tegra20/30/210.

Risks and test signals: fixed base `0` can collide in systems with multiple static GPIO ranges. Edge handler temporarily exits chained context for edge interrupts, so IRQ ordering should be tested. Test all SoC configs, debounce shared-port maximum behavior, PMC wake routing, suspend wake masks, debugfs output, and pinctrl failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tegra.c -->
