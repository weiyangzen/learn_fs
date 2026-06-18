# sources/distributed-fs/ceph-client/arch/x86/kernel/doublefault_32.c

## Purpose
Sets up the 32-bit double-fault task gate/TSS stack and converts task-switch state into `pt_regs` for the common double-fault handler.

## Important APIs, Types, And Functions
`doublefault_shim()` is the non-returning C shim entered after the double-fault task switch. `doublefault_stack` is per-CPU page-aligned TSS/stack storage. `set_df_gdt_entry()` writes the GDT TSS descriptor. `doublefault_init_cpu_tss()` initializes per-CPU stack pointer and descriptor.

## Control Flow
The shim saves CR2, reloads the normal task register, reinstalls the double-fault GDT entry, marks hard IRQs off, builds a synthetic `pt_regs` from the double-fault TSS slots, calls `exc_double_fault()`, and panics because x86_32 cannot reconstruct CR3 safely after the task switch.

## State, Persistence, And Dependencies
Persistent per-CPU state is the double-fault TSS and stack in the CPU entry area. It depends on GDT/TSS helpers, CPU entry area layout, trap handling, and low-level assembly entry.

## Integration Points
Works with `asm_exc_double_fault`, common exception handling, and `dumpstack_32.c` stack recognition of double-fault stacks.

## Risks
This code runs in a catastrophic fault path and cannot return. Incorrect TSS descriptors or stack pointers can triple-fault. The synthetic regs are not visible to the unwinder as a normal frame.

## Test Signals
Forced double faults on 32-bit kernels should reach the double-fault oops path with meaningful registers and stack trace instead of immediate reset.
