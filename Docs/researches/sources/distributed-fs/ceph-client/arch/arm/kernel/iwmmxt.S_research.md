# sources/distributed-fs/ceph-client/arch/arm/kernel/iwmmxt.S

Purpose: implements lazy context management for Intel/XScale iWMMXt/Concan coprocessor state, including undefined-instruction enablement, task switch gating, signal/ptrace save-restore, and owner release.

Important APIs/types/functions: entry points include `iwmmxt_undef_handler`, `iwmmxt_task_enable`, `iwmmxt_task_disable`, `iwmmxt_task_copy`, `iwmmxt_task_restore`, `iwmmxt_task_switch`, and `iwmmxt_task_release`. Internal helpers `concan_save`, `concan_dump`, and `concan_load` manipulate WR and control registers using macros from `iwmmxt.h`.

Control flow: an undef trap enables CP0/CP1 access, backs PC up to retry the faulting instruction, saves the previous owner when needed, records the current task as `concan_owner`, and loads its saved state. Disable/copy/restore paths run with interrupts masked to keep ownership coherent. Task switch toggles coprocessor access to force lazy reloads.

State and persistence: global `concan_owner` points to the owning task save area; each thread stores iWMMXt state under `TI_IWMMXT_STATE`/fpstate.

Dependencies and integration: used by ptrace, signal handling, thread notifiers, undefined instruction handling, and ARM coprocessor access control.

Risks: ownership races corrupt user vector state; alignment and interrupt masking are critical; unsupported toolchains need raw instruction macros. Test signals include iWMMXt userspace context-switch tests, signal save/restore, ptrace register access, suspend save, and preemption stress.
