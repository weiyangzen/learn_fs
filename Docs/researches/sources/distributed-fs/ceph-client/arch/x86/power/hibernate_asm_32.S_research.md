<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_asm_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/power/hibernate_asm_32.S

## Purpose
Contains 32-bit assembly for saving suspend registers, copying the hibernation image back to original pages, and jumping into restored kernel state.

## Important APIs, Types, And Functions
Defines `swsusp_arch_suspend`, `restore_image`, `core_restore_code`, and `restore_registers`. Uses saved context symbols from `cpu.c` and hibernation globals such as `temp_pgt`, `restore_cr3`, and `restore_jump_address`.

## Control Flow
Suspend saves callee-saved registers and stack return context before returning to the hibernation core. Restore switches to temporary page tables, copies memory pages from the snapshot list to original locations, switches to the restored CR3, and jumps to `restore_registers`, which restores saved registers and returns to the image kernel.

## State And Persistence
Assembly stores register values in global saved-context symbols and consumes the relocated restore code copied by C.

## Dependencies And Integration Points
Depends on common hibernate C, 32-bit paging/control register conventions, and `restore_processor_state()` after control returns to C.

## Risks And Edge Cases
Copying over live memory is irreversible. Register and stack restoration must match the C save side exactly. Interrupts and page tables must remain controlled until the restored kernel resumes.

## Test Signals
32-bit hibernate suspend/resume and stress tests with varied memory layouts exercise this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_asm_32.S -->
