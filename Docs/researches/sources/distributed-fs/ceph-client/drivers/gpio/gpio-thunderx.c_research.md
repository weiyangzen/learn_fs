<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-thunderx.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-thunderx.c

Purpose: implements the Cavium ThunderX/OCTEON-TX PCI GPIO controller with MMIO GPIO access, per-line MSI-X backed interrupts, open-drain handling, inversion compensation, and debounce/glitch filter configuration.

Important APIs, types, and functions: `struct thunderx_gpio` owns the gpiochip, register base, MSI-X entries, per-line metadata, raw spinlock, invert/open-drain masks, and MSI base. `struct thunderx_line` stores per-line filter bits. GPIO callbacks include request, direction, get/set, set_multiple, get_direction, and set_config. IRQ callbacks include ack, mask, mask_ack, unmask, enable/disable, set_type, parent hwirq translation, and MSI allocation info population.

Control flow: PCI probe enables and maps BAR0, determines GPIO count and base MSI from `GPIO_CONST` or CN88XX fallback, initializes per-line filter/inversion/open-drain state from hardware, enables MSI-X for every line, configures gpiochip callbacks and a hierarchical IRQ chip using the MSI domain, registers the gpiochip, then pushes irq_data/domain state for each MSI vector. Remove pops those IRQs and removes the gpio IRQ domain.

State and persistence behavior: hardware contains line config, output, interrupt, and filter state. Driver bitmaps mirror inversion and open-drain choices so get/set and direction compensate for hardware inversion behavior. No PM persistence is implemented.

Dependencies and integration points: depends on PCI managed resources, MSI-X, gpiolib hierarchical IRQ support, pinconf drive/debounce parameters, and 64-bit MMIO access.

Risks and test signals: `set_multiple()` loops through `chip->ngpio / 64` inclusive, so mask array sizing and partial second banks must be correct. Open-drain causes hardware inversion and requires careful value preservation. Test CN88XX fallback, non-GPIO pin rejection, MSI-X allocation, IRQ type flow-handler selection, debounce bounds, open-drain/push-pull transitions while output, and remove-time domain cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-thunderx.c -->
