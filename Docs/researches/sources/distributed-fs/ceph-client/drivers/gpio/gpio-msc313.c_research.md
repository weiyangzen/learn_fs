# sources/distributed-fs/ceph-client/drivers/gpio/gpio-msc313.c

Purpose: supports GPIO pads on MStar/SigmaStar MSC313 and SSD20x-family SoCs. It maps SoC-specific named pad lists to sparse register offsets, exposes GPIO operations, saves output-enable/value state across suspend, and delegates selected GPIO interrupts to the parent interrupt controller.

Important APIs/types/functions: `struct msc313_gpio_data` contains per-SoC line names, register offsets, and count. Large static name/offset tables describe functional pads and SSD20x GPIO/TTL/UART/SD variants. `struct msc313_gpio` stores the base, matched data, and suspend save array. GPIO callbacks are set/get/direction_input/direction_output. IRQ integration uses `msc313_gpio_irqchip`, `msc313_gpio_populate_parent_fwspec()`, and `msc313e_gpio_child_to_parent_hwirq()`.

Control flow: probe obtains match data, finds the parent IRQ domain, allocates state and the save array, maps MMIO, allocates and fills a gpiochip with names and callbacks, configures hierarchical IRQ mapping to the parent domain, and registers the chip. Direction input sets the OEN bit; direction output clears OEN and updates OUT. Interrupt child-to-parent mapping only accepts offsets in the SPI0 pad range and maps them to parent SPI interrupts 28-31 with the requested type.

State and persistence behavior: each pad register contains IN, OUT, and OEN bits. Suspend saves only OUT and OEN bits (`MSC313_GPIO_BITSTOSAVE`) for every configured line; resume writes those bits back to each sparse register. Input state is hardware sampled and not persisted.

Dependencies and integration points: depends on OF match data gated by `CONFIG_MACH_INFINITY`, parent interrupt controller domain discovery, ARM GIC fwspec format, gpiolib, and generic pin request/free. The IRQ chip forwards EOI, mask, unmask, type, and affinity operations to the parent.

Risks: only SPI0 pins support parent IRQ mapping; IRQ requests on other GPIOs fail. Writing saved OUT/OEN bits on resume overwrites only the saved byte value and may drop any unrelated bits in those registers if future hardware adds them. The match table is empty unless `CONFIG_MACH_INFINITY` is enabled. Sparse offset/name tables are large and prone to ordering mistakes.

Test signals: compatible-specific line count/names, sparse offset get/set/direction behavior, suspend/resume preservation of OUT/OEN, parent fwspec creation with `GIC_SPI`, SPI0 IRQ mapping to parent hwirqs 28-31, and rejection of unsupported IRQ-capable lines.
