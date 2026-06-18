# sources/distributed-fs/ceph-client/arch/mips/include/asm/switch_to.h

## Purpose

`switch_to.h` defines MIPS scheduler context-switch orchestration around the low-level `resume()` assembly routine.

## Important APIs, Types, And Functions

Key APIs are `switch_to()`, `resume()`, LL/SC clearing helpers, FPU-affinity cleanup, `__sanitize_fcr31()`, DSP/COP2 save-restore hooks, userlocal register reload, and watch-register restoration. Includes: `asm/cpu-features.h`, `asm/watch.h`, `asm/dsp.h`, `asm/cop2.h`, `asm/fpu.h`. Macros/constants: `_ASM_SWITCH_TO_H`, `__mips_mt_fpaff_switch_to`, `__clear_r5_hw_ll_bit`, `__clear_software_ll_bit`, `__sanitize_fcr31`, `switch_to`. Types/enums/unions: `task_struct`, `thread_info`. Functions/prototypes/helpers: `resume`, `task_thread_info`, `clear_ti_thread_flag`, `write_c0_lladdr`, `mask_fcr31_x`, `force_fcr31_sig`, `__mips_mt_fpaff_switch_to`, `lose_fpu_inatomic`, `__sanitize_fcr31`, `__save_dsp`, `__restore_dsp`, `read_c0_status`, `set_c0_status`, `cop2_save`, `cop2_restore`, `write_c0_status`, `__clear_r5_hw_ll_bit`, `__clear_software_ll_bit`, `__restore_watch`.

## Control Flow

On a context switch the macro handles FPU ownership, optional FPU-affinity mask relaxation, pending FCSR exception signaling, DSP and COP2 state save/restore, hardware and software LL-bit clearing, user TLS reload through CP0 UserLocal, hardware watchpoint restoration, then calls `resume(prev,next,next_ti)`.

## State And Persistence

State includes per-task FPU/DSP/COP2/watch/TLS fields, global software LL state (`ll_bit`, `ll_task`), CP0 UserLocal, and scheduler-visible CPU masks. No filesystem persistence exists.

## Dependencies And Integration Points

It depends on CPU feature detection, `watch.h`, DSP/COP2/FPU helpers, `thread_info`, task register state, and scheduler switch semantics.

## Risks

Risks include leaked FPU/COP2/DSP state between tasks, incorrect LL/SC semantics after context switch, spurious or missed FP exceptions, lost TLS, and watchpoint misprogramming.

## Test Signals

Test signals are context-switch stress, FP/DSP/MSA workloads, ptrace watchpoints, MIPS MT FPU affinity tests, and LL/SC atomic stress.
Static review signal: this source currently has 143 lines and 4455 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
