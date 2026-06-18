<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/irq_txx9.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/irq_txx9.c

### Purpose
`irq_txx9.c` implements the Toshiba TXx9 interrupt controller driver. It maps IRC registers, configures interrupt priorities and trigger modes, masks/acknowledges/unmasks sources, and returns the current pending IRQ.

### Important APIs, Types, And Functions
Public functions are `txx9_irq_init()`, `txx9_irq_set_pri()`, and `txx9_irq()`. IRQ chip callbacks are `txx9_irq_unmask()`, `txx9_irq_mask()`, `txx9_irq_mask_ack()`, and `txx9_irq_set_type()`. The file defines `struct txx9_irc_reg` and per-line `txx9irq[]` level/mode state.

### Control Flow
Initialization maps the IRC, assigns default priority and low-level mode to each line, registers all lines as level IRQs, masks all interrupts, clears interrupt level registers, sets control registers to low-active, enables interrupt control, and sets enabled priority level. Runtime type changes update control-register two-bit fields. Masking writes the disabled priority to the selected ILR slot; unmasking writes the stored priority. Edge ack clears edge detection through `scr`.

### State, Persistence, And Dependencies
State is split between `txx9_ircptr`, the `txx9irq[]` software shadow for priority/mode, and IRC MMIO registers. The file depends on `asm/txx9irq.h`, gpiolib-adjacent TXx9 board setup, IRQ core, raw MMIO, and `mmiowb()`.

### Integration Points
Board interrupt dispatch calls `txx9_irq()` to obtain the pending Linux IRQ number and then dispatches it. Device drivers use IRQs starting at `TXX9_IRQ_BASE`.

### Risks
Register field math for ILR offsets is compact and easy to break. `txx9_irq()` returns `-1` when the current-status flag indicates no interrupt, so callers must handle spurious cases. Defaulting all handlers to level IRQs means edge users must call `irq_set_type()`.

### Test Signals
Test priority changes, all four trigger types, edge clear behavior, masking/unmasking, spurious `-1` returns, and interrupt numbering against `TXX9_IRQ_BASE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/irq_txx9.c -->
