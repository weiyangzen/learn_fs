# sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/irq.c

Purpose: low-level SB1250 interrupt mapper setup, masking, affinity, acknowledge, and dispatch.

Important APIs/types/functions: `sb1250_mask_irq`, `sb1250_unmask_irq`, SMP `sb1250_set_affinity`, `ack_sb1250_irq`, `init_sb1250_irqs`, `arch_init_irq`, `plat_irq_dispatch`, and the `SB1250-IMR` irq_chip.

Control flow and state: boot maps all mapper interrupts to IP2, mailbox to IP3, masks everything except mailboxes, registers level handlers, and enables CP0 IP bits; dispatch prioritizes CPU perf counter, timer, SMP mailbox, then IMR status via `fls64`; affinity moves ownership by masking old CPU and unmasking new CPU under a raw spinlock; LDT acknowledge clears pending bits across CPUs and writes EOI.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: wrong mapper/IP programming can lose all board interrupts; affinity assumes valid online CPU mapping; LDT path depends on external `ldt_eoi_space`; high 64-bit register handling is delicate under o32 as noted in comments.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
