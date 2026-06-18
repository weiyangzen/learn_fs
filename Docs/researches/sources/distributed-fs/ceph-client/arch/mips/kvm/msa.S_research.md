## sources/distributed-fs/ceph-client/arch/mips/kvm/msa.S

Purpose: Provides assembly routines for saving/restoring MIPS SIMD Architecture vector state and MSACSR for KVM guests.

Important APIs, types, and functions: Exports `__kvm_save_msa`, `__kvm_restore_msa`, `__kvm_restore_msa_upper`, and `__kvm_restore_msacsr`. The `kvm_restore_msa_upper` macro restores upper 64 bits of each 128-bit vector, with 64-bit and endian-specific 32-bit variants.

Control flow: Full save/restore stores or loads all 32 vector registers through `st_d`/`ld_d` macros into the FPR save area. Upper restore patches only the high half of each vector when FPU lower state is already live. MSACSR restore loads `VCPU_MSA_CSR` and writes it with `_ctcmsa`.

State and persistence: Reads/writes MSA vector state in the VCPU FPR storage and `msacsr`. Hardware MSA registers are temporary live guest CPU state when MSA is enabled.

Dependencies and integration points: Used by `mips.c` MSA ownership paths. The `_ctcmsa` instruction location is part of the die-notifier contract in `kvm_mips_csr_die_notify()` for harmless MSA FP exceptions during MSACSR restore.

Risks: Endianness and 32/64-bit paths must preserve vector lane order. Instruction offset changes in `__kvm_restore_msacsr` can break exception recovery. Upper-only restore assumes lower FPU state is already valid and FR/MSA enable sequencing is correct.

Test signals: MSA capability enable, full restore from cold state, upper restore after FPU-only state, endian-specific vector register ABI checks, MSACSR pending exception bits, and VCPU migration/save/restore.
