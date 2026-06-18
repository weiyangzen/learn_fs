# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/fpsimd.S

## Purpose

This assembly wrapper exposes hyp-callable FPSIMD and SVE save/restore entry points backed by arm64 FPSIMD macros.

## Important APIs, Types, And Functions

The symbols are `__fpsimd_save_state`, `__fpsimd_restore_state`, `__sve_restore_state`, and `__sve_save_state`. They expand to `fpsimd_save`, `fpsimd_restore`, `sve_load`, and `sve_save`.

## Control Flow

Each symbol is a straight-line wrapper: save/restore the requested vector state and return. SVE wrappers pass through their arguments to the macro implementation.

## State And Persistence Behavior

The file reads or writes architectural FP/SIMD/SVE registers and memory buffers provided by the caller. It has no static state.

## Dependencies And Integration Points

It is called from `hyp/include/hyp/switch.h` during lazy FP/SVE switching. It depends on `asm/fpsimdmacros.h` and correct caller-managed vector lengths.

## Risks And Test Signals

Risks are ABI mismatch with macro arguments, wrong active SVE VL before save/restore, and clobber assumptions around hyp calls. Test signals are FPSIMD-only and SVE guest state preservation across exits and host FP use.
