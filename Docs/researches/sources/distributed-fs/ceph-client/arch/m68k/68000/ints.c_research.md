# sources/distributed-fs/ceph-client/arch/m68k/68000/ints.c

Purpose: generic interrupt controller and vector setup for 68x328/68000 non-MMU systems where the CPU provides limited interrupt source information.

Important APIs are `process_int(int vec, struct pt_regs *fp)`, `trap_init()`, and `init_IRQ()`. The file declares the assembly trap and interrupt entry points installed into `_ramvec`. `process_int()` reads the DragonBall interrupt status register `ISR`, finds pending set bits with a nested coarse-to-fine search, calls `do_IRQ(irq, fp)` for each pending IRQ, and clears the bit from its local snapshot.

The IRQ chip is `intc_irq_chip`; `intc_irq_mask()` sets the corresponding bit in `IMR`, while `intc_irq_unmask()` clears it. `init_IRQ()` programs `IVR = 0x40`, masks all interrupts with `IMR = ~0`, then assigns the chip and `handle_level_irq` to every IRQ. `trap_init()` installs syscall vector 32 and autovector handlers 65-71, while vectors 72-255 default to `bad_interrupt`.

State is held in memory-mapped DragonBall registers (`ISR`, `IMR`, `IVR`) and the RAM vector table. There is no persistent software queue; pending interrupt state is consumed directly from hardware each entry.

Dependencies include `asm/MC68328.h` or the EZ/VZ variants, `_ramvec`, assembly handlers in `entry.S`, `do_IRQ()`, and generic irq core functions. Integration is early architecture startup and machine timer/driver IRQ registration.

Risks and test signals: the software bit search assumes ISR bit-to-IRQ numbering is stable and that pending bits remain meaningful while dispatching. Validate by booting with timer IRQs, masking/unmasking devices, checking spurious interrupt counts, and ensuring all `NR_IRQS` receive a chip/handler. A specific regression signal is a timer storm or no timer ticks after `init_IRQ()`.
