# sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/kvm.h

## Purpose
Large PowerPC userspace KVM ABI header for tools, covering register state, special registers, BookE/BookS MMU state, TCE/RMA/RTAS, hash page-table streaming, radix MMU configuration, CPU characteristics, XICS/XIVE interrupt controllers, and one-reg IDs.

## Important APIs, Types, and Functions
Key types include `struct kvm_regs`, feature-gated `struct kvm_sregs`, `kvm_fpu`, debug structs, TCE creation structs, `kvm_rtas_token_args`, Book3E TLB structs, `kvm_get_htab_fd/header`, `kvm_ppc_mmuv3_cfg`, `kvm_ppc_rmmu_info`, `kvm_ppc_cpu_char`, `kvm_ppc_xive_eq`, `kvm_ppc_pvinfo`, `kvm_ppc_smmu_info`, and `kvm_ppc_resize_hpt`. Macros enumerate many one-reg IDs for SPRs, FPR/VR/VSR, TM checkpointed state, ICP/VP state, and XICS/XIVE attributes.

## Control Flow, State, and Persistence
This is ABI layout, not implementation. Userspace fills ioctls and register IDs; kernel KVM owns guest CPU/MMU/interrupt state. Feature bits in `kvm_sregs` gate which embedded registers are valid or updated, and special update bits avoid clobbering asynchronous state.

## Dependencies and Integration Points
Depends on `linux/types.h` and generic KVM register-size namespaces. Integrated with PowerPC KVM userspace, migration/checkpointing, interrupt controller device APIs, and perf/test tools.

## Risks and Test Signals
Risks are high because padding, feature bits, and one-reg IDs are ABI. Particular risks include partial 64-bit debug register exposure, special-update semantics, HPT stream format compatibility, and XIVE/XICS attribute packing. Test signals are KVM selftests, migration round trips across BookE/BookS and ppc32/ppc64, one-reg enumeration tests, and interrupt controller save/restore.
