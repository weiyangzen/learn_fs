# sources/distributed-fs/ceph-client/arch/x86/kernel/dumpstack_64.c

## Purpose
Provides 64-bit x86 stack classification for task, IRQ, entry trampoline, and IST exception stacks.

## Important APIs, Types, And Functions
`stack_type_name()` names task/IRQ/softirq/entry and exception stack types. `struct estack_pages` maps CPU entry area exception stack pages to stack metadata. `in_exception_stack()` and `in_irq_stack()` identify special stacks. `get_stack_info_noinstr()` is noinstr-safe; `get_stack_info()` adds recursion checks.

## Control Flow
The classifier checks the task stack first, then for current checks exception stacks, IRQ stack, and entry stack. Exception stack lookup computes an offset in `cea_exception_stacks`, rejects guard pages, and derives `next_sp` from the pt_regs at the stack top. IRQ stack lookup adjusts the stored top pointer and reads the saved next stack pointer from the top entry.

## State, Persistence, And Dependencies
State is static exception page descriptors; runtime reads CPU entry area and hardirq stack pointers. It depends on CEA layout, IST stack sizes, IRQ stack switching ABI, and stacktrace interfaces.

## Integration Points
Used by common dumpstack and unwinder code, including noinstr contexts where instrumentation must be avoided.

## Risks
CEA exception stacks may be uninitialized early, so the code must fail gracefully. Guard pages must remain unclassified. Wrong next-SP computation can hide entry frames or loop traces.

## Test Signals
64-bit fault/NMI/#DB/#MC/#VC/IRQ traces should label stacks accurately, include transitions back to interrupted stacks, and warn once on recursion.
