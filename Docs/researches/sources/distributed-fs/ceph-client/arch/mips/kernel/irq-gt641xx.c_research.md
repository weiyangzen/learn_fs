<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/irq-gt641xx.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/irq-gt641xx.c

### Purpose
`irq-gt641xx.c` implements IRQ chip and dispatch support for GT641xx system controller interrupts. It masks, unmasks, acknowledges, initializes, and dispatches interrupt bits from the GT interrupt cause and mask registers.

### Important APIs, Types, And Functions
Public functions are `gt641xx_irq_dispatch()` and `gt641xx_irq_init()`. IRQ-chip callbacks are `ack_gt641xx_irq()`, `mask_gt641xx_irq()`, `mask_ack_gt641xx_irq()`, and `unmask_gt641xx_irq()`. The `gt641xx_irq_chip` is registered for interrupts `GT641XX_IRQ_BASE + 1` through `+29`.

### Control Flow
Initialization disables all GT interrupts, clears cause, and installs a level IRQ handler for supported bits. Dispatch reads cause and mask, intersects them, scans bits 1 through 29, and calls `do_IRQ()` for the first active source. If no source is found it increments `irq_err_count`.

### State, Persistence, And Dependencies
State is in GT interrupt MMIO registers and protected by `gt641xx_irq_lock` for mask/cause read-modify-write. The file depends on `GT_READ`, `GT_WRITE`, `GT_INTRCAUSE_OFS`, `GT_INTRMASK_OFS`, Linux IRQ core, and `irq_err_count`.

### Integration Points
Platform interrupt code calls `gt641xx_irq_init()` and `gt641xx_irq_dispatch()` when the CPU interrupt line represents GT641xx aggregated interrupts. Child device drivers receive Linux IRQ numbers under `GT641XX_IRQ_BASE`.

### Risks
The dispatcher ignores summary bits 0, 30, and 31 and handles only one pending bit per entry. Incorrect base numbering or summary-bit interpretation can drop interrupts. Ack and mask operations share one lock but direct hardware behavior depends on cause bits being write-clear by writing the masked value.

### Test Signals
Exercise each usable GT interrupt input, verify masking/unmasking, confirm spurious counts only rise on real spurious events, and inspect `/proc/interrupts` for expected child IRQ numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/irq-gt641xx.c -->
