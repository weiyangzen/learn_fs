# sources/distributed-fs/ceph-client/arch/riscv/kvm/nacl.c

Purpose: This file implements KVM support for the SBI Nested Acceleration extension. It probes NACL and feature availability, allocates per-CPU shared memory, enables/disables NACL shmem on CPU virtualization entry/exit, and queues shared-memory HFENCE requests for accelerated synchronization.

Important APIs/types/functions: Static keys include `kvm_riscv_nacl_available`, `kvm_riscv_nacl_sync_csr_available`, `kvm_riscv_nacl_sync_hfence_available`, `kvm_riscv_nacl_sync_sret_available`, and `kvm_riscv_nacl_autoswap_csr_available`. `DEFINE_PER_CPU(struct kvm_riscv_nacl, kvm_riscv_nacl)` stores shmem virtual/physical addresses. Public functions are `__kvm_riscv_nacl_hfence`, `kvm_riscv_nacl_enable`, `kvm_riscv_nacl_disable`, `kvm_riscv_nacl_init`, and `kvm_riscv_nacl_exit`.

Control flow: Init requires SBI 1.0+ and the NACL extension, enables the base static key, probes individual NACL features, and allocates zeroed per-CPU shared-memory pages. CPU enable sets the per-CPU shared memory through `SBI_EXT_NACL_SET_SHMEM`; disable passes the SBI disable sentinel. HFENCE enqueue searches NACL shmem entries for a nonpending slot, tries a sync flush up to five times if full, and writes little-endian control/page/count fields.

State and persistence: Per-CPU shmem persists from module init to NACL exit and is registered/unregistered with firmware on CPU virtualization enable/disable. Feature static keys persist module-wide and drive optimized CSR, HFENCE, SRET, and autoswap paths in other files.

Dependencies and integration points: It depends on SBI extension calls and NACL shmem layout macros from `asm/kvm_nacl.h`. It is used by `main.c` CPU hooks, `vcpu.c` context switching and CSR sync, `vcpu_config.c` CSR load, and `tlb.c` HFENCE request processing.

Risks and test signals: Shared-memory entries can fill under heavy HFENCE load; the retry path must not spin indefinitely or silently corrupt pending entries. Tests should cover absence of NACL, all feature-bit combinations, per-CPU allocation failure cleanup, CPU enable/disable SBI errors, HFENCE queue saturation warning, little-endian shmem encoding, and fallback to direct CSR/HFENCE paths.
