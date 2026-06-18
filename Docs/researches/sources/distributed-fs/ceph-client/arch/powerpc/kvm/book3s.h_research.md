# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s.h

## Purpose
Declares internal Book3S KVM entry points shared between the common Book3S core, PR implementation, HV implementation, and MMU/memslot code.

## Important APIs, Types, And Functions
Declarations include HV memslot/MMU invalidation hooks `kvmppc_core_flush_memslot_hv`, `kvm_unmap_gfn_range_hv`, `kvm_age_gfn_hv`, and `kvm_test_age_gfn_hv`; PR hooks `kvmppc_mmu_init_pr`, `kvmppc_mmu_destroy_pr`, `kvmppc_core_emulate_op_pr`, `kvmppc_core_emulate_mtspr_pr`, `kvmppc_core_emulate_mfspr_pr`, `kvmppc_book3s_init_pr`, `kvmppc_book3s_exit_pr`, and `kvmppc_handle_exit_pr`; transactional-memory abort emulation; and HV interrupt/MSR helpers `kvmppc_set_msr_hv` and `kvmppc_inject_interrupt_hv`.

## Control Flow
This header has no runtime control flow. It supplies compile-time contracts that allow common Book3S code and mode-specific files to call each other.

## State And Persistence
No state is stored here. The declared functions operate on `struct kvm`, `struct kvm_vcpu`, `struct kvm_memory_slot`, and `struct kvm_gfn_range` owned by KVM core and mode-specific implementations.

## Dependencies And Integration Points
Integrates Book3S PR, Book3S HV, transactional memory, and generic KVM memory invalidation paths. The `CONFIG_PPC_TRANSACTIONAL_MEM` guard provides a no-op inline when TM is unavailable.

## Risks And Edge Cases
Prototype drift between this header and C definitions breaks builds or, worse for assembly-adjacent code, ABI assumptions. The no-op TM helper must be acceptable for non-TM builds. HV and PR hooks have similar names but different semantics, so caller selection must be mode-aware.

## Test Signals
Compile coverage across PR-only, HV-only, PR+HV possible, and no transactional-memory configurations is the main signal. Runtime signals come indirectly from memslot invalidation, PR emulation, and HV interrupt injection tests.
