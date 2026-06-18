# sources/distributed-fs/ceph-client/arch/arm64/kvm/fpsimd.c

## Purpose

This file coordinates host and guest FPSIMD/SVE register ownership around vCPU load, guest entry, guest exit, and vCPU put. It is the host-side companion to the hyp lazy-FP trap path.

## Important APIs, Types, And Functions

The exported hooks are `kvm_arch_vcpu_load_fp()`, `kvm_arch_vcpu_ctxflush_fp()`, `kvm_arch_vcpu_ctxsync_fp()`, and `kvm_arch_vcpu_put_fp()`. They use `fpsimd_save_and_flush_cpu_state()`, `guest_owns_fp_regs()`, `fpsimd_bind_state_to_cpu()`, `TIF_FOREIGN_FPSTATE`, `FP_STATE_FREE`, and `struct cpu_fp_state`.

## Control Flow

On vCPU load, host FP/SVE/SME state is saved and flushed, and hyp ownership is marked free. Just before non-preemptible guest entry, any foreign FP state observed after host kernel FP use clears ownership again. On guest exit, if the guest owns hardware FP registers, the vCPU FP or SVE backing state is bound to CPU context tracking. On vCPU put, local IRQs are disabled and guest-owned FP state is saved/flushed so later host FP use cannot consume stale guest data.

## State And Persistence Behavior

Persistent state lives in `vcpu->arch.ctxt.fp_regs`, `vcpu->arch.sve_state`, `sve_max_vl`, `fp_type`, `SVCR`, `FPMR`, host per-CPU `fp_owner`, and the current thread's `TIF_FOREIGN_FPSTATE`. The code intentionally leaves host userspace restoration to normal FPSIMD tracking.

## Dependencies And Integration Points

It integrates with scheduler FPSIMD state management, hyp `host_data_ptr(fp_owner)`, SVE/SME feature checks, and the hyp file `switch.h` that lazily restores guest FP after a trap.

## Risks And Test Signals

Risks include stale guest data exposure, incorrect SVE vector-length binding, SME state leakage, and calling paths with IRQ/preemption assumptions violated. Test signals are FP/SVE guest migration, host kernel NEON use between exits, SVE-enabled vCPU get/set state, and `WARN_ON_ONCE` triggers for SME `SVCR` or IRQ state.
