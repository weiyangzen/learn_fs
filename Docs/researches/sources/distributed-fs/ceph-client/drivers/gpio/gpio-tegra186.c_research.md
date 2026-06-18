<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tegra186.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tegra186.c

Purpose: implements the newer NVIDIA Tegra186-and-later GPIO controller family, covering many main/AON/UPHY/compute/system instances with data-driven port tables, security/VM accessibility filtering, hierarchical IRQ routing, optional hardware timestamping, and OF/ACPI matching.

Important APIs, types, and functions: `struct tegra_gpio_port` describes hardware bank/port/pin counts, `struct tegra_gpio_soc` describes a controller instance, and `struct tegra_gpio` owns gpiochip, register apertures, IRQ list, and SoC data. GPIO callbacks include base lookup, valid-mask initialization, direction, get/set, debounce `set_config`, pin-range addition, OF xlate, and HTE timestamp enable/disable. IRQ callbacks include ack, mask/unmask, set_type, set_wake, chained `tegra186_gpio_irq()`, translation, parent fwspec population, and child-to-parent mapping.

Control flow: probe counts IRQs, allocates a variable-size state object, maps security and GPIO apertures, validates interrupts-per-bank, records IRQs, builds line names, initializes gpio callbacks and a hierarchical gpio IRQ chip, optionally programs default interrupt route mappings, locates a wakeup/PMC parent domain, builds the per-line parent IRQ map, and registers the gpiochip. Chained IRQ handling scans ports belonging to the triggering bank and dispatches set status bits.

State and persistence behavior: line value, direction, trigger, debounce, interrupt enable, and timestamp enable live in per-pin registers. Valid line masks are derived from security and optional VM registers at registration. No suspend snapshot is implemented in this file.

Dependencies and integration points: depends on DT binding GPIO numbers, ACPI IDs, platform resources named `security` and `gpio`, parent irqdomains, optional HTE support, pinctrl group ranges for selected SoCs, and PMC/wakeup-parent nodes.

Risks and test signals: port tables are large and SoC-specific; any bank/port/pin error corrupts numbering and IRQ routing. Default route programming assumes host ownership when security registers are unlocked. Test each compatible/ACPI ID, VM inaccessible-line masking, multi-IRQ-per-bank route selection, wakeup-parent deferral, HTE edge modes, debounce limits, pin range registration, and line-name numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tegra186.c -->
