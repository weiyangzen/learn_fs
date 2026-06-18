<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108_irq.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108_irq.h

Purpose: Defines TSI108 interrupt vector numbers, priorities, and register offsets.

Important APIs/types/functions: IRQ source constants, vector count, priority defaults, spurious vector, and interrupt-control register definitions. Source-visible declarations include: #define _ASM_POWERPC_TSI108_IRQ_H; #define TSI108_IRQ_REG_BASE 0; #define TSI108_IRQ(x) (TSI108_IRQ_REG_BASE + (x)); #define TSI108_MAX_VECTORS (36 + 4) /* 36 sources + PCI INT demux */; #define MAX_TASK_PRIO 0xF; #define TSI108_IRQ_SPURIOUS (TSI108_MAX_VECTORS); #define DEFAULT_PRIO_LVL 10 /* initial priority level */; #define IRQ_TSI108_EXT_INT0 TSI108_IRQ(0) /* External Source at INT[0] */.

Control flow: interrupt controller code maps hardware sources to Linux IRQs and programs priority/mask registers. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: hardware interrupt mask/priority state persists in TSI108 registers. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with TSI108 MPIC/interrupt setup and board device IRQ routing.

Risks: vector numbering must match hardware and PCI INT demux sources or devices receive wrong IRQs. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 110 lines, 3916 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108_irq.h -->
