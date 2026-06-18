# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/xstate.h

## Purpose
Provides internal FPU xstate helpers, declarations, and inline assembly wrappers for saving/restoring XSAVE state in kernel and signal-frame contexts. It is the contract between the generic FPU code and `xstate.c`.

## Important APIs, Types, And State
Defines `enum xstate_copy_mode`, declarations for UABI copy helpers, system/per-CPU init functions, and `get_xsave_addr_user()`. Inline helpers include `xstate_init_xcomp_bv()`, `xstate_get_group_perm()`, `xfeatures_mask_supervisor()`, `xfeatures_mask_independent()`, signal-frame PKRU helpers, `xfd_set_state()`, `xfd_update_state()`, `os_xsave()`, `os_xrstor()`, `os_xrstor_supervisor()`, `xsave_to_user_sigframe()`, `xrstor_from_user_sigframe()`, and `os_xrstor_safe()`. On x86-64 it declares per-CPU `xfd_state`.

## Control Flow And State Behavior
Save/restore wrappers choose XSAVE, XSAVEOPT, XSAVEC, XSAVES, XRSTOR, or XRSTORS through alternatives and exception-table fixups. Kernel saves use `fpstate->xfeatures`, validate XFD state under debug builds, and warn on kernel-buffer faults. Signal-frame saves force standard, uncompacted XSAVE ABI format and optionally omit init-optimized dynamic features; they update PKRU in the userspace buffer. Restores from userspace use `stac()`/`clac()` and return trap-derived errors rather than taking raw exceptions. XFD helpers keep the IA32_XFD MSR synchronized with the cached per-CPU value.

## Dependencies And Integration Points
Uses asm xstate definitions, feature alternatives, exception table types, MSR accessors, pkey/PKRU helpers, task FPU state, and signal code. It is included by xstate implementation and lower FPU context-switch paths.

## Risks And Test Signals
Risks include wrong feature masks causing #GP/#PF, signal ABI regressions from compacted-format leakage, stale XFD MSR values, and missing PKRU marking in signal frames. Tests should exercise XSAVE/XRSTOR under multiple CPU feature combinations, signal delivery/return with PKRU and AMX, debug FPU validation, and fault injection for user sigframe copy.
