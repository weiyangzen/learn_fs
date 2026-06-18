# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_asm.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_asm.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_asm.h

### Purpose
`kvm_asm.h` is the ABI between C code and ARM64 KVM hypervisor assembly. It names exception codes, SMCCC hypercalls, hyp symbols, per-CPU hyp data accessors, init parameter blocks, and low-level hyp entry points.

### Important APIs, Types, And Functions
Notable exports include `ARM_EXCEPTION_*`, `KVM_HOST_SMCCC_FUNC()`, `enum __kvm_host_smccc_func`, symbol-selection macros (`DECLARE_KVM_*_SYM`, `CHOOSE_*_SYM`, `kvm_nvhe_sym`), `struct kvm_nvhe_init_params`, `struct kvm_nvhe_stacktrace_info`, `__kvm_flush_*`, `__kvm_tlb_flush_*`, `__kvm_at_*`, `__kvm_vcpu_run()`, `__kvm_adjust_pc()`, hyp panic handlers, PSCI entry points, and CPU context offsets for assembly.

### Control Flow
EL1 uses SMCCC/HVC calls for nVHE hyp services; VHE may call functions directly. Hyp assembly uses the declared symbols and offsets to save/restore CPU context, run vCPUs, perform TLB maintenance, and handle unexpected EL2 traps.

### State, Persistence, And Dependencies
State includes nVHE init params, per-CPU hyp bases, stacktrace info, and hyp-only symbol addresses. It depends on hyp image/linker naming, `asm/insn.h`, `asm/virt.h`, `asm/sysreg.h`, and generated offsets.

### Integration Points
KVM world switch, pKVM, hyp initialization, PSCI, TLB invalidation, GIC virtualization, and backtrace/panic paths all consume this header.

### Risks
C/assembly ABI drift is severe: bad offsets corrupt register state. Symbol choice macros must prevent illegal VHE/nVHE references. SMCCC function numbering is an ABI with hyp code.

### Test Signals
Build VHE, nVHE, and pKVM configs; run KVM selftests, hyp panic/backtrace tests, vCPU run loops, and TLB invalidation stress; inspect generated asm offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_asm.h -->
