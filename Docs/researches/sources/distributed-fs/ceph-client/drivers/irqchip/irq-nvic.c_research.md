<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-nvic.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-nvic.c

### Purpose
`irq-nvic.c` supports the ARMv7-M Nested Vectored Interrupt Controller. It creates a generic-chip domain over implemented NVIC external interrupts and installs the Cortex-M exception IRQ handler.

### Important APIs, Types, And Functions
`nvic_irq_domain` is the global domain. `nvic_of_init()` reads the number of interrupt banks, maps NVIC registers, allocates generic chips, disables all interrupts, sets priorities, and calls `set_handle_irq()`. `nvic_handle_irq()` reads SCB `ICSR.VECTACTIVE` and subtracts 16 to obtain the external hwirq. `nvic_irq_domain_alloc()` maps one-cell specs to generic chips.

### Control Flow
Initialization reads `V7M_SCS_ICTR` to compute implemented banks, caps the total at `NVIC_MAX_IRQ`, maps the NVIC resource, creates a linear domain, allocates one generic chip per 32 interrupts using `handle_fasteoi_irq`, programs each bank's enable/disable registers, disables all lines, zeroes priority registers, and installs the handler. Runtime dispatch handles the active exception's corresponding hwirq through the domain.

### State, Persistence, And Dependencies
Persistent state is the global NVIC domain, mapped NVIC base stored in generic chips, mask cache, and priority/enable hardware registers. It depends on ARMv7-M SCB definitions, OF resources, generic IRQ chips, and exception return providing EOI semantics.

### Integration Points
This is the root irqchip for ARMv7-M platforms. Device tree interrupt specifiers are one-cell NVIC external interrupt numbers.

### Risks
`nvic_handle_irq()` assumes `VECTACTIVE >= 16` for external interrupts. The last bank may expose only 16 interrupts, but generic chips are allocated in 32-line units while total IRQ count is capped. EOI is a no-op because exception return completes the interrupt.

### Test Signals
Validate bank count detection, max IRQ capping, priority initialization, enable/disable registers, active-vector dispatch, one-cell mappings, and Cortex-M systems with partial final banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-nvic.c -->
