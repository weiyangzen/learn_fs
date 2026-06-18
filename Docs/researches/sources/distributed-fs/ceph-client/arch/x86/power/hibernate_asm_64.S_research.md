<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/power/hibernate_asm_64.S

## Purpose
Contains 64-bit hibernation assembly for register restoration, suspend checkpointing, image copyback, and final jump to the restored kernel.

## Important APIs, Types, And Functions
Defines `restore_registers`, `swsusp_arch_suspend`, `restore_image`, and `core_restore_code`. It coordinates with `saved_context`, `restore_cr3`, `temp_pgt`, `restore_jump_address`, and `restore_processor_state()`.

## Control Flow
Suspend saves nonvolatile registers around the hibernation snapshot. Restore code runs from the relocated page, switches to temporary page tables and current CR4 feature mask, copies image pages back, switches to the image kernel CR3, updates CR4 again for the image kernel, and jumps to `restore_registers` to restore processor state and return to the saved control point.

## State And Persistence
Uses global hibernation symbols as handoff state between C and assembly. The copied image overwrites current kernel memory during restore.

## Dependencies And Integration Points
Depends on x86_64 calling convention, hibernation C setup, page-table globals, and CPU state restoration in `cpu.c`.

## Risks And Edge Cases
The CR3/CR4 ordering must avoid illegal PCID transitions and match comments in `hibernate.c`. Any compiler instrumentation or relocation assumption would be unsafe in this path.

## Test Signals
64-bit hibernate resume, especially with PCID, KASLR, and varied CR4 feature sets, validates the assembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_asm_64.S -->
