# sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp.c

## Purpose
Provides common PowerPC processor-state save/restore hooks for software suspend.

## Important APIs, Types, and Functions
- `save_processor_state()` flushes lazy special register state from the current task and hard-disables IRQs on PPC64.
- `restore_processor_state()` restores the MMU context on PPC32.

## Control Flow and State
Called by hibernation core before and after image creation/copyback. Save flushes all lazy FP/vector/etc. state into `current->thread`; restore reselects the active MM on 32-bit.

## State and Persistence Behavior
Mutates current task thread state by forcing lazy register materialization. IRQ state is changed on PPC64.

## Dependencies and Integration Points
Uses `flush_all_to_thread()`, `hard_irq_disable()`, and `switch_mmu_context()`. Pairs with assembly resume/suspend routines in `swsusp_*.S`.

## Risks
Missing lazy state flush would produce corrupted hibernation images. IRQ/MMU state assumptions must match the low-level assembly resume path.

## Test Signals
Hibernate/resume with FP, VMX, VSX, and active user state; PPC32 MM context restoration; PPC64 interrupt state during suspend.
