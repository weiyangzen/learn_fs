<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/sys_regs.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/sys_regs.c

## Purpose
`sys_regs.c` defines the protected-VM system-register policy. It computes sanitized AArch64 ID-register values, handles allowed RAZ/WI or host-handled sysregs, injects undefined/synchronous exceptions for restricted accesses, and validates that the sysreg descriptor table is sorted.

## Important APIs, Types, and Functions
Global `id_aa64*_*_sys_val` variables hold sanitized host CPU feature values visible to hyp. `struct pvm_ftr_bits` describes feature-field maximums and optional VM-support predicates. `get_restricted_features()` clamps system feature fields to pVM-supported values. `pvm_calc_id_reg()` computes individual ID register values. Accessors include `pvm_access_raz_wi()`, `pvm_access_id_aarch32()`, `pvm_access_id_aarch64()`, `pvm_gic_read_sre()`, and `pvm_idst_access()`. `pvm_sys_reg_descs[]` is the sorted policy table. Public APIs are `kvm_init_pvm_id_regs()`, `kvm_check_pvm_sysreg_table()`, `kvm_handle_pvm_sysreg()`, and `kvm_handle_pvm_restricted()`.

## Control Flow, State, and Persistence
During vCPU initialization, protected VM ID registers are calculated once under `vm_table_lock` and stored in `kvm->arch.id_regs`, then `KVM_ARCH_FLAG_ID_REGS_INITIALIZED` is set. Runtime sysreg exits decode ESR into parameters, binary-search the descriptor table, inject undefined for absent descriptors, return false for host-handled descriptors, and otherwise execute the hyp accessor and optionally skip the guest instruction.

## Dependencies and Integration Points
It depends on KVM sysreg descriptors, ID register field macros, pKVM feature gating, exception injection helpers, VGIC definitions, and protected guest exit dispatch in `switch.c`. It also interacts with `pkvm.c` when initializing protected vCPU features and trap settings.

## Risks and Test Signals
Risks include exposing unsupported CPU features to protected guests, descriptor table ordering errors, wrong signed-field clamping, accidental host handling for sensitive registers, and exception injection while sysregs are live. Test signals are `kvm_check_pvm_sysreg_table()` at init, guest reads of each ID register, writes to ID registers injecting undef, RAZ/WI debug/error registers, GIC SRE reads, IDS-dependent behavior, and fuzzing unlisted sysreg encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/sys_regs.c -->
