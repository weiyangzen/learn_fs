# sources/distributed-fs/ceph-client/arch/x86/kernel/dumpstack_32.c

## Purpose
Provides 32-bit x86 stack classification for task, entry, hardirq, softirq, and double-fault stacks.

## Important APIs, Types, And Functions
`stack_type_name()` names stack types. `in_hardirq_stack()`, `in_softirq_stack()`, and `in_doublefault_stack()` identify special stacks and set `next_sp`. `get_stack_info()` is the exported classifier used by common dumpstack/unwinder code.

## Control Flow
`get_stack_info()` checks task stack first, then only for current checks entry, hardirq, softirq, and double-fault stacks. Each match fills begin/end/type/next_sp. A visit mask detects stack recursion and reports unknown if a stack type repeats.

## State, Persistence, And Dependencies
No new persistent state is created; it reads per-CPU irq stack pointers, CPU entry area double-fault stack, and current TSS saved SP. It depends on 32-bit IRQ stack layout and double-fault TSS setup.

## Integration Points
Feeds `dumpstack.c` stack walking and frame transition logic on 32-bit kernels.

## Risks
Stack boundary checks differ for software stacks where `end` may be a valid empty-stack pointer. Incorrect `next_sp` extraction can truncate traces or recurse.

## Test Signals
32-bit traces from task, IRQ, softirq, entry, and double-fault contexts should label stacks correctly and stop on recursive or invalid stack transitions.
