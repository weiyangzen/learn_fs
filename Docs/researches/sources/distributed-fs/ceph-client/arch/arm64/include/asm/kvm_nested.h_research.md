# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_nested.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_nested.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_nested.h

### Purpose
`kvm_nested.h` defines ARM64 nested virtualization helpers for exposing virtual EL2, translating EL2-style registers, managing nested stage-2 MMUs, walking guest stage-2 tables, validating TLBI operations, and translating virtual addresses.

### Important APIs, Types, And Functions
Important exports include `vcpu_has_nv()`, `translate_tcr_el2_to_tcr_el1()`, `translate_cptr_el2_to_cpacr_el1()`, `translate_sctlr_el2_to_sctlr_el1()`, `translate_ttbr0_el2_to_ttbr0_el1()`, nested init/load/sync functions, `struct kvm_s2_trans`, `kvm_walk_nested_s2()`, `kvm_s2_handle_perm_fault()`, `kvm_inject_s2_fault()`, TLBI support checks, `decode_range_tlbi()`, `struct s1_walk_info`, `struct s1_walk_result`, `__kvm_translate_va()`, VNCR helpers, and `__kvm_at_swap_desc()`.

### Control Flow
When a vCPU has virtual EL2, KVM translates guest hypervisor state into host-manageable EL1/EL2 forms, selects nested or canonical stage-2 MMUs, walks L1-provided stage-2 tables, injects virtual faults, and handles TLBI/VNCR traps.

### State, Persistence, And Dependencies
State lives in nested MMU arrays, VNCR TLBs, vCPU sysregs, stage-1 walk context, and `struct kvm_s2_trans` results. It depends on `kvm_emulate.h`, `kvm_pgtable.h`, sysreg/TLBI definitions, and CPU nested-virt capability.

### Integration Points
Used by sysreg emulation, abort handling, stage-2 MMU management, nested TLB invalidation, and guest AT instruction emulation.

### Risks
Nested translation bugs can grant wrong permissions or inject wrong faults. TLBI range decoding must respect feature exposure. Register translation is sensitive to VHE/nVHE and E2H/TGE semantics.

### Test Signals
Run nested KVM selftests, L1 guest hypervisor boots, TLBI range tests, VNCR abort tests, AT instruction tests, S2 permission fault tests, and ptrauth ERET checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_nested.h -->
