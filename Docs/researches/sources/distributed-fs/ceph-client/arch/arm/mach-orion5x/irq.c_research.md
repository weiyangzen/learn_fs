<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/irq.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/irq.c

### Purpose
`irq.c` initializes the legacy Orion5x interrupt controller and GPIO interrupt ranges.

### Important APIs, Types, And Functions
The public entry is `orion5x_init_irq()`. The IRQ handler is `orion5x_legacy_handle_irq()`, and `gpio0_irqs[]` maps four GPIO cause groups to main IRQ lines.

### Control Flow
IRQ init initializes the main interrupt controller at IRQ base 1, installs the custom IRQ handler, and registers GPIOs 0-31 with their parent IRQ groups. The handler reads cause and mask registers, finds the highest pending bit with `__fls()`, converts it to Linux IRQ numbering, and calls `handle_IRQ()`.

### State, Persistence, And Dependencies
State persists in the kernel IRQ handler and GPIO IRQ registration. Dependencies include bridge interrupt registers, plat-orion IRQ helpers, and Orion GPIO support.

### Integration Points
ATAGS machine descriptors call this during `.init_irq`; DT mode uses `ORION_IRQCHIP` instead of this legacy path.

### Risks
The handler handles one pending interrupt per entry and silently returns if none are masked pending. IRQ numbering starts at 1, so off-by-one errors are easy.

### Test Signals
Timer, UART, Ethernet, and GPIO interrupt activity on ATAGS boards should dispatch to the expected IRQ numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/irq.c -->
