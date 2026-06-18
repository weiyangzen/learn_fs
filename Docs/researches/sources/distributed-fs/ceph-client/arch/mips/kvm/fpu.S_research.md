## sources/distributed-fs/ceph-client/arch/mips/kvm/fpu.S

Purpose: Provides assembly routines for saving/restoring guest FPU register state and restoring FCSR for MIPS KVM.

Important APIs, types, and functions: Exports leaf routines `__kvm_save_fpu`, `__kvm_restore_fpu`, and `__kvm_restore_fcsr`. They use offsets from `asm-offsets.h` into `struct kvm_vcpu_arch`.

Control flow: Save/restore routines inspect CP0 Status.FR by shifting status and branching. If FR=1, odd double registers are saved/restored; even registers are always handled. `__kvm_restore_fcsr` loads `VCPU_FCR31` and writes FCR31 with `ctc1`.

State and persistence: Reads/writes guest FPU state in the VCPU arch save area: FPR0-FPR31 and FCR31. Hardware FPU registers are volatile CPU state owned temporarily by the guest when KVM enables CU1.

Dependencies and integration points: Called from `mips.c` FPU ownership paths and exit re-entry handling. The `ctc1` instruction offset in `__kvm_restore_fcsr` is part of the contract with `kvm_mips_csr_die_notify()`, which steps over harmless FP exceptions caused by guest FCSR cause bits.

Risks: Offset or instruction-order changes can break die-notifier matching. FR mode handling must match the guest CP0 Status state or odd doubles can be corrupted. These routines require hard-float assembly support and correct hazard handling by callers.

Test signals: Guest FPU enable/disable, FR=0 and FR=1 modes, odd-double access rejection in userspace register APIs, migration/save-restore cycles, and FCSR values with pending exception bits.
