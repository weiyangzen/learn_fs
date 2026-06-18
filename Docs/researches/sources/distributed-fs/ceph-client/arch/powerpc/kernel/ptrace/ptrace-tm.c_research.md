# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-tm.c

## Purpose
`ptrace-tm.c` exposes transactional-memory checkpointed register state and TM SPRs to ptrace and coredump regsets.

## Important APIs, Types, And Functions
The file exports `flush_tmregs_to_thread()`, active/get/set functions for checkpointed GPR (`tm_cgpr_*`), FPR (`tm_cfpr_*`), VMX (`tm_cvmx_*`), VSX (`tm_cvsx_*`), TM SPRs (`tm_spr_*`), checkpointed TAR/PPR/DSCR (`tm_tar_*`, `tm_ppr_*`, `tm_dscr_*`), and compat checkpointed GPR helpers (`tm_cgpr32_*`). Internal helpers sanitize checkpointed MSR and trap fields.

## Control Flow
Every active/get/set path first checks `CPU_FTR_TM`; checkpointed data paths additionally require `MSR_TM_ACTIVE(target->thread.regs->msr)`, except the TM SPR regset reports available registers whenever TM exists. `flush_tmregs_to_thread()` reclaims suspended current transactions or saves TM SPRs before exposing state. Getters flush TM/FP/Altivec/VSX state as needed, then copy checkpointed state with `membuf`. Setters copy through temporary buffers or field-by-field to keep special MSR/trap rules and ABI padding intact.

## State And Persistence
Persistent state lives in `thread.ckpt_regs`, `ckfp_state`, `ckvr_state`, `ckvrsave`, `tm_tfhar`, `tm_texasr`, `tm_tfiar`, `tm_tar`, `tm_ppr`, and `tm_dscr`. The code is not persistent across tasks beyond normal `thread_struct` scheduling state.

## Dependencies And Integration Points
It depends on PowerPC TM feature detection, `asm/tm.h`, transactional reclaim/save helpers, normal FP/Altivec/VSX flush paths, and common GPR32 helpers from `ptrace-view.c`. It fills the `REGSET_TM_*` entries declared in `ptrace-decl.h`.

## Risks
The main risk is exposing stale checkpointed state if live TM registers are not reclaimed or saved. Active-state checks depend on `thread.regs` and the MSR TM bits. The compat GPR32 helpers assume checkpointed GPR layout mirrors normal GPR layout. Partial copy paths must preserve unwriteable registers and padding.

## Test Signals
Useful signals include TM-enabled and TM-disabled builds, active and inactive transaction ptrace GETREGSET behavior, checkpointed GPR/FPR/VMX/VSX round trips, SPR note values after transaction abort/suspend paths, compat coredumps, and negative tests for `-ENODEV` and `-ENODATA`.
