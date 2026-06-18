## sources/distributed-fs/ceph-client/arch/mips/kvm/interrupt.h

Purpose: Defines MIPS KVM exception priority numbers, timer interrupt bit helpers, and interrupt-related function declarations.

Important APIs, types, and functions: Priority constants run from `MIPS_EXC_RESET` through `MIPS_EXC_MAX`, including timer, IO, execute, and IPI priorities. `C_TI` represents the Cause.TI bit. Externs include `kvm_priority_to_irq`, `kvm_irq_to_priority()`, `kvm_mips_pending_timer()`, `kvm_mips_deliver_interrupts()`, and optional `kvm_init_loongson_ipi()`.

Control flow: This header establishes the priority ordering used by interrupt delivery and IRQ ioctl mapping. It does not execute code directly.

State and persistence: Declares the global priority-to-IRQ mapping pointer implemented in `mips.c`.

Dependencies and integration points: Used by `interrupt.c`, `mips.c`, `emulate.c`, and `loongson_ipi.c`. The priority values must match callback implementation expectations and guest CP0 Cause/IP line usage.

Risks: Priority and IRQ mapping mismatches can deliver interrupts on incorrect guest lines. `MIPS_EXC_MAX` bounds bitmap iteration, so adding priorities requires updating all arrays and loops.

Test signals: Compile-time coverage for Loongson and non-Loongson builds; IRQ-to-priority lookups for timer/IO/IPI; bitmap iteration through all declared priorities.
