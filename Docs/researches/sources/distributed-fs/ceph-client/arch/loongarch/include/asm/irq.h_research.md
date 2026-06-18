# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/irq.h

## Purpose

`irq.h` defines IRQ stack, vector numbering, interrupt domains and ACPI interrupt-controller state. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 144 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: irq_stack, on_irq_stack, NR_VECTORS, AVEC encoding, NR_IRQS, acpi_vector_group, get_percpu_irq, interrupt-controller fwnode globals. Symbol extraction from the file shows representative defines `_ASM_IRQ_H`, `IRQ_STACK_SIZE`, `IRQ_STACK_START`, `NR_IRQS_LEGACY`, `NR_VECTORS`, `NR_LEGACY_VECTORS`, `AVEC_IRQ_SHIFT`, `AVEC_IRQ_BIT`, `AVEC_IRQ_MASK`, `AVEC_CPU_SHIFT`, `AVEC_CPU_BIT`, `AVEC_CPU_MASK`, representative callable declarations or inline helpers `on_irq_stack`, `spurious_interrupt`, `arch_trigger_cpumask_backtrace`, `complete_irq_moving`, `get_percpu_irq`, and representative local types `acpi_vector_group`, `acpi_madt_lio_pic`, `acpi_madt_eio_pic`, `acpi_madt_ht_pic`, `acpi_madt_bio_pic`, `acpi_madt_msi_pic`, `acpi_madt_lpc_pic`, `fwnode_handle`. Direct includes seen in the header are `asm-generic/irq.h`, `linux/irqdomain.h`, `linux/irqreturn.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header integrates CPU, LIO, EIO, PCH, MSI and ACPI MADT interrupt setup. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: vector math, MAX_IO_PICS and domain handles affect all interrupt delivery. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
