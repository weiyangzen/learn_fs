# sources/distributed-fs/ceph-client/include/linux/sh_intc.h

## Purpose

`sh_intc.h` defines the descriptor format and helper macros for SuperH interrupt controller registration. It maps event codes or IRQ numbers to enum IDs, groups, mask registers, priority registers, sense registers, acknowledgement registers, subgroups, and optional SMP or balancing metadata.

## Important APIs, Types, And Functions

Types include `intc_enum`, `struct intc_vect`, `struct intc_group`, `struct intc_subgroup`, `struct intc_mask_reg`, `struct intc_prio_reg`, `struct intc_sense_reg`, `struct intc_hw_desc`, and `struct intc_desc`. Macros include `evt2irq()`, `irq2evt()`, `INTC_VECT()`, `INTC_IRQ()`, `INTC_GROUP()`, `INTC_SMP_BALANCING()`, `INTC_SMP()`, `INTC_HW_DESC()`, `DECLARE_INTC_DESC()`, and `DECLARE_INTC_DESC_ACK()`.

APIs are `register_intc_controller()`, `intc_set_priority()`, `intc_irq_lookup()`, `intc_finalize()`, and optional `register_intc_userimask()`.

## Control Flow

SoC code declares descriptor tables with vectors, groups, mask registers, priority registers, sense registers, and optional ack registers. `register_intc_controller()` consumes the descriptor and installs irqchip behavior. The code also supports looking up IRQ numbers by chip name and enum ID, setting priorities, finalizing setup, and registering a user interrupt mask register when configured.

## State And Persistence

Descriptor data is usually `__initdata` and describes persistent hardware topology during boot. Runtime IRQ masking, priority, sense, SMP distribution, and acknowledgement state live in hardware registers and irqchip implementation state.

## Dependencies And Integration Points

Dependencies include IO resource descriptors and optional `CONFIG_SUPERH`, `CONFIG_CPU_HAS_INTEVT`, `CONFIG_INTC_BALANCING`, `CONFIG_SMP`, and `CONFIG_INTC_USERIMASK`. Integration points are arch interrupt setup, irqchip core, platform device IRQ numbering, SMP routing, and syscore suspend behavior through `skip_syscore_suspend`.

## Risks And Test Signals

Risks are bad event-to-IRQ conversion, arrays with missing zero terminators or wrong enum IDs, incorrect register width/field width, conflicting force-enable/disable IDs, and wrong SMP stride/count encoding. Test signals include boot IRQ registration, interrupt delivery from each vector group, priority changes, wake/suspend paths, SMP interrupt distribution, and usermask behavior when enabled.
