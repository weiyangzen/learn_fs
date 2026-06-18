# sources/distributed-fs/ceph-client/arch/loongarch/kvm/switch.S

Purpose: provides the low-level LoongArch KVM world switch, guest exception entry, and FPU/LSX/LASX save/restore assembly routines.

Important APIs, types, and functions: exported symbols include `kvm_exc_entry`, `kvm_enter_guest`, `kvm_save_fpu()`, `kvm_restore_fpu()`, optional `kvm_save_lsx()`, `kvm_restore_lsx()`, `kvm_save_lasx()`, and `kvm_restore_lasx()`. Macros save/restore host and guest GPRs and implement `kvm_switch_to_guest`.

Control flow: `kvm_enter_guest()` saves host callee state, stores host SP/TP/per-CPU register in vCPU arch state, writes the vCPU pointer to scratch CSR, and branches into `kvm_switch_to_guest`. The switch macro programs ECFG/EENTRY/ERA/PGDL/GTLBC/PRMD/GSTAT, restores guest GPRs, and executes `ertn`. `kvm_exc_entry` saves guest GPR/CSR exit state, restores host exception state and PGD, clears guest mode/TGID, calls the C exit handler, and either resumes guest or returns to host.

State and persistence: moves state between hardware CSRs/GPRs and `struct kvm_vcpu_arch` fields. Scratch CSRs hold the vCPU pointer and temporary A2 during exception entry.

Dependencies and integration points: tightly coupled to `asm-offsets.h`, CSR definitions, `vcpu.c` run/load paths, `main.c` world-switch ops, exception entry placement, unwind hints, and aux state functions called by `vcpu.c`.

Risks: register offset mismatch or missing save/restore corrupts host or guest state. World-switch code must avoid TLB-dependent paths while PGD/context are transient. Interrupt and PRMD/GSTAT sequencing affects host interrupt responsiveness and guest entry correctness.

Test signals: booting guests, stress with interrupts and exits, register preservation tests, FPU/LSX/LASX context tests, lockdep/noinstr validation, and unwinder behavior through nonstandard frames.
