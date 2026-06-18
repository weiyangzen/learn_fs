<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_stack.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_stack.h

## Purpose
x86 IRQ stack switching macros for running hard IRQ, system vector, and softirq work on the per-CPU interrupt stack. The header is 241 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/ptrace.h>`; `#include <linux/objtool.h>`; `#include <asm/processor.h>`

Notable constants/macros: `#define _ASM_X86_IRQ_STACK_H`; `#define call_on_stack(stack, func, asm_call, argconstr...) \`; `#define ASM_CALL_ARG0 \`; `#define ASM_CALL_ARG1 \`; `#define ASM_CALL_ARG2 \`; `#define ASM_CALL_ARG3 \`; `#define call_on_irqstack(func, asm_call, argconstr...) \`; `#define assert_function_type(func, proto) \`; `#define assert_arg_type(arg, proto) \`; `#define call_on_irqstack_cond(func, regs, asm_call, constr, c_args...) \`; `#define ASM_CALL_SYSVEC \`; `#define SYSVEC_CONSTRAINTS , [arg1] "r" (regs)`; `#define run_sysvec_on_irqstack_cond(func, regs) \`; `#define ASM_CALL_IRQ \`; `#define IRQ_CONSTRAINTS , [arg1] "r" (regs), [arg2] "r" ((unsigned long)vector)`; `#define run_irq_on_irqstack_cond(func, regs, vector) \`; `#define do_softirq_own_stack() \`

Notable declarations and inline helpers: `#define _ASM_X86_IRQ_STACK_H`; `#define call_on_stack(stack, func, asm_call, argconstr...) \`; `#define ASM_CALL_ARG0 \`; `#define ASM_CALL_ARG1 \`; `#define ASM_CALL_ARG2 \`; `#define ASM_CALL_ARG3 \`; `#define call_on_irqstack(func, asm_call, argconstr...) \`; `#define assert_function_type(func, proto) \`; `#define assert_arg_type(arg, proto) \`; `#define call_on_irqstack_cond(func, regs, asm_call, constr, c_args...) \`; `#define ASM_CALL_SYSVEC \`; `#define SYSVEC_CONSTRAINTS , [arg1] "r" (regs)`; `#define run_sysvec_on_irqstack_cond(func, regs) \`; `#define ASM_CALL_IRQ \`; `#define IRQ_CONSTRAINTS , [arg1] "r" (regs), [arg2] "r" ((unsigned long)vector)`; `#define run_irq_on_irqstack_cond(func, regs, vector) \`; `#define do_softirq_own_stack() \`

## Control Flow
call_on_stack() saves the original SP at the top of the IRQ stack, switches stacks, invokes typed assembly call glue, restores SP, and conditionally avoids switching when already on the IRQ stack or from user mode.

## State and Persistence
State is per-CPU hardirq_stack_ptr and transient stack linkage for unwinders.

## Dependencies and Integration Points
Depends on objtool noinstr expectations, pt_regs, processor stack layout, hardirq state, and idtentry system vector wrappers.

## Risks
Risks include broken unwinding, wrong argument constraints, stack corruption, and running instrumented code before entry state is valid.

## Test Signals
Tests should cover nested IRQs, sysvec/device IRQs, softirq own stack, objtool validation, unwinds through IRQ stack, and 32-bit fallback macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_stack.h -->
