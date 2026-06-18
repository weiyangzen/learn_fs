<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mxs.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mxs.c

### Purpose
`irq-mxs.c` implements the Freescale MXS ICOLL interrupt collector and the related Alphascale ASM9260 variant. It installs the architecture top-level IRQ handler and maps collector hwirqs into a linear domain.

### Important APIs, Types, And Functions
`struct icoll_priv` stores register pointers and controller type. `icoll_of_init()` handles MXS ICOLL, while `asm9260_of_init()` handles ASM9260. `icoll_handle_irq()` reads the active vector/status, acknowledges the vector register, and handles the domain IRQ. `mxs_icoll_chip` and `asm9260_icoll_chip` provide variant-specific mask/unmask operations.

### Control Flow
MXS init maps registers, assigns register pointers, resets the block with `stmp_reset_block()`, creates a 128-entry domain, and installs `icoll_handle_irq()`. ASM9260 init maps alternate register offsets, enables controller IRQs, manually initializes priority/level registers because no reset bit exists, creates its domain, and installs the same handler. The top-level handler reads the current hwirq, writes it to the vector register, and calls `generic_handle_domain_irq()`.

### State, Persistence, And Dependencies
State is global `icoll_priv` and `icoll_domain`. Dependencies include OF mapping, STMP reset support, ARM exception handling, variant register definitions, and irqdomain APIs.

### Integration Points
The driver is the root interrupt controller for MXS/ASM9260 systems. Child devices use one-cell interrupt specifiers into the linear domain.

### Risks
Global state allows one controller. The handler assumes the status register always returns a valid active hwirq. ASM9260 packs four interrupts per register, so bit-shift helper correctness is critical. There is no explicit spurious handling.

### Test Signals
Boot both compatibles, validate controller reset/manual initialization, mask/unmask bit positions for representative hwirqs, top-level vector dispatch, domain map size differences, and invalid MMIO mapping failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mxs.c -->
