<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-meson-gpio.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-meson-gpio.c

### Purpose
`irq-meson-gpio.c` implements the Amlogic Meson GPIO interrupt multiplexer. It maps many GPIO input hwirqs onto a small number of hardware interrupt channels connected to a parent GIC, with SoC-specific mux and trigger programming.

### Important APIs, Types, And Functions
`struct meson_gpio_irq_params` captures per-SoC hwirq count, channel count, register bit layout, both-edge support, and operation callbacks. `struct meson_gpio_irq_controller` stores params, MMIO base, channel IRQ numbers, channel bitmap, and lock. `meson_gpio_irq_domain_alloc()` assigns a channel and allocates the parent GIC IRQ. `meson_gpio_irq_set_type()` programs local trigger bits and converts output type for the parent.

### Control Flow
Probe finds the parent domain, allocates controller state, maps registers, matches SoC params, reads `amlogic,channel-interrupts`, runs optional hardware init, and creates a hierarchical domain sized by available GPIO hwirqs. Allocation translates the two-cell child spec, reserves the first free channel, programs that channel's pin mux to the requested GPIO, allocates the parent SPI listed for that channel, and stores a pointer to the channel entry as chip data. Freeing releases the parent IRQ and clears the channel bit. Type changes use Meson8/A1/S4-specific register layouts and always tell the GIC to expect active-high level or rising edge.

### State, Persistence, And Dependencies
Persistent state is the channel allocation bitmap, channel-to-parent IRQ table, SoC parameter table, and MMIO trigger/mux registers. It depends on OF matching, parent GIC domains, raw spinlocks for register RMW, and Amlogic binding properties.

### Integration Points
GPIO controller drivers or board devices request interrupts from this domain. The driver hides the limited channel hardware by dynamically multiplexing GPIO hwirqs onto parent GIC SPIs.

### Risks
Channels are scarce; allocation fails with `-ENOSPC` when all are in use. Trigger-bit layouts vary widely by SoC, including special both-edge behavior. Freeing uses pointer arithmetic on `channel_irqs`, so chip data must remain a valid pointer into the controller. S4-style type programming touches two registers with different bit meanings.

### Test Signals
Exercise all compatible parameter sets, channel exhaustion/reuse, both-edge support and rejection on older SoCs, mux register programming for low/high channel numbers, parent SPI type conversion, allocation failure cleanup, and concurrent type changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-meson-gpio.c -->
