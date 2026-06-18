# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_onereg.c

Purpose: This file implements the RISC-V KVM one-reg ABI for vCPU configuration, core registers, CSRs, ISA extensions, timers, FP, vector, SBI extension state, and register-list enumeration. It is the main userspace migration/configuration interface for vCPU architectural state.

Important APIs/types/functions: `kvm_riscv_vcpu_setup_isa` initializes the guest ISA bitmap from host-supported and allowed extensions. Get/set helpers cover config registers, core registers, general/AIA/Smstateen CSRs, single and multi ISA extension registers, and register-index copy/count functions. Public APIs are `kvm_riscv_vcpu_num_regs`, `kvm_riscv_vcpu_copy_reg_indices`, `kvm_riscv_vcpu_set_reg`, and `kvm_riscv_vcpu_get_reg`.

Control flow: Config getters return base ISA, cache block sizes, vendor IDs, and SATP mode. Config setters allow base ISA and vendor ID changes only before first run and validate block sizes as read-only host properties. Core access maps PC, GPRs, and mode to `guest_context`. CSR access dispatches to general, AIA, or Smstateen subtypes and marks `csr_dirty` on successful writes. ISA extension access supports old single-register and newer multi-register enable/disable masks, applying host availability plus policy from `isa.c`. Register-list construction emits only state supported by the current guest ISA.

State and persistence: One-reg writes directly modify persistent vCPU state: ISA bitmaps, vendor IDs, guest context, CSR shadows, timer/FP/vector/SBI state, and dirty flags. Many configuration fields become immutable once `ran_atleast_once` is true. `csr_dirty` persists until the next vCPU load reloads CSRs.

Dependencies and integration points: It depends on cpufeature and ISA policy, cache-block globals, AIA CSR helpers, timer/FP/vector/SBI one-reg helpers, KVM user-copy APIs, and the vCPU ioctl path in `vcpu.c`.

Risks and test signals: Register ID encoding and size validation are ABI-critical for migration. Multi-extension setters currently ignore individual helper return values inside the mask loop, so tests should confirm unsupported bits do not silently produce unexpected guest state. Tests should cover GET_REG_LIST counts against actual copied indices, pre-run/post-run config mutability, CSR dirty reload, AIA/Smstateen conditional CSR exposure, RV32/RV64 sizes, vector variable-size registers, and migration round trips.
