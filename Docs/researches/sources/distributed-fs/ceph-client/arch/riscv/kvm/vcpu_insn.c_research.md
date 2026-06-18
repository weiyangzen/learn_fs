# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_insn.c

Purpose: This file emulates trapped guest instructions that KVM can handle in-kernel and prepares exits for userspace emulation. It covers virtual instruction faults for SYSTEM opcodes, CSR accesses, WFI/WRS behavior, illegal/virtual trap injection, MMIO load/store decoding, and completion of MMIO or CSR exits.

Important APIs/types/functions: `struct insn_func` and `struct csr_func` define decode tables. Trap helpers are `truly_illegal_insn` and `truly_virtual_insn`. Runtime APIs include `kvm_riscv_vcpu_wfi`, `kvm_riscv_vcpu_csr_return`, `kvm_riscv_vcpu_virtual_insn`, `kvm_riscv_vcpu_mmio_load`, `kvm_riscv_vcpu_mmio_store`, and `kvm_riscv_vcpu_mmio_return`. CSR handling integrates AIA, HPM counter, and seed CSR callbacks.

Control flow: Virtual instruction emulation uses `stval` when available or unprivileged instruction fetch when not, rejects compressed SYSTEM traps as illegal, then dispatches SYSTEM instructions. CSR instructions decode read/write masks and new values, populate `run->riscv_csr`, try in-kernel CSR handlers first, complete in-kernel reads immediately, or exit to userspace. WFI may halt the vCPU until runnable; WRS calls spin/yield handling. MMIO load/store decode transformed `htinst` or fetch the original instruction, determine width/sign-extension and source/destination register, try KVM MMIO bus access, and either complete immediately or populate `run->mmio` for userspace.

State and persistence: Decode state persists across userspace exits in `vcpu->arch.csr_decode` and `vcpu->arch.mmio_decode`, including return-handled flags to avoid double completion. Instruction completion advances guest `sepc`; load completion writes the destination register.

Dependencies and integration points: It depends on RISC-V instruction masks, compressed instruction helpers, CSR emulation from AIA/PMU, MMIO bus, unprivileged read/trap redirection in `vcpu_exit.c`, and the run-loop return handling in `vcpu.c`.

Risks and test signals: Instruction decoding must distinguish signed/unsigned loads, compressed register aliases, transformed instruction lengths, and misaligned MMIO. Tests should cover all load/store widths on RV32/RV64, compressed MMIO forms, in-kernel versus userspace MMIO, CSR read/write/set/clear/immediate variants, seed CSR userspace exits, WFI wakeup, WRS accounting, and illegal/virtual trap injection.
