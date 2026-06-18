# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_fp.c

Purpose: This file manages guest and host floating-point state for RISC-V KVM and exposes F/D register state through the KVM one-reg ABI. It resets guest FS state, lazily saves dirty guest FP registers, restores guest FP state when enabled, preserves host FP state, and validates user register access sizes.

Important APIs/types/functions: Under `CONFIG_FPU`, core functions are `kvm_riscv_vcpu_fp_reset`, `kvm_riscv_vcpu_guest_fp_save`, `kvm_riscv_vcpu_guest_fp_restore`, `kvm_riscv_vcpu_host_fp_save`, and `kvm_riscv_vcpu_host_fp_restore`. ABI functions are `kvm_riscv_vcpu_get_reg_fp` and `kvm_riscv_vcpu_set_reg_fp` for `KVM_REG_RISCV_FP_F` and `KVM_REG_RISCV_FP_D`.

Control flow: Reset sets guest `sstatus.FS` to INITIAL when F or D is exposed and OFF otherwise. Guest save only writes back registers when FS is DIRTY, choosing D save before F when D is available, then marks FS CLEAN. Restore loads F/D registers when FS is not OFF and marks clean. Host save/restore mirrors host availability. One-reg handlers select fcsr or f[0..31], enforce 32-bit F register/fcsr or 64-bit D register sizes, use nospec indexing, and copy values to or from userspace.

State and persistence: Guest FP state persists inside `vcpu->arch.guest_context.fp`, plus FS bits in guest `sstatus`. Host temporary state persists in `vcpu->arch.host_context` while guest state is active. One-reg writes directly mutate saved guest FP state.

Dependencies and integration points: It depends on RISC-V FPU assembly helpers, cpufeature/ISA checks, KVM one-reg dispatch in `vcpu_onereg.c`, and vCPU load/put in `vcpu.c`.

Risks and test signals: FS state must correctly track dirty/clean/off or guest FP state can be lost or host FP state corrupted. Tests should cover F-only, D, and no-FPU guests, one-reg get/set size validation, fcsr handling, guest dirty-save behavior, host FP preservation across KVM_RUN, and build coverage with `CONFIG_FPU` disabled.
