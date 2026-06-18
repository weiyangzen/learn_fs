<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/idtentry.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/idtentry.h

## Purpose
Central x86 interrupt/exception entry declaration framework for C handlers, assembly stubs, FRED dispatch, system vectors, IST/NMI/MCE/VC special cases, and common IRQ stubs. The header is 781 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/trapnr.h>`; `#include <linux/entry-common.h>`; `#include <linux/hardirq.h>`; `#include <asm/irq_stack.h>`

Notable constants/macros: `#define _ASM_X86_IDTENTRY_H`; `#define IDT_ALIGN (8 * (1 + HAS_KERNEL_IBT))`; `#define DECLARE_IDTENTRY(vector, func) \`; `#define DEFINE_IDTENTRY(func) \`; `#define DECLARE_IDTENTRY_SW DECLARE_IDTENTRY`; `#define DEFINE_IDTENTRY_SW DEFINE_IDTENTRY`; `#define DECLARE_IDTENTRY_ERRORCODE(vector, func) \`; `#define DEFINE_IDTENTRY_ERRORCODE(func) \`; `#define DECLARE_IDTENTRY_RAW(vector, func) \`; `#define DEFINE_IDTENTRY_RAW(func) \`; `#define DEFINE_FREDENTRY_RAW(func) \`; `#define DECLARE_IDTENTRY_RAW_ERRORCODE(vector, func) \`; `#define DEFINE_IDTENTRY_RAW_ERRORCODE(func) \`; `#define DECLARE_IDTENTRY_IRQ(vector, func) \`; `#define DEFINE_IDTENTRY_IRQ(func) \`; `#define DECLARE_IDTENTRY_SYSVEC(vector, func) \`; `#define DEFINE_IDTENTRY_SYSVEC(func) \`; `#define DEFINE_IDTENTRY_SYSVEC_SIMPLE(func) \`

Notable declarations and inline helpers: `#define _ASM_X86_IDTENTRY_H`; `#define IDT_ALIGN (8 * (1 + HAS_KERNEL_IBT))`; `typedef void (*idtentry_t)(struct pt_regs *regs);`; `#define DECLARE_IDTENTRY(vector, func) \`; `asmlinkage void asm_##func(void); \`; `asmlinkage void xen_asm_##func(void); \`; `void fred_##func(struct pt_regs *regs); \`; `#define DEFINE_IDTENTRY(func) \`; `static __always_inline void __##func(struct pt_regs *regs); \`; `static __always_inline void __##func(struct pt_regs *regs)`; `#define DECLARE_IDTENTRY_SW DECLARE_IDTENTRY`; `#define DEFINE_IDTENTRY_SW DEFINE_IDTENTRY`; `#define DECLARE_IDTENTRY_ERRORCODE(vector, func) \`; `#define DEFINE_IDTENTRY_ERRORCODE(func) \`; `static __always_inline void __##func(struct pt_regs *regs, \`; `unsigned long error_code); \`; `unsigned long error_code) \`; `unsigned long error_code)`; `#define DECLARE_IDTENTRY_RAW(vector, func) \`; `#define DEFINE_IDTENTRY_RAW(func) \`; `#define DEFINE_FREDENTRY_RAW(func) \`; `#define DECLARE_IDTENTRY_RAW_ERRORCODE(vector, func) \`; `#define DEFINE_IDTENTRY_RAW_ERRORCODE(func) \`; `#define DECLARE_IDTENTRY_IRQ(vector, func) \`

## Control Flow
DECLARE_* macros emit either C prototypes or assembly stubs; DEFINE_* wrappers run irqentry_enter/exit, instrumentation windows, IRQ-stack switching, L1D flush marking, and raw special-case handlers.

## State and Persistence
State is mostly entry-stack/register state plus IDT/FRED installed function pointers; generated stubs form part of the binary ABI between assembly and C.

## Dependencies and Integration Points
Depends on trap numbers, irq_stack.h, entry-common, hardirq, APIC vectors, KVM, Xen, TDX, SEV-ES #VC, FRED, IBT alignment, and assembler macro support.

## Risks
Risks are high: wrong macro variant can enable instrumentation too early, skip irq accounting, mishandle error codes, break IST/NMI safety, or desynchronize C and assembly symbols.

## Test Signals
Tests should cover every exception vector, common/spurious IRQs, system IPIs, NMI/MCE/#DB/#DF/#VC/#VE, Xen/KVM/Hyper-V variants, FRED and non-FRED boots, objtool noinstr validation, and tracing entry symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/idtentry.h -->
