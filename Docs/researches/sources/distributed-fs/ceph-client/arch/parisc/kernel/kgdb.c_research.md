# sources/distributed-fs/ceph-client/arch/parisc/kernel/kgdb.c

## Purpose

`kgdb.c` implements PA-RISC architecture support for KGDB. It registers a die notifier, converts register state to and from GDB layout, patches breakpoints, adjusts the PA-RISC instruction address queues, and handles continue/single-step commands.

## Important APIs, Types, And Functions

`arch_kgdb_ops` defines the PA-RISC breakpoint instruction bytes. `kgdb_arch_init()` and `kgdb_arch_exit()` register and unregister `kgdb_notifier`. `pt_regs_to_gdb_regs()`, `gdb_regs_to_pt_regs()`, and `sleeping_thread_to_gdb_regs()` translate between `struct pt_regs` and `struct parisc_gdb_regs`.

Breakpoint APIs are `kgdb_arch_set_breakpoint()` and `kgdb_arch_remove_breakpoint()`, using `copy_from_kernel_nofault()` and `__patch_text()`. `kgdb_arch_set_pc()` and `step_instruction_queue()` update `iaoq[0]` and `iaoq[1]`. `kgdb_arch_handle_exception()` handles GDB remote commands.

## Control Flow

The die notifier disables local IRQs around `kgdb_handle_exception()`. Register export zeros the GDB register buffer, copies GPRs/FPRs, segment registers, SAR/IIR/ISR/IOR/IPSW/CR27, and front/back instruction queues. Import writes the same fields back.

For sleeping threads, the code temporarily substitutes `ksp` and `kpc` into `gr[30]` and `iaoq[0]`, exports registers, then restores the original values.

On continue, detach, or kill commands, the handler clears KGDB current thread/single-step state, optionally sets PC from an address, and steps past compiled break instructions. On single-step, it sets `kgdb_single_step`, optionally sets PC, manipulates control register 0 for break-step behavior, sets `PSW_R`, and returns handled.

## State And Persistence Behavior

State is runtime debug state: notifier registration, patched breakpoint instructions, KGDB global current-thread/single-step flags, and modified `pt_regs`. No persistent storage is used.

## Dependencies And Integration Points

The file depends on generic KGDB, die notifiers, PA-RISC trap constants, text patching, cache flushing, and the architecture's dual instruction queue model. It integrates with compiled breakpoints and GDB remote protocol command parsing.

## Risks

Incorrect register mapping can make remote debugging misleading or destructive. PA-RISC uses front/back instruction queues, so setting only one PC word would be wrong. Breakpoint patching must preserve original instructions exactly and must be safe under nofault reads. Single-step depends on PSW and control-register behavior that is architecture-specific.

## Test Signals

Signals include connecting KGDB, reading and writing registers, setting and removing breakpoints, continuing past compiled break instructions, single-stepping over normal and breakpoint traps, and inspecting sleeping tasks with correct stack and PC values.
