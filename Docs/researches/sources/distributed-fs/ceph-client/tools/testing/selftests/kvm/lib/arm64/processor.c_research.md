# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/processor.c

## Purpose
This is the arm64 processor backend for KVM selftests. It implements guest page-table management, vCPU setup, exception handling, guest-mode probing, SMCCC calls, and default VGIC integration.

## Important APIs, Types, and Functions
Page-table helpers include `virt_arch_pgd_alloc()`, `_virt_pg_map()`, `virt_get_pte_hva_at_level()`, `addr_arch_gva2gpa()`, and `virt_arch_dump()`. vCPU setup flows through `kvm_get_default_vcpu_target()`, `aarch64_vcpu_setup()`, `aarch64_vcpu_add()`, and `vm_arch_vcpu_add()`. Exception APIs include `vm_init_descriptor_tables()`, `vm_install_sync_handler()`, `vm_install_exception_handler()`, `route_exception()`, and `assert_on_unhandled_exception()`. Architecture hooks include `kvm_selftest_arch_init()`, `kvm_arch_vm_post_create()`, `kvm_arch_vm_finalize_vcpus()`, and `kvm_arch_vm_release()`.

## Control Flow
VM page mappings allocate page tables lazily according to the selected guest mode and LPA2 format. vCPU setup initializes target features, FP/ASIMD, SCTLR/TCR/MAIR/TTBR/TPIDR, stack pointer, and optional EL2 state. Exception vectors route synchronous exceptions by ESR EC and asynchronous vectors by vector number. VM post-create optionally enables MTE and creates a default VGICv3; finalize initializes the VGIC.

## State, Dependencies, and Integration
Static state tracks the guest exception handler table GVA and default feature requests (`request_mte`, `request_vgic`). It depends on KVM ARM ioctls, sysreg IDs, `guest_modes`, `vgic`, and generic `kvm_util` allocation.

## Risks and Test Signals
Risks include incorrect PTE address encoding for 52-bit/LPA2 modes, unsupported guest modes, and implicit default VGIC behavior affecting tests. Signals are assertion failures, unexpected exception ucalls, or failed KVM register/device ioctls.
