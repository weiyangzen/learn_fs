<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/irqflags.h

## Purpose
Low-level x86 interrupt flag helpers for saving/restoring EFLAGS/RFLAGS.IF, enabling/disabling IRQs, halt/safe_halt, and paravirt-aware arch wrappers. The header is 163 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/processor-flags.h>`; `#include <asm/nospec-branch.h>`; `#include <asm/paravirt.h>`; `#include <linux/types.h>`

Notable constants/macros: `#define _X86_IRQFLAGS_H_`; `#define SAVE_FLAGS pushfq; popq %rax`

Notable declarations and inline helpers: `#define _X86_IRQFLAGS_H_`; `extern inline unsigned long native_save_fl(void);`; `extern __always_inline unsigned long native_save_fl(void)`; `unsigned long flags;`; `static __always_inline void native_irq_disable(void)`; `static __always_inline void native_irq_enable(void)`; `static __always_inline void native_safe_halt(void)`; `static __always_inline void native_halt(void)`; `static __always_inline int native_irqs_disabled_flags(unsigned long flags)`; `static __always_inline unsigned long native_local_irq_save(void)`; `unsigned long flags = native_save_fl();`; `static __always_inline void native_local_irq_restore(unsigned long flags)`; `static __always_inline void arch_safe_halt(void)`; `static __always_inline void halt(void)`; `static __always_inline unsigned long arch_local_save_flags(void)`; `static __always_inline void arch_local_irq_disable(void)`; `static __always_inline void arch_local_irq_enable(void)`; `static __always_inline unsigned long arch_local_irq_save(void)`; `unsigned long flags = arch_local_save_flags();`; `#define SAVE_FLAGS pushfq; popq %rax`; `static __always_inline int arch_irqs_disabled_flags(unsigned long flags)`; `static __always_inline int arch_irqs_disabled(void)`; `static __always_inline void arch_local_irq_restore(unsigned long flags)`

## Control Flow
Native helpers emit pushf/pop, cli, sti, sti;hlt, hlt, and save/restore sequences; arch wrappers either call native or paravirt versions depending on config.

## State and Persistence
State affected is CPU interrupt-enable flag and halt state; saved flags values are transient per caller.

## Dependencies and Integration Points
Depends on processor flags, paravirt patching, nospec branch headers, and generic local_irq APIs.

## Risks
Risks include restoring stale flags, enabling interrupts too early in entry/exit, paravirt mismatch, and unsafe halt with interrupts disabled.

## Test Signals
Tests should cover local_irq_save/restore nesting, lockdep IRQ state, idle halt paths, paravirt guests, and objtool/noinstr entry users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irqflags.h -->
